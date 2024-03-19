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
class YTCommentsWorkerRecord(Base):
  __tablename__            = 'ytcommentworkerrecord0_1'
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(12),primary_key=True)
  lastrefreshed            = sqlalchemy.Column(sqlalchemy.DateTime)
  infulldownload           = sqlalchemy.Column(sqlalchemy.Boolean)
  nexttreadpagetoken       = sqlalchemy.Column(sqlalchemy.Unicode(200))
  nextcmtpagetoken         = sqlalchemy.Column(sqlalchemy.Unicode(200))

  def __init__(self,yid):
    self.yid=yid
    self.db_create_or_load()

  def copy_from(self,o):
    self.lastrefreshed      = o.lastrefreshed
    self.infulldownload     = o.infulldownload
    self.nexttreadpagetoken = o.nexttreadpagetoken
    self.nextcmtpagetoken   = o.nextcmtpagetoken

  def db_create_or_load(self):
    dbsession=Session.object_session(self)
    if not dbsession:
      dbsession=SqlSingleton().mksession()
    w=dbsession.query(YTCommentsWorkerRecord).get(self.yid)
    if not w:
      print("New Worker: "+self.yid)
      dbsession.add(self)
      self.populate_variables_default()
    else:
      self.copy_from(w)
    dbsession.commit()

  def populate_variables_default(self):
    self.lastrefreshed                = None
    self.infulldownload               = True
    self.fullrefreshcandidatecid      = None
    self.nexttreadpagetoken           = None
    self.nextcmtpagetoken             = None

  def download_chunck(self,youtube):
    if (self.infulldownload):
      if (not self.nexttreadpagetoken):
        request=youtube.commentThreads().list(part='snippet',videoId=self.yid,maxResults=100,textFormat='html')
        print(request.execute())

    self.semaphore.release()

