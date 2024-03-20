#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from ytqueue import YtQueue, YtTask
from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideoRecord(Base):
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
    self.oldcommentcount   = o.commentcount
    self.lastrefreshed     = o.lastrefreshed
    self.oldrefreshed      = o.oldrefreshed
    self.monitor           = o.monitor
    self.suspended         = o.suspended

  def db_create_or_load(self):
    dbsession=Session.object_session(self)
    if not dbsession:
      dbsession=SqlSingleton().mksession()
    v=dbsession.query(YTVideoRecord).get(self.yid)
    if not v:
      print("New video: "+self.yid)
      dbsession.add(self)
      self.populate_variables_default()
    else:
      self.copy_from(v)
    dbsession.commit()


  def RefreshPriority(self):
    # Lower the more prioritized, number should roughlt reflects
    # time (in second) before next update would be nice.
    # Refresh priority should depends heavily on interractive accesses
    # but we don't have that metric yet (FIXME)

    if (not self.populated):
      return 0
    if (not self.monitor):
      returnsys.maxsize # Max easy to handle number
    if (self.suspended):
      return sys.maxsize
    # From here, without metrics, it's fuzzy
    # Lets use just time to last refresh, and tagetting once a month.
    Δt=datetime.datetime.now()-self.lastrefreshed
    if (Δt.total_seconds() > 30*24*3600):
      return 3600 # lets do that under an hour
    return sys.maxsize

  def call_populate(self,priority=0):
    task=YtTask('populate:'+self.yid,self.queued_populate,priority)
    YtQueue().add(task)


  def queued_populate(self,youtube):
    dbsession=SqlSingleton().mksession()
    v=dbsession.query(YTVideoRecord).get(self.yid)
    dbsession.add(v)
    request=youtube.videos().list(part='snippet,statistics', id=self.yid)
    rawytdata = request.execute()
    if len(rawytdata['items']) != 1:
      v.valid=False
    else:
      #print(v.rawytdatajson)
      #print(v.rawytdata)
      v.title          =rawytdata['items'][0]['snippet']['title']
      v.thumb_url_s    =rawytdata['items'][0]['snippet']['thumbnails']['default']['url']
      v.viewcount      =rawytdata['items'][0]['statistics']['viewCount']
      v.oldcommentcount=v.commentcount
      v.commentcount   =rawytdata['items'][0]['statistics']['commentCount']
      v.populated=True
      v.oldrefreshed=v.lastrefreshed
      v.lastrefreshed=datetime.datetime.now()
    dbsession.commit()
    dbsession.close()

  def populate_variables_default(self):
    self.populated       = False
    self.title           = self.url
    self.thumb_url_s     = None
    self.viewcount       = 0
    self.commentcount    = 0
    self.oldcommentcount = 0
    self.monitor         = True
    self.suspended       = False
    self.lastrefreshed   = None
    self.oldrefreshed    = None
