#!/usr/bin/env python3
import time
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue         import YtQueue, YtTask
from sqlrecord       import SqlRecord
from ytcommentrecord import YTCommentRecord
from ytauthorrecord  import YTAuthorRecord
from ytvideorecord   import YTVideoRecord

# FIXME: this creates a loop
#from ytcommentthread import YTCommentThread


from sqlsingleton    import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord0(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_7'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50))
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  done                     = sqlalchemy.Column(sqlalchemy.Boolean)
  interest_level           = sqlalchemy.Column(sqlalchemy.Integer)
  most_recent_me           = sqlalchemy.Column(sqlalchemy.DateTime)
  most_recent_reply        = sqlalchemy.Column(sqlalchemy.DateTime)
  ignore_before            = sqlalchemy.Column(sqlalchemy.DateTime)
  lastcompute              = sqlalchemy.Column(sqlalchemy.DateTime)
  etag                     = sqlalchemy.Column(sqlalchemy.Unicode(100))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,dbsession,tid,commit=True):
    self.tid=tid
    super().__init__(dbsession,commit)

  def set_yid_etag(self,yid,etag,commit=True):
    if (commit):
      dbsession=get_dbsession(self)
    self.yid=yid
    self.etag=etag
    if (commit):
      dbsession.commit()

  def call_sql_task_threaded(self,priority=0,semaphore=None,options=None):
    logging.debug(type(self).__name__+".call_sql_task_threaded(): START")
    task=YtTask('populate: '+type(self).__name__
                +" - "+str(self.get_id()),type(self),self.get_id(),priority,semaphore,options)
    if not YtQueue().add(task):
      time.sleep(30)
    logging.debug(type(self).__name__+".call_sql_task_threaded(): END")


  def populate_default(self):
    self.lastwork        =None
    self.done            =False
    self.interest_level  =0
    self.lastcompute     =None


  def completed(self,dbsession):
    logging.debug("YTCommentWorkerRecord.completed(): WARNING: placeholder, should never be called")

  def process_result(self,dbsession,youtube,result,force):
    logging.debug("YTCommentWorkerRecord.process_result(): START")
    cn=0
    for comment in result['items']:
      cn+=1
      cid=comment['id']
      logging.debug("YTCommentWorkerRecord.process_result(): working on cid = "+str(cid))
      o=get_dbobject_if_exists(YTCommentRecord,cid,dbsession)
      if ((not force) and o):
          logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): Merged with old")
          self.completed(dbsession)
          logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): Merged with old: done")
          return
      c=get_dbobject(YTCommentRecord,cid,dbsession)
      # yid is not in the subcomment (only in topcomment)
      # adding it by hand
      comment['snippet']['videoId']=self.yid
      c.fill_from_json(comment,dbsession,False)
    logging.debug("YTCommentWorkerRecord.process_result(): number of processed comments = "+str(cn))
    if ('nextPageToken' in result):
      logging.debug("YTCommentWorkerRecord.process_result(): nextPageToken: "+str(result['nextPageToken']))
      self.nextcmtpagetoken=result['nextPageToken'].replace('=','') # FIXME: this is strange but needed.
    else:
      logging.debug("YTCommentWorkerRecord.process_result(): completed")
      self.completed(dbsession)
    self.lastwork=datetime.datetime.now()

  def sql_task_one_chunck(self,dbsession,youtube,force):
    logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): START")
    #logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): 1: "+str(self.nextcmtpagetoken))
    if (not self.nextcmtpagetoken):
      #logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): 2")
      request=youtube.comments().list(
        part='snippet',
        parentId=self.tid,
        maxResults=100)
    else:
      #logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): 3")
      request=youtube.comments().list(
        part='snippet',
        parentId=self.tid,
        pageToken=self.nextcmtpagetoken,
        maxResults=100)
    result=request.execute(force)
    self.process_result(dbsession,youtube,result,force)
    logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): END")


  def sql_task_threaded(self,dbsession,youtube,force=False):
    logging.debug("YTCommentWorkerRecord.sql_task_threaded("+str(force)+"): START : "+self.yid+" "+self.tid)
    if (self.done):
      request=youtube.comments().list(
            part='snippet',
            parentId=self.tid,
            maxResults=100)
      result=request.execute(True)
      if (len(result['items'])):
        cid=result['items'][0]['id']
        o=get_dbobject_if_exists(YTCommentRecord,cid,dbsession)
        if ((not force) and o):
          logging.debug("YTCommentWorkerRecord.sql_task_threaded(): Nothing changed")
          self.lastwork=datetime.datetime.now()
          return
        self.done=False
        self.process_result(dbsession,youtube,result,force)
      else:
        logging.debug("YTCommentWorkerRecord.sql_task_threaded(): No item")
        self.lastwork=datetime.datetime.now()
        return
    v=0
    while not self.done:
      v+=1
      if v>10: # Max nb of comments is 500, but chunk size is strange (not always 100?) FIXME
        raise  # Should not happens
      self.sql_task_one_chunck(dbsession,youtube,force)
    logging.debug("YTCommentWorkerRecord.sql_task_threaded: END")

def import_from_file(dbsession):
  f=open('parents-id.txt','rt')
  for line in f.readlines():
    res=line.split(',')
    if (len(res)==2):
      tid=res[0].strip()
      yid=res[1].strip()
      ycw=get_dbobject_if_exists(YTCommentWorkerRecord,tid,dbsession)
      if True:
        if (ycw): dbsession.delete(ycw)
        logging.debug("Adding "+str(tid)+" from "+str(yid))
        ycw=get_dbobject(YTCommentWorkerRecord,tid,dbsession,False)
        ycw.set_yid_etag(yid,None,False)

  dbsession.commit()

#  --------------------------------------------------------------------------
def main():
  import time
  from ytqueue        import YtQueue
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue(1)
  vidlist=get_video_ids_from_file('yturls.txt')
  ycwlist=[]
  for yid in vidlist:
    ycwl=dbsession.query(YTCommentWorkerRecord0).filter( YTCommentWorkerRecord0.yid == yid )
    if (not ycwl): continue
    ycwlist.append(ycwl)

  for ycwl in ycwlist:
    for ycw in ycwl:
        ycw.call_sql_task_threaded()
        dbsession.commit()
    time.sleep(1)
  YtQueue().join()
  dbsession.commit()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
