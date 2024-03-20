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
class YTThreadWorkerRecord(SqlRecord,Base):
  __tablename__ = 'ytthreadworkers0_3'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  firstthreadcid           = sqlalchemy.Column(sqlalchemy.Unicode(50))
  firstthreadcidcandidate  = sqlalchemy.Column(sqlalchemy.Unicode(50))
  nexttreadpagetoken       = sqlalchemy.Column(sqlalchemy.Unicode(200))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))

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
    dbsession=get_dbsession(self)
    if not (self.firstthreadcid):
      if (not self.nexttreadpagetoken):
        request=youtube.commentThreads().list(
          part='snippet',
          videoId=self.yid,
          maxResults=100,
          textFormat='html')
      else:
        request=youtube.commentThreads().list(
          part='snippet',
          videoId=self.yid,
          pageToken=self.nexttreadpagetoken,
          maxResults=100,
          textFormat='html')
      result=request.execute()
      nbc=result['pageInfo']['totalResults']
      for thread in result['items']:
        tlc=thread['snippet']['topLevelComment']
        cid=tlc['id']
        if (not self.firstthreadcidcandidate):
          self.firstthreadcidcandidate=cid
        c=get_dbobject(YTCommentRecord,cid,dbsession)
        c.fill_from_json(tlc,False)
      if (nbc)<100: # we have all
        self.firstthreadcid=self.firstthreadcidcandidate
      self.nexttreadpagetoken=result['nextPageToken']
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
  for ytw in ytwd:
    ytw.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

