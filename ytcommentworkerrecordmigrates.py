#!/usr/bin/env python3
import time
import sqlalchemy
from sqlrecord      import SqlRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject
from ytcommentworkerrecord import YTCommentWorkerRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentWorkerRecordold(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_8'
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
  

  def __init__(self,dbsession,cid,commit=True):
    self.cid=cid
    super().__init__(dbsession,commit)


def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  """
  Migrates all records in the old ytcommentworkerrecord table to the new
  format.

  This function should be called once, then removed from the codebase.
  """
  return -1
  n=0
  for cold in dbsession.query(YTCommentWorkerRecordold):
    cnew=get_dbobject(YTCommentWorkerRecord,cold.tid,dbsession,False)
    dbsession.add(cnew)
    cnew.copy_from(cold)
    #cnew.lastcompute=None
    n+=1
    if (not n % 100):
      print (" ================== ROW "+str(n)+" PROCESSED ============")
  dbsession.commit()

# --------------------------------------------------------------------------
def main():
  logging.debug("ytcommentrecord migrates: START")
  init_db()
  dbsession=SqlSingleton().mksession()
  migrates(dbsession)
  dbsession.commit()
  time.sleep(10)
  logging.debug("ytcommentrecord migrates: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
