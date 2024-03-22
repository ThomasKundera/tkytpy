#!/usr/bin/env python3
import json
import requests

from ytvideorecord import YTVideoRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
def valid_url(url):
  r = requests.head(url)
  print(r)
  return(r.status_code == 200)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideo(YTVideoRecord):
  def __init__(self,dbsession,yid,commit=True):
    self.yid=yid
    self.url='https://www.youtube.com/watch?v='+self.yid
    if not self.is_valid_id():
      print("Not valid yid:"+self.yid)
      self.valid=False
      return
    self.valid=True
    super().__init__(dbsession,yid,commit)

  def is_valid_id(self):
    if (len(self.yid) != 11): return False
    return valid_url(self.url)

  def get_dict(self):
    # FIXME: should use default
    return {
      'yid'  :          self.yid,
      'url'  :          self.url,
      'title':          self.title,
      'thumb_url_s':    self.thumb_url_s,
      'viewcount':      self.viewcount,
      'commentcount':   self.commentcount,
      'last_refreshed': self.lastrefreshed.timestamp()
      }

  def __str__(self):
    return self.yid

  def dump(self):
    return {
      'valid':     self.valid,
      'populated': self.populated,
      'yid'  :     self.yid,
      'url'  :     self.url,
      'title':     self.title,
    }

# --------------------------------------------------------------------------
def main():
  from sqlsingleton import SqlSingleton, Base
  from sqlrecord    import SqlRecord, get_dbsession, get_dbobject
  from ytqueue         import YtQueue, YtTask
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  v=get_dbobject(YTVideo,'LaVip3J__8Y',dbsession)
  dbsession.commit()
  return
  yvd=dbsession.query(YTVideo)
  for v in yvd[:5]:
    v.call_populate()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
