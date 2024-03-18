#!/usr/bin/env python3
import time
import sqlalchemy
from sqlalchemy_utils import JSONType

from sqlsingleton import SqlSingleton, Base
from ytvideorecord import YTVideoRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class YTVideoRecord5(Base):
  __tablename__ = 'ytvideos5'
  yid               = sqlalchemy.Column(sqlalchemy.Unicode(12),primary_key=True)
  valid             = sqlalchemy.Column(sqlalchemy.Boolean)
  populated         = sqlalchemy.Column(sqlalchemy.Boolean)
  url               = sqlalchemy.Column(sqlalchemy.Unicode(100))
  title             = sqlalchemy.Column(sqlalchemy.Unicode(200))
  thumb_url_s       = sqlalchemy.Column(sqlalchemy.Unicode(100))
  viewcount         = sqlalchemy.Column(sqlalchemy.Integer)
  commentcount      = sqlalchemy.Column(sqlalchemy.Integer)
  last_refreshed    = sqlalchemy.Column(sqlalchemy.DateTime)
  watch_new_threads = sqlalchemy.Column(sqlalchemy.Boolean)
  suspended         = sqlalchemy.Column(sqlalchemy.Boolean)

  def __init__(self,yid):
    self.yid=yid.strip()
    self.db_create_or_load()

  def copy_from(self,o):
    self.valid             = o.valid
    self.populated         = o.populated
    self.url               = o.url
    self.title             = o.title
    self.thumb_url_s       = o.thumb_url_s
    self.viewcount         = o.viewcount
    self.commentcount      = o.commentcount
    self.last_refreshed    = o.last_refreshed
    self.watch_new_threads = o.watch_new_threads
    self.suspended         = o.suspended

  def copy_to(self,o):
    o.valid             = self.valid
    o.populated         = self.populated
    o.url               = self.url
    o.title             = self.title
    o.thumb_url_s       = self.thumb_url_s
    o.viewcount         = self.viewcount
    o.commentcount      = self.commentcount
    o.lastrefreshed     = self.last_refreshed
    o.monitor           = self.watch_new_threads
    o.suspended         = self.suspended

def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  for v5 in dbsession.query(YTVideoRecord5):
    v06=YTVideoRecord(v5.yid)
    v5.populated=False
    dbsession.add(v06)
    v5.copy_to(v06)


# --------------------------------------------------------------------------
def main():
  import time
  import ytqueue
  logging.debug("ytvideolist migrates: START")
  init_db()
  dbsession=SqlSingleton().mksession()
  migrates(dbsession)
  dbsession.commit()
  time.sleep(10)
  logging.debug("ytvideolist migrates: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
