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
class YTCommentRecord(Base):
  __tablename__ = 'ytcomment0_1'
  cid               = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  parent            = sqlalchemy.Column(sqlalchemy.Unicode(50))
  author            = sqlalchemy.Column(sqlalchemy.Unicode(100),primary_key=True)
  text              = sqlalchemy.Column(sqlalchemy.Unicode)
  published         = sqlalchemy.Column(sqlalchemy.DateTime)
  edited            = sqlalchemy.Column(sqlalchemy.DateTime)

  def __init__(self,cid):
    self.cid=cid
    self.db_create_or_load()

  def copy_from(self,o):
    self.parent            = o.parent
    self.author            = o.parent
    self.text              = o.text
    self.published         = o.published
    self.edited            = o.edited

  def db_create_or_load(self):
    dbsession=Session.object_session(self)
    if not dbsession:
      dbsession=SqlSingleton().mksession()
    c=dbsession.query(YTCommentRecord).get(self.cid)
    if not c:
      print("New comment: "+self.cid)
      dbsession.add(self)
      self.populate_variables_default()
    else:
      self.copy_from(c)
    dbsession.commit()

  def populate_variables_default(self):
    return
