#!/usr/bin/env python3
import time
import datetime
import json
from threading import Thread, Semaphore

import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue               import YtQueue, YtTask
from sqlrecord             import SqlRecord
from ytcommentworkerrecord import YTCommentWorkerRecord
from ytcommentrecord       import YTCommentRecord
from ytauthorrecord        import YTAuthorRecord
from ytvideorecord         import YTVideoRecord

from sqlsingleton          import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class Options:
  # Placeholder for options, FIXME: is there something better?
  options=None


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadWorkerRecord(SqlRecord,Base):
  __tablename__ = 'ytthreadworkers0_5'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  firstthreadcid           = sqlalchemy.Column(sqlalchemy.Unicode(50))
  firstthreadcidcandidate  = sqlalchemy.Column(sqlalchemy.Unicode(50))
  nexttreadpagetoken       = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,dbsession,yid,commit=True):
    self.yid=yid
    super().__init__(dbsession,commit)

  def populate_default(self):
    self.lastwork=None
    self.firstthreadcidcandidate=None
    self.firstthreadcid=None
    self.nexttreadpagetoken=None


  def call_sql_task_threaded(self,priority=0,semaphore=None,options=None):
    logging.debug(type(self).__name__+".call_sql_task_threaded(): START")
    task=YtTask('populate: '+type(self).__name__
                +" - "+str(self.get_id()),type(self),self.get_id(),priority,semaphore,options)
    if not YtQueue().add(task):
      time.sleep(30)
    logging.debug(type(self).__name__+".call_sql_task_threaded(): END")


  def get_tlc_date_tid(self,thread):
    date=datetime.datetime.strptime(
      thread['snippet']['topLevelComment']['snippet']['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
    tid=thread['id']
    return (date,tid)


  def set_options(self,options):
    if (not options):
      options=Options()
      options.force_restart =False
      options.force_continue=False
      options.force_refresh =False
    return options

  def manage_first_request(self,youtube):
    logging.debug("YTThreadWorkerRecord.manage_first_request(): START")
    request=youtube.commentThreads().list(
          part='id,snippet,replies',
          videoId=self.yid,
          maxResults=100)
    # We cannot use option here, we have to force a refresh
    result=request.execute(True)

    if (len(result['items']) == 0):
      raise # Should never occurs
    pintid=None
    (date0,tid0)=self.get_tlc_date_tid(result['items'][0])
    #logging.debug(date0)
    if (len(result['items']) == 1):
      #logging.debug("GARP 1")
      tid=tid0
    else:
      #logging.debug("GARP 2")
      (date1,tid1)=self.get_tlc_date_tid(result['items'][1])
      #logging.debug(date1)
      if date0>date1:
        #logging.debug("GARP 3")
        tid=tid0
      else:
        #logging.debug("GARP 4")
        tid=tid1
        pintid=tid0,
    logging.debug("YTThreadWorkerRecord.manage_first_request(): END "+str(tid)+" "+str(pintid))
    return (tid,pintid,result)


  def sql_handle_start(self,dbsession,youtube,options):
    logging.debug("YTThreadWorkerRecord.sql_handle_start(): START : "+self.yid)
    # For a single misplaced comment by that fkng ggl API
    # we'll have to check
    # FIXME: can't handle video without any comment.
    result=None
    pintid=None
    if (not self.nexttreadpagetoken):
      logging.debug("YTThreadWorkerRecord.sql_handle_start(): no nextpagetoken")
      # first try or rework
      (tid,pintid,result)=self.manage_first_request(youtube)
      #print(tid)
      if (not self.firstthreadcid):
        # first try
         logging.debug("YTThreadWorkerRecord.sql_handle_start(): First scan")
         if (not self.firstthreadcidcandidate):
           self.firstthreadcidcandidate=tid
      else:
        # Rework: Check if there is anything new:
        #print(self.firstthreadcid)
        #print(self.nexttreadpagetoken)
        if (tid == self.firstthreadcid and not options.force_restart):
          # Nothing changed, return
          logging.debug("YTThreadWorkerRecord.sql_handle_start(): Nothing changed")
          self.lastwork=datetime.datetime.now()
          return (result,pintid)
        # Reworking
        logging.debug("YTThreadWorkerRecord.sql_handle_start(): force restart")
        self.firstthreadcidcandidate=tid
        self.firstthreadcid=None
        self.nexttreadpagetoken=None
    return (result,pintid)

  def close_commentworkerreccord(self,dbsession,ctr):
    ctr.completed(dbsession)

  def sql_handle_replies(self,dbsession,youtube,options,thread,ctr):
    logging.debug("YTThreadWorkerRecord.sql_handle_replies(): START : "+self.yid+" "+ctr.tid)
    replycount=thread['snippet']['totalReplyCount']
    if (replycount == 0): # Useless to run a commentspinner: there is nothing under
      self.close_commentworkerreccord(dbsession,ctr)
      return

    if not 'replies' in thread:  # As amazing as it looks, sometimes we don't have replies with non-zero reply count
      self.close_commentworkerreccord(dbsession,ctr)
      return

    replies=thread['replies']
    comments=replies['comments']
    #logging.debug("YTThreadWorkerRecord.sql_handle_replies(): 2 : "+str(replycount)+" "+str(len(comments)))
    if (len(comments)==replycount): # We have them all
      for jc in comments:
        cid=jc['id']
        c=get_dbobject(YTCommentRecord,cid,dbsession)
        c.fill_from_json(jc,dbsession,False)
      self.close_commentworkerreccord(dbsession,ctr)
    else: # There are too many comments in that thread, lets get them now.
      #logging.debug("YTThreadWorkerRecord.sql_handle_replies(): 3")
      ctr.sql_task_threaded(dbsession,youtube,options.force_refresh)
      #self.close_commentworkerreccord(dbsession,ctr) # redundent here


  def sql_handle_thread(self,dbsession,youtube,options,thread,pintid):
    logging.debug("YTThreadWorkerRecord.sql_handle_thread(): START : "+self.yid+" "+str(thread['id']))
    tid=thread['id']
    etag=thread['etag']
    tlc=thread['snippet']['topLevelComment']
    #cid=tlc['id'] # Is same at tid, actually
    if ((pintid) and (tid !=pintid)):
      ct=get_dbobject_if_exists(YTCommentWorkerRecord,tid,dbsession)
      if (ct and not options.force_continue): # That cid exists!
        logging.debug("YTThreadWorkerRecord.sql_handle_thread(): Merged with old: "
          +str(tid)+" "+str(self.yid))
        if (self.firstthreadcidcandidate):
          self.firstthreadcid=self.firstthreadcidcandidate
        else: # Should not happens
          raise
        self.nexttreadpagetoken=None
        self.lastwork=datetime.datetime.now()
        return False
    #logging.debug("YTThreadWorkerRecord.sql_handle_thread(): 2")
    # Still new stuff (or force_continue)
    #ct=get_dbobject_if_exists(YTCommentWorkerRecord,tid,dbsession)
    #logging.debug(ct)
    ctr=get_dbobject(YTCommentWorkerRecord,tid,dbsession)
    #logging.debug("YTThreadWorkerRecord.sql_handle_thread(): 3")
    if (options.force_continue):
      if (ctr.done and ctr.etag==etag): # Thread didn't changed, as verified by etags
        logging.debug("YTThreadWorkerRecord.sql_handle_thread(): same etags : "+etag)
        return True # We go to next thread, not rewriting anything
                    # FIXME: We should notify we looked a it, and it didn't change (maybe another date field?)

    #logging.debug("YTThreadWorkerRecord.sql_handle_thread(): 4 : "+self.yid)
    ctr.set_yid_etag(self.yid,etag,False)
    c=get_dbobject(YTCommentRecord,tid,dbsession)
    c.fill_from_json(tlc,dbsession,False)
    #print(thread['snippet'])
    self.sql_handle_replies(dbsession,youtube,options,thread,ctr)
    logging.debug("YTThreadWorkerRecord.sql_handle_thread(): END")
    return True


  def sql_task_threaded(self,dbsession,youtube,options=None):
    logging.debug("YTThreadWorkerRecord.sql_task_threaded(): START : "+self.yid)
    options=self.set_options(options)
    logging.debug("YTThreadWorkerRecord.sql_task_threaded(): self.firstthreadcid: "+str(self.firstthreadcid))
    if (self.firstthreadcid and not options.force_restart):
      logging.debug("YTThreadWorkerRecord.sql_task_threaded(): Won't redo : "+self.yid)
      return
    (result,pintid)=self.sql_handle_start(dbsession,youtube,options)
    if (not result):
      logging.debug("YTThreadWorkerRecord.sql_task_threaded(): not result")
      request=youtube.commentThreads().list(
        part='id,snippet,replies',
        videoId=self.yid,
        pageToken=self.nexttreadpagetoken,
        maxResults=100)
      result=request.execute(options.force_refresh)

    for thread in result['items']:
      if (not self.sql_handle_thread(dbsession,youtube,options,thread,pintid)):
        logging.debug("YTThreadWorkerRecord.sql_task_threaded(): break")
        return

    if ('nextPageToken' in result):
      self.nexttreadpagetoken=result['nextPageToken'].replace('=','') # FIXME: this is strange but needed.
    else:
      logging.debug("YTThreadWorkerRecord.sql_task_threaded(): end of all threads")
      self.firstthreadcid=self.firstthreadcidcandidate
      self.nexttreadpagetoken=None

    self.lastwork=datetime.datetime.now()
    print(self.firstthreadcid)
    print(self.nexttreadpagetoken)
    logging.debug("YTThreadWorkerRecord.sql_task_threaded(): END")


  def call_refresh(self,options):
    logging.debug("YTThreadWorkerRecord.call_refresh(): START : "+self.yid)
    task = Thread(target=self.refresh,args=(options,))
    task.start()

  def refresh(self,options):
    logging.debug("YTThreadWorkerRecord.refresh(): START : "+self.yid)
    dbsession=SqlSingleton().mksession()
    semaphore=Semaphore(1)
    # Ensuring we're working with a clean object in this threaded session:
    o=get_dbobject_if_exists(YTThreadWorkerRecord,self.yid,dbsession)
    if (not o):
      logging.debug("YTThreadWorkerRecord.refresh(): "+self.yid+" ERROR: non existing yid")
      return
    if (options.force_restart):
      o.nexttreadpagetoken=None
      o.firstthreadcid=None
      dbsession.commit()
    options.force_restart=False
    while not (o.firstthreadcid):
      logging.debug("YTThreadWorkerRecord.refresh(): o.firstthreadcid: "+str(o.firstthreadcid))
      semaphore.acquire()
      #dbsession.merge(o) # FIXME: I have to better understand
      dbsession.refresh(o) # FIXME: this is important but I dunno exactly why.
      o.call_sql_task_threaded(1000,semaphore,options)
      #dbsession.refresh(o) o=dbsession.merge(ytw) # FIXME: I have to better understand
      time.sleep(1)
      #logging.debug("YTThreadWorkerRecord.refresh(): self.firstthreadcid: 3")
    # Ensuring last call is processed before ending
    semaphore.acquire()
    semaphore.release()
    logging.debug("YTThreadWorkerRecord.refresh(): END")


def test_refresh():
  YtQueue(1)
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue().meanpriority=10000
  options=Options()
  options.force_restart =True
  options.force_continue=True
  options.force_refresh =True
  vidlist=get_video_ids_from_file('yturls.txt')
  ytwlist=[]
  for yid in vidlist:
    ytw=get_dbobject_if_exists(YTThreadWorkerRecord,yid,dbsession)
    if (not ytw): continue
    logging.debug("==== test_refresh: "+str(yid))
    ytw.refresh(options)
  YtQueue().join()
  dbsession.commit()


def refresh_all():
  YtQueue(1)
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue().meanpriority=10000
  #semaphore=Semaphore(1)
  #for v in dbsession.query(YTVideoRecord):
  #  if not v.suspended:
  #    logging.debug("refresh_all(): Do refresh for "+str(v.yid))
  #    semaphore.acquire()
  #    v.call_sql_task_threaded_never_give_up(1000,semaphore)
  #semaphore.acquire()
  #semaphore.release()

  for v in dbsession.query(YTVideoRecord):
    #print(v.yid)
    if (not v.suspended) and (v.yid >= 'xPksF_JFNEI'):
      #print(v.yid)
      #break
      #raise
      options=Options()
      options.force_restart =True
      options.force_continue=True
      options.force_refresh =True
      options.priority=1000
      ytw=get_dbobject(YTThreadWorkerRecord,v.yid,dbsession)
      dbsession.commit()
      ytw.refresh(options)
  YtQueue().join()
  dbsession.commit()


# --------------------------------------------------------------------------
def main():
  refresh_all()
  return


def old():
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue().meanpriority=10000
  options=Options()
  options.force_restart =False
  options.force_continue=True
  options.force_refresh =False
  ytw=get_dbobject_if_exists(YTThreadWorkerRecord,'TW6hgOc3wuI',dbsession)
  ytw.call_refresh(options)
  YtQueue().join()
  return
  ytw=get_dbobject_if_exists(YTThreadWorkerRecord,'C6hsgRWjf-4',dbsession)
  ytw.call_sql_task_threaded()
  YtQueue().join()
  dbsession.commit()
  return

  vidlist=get_video_ids_from_file('yturls.txt')
  ytwlist=[]
  for yid in vidlist:
    ytw=get_dbobject_if_exists(YTThreadWorkerRecord,yid,dbsession)
    if (not ytw): continue
    ytwlist.append(ytw)

  for i in range(100):
    for ytw in ytwlist:
      ytw.call_sql_task_threaded()
    time.sleep(1)
  YtQueue().join()
  dbsession.commit()
  #for ytw in ytwd[:2]:
  #  o=dbsession.merge(ytw)
  #  dbsession.commit()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

