#!/usr/bin/env python3
import time
import sqlalchemy
from sqlalchemy_utils import JSONType

from ytcommentworkerrecord import YTCommentWorkerRecord
from sqlrecord             import SqlRecord, get_dbsession, get_dbobject, get_dbobject_if_exists

from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord0_5(SqlRecord,Base):
  __tablename__            = 'ytcommentworkerrecord0_5'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50))
  lastwork                 = sqlalchemy.Column(sqlalchemy.DateTime)
  done                     = sqlalchemy.Column(sqlalchemy.Boolean)
  etag                     = sqlalchemy.Column(sqlalchemy.Unicode(100))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,dbsession,tid,commit=True):
    self.tid=tid
    super().__init__(dbsession,commit)




def migrates(dbsession):
  for v5 in dbsession.query(YTCommentWorkerRecord0_5):
    #print("Copying "+str(v5))
    v6=get_dbobject(YTCommentWorkerRecord,v5.tid,dbsession,False)
    v6.copy_from(v5)



# --------------------------------------------------------------------------
def main():
  import time
  import ytqueue
  logging.debug("YTCommentWorkerRecord migrates: START")
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  migrates(dbsession)
  dbsession.flush()
  dbsession.commit()
  dbsession.close()
  time.sleep(10)
  logging.debug("YTCommentWorkerRecord migrates: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
