#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session

from sqlsingleton    import SqlSingleton, Base
from sqlrecord       import SqlRecord, get_dbsession, get_dbobject, get_dbobject_if_exists
from ytcommentrecord import YTCommentRecord
from ytauthorrecord  import YTAuthorRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord(SqlRecord,Base):
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

  def set_yid_etag(self,yid,etag,commit=True):
    if (commit):
      dbsession=get_dbsession(self)
    self.yid=yid
    self.etag=etag
    if (commit):
      dbsession.commit()


  def get_priority(self):
    # FIXME: refreshing priority value is also complex
    if (self.done):
      return sys.maxsize
    if not(self.lastwork):
      return 0
    # FIXME
    if (Δt.total_seconds() > 30*24*3600):
      return max((30*24*3600-Δt.total_seconds())/3,0)
    return sys.maxsize

  def populate_default(self):
    self.lastwork=None
    self.done    =False
    self.etag    =None
    self.nextcmtpagetoken=None

  def populate(self,youtube):
    logging.debug("YTCommentWorkerRecord.populate(): START")
    if (self.done):
      logging.debug("YTCommentWorkerRecord.populate(): done: "+str(self.tid))
      return
    dbsession=SqlSingleton().mksession()
    if (not self.nextcmtpagetoken):
      request=youtube.comments().list(
        part='snippet',
        parentId=self.tid,
        maxResults=100)
    else:
      request=youtube.comments().list(
        part='snippet',
        pageToken=self.nexttreadpagetoken,
        maxResults=100)
    result=request.execute()
    for comment in result['items']:
      cid=comment['id']
      c=get_dbobject(YTCommentRecord,cid,dbsession)
      # yid is not in the subcomment (only in topcomment)
      # adding it by hand
      comment['snippet']['videoId']=self.yid
      c.fill_from_json(comment,False)
      name=comment['snippet']['authorDisplayName']
      a=get_dbobject_if_exists(YTAuthorRecord,name,dbsession)
      if not a:
        a=get_dbobject(YTAuthorRecord,name,dbsession)
      a.fill_from_json(comment)

    if ('nextPageToken' in result):
       self.nexttreadpagetoken=result['nextPageToken']
    else:
      self.done=True

    self.lastwork=datetime.datetime.now()
    dbsession.commit()
    logging.debug("YTCommentWorkerRecord.populate(): END")

# --------------------------------------------------------------------------
def main():
  from ytqueue         import YtQueue, YtTask
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  ycwd=dbsession.query(YTCommentWorkerRecord)
  for ycw in ycwd[:5]:
    ycw.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
