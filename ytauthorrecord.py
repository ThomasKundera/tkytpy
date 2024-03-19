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
class YTAuthorRecord(Base):
  __tablename__ = 'ytauthor0_1'
  name              = sqlalchemy.Column(sqlalchemy.Unicode(100),primary_key=True)
  pp                = sqlalchemy.Column(sqlalchemy.Unicode(200))
  me                = sqlalchemy.Column(sqlalchemy.Boolean)
  follow            = sqlalchemy.Column(sqlalchemy.Boolean)
  friend            = sqlalchemy.Column(sqlalchemy.Boolean)
  ignore            = sqlalchemy.Column(sqlalchemy.Boolean)


  def __init__(self,name):
    self.name=name
    self.db_create_or_load()

  def copy_from(self,o):
    self.pp                = o.pp
    self.me                = o.me
    self.follow            = o.follow
    self.friend            = o.friend
    self.ignore            = o.ignore


  def db_create_or_load(self):
    dbsession=Session.object_session(self)
    if not dbsession:
      dbsession=SqlSingleton().mksession()
    a=dbsession.query(YTAuthorRecord).get(self.name)
    if not a:
      print("New Author: "+self.name)
      dbsession.add(self)
      self.populate_variables_default()
    else:
      self.copy_from(a)
    dbsession.commit()


  def populate_variables_default(self):
    self.pp                = None
    self.me                = False
    self.follow            = False
    self.friend            = False
    self.ignore            = False

