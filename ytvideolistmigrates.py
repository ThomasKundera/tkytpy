#!/usr/bin/env python3
import time
import sqlalchemy
from sqlalchemy_utils import JSONType

from sqlsingleton import SqlSingleton, Base
from ytvideorecord import YTVideoRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideoRecord3(Base):
  __tablename__ = 'ytvideos3'
  yid           = sqlalchemy.Column(sqlalchemy.Unicode(12),primary_key=True)
  valid         = sqlalchemy.Column(sqlalchemy.Boolean)
  populated     = sqlalchemy.Column(sqlalchemy.Boolean)
  url           = sqlalchemy.Column(sqlalchemy.Unicode(100))
  title         = sqlalchemy.Column(sqlalchemy.Unicode(200))
  thumb_url_s   = sqlalchemy.Column(sqlalchemy.Unicode(100))
  rawytdatajson = sqlalchemy.Column(           JSONType)

  def __init__(self,yid):
    self.yid=yid.strip()
    self.db_create_or_load()

  def copy_to(self,o):
    o.valid            =self.valid
    o.populated        =self.populated
    o.url              =self.url
    o.title            =self.title
    o.thumb_url_s      =self.thumb_url_s

  def db_create_or_load(self):
    dbsession=Session.object_session(self)
    if not dbsession:
      dbsession=SqlSingleton().mksession()
    v=dbsession.query(YTVideoRecord).get(self.yid)
    if not v:
      print("New video: "+self.yid)
      dbsession.add(self)
      self.populate_variables_dummy()
    else:
      self.copy_from(v)
    if not self.populated:
      self.call_populate()
    dbsession.commit()

def init_db():
  Base.metadata.create_all()
  print("Initialized the db")


def migrates(dbsession):
  for v3 in dbsession.query(YTVideoRecord3):
    v5=YTVideoRecord(v3.yid)
    v3.populated=False
    bsession.add(v5)
    v3.copy_to(v5)


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
