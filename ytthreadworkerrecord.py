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

  def get_priority(self):
    dbsession=get_dbsession(self)
    ytv=get_dbobject_if_exists(YTVideoRecord,self.yid,dbsession)
    if (not ytv): return sys.maxsize
    if ((not ytv.valid) or (ytv.suspended)):
      return sys.maxsize
    # FIXME: refreshing priority value is also complex
    if not(self.lastwork):
      return 0
    Δt=datetime.datetime.now()-self.lastwork
    if (Δt<600):  # FIXME
      return sys.maxsize
    # Fit that between 1000 and 2000
    # FIXME
    return max((30*24*3600-Δt.total_seconds())/3,0)


  def populate_default(self):
    self.lastwork=None
    self.firstthreadcidcandidate=None
    self.firstthreadcid=None
    self.nexttreadpagetoken=None
    self.nextcmtpagetoken=None

  def sql_task_threaded(self,dbsession,youtube):
    logging.debug("YTThreadWorkerRecord.populate(): START")
    # FIXME: can't handle video without any comment.
    if not (self.firstthreadcid):
      if (not self.nexttreadpagetoken):
        request=youtube.commentThreads().list(
          part='id,snippet',
          videoId=self.yid,
          maxResults=100)
      else:
        request=youtube.commentThreads().list(
          part='id,snippet',
          videoId=self.yid,
          pageToken=self.nexttreadpagetoken,
          maxResults=100)
      result=request.execute()
      for thread in result['items']:
        tid=thread['id']
        etag=thread['etag']
        tlc=thread['snippet']['topLevelComment']
        cid=tlc['id'] # Is same at tid, actually
        c=get_dbobject(YTCommentRecord,cid,dbsession)
        if (not self.firstthreadcidcandidate):
          self.firstthreadcidcandidate=tid

        c.fill_from_json(tlc,False)
        c=get_dbobject(YTCommentWorkerRecord,tid,dbsession)
        c.set_yid_etag(self.yid,etag,False)

        name=tlc['snippet']['authorDisplayName']
        a=get_dbobject_if_exists(YTAuthorRecord,name,dbsession)
        if not a:
          a=get_dbobject(YTAuthorRecord,name,dbsession)
        a.fill_from_json(tlc)

      if ('nextPageToken' in result):
        self.nexttreadpagetoken=result['nextPageToken']
      else:
        self.firstthreadcid=self.firstthreadcidcandidate
    else:
      time.sleep(1) # FIXME
    self.lastwork=datetime.datetime.now()
    logging.debug("YTThreadWorkerRecord.populate(): END")


# --------------------------------------------------------------------------
def main():
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue(1)
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

