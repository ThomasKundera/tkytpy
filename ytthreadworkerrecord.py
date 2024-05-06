#!/usr/bin/env python3
import time
import datetime
import json
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

  def get_priority_dont_use(self):
    dbsession=get_dbsession(self)
    ytv=get_dbobject_if_exists(YTVideoRecord,self.yid,dbsession)
    if (not ytv): return sys.maxsize
    if ((not ytv.valid) or (ytv.suspended)):
      return sys.maxsize
    # FIXME: refreshing priority value is also complex
    if not(self.lastwork):
      return 100
    Δt=(datetime.datetime.now()-self.lastwork).total_seconds()
    if (self.firstthreadcid): # We already done it once fully
      if (Δt<24*3600):  # FIXME
        return sys.maxsize
    # Fit that between 1000 and 2000
    # FIXME
    return max((30*24*3600-Δt)/3,100)


  def populate_default(self):
    self.lastwork=None
    self.firstthreadcidcandidate=None
    self.firstthreadcid=None
    self.ftcdate=None
    self.nexttreadpagetoken=None
    self.nextcmtpagetoken=None


  def get_tlc_date_tid(self,thread):
    date=datetime.datetime.strptime(
      thread['snippet']['topLevelComment']['snippet']['updatedAt'],"%Y-%m-%dT%H:%M:%SZ")
    tid=thread['id']
    return (date,tid)

  def manage_first_request(self,youtube):
    request=youtube.commentThreads().list(
          part='id,snippet,replies',
          videoId=self.yid,
          maxResults=100)
    result=request.execute(True)

    if (len(result['items']) == 0):
      raise # Should never occurs
    pintid=None
    (date0,tid0)=self.get_tlc_date_tid(result['items'][0])
    if (len(result['items']) == 1):
      tid=tid0
    else:
      (date1,tid1)=self.get_tlc_date_tid(result['items'][1])
      if date0>date1:
        tid=tid0
      else:
        tid=tid1
        pintid=tid0,

    return (tid,pintid,result)


  def sql_task_threaded(self,dbsession,youtube):
    # For a single misplaced comment by that fkng ggl API
    # we'll have to check
    logging.debug("YTThreadWorkerRecord.sql_task_threaded(): START : "+self.yid)
    # FIXME: can't handle video without any comment.
    result=None
    pintid=None
    if (not self.nexttreadpagetoken):
      # first try or rework
      (tid,pintid,result)=self.manage_first_request(youtube)
      print(tid)
      if (not self.firstthreadcid):
        # first try
         logging.debug("YTThreadWorkerRecord.sql_task_threaded(): First scan")
      else:
        # Rework: Check if there is anything new:
        print(self.firstthreadcid)
        if (tid == self.firstthreadcid):
          # Nothing changed, return
          logging.debug("YTThreadWorkerRecord.sql_task_threaded(): Nothing changed")
          self.lastwork=datetime.datetime.now()
          return
      # Reworking
      self.firstthreadcidcandidate=tid
      self.firstthreadcid=None
      self.nexttreadpagetoken=None

    if (not result):
      request=youtube.commentThreads().list(
        part='id,snippet,replies',
        videoId=self.yid,
        pageToken=self.nexttreadpagetoken,
        maxResults=100)
      result=request.execute()

    for thread in result['items']:
      tid=thread['id']
      etag=thread['etag']
      tlc=thread['snippet']['topLevelComment']
      #cid=tlc['id'] # Is same at tid, actually
      if ((pintid) and (tid !=pintid)):
        ct=get_dbobject_if_exists(YTCommentRecord,tid,dbsession) # FIXME: use comment worker record instead
        if (ct): # That cid exists!
          logging.debug("YTThreadWorkerRecord.sql_task_threaded(): Merged with old: "
            +str(tid)+" "+str(self.yid))
          self.firstthreadcid=self.firstthreadcidcandidate
          self.lastwork=datetime.datetime.now()
          return
      # Still new stuff...
      c=get_dbobject(YTCommentRecord,tid,dbsession)
      c.fill_from_json(tlc,dbsession,False)
      ct=get_dbobject(YTCommentWorkerRecord,tid,dbsession)
      ct.set_yid_etag(self.yid,etag,False)
      #print(thread['snippet'])
      replycount=thread['snippet']['totalReplyCount']
      if (replycount == 0): # Useless to run a commentspinner: there is nothing under
        ct.done=True
        ct.nextcmtpagetoken=None
        ct.lastwork=datetime.datetime.now()
      else:
        if not 'replies' in thread:
          break # As amazing as it looks, sometimes we don't have replies with non-zero reply count
        replies=thread['replies']
        comments=replies['comments']
        if (len(comments)==replycount): # We have them all
          for jc in comments:
            cid=jc['id']
            c=get_dbobject(YTCommentRecord,cid,dbsession)
            c.fill_from_json(jc,dbsession,False)
          ct.done=True
          ct.nextcmtpagetoken=None
          ct.lastwork=datetime.datetime.now()

    if ('nextPageToken' in result):
      self.nexttreadpagetoken=result['nextPageToken']
    else:
      self.firstthreadcid=self.firstthreadcidcandidate
      self.nexttreadpagetoken=None

    self.lastwork=datetime.datetime.now()
    logging.debug("YTThreadWorkerRecord.populate(): END")


# --------------------------------------------------------------------------
def main():
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue(1)
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

