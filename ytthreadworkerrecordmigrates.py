#!/usr/bin/env python3
import time
import sqlalchemy
from sqlrecord      import SqlRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject
from ytthreadworkerrecord import YTThreadWorkerRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTThreadWorkerRecord5(SqlRecord,Base):
  __tablename__ = 'ytthreadworkers0_5'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  firstthreadcid           = sqlalchemy.Column(sqlalchemy.Unicode(50))
  firstthreadcidcandidate  = sqlalchemy.Column(sqlalchemy.Unicode(50))
  nexttreadpagetoken       = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,dbsession,yid,commit=True):
    self.yid=yid
    super().__init__(dbsession,commit)


def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  n=0
  for t5 in dbsession.query(YTThreadWorkerRecord5):
    t6=get_dbobject(YTThreadWorkerRecord5,t5.yid,dbsession,False)
    dbsession.add(t6)
    t6.copy_from(t5)
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
