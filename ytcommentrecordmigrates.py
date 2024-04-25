#!/usr/bin/env python3
import time
import sqlalchemy
from sqlrecord      import SqlRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject
from ytcommentrecord import YTCommentRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentRecord3(SqlRecord,Base):
  __tablename__ = 'ytcomment0_3'
  cid               = sqlalchemy.Column(sqlalchemy.Unicode(100),primary_key=True)
  yid               = sqlalchemy.Column(sqlalchemy.Unicode(50))
  parent            = sqlalchemy.Column(sqlalchemy.Unicode(50))
  author            = sqlalchemy.Column(sqlalchemy.Unicode(100))
  text              = sqlalchemy.Column(sqlalchemy.Unicode(11000))
  published         = sqlalchemy.Column(sqlalchemy.DateTime)
  updated           = sqlalchemy.Column(sqlalchemy.DateTime)


  def __init__(self,dbsession,cid,commit=True):
    self.cid=cid
    super().__init__(dbsession,commit)

def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  n=0
  for c3 in dbsession.query(YTCommentRecord3):
    c4=get_dbobject(YTCommentRecord,c3.cid,dbsession,False)
    dbsession.add(c4)
    c4.copy_from(c3)
    n+=1
    if (not n % 100):
      print (" ================== ROW "+str(n)+" PROCESSED ============")


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
