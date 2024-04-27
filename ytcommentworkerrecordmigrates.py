#!/usr/bin/env python3
import time
import sqlalchemy
from sqlrecord      import SqlRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject
from ytcommentworkerrecord import YTCommentWorkerRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentWorkerRecord6(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_6'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50))
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  done                     = sqlalchemy.Column(sqlalchemy.Boolean)
  interest_level           = sqlalchemy.Column(sqlalchemy.Integer)
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
  n=0
  for c6 in dbsession.query(YTCommentWorkerRecord6):
    c7=get_dbobject(YTCommentWorkerRecord,c6.tid,dbsession,False)
    dbsession.add(c7)
    c7.copy_from(c6)
    c7.lastcompute=None
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
