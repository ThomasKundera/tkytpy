#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue         import YtQueue, YtTask
from sqlsingleton    import SqlSingleton, Base
from sqlrecord       import SqlRecord, get_dbsession, get_dbobject
from ytcommentrecord import YTCommentRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_4'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  done                     = sqlalchemy.Column(sqlalchemy.Boolean)
  etag                     = sqlalchemy.Column(sqlalchemy.Unicode(100))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,dbsession,tid,commit=True):
    self.tid=tid
    super().__init__(dbsession,commit)

  def set_etag(self,etag,commit=True):
    if (commit):
      dbsession=get_dbsession(self)
    self.etag=etag
    if (commit):
      dbsession.commit()


  def get_priority(self):
    # FIXME: refreshing priority value is also complex
    if (self.done):
      return sys.maxsize
    if not(self.lastwork):
      return 0
    Δt=datetime.datetime.now()-self.lastwork
    # Fit that between 1000 and 2000
    # FIXME
    return 3600*24*365-Δt.total_seconds()

  def populate_default(self):
    self.lastwork=None
    self.done    =False
    self.etag    =None
    self.nextcmtpagetoken=None

  def populate(self,youtube):
    logging.debug("YTCommentWorkerRecord.populate(): START")
    if (self.done):
      logging.debug("YTCommentWorkerRecord.populate(): done: "+str(self.tid))
      return
    dbsession=get_dbsession(self)
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
      tid=thread['id']
      etag=thread['etag']
      tlc=thread['snippet']['topLevelComment']
      cid=tlc['id'] # Is same at tid, actually
      c=get_dbobject(YTCommentRecord,cid,dbsession)
      if (not self.firstthreadcidcandidate):
        self.firstthreadcidcandidate=tid

      c.fill_from_json(tlc,False)
      c=get_dbobject(YTCommentWorkerRecord,tid,dbsession)
      c.set_etag(etag,False)

    if ('nextPageToken' in result):
       self.nexttreadpagetoken=result['nextPageToken']
    else:
      self.done=True

    self.lastwork=datetime.datetime.now()
    dbsession.commit()
    logging.debug("YTCommentWorkerRecord.populate(): END")



# --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  ycwd=dbsession.query(YTCommentWorkerRecord)
  for ycw in ycwd[:5]:
    ycw.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
