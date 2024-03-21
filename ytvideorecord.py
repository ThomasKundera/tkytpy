#!/usr/bin/env python3
import datetime
import json
import sqlalchemy

from sqlsingleton import SqlSingleton, Base
from sqlrecord    import SqlRecord, get_dbsession, get_dbobject

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideoRecord(SqlRecord,Base):
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
    self.yid=yid
    super().__init__(dbsession,commit)

  def get_priority(self):
    # Lower the more prioritized, number should roughlt reflects
    # time (in second) before next update would be nice.
    # Refresh priority should depends heavily on interractive accesses
    # but we don't have that metric yet (FIXME)

    if (not self.populated):
      return 100
    if (not self.monitor):
      returnsys.maxsize # Max easy to handle number
    if (self.suspended):
      return sys.maxsize
    # From here, without metrics, it's fuzzy
    # Lets use just time to last refresh, and tagetting once a month.
    Δt=datetime.datetime.now()-self.lastrefreshed
    # FIXME
    if (Δt.total_seconds() > 30*24*3600):
      return max((30*24*3600-Δt.total_seconds())/3,0)
    return sys.maxsize


  def populate(self,youtube):
    logging.debug("YTVideoRecord.populate(): START")
    dbsession=SqlSingleton().mksession()
    request=youtube.videos().list(part='snippet,statistics', id=self.yid)
    rawytdata = request.execute()
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
    dbsession.commit()
    dbsession.close()

  def populate_default(self):
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


# --------------------------------------------------------------------------
def main():
  from ytqueue         import YtQueue, YtTask
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  yvd=dbsession.query(YTVideoRecord)
  for v in yvd[:5]:
    v.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()


