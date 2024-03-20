#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue      import YtQueue, YtTask
from sqlsingleton import SqlSingleton, Base
from sqlrecord    import SqlRecord, get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class TestRecord(SqlRecord,Base):
  __tablename__ = 'testrecord0_1'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  data1                    = sqlalchemy.Column(sqlalchemy.Unicode(50))
  data2                    = sqlalchemy.Column(sqlalchemy.Unicode(50))
  data3                    = sqlalchemy.Column(sqlalchemy.Unicode(50))
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
    self.data1="something"
    self.data2="whatever"
    self.data3="and this"
    self.lastwork=None

  def populate(self,youtube):
    logging.debug("YTThreadWorkerRecord.populate(): START")
    dbsession=get_dbsession(self)
    request=youtube.videos().list(part='snippet',id=self.yid)
    result=request.execute()
    print(result)
    self.lastwork=datetime.datetime.now()
    dbsession.commit()
    logging.debug("YTThreadWorkerRecord.populate(): END")


# --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  ytwd=dbsession.query(TestRecord)
  for ytw in ytwd:
    ytw.call_populate()
  YtQueue().join()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

