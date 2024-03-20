#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue         import YtQueue, YtTask
from sqlsingleton    import SqlSingleton, Base
from sqlrecord       import SqlRecord, get_dbsession, get_dbobject

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_2'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
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
    if not(self.lastwork):
      return 0
    Δt=datetime.datetime.now()-self.lastwork
    # Fit that between 1000 and 2000
    # FIXME
    return 3600*24*365-Δt.total_seconds()

  def populate_default(self):
    self.lastwork=None
    self.etag=None
    self.nextcmtpagetoken=None

  def populate(self,youtube):
    logging.debug("YTCommentWorkerRecord.populate(): START")

    logging.debug("YTCommentWorkerRecord.populate(): END")



# --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  ycwd=dbsession.query(YTCommentWorkerRecord)
  for ycw in ycwd:
    ycw.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
