#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideoRecord(Base):
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
    self.valid            =o.valid
    self.populated        =o.populated
    self.url              =o.url
    self.title            =o.title
    self.thumb_url_s=o.thumb_url_s

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

  def queued_populate(self,youtube):
    dbsession=SqlSingleton().mksession()
    v=dbsession.query(YTVideoRecord).get(self.yid)
    dbsession.add(v)
    request=youtube.videos().list(part='snippet,statistics', id=self.yid)
    rawytdata = request.execute()
    if len(v.rawytdata['items']) != 1:
      v.valid=False
    else:
      rawytdatajson=json.dumps(v.rawytdata)
      #print(v.rawytdatajson)
      #print(v.rawytdata)
      v.title=v.rawytdata['items'][0]['snippet']['title']
      v.thumb_url_s=rawytdata['items'][0]['snippet']['thumbnails']['default']['url']
      v.viewcount=rawytdata['items'][0]['statistics']['viewcount']
      v.commentcount=rawytdata['items'][0]['statistics']['commentcount']
      v.populated=True
      v.last_refreshed=datetime.datetime.now()
    dbsession.commit()
    dbsession.close()

  def populate_variables_dummy(self):
    self.populated     = False
    self.title         = self.url
    self.rawytdata     = None
    self.thumb_url_s   = None
    self.viewcount=0
    self.commentcount=0
    self.watch_new_threads=True
    self.suspended=False
    self.last_refreshed   =None

