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
    Δt=datetime.datetime.now()-self.lastwork
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
          if (not self.firstthreadcidcandidate):
            self.firstthreadcidcandidate=cid
          c=get_dbobject(YTCommentRecord,cid,dbsession)
          c.fill_from_json(tlc,False)
        if (nbc)<100: # we have all
          self.firstthreadcid=self.firstthreadcidcandidate
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

