#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
import requests

from sqlsingleton import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists
from sqlrecord    import SqlRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# FIXME: I don't like to mix SQL with direct URL accesses, but that's easier.
# --------------------------------------------------------------------------
def valid_url(url):
  r = requests.head(url)
  print(r)
  return(r.status_code == 200)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideoRecord(SqlRecord,Base):
  __tablename__ = 'ytvideos0_9'
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
  lastinterract     = sqlalchemy.Column(sqlalchemy.DateTime)
  mostrecentme      = sqlalchemy.Column(sqlalchemy.DateTime)
  monitor           = sqlalchemy.Column(sqlalchemy.Integer)
  suspended         = sqlalchemy.Column(sqlalchemy.Boolean)

  def __init__(self,dbsession,yid,commit=True):
    self.yid=yid
    super().__init__(dbsession,commit)


  def is_valid_id(self):
    if (len(self.yid) != 11): return False
    return valid_url(self.url)


  def sql_task_threaded(self,dbsession,youtube):
    logging.debug("YTVideoRecord.populate(): START")
    if (not self.valid):
      self.valid=self.is_valid_id()
      return
    # FIXME: sleep if too short
    request=youtube.videos().list(part='snippet,statistics', id=self.yid)
    rawytdata = request.execute(True)
    if len(rawytdata['items']) != 1:
      self.valid=False
    else:
      self.title          =rawytdata['items'][0]['snippet']['title']
      self.thumb_url_s    =rawytdata['items'][0]['snippet']['thumbnails']['default']['url']
      self.viewcount      =rawytdata['items'][0]['statistics']['viewCount']
      self.oldcommentcount=self.commentcount
      self.commentcount   =rawytdata['items'][0]['statistics']['commentCount']
      self.populated=True
      self.oldrefreshed=self.lastrefreshed
      self.lastrefreshed=datetime.datetime.now()

  def populate_default(self):
    self.populated       = False
    self.title           = self.url
    self.thumb_url_s     = None
    self.viewcount       = 0
    self.commentcount    = 0
    self.oldcommentcount = 0
    self.monitor         = 1
    self.suspended       = False
    self.mostrecentme    = None
    self.lastrefreshed   = None
    self.oldrefreshed    = None

# --------------------------------------------------------------------------
def main():
  from ytqueue         import YtQueue, YtTask
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  yvd=dbsession.query(YTVideoRecord)
  for v in yvd[:5]:
    v.call_sql_task_threaded()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()


