#!/usr/bin/env python3
import time
import sqlalchemy
from sqlrecord      import SqlRecord
from ytvideorecord import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTVideoRecord6(SqlRecord,Base):
  __tablename__ = 'ytvideos0_6'
  yid               = sqlalchemy.Column(sqlalchemy.Unicode(12),primary_key=True)
  valid             = sqlalchemy.Column(sqlalchemy.Boolean)
  populated         = sqlalchemy.Column(sqlalchemy.Boolean)
  url               = sqlalchemy.Column(sqlalchemy.Unicode(100))
  title             = sqlalchemy.Column(sqlalchemy.Unicode(200))
  thumb_url_s       = sqlalchemy.Column(sqlalchemy.Unicode(100))
  viewcount         = sqlalchemy.Column(sqlalchemy.Integer)
  commentcount      = sqlalchemy.Column(sqlalchemy.Integer)
  oldcommentcount   = sqlalchemy.Column(sqlalchemy.Integer)
  lastrefreshed     = sqlalchemy.Column(sqlalchemy.DateTime)
  oldrefreshed      = sqlalchemy.Column(sqlalchemy.DateTime)
  monitor           = sqlalchemy.Column(sqlalchemy.Boolean)
  suspended         = sqlalchemy.Column(sqlalchemy.Boolean)


  def __init__(self,dbsession,cid,commit=True):
    self.cid=cid
    super().__init__(dbsession,commit)

def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  n=0
  for v6 in dbsession.query(YTVideoRecord6):
    v7=get_dbobject(YTVideoRecord,v6.yid,dbsession,False)
    dbsession.add(v7)
    v7.copy_from(v6)
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
