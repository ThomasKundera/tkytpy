#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from sqlrecord       import SqlRecord
from ytcommentrecord import YTCommentRecord
from ytauthorrecord  import YTAuthorRecord
from ytvideorecord   import YTVideoRecord

from sqlsingleton    import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord(SqlRecord,Base):
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


  def get_priority(self):
    #logging.debug(type(self).__name__+".get_priority(): START")
    # FIXME: refreshing priority value is also complex
    if (self.done):
      return sys.maxsize
    #dbsession=get_dbsession(self) # FIXME: this is too slow
    #ytv=get_dbobject_if_exists(YTVideoRecord,self.yid,dbsession)
    #if (not ytv): return sys.maxsize
    #if ((not ytv.valid) or (ytv.suspended)):
    #  return sys.maxsize
    if not(self.lastwork):
      return 100
    # FIXME
    Δt=(datetime.datetime.now()-self.lastwork).total_seconds()
    return max((30*24*3600-Δt)/3,100)

  def populate_default(self):
    self.lastwork        =None
    self.done            =False
    self.interest_level  =0
    self.lastcompute     =None
    self.etag            =None
    self.nextcmtpagetoken=None

  def sql_task_one_chunck(self,dbsession,youtube):
    logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): START")
    if (not self.nextcmtpagetoken):
          request=youtube.comments().list(
            part='snippet',
            parentId=self.tid,
            maxResults=100)
    else:
      request=youtube.comments().list(
        part='snippet',
        pageToken=self.nexttreadpagetoken,
        maxResults=100)
    result=request.execute()
    for comment in result['items']:
      cid=comment['id']
      o=get_dbobject_if_exists(YTCommentRecord,cid,dbsession)
      if (o):
          logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): Merged with old")
          self.done=True
          self.lastwork=datetime.datetime.now()
          return
      c=get_dbobject(YTCommentRecord,cid,dbsession)
      # yid is not in the subcomment (only in topcomment)
      # adding it by hand
      comment['snippet']['videoId']=self.yid
      c.fill_from_json(comment,False)
      name=comment['snippet']['authorDisplayName']
      a=get_dbobject_if_exists(YTAuthorRecord,name,dbsession)
      if not a:
        a=get_dbobject(YTAuthorRecord,name,dbsession)
      a.fill_from_json(comment)

    if ('nextPageToken' in result):
      self.nexttreadpagetoken=result['nextPageToken']
    else:
      self.done=True
    self.lastwork=datetime.datetime.now()
    logging.debug("YTCommentWorkerRecord.sql_task_one_chunck(): END")


  def sql_task_threaded(self,dbsession,youtube):
    logging.debug("YTCommentWorkerRecordsql_task_threaded.(): START")
    if (self.done):
      request=youtube.comments().list(
            part='snippet',
            parentId=self.tid,
            maxResults=100)
      result=request.execute(True)
      if (len(result['items'])):
        cid=result['items'][0]['id']
        o=get_dbobject_if_exists(YTCommentRecord,cid,dbsession)
        if (o):
          logging.debug("YTCommentWorkerRecord.sql_task_threaded(): Nothing changed")
          self.lastwork=datetime.datetime.now()
          return
        self.done=False
      else:
        logging.debug("YTCommentWorkerRecord.sql_task_threaded(): No item")
        self.lastwork=datetime.datetime.now()
        return
    v=0
    while not self.done:
      v+=1
      if v>10: # Max nb of comments is 500, so 5 iterations.
        raise  # Should not happens
      self.sql_task_one_chunck(dbsession,youtube)
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
    ycwl=dbsession.query(YTCommentWorkerRecord).filter( YTCommentWorkerRecord.yid == yid )
    if (not ycwl): continue
    ycwlist.append(ycwl)

  for i in range(100):
    for ycwl in ycwlist:
      for ycw in ycwl:
        ycw.call_sql_task_threaded()
    time.sleep(1)
  YtQueue().join()
  dbsession.commit()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
