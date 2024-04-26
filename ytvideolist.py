#!/usr/bin/env python3
from ytvideo        import YTVideo

from sqlsingleton   import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
class YTVideoList:
  def __init__(self,field_storage):
    logging.debug("YTVideoList.__init__(): START")
    self.field_storage=field_storage

  def add_from_yid(self,yid):
    if (len(yid) != 11): return False
    dbsession=SqlSingleton().mksession()
    v=get_dbobject(YTVideo,yid,dbsession,False)
    dbsession.commit()
    return v.valid

  def get_video_dict(self):
    dbsession=SqlSingleton().mksession()
    l=[]
    for v in dbsession.query(YTVideo):
      #print("video: "+str(v))
      if v.valid:
        l.append(v.to_dict())
    return  {'ytvlist': l}

  def checkbox_action(self,action,yid,checked):
    dbsession=SqlSingleton().mksession()
    v=get_dbobject_if_exists(YTVideo,yid,dbsession)
    if not v: return
    if (action == "suspended"):
      v.suspended=checked
      dbsession.commit()
