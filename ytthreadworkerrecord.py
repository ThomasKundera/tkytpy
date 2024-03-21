#!/usr/bin/env python3
import time
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue               import YtQueue, YtTask
from sqlsingleton          import SqlSingleton, Base
from sqlrecord             import SqlRecord, get_dbsession, get_dbobject
from ytcommentworkerrecord import YTCommentWorkerRecord
from ytcommentrecord       import YTCommentRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from threading import get_ident

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
    # FIXME: refreshing priority value is also complex
    if not(self.lastwork):
      return 0
    Δt=datetime.datetime.now()-self.lastwork
    # Fit that between 1000 and 2000
    # FIXME
    return 3600*24*365-Δt.total_seconds()

  def populate_default(self):
    self.firstthreadcidcandidate=None
    self.firstthreadcid=None
    self.nexttreadpagetoken=None
    self.nextcmtpagetoken=None
    self.lastwork=None

  def populate(self,youtube):
    logging.debug("YTThreadWorkerRecord.populate(): START")
    dbsession= dbsession=SqlSingleton().mksession()

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

      if ('nextPageToken' in result):
        self.nexttreadpagetoken=result['nextPageToken']
      else:
        self.firstthreadcid=self.firstthreadcidcandidate
    else:
      time.sleep(1) # FIXME
    self.lastwork=datetime.datetime.now()
    dbsession.commit()
    logging.debug("YTThreadWorkerRecord.populate(): END")



# --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  ytwd=dbsession.query(YTThreadWorkerRecord)
  for ytw in ytwd[:10]:
    ytw.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

