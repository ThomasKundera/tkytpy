#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue      import YtQueue, YtTask
from sqlsingleton import SqlSingleton, Base
from sqlrecord    import SqlRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadWorkerRecord(SqlRecord,Base):
  __tablename__ = 'ytthreadworkers0_1'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  firstthreadcidcandidate  = sqlalchemy.Column(sqlalchemy.Unicode(50))
  firstthreadcid           = sqlalchemy.Column(sqlalchemy.Unicode(50))
  nexttreadpagetoken       = sqlalchemy.Column(sqlalchemy.Unicode(200))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)


  def __init__(self,dbsession,yid,commit=True):
    self.yid=yid
    super().__init__(dbsession,commit)


  def get_priority(self):
    # FIXME: refreshing priority value is also complex
    if not(self.lastwork):
      return 0
    return self.lastwork-datetime.datetime(now)+3600*24*365

  def populate_default(self):
    self.nexttreadpagetoken=None
    self.nextcmtpagetoken=None
    self.lastwork=None

  def populate(self,youtube):
    logging.debug("YTThreadWorkerRecord.populate(): START")
    if not (self.firstthreadcid):
      logging.debug(type(self).__name__+".populate(): 1")
      if (not self.nexttreadpagetoken):
        logging.debug(type(self).__name__+".populate(): 2")
        request=youtube.commentThreads().list(part='snippet',videoId=self.yid,maxResults=100,textFormat='html')
        logging.debug(type(self).__name__+".populate(): 3")
        result=request.execute()
        nbc=result['pageInfo']['totalResults']

        for thread in result['items']:
          tlc=thread['snippet']['topLevelComment']
          cid=tlc['id']
          print("------------------------------"+cid)

        if (nbc)<100: # we have all
          self.firstthreadcid=self.firstthreadcidcandidate
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

