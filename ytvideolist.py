#!/usr/bin/env python3
from ytvideo        import YTVideo
from threading import Thread, Semaphore

from ytthreadworkerrecord import YTThreadWorkerRecord, Options

from sqlsingleton   import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
class YTVideoList:
  semadict={}
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

  def set_monitor(self,yid,value):
    if (value<0) or (value>10): return
    dbsession=SqlSingleton().mksession()
    v=get_dbobject_if_exists(YTVideo,yid,dbsession)
    if not v: return
    v.monitor=value
    dbsession.commit()

  def refresh(self,yid):
    logging.debug(type(self).__name__+".refresh("+yid+"): START")
    do_refresh = Thread(target=self.do_refresh, args=(yid,))
    do_refresh.start()

  def do_refresh(self,yid):
    logging.debug(type(self).__name__+".do_refresh("+yid+"): START")
    dbsession=SqlSingleton().mksession()
    v=get_dbobject_if_exists(YTVideo,yid,dbsession)
    if not v: return
    if not yid in semadict:
      semadict[yid]=Semaphore(1)
    semadict[yid].acquire()
    # Video info refresh first
    v.call_sql_task_threaded(10,self.semaphore)
    dbsession.merge(v)
    dbsession.commit()
    # Video comments refresh then
    semadict[yid].acquire()
    options=Options()
    options.force_restart =True
    options.force_continue=True
    options.force_refresh =True
    options.priority=10
    ytw=get_dbobject_if_exists(YTThreadWorkerRecord,yid)
    ytw.call_refresh(options)
    logging.debug(type(self).__name__+".do_refresh("+yid+"): END")
