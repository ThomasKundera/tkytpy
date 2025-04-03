#!/usr/bin/env python3
from ytvideo        import YTVideo
from threading import Thread, Semaphore

from ytthreadworkerrecord import YTThreadWorkerRecord, Options

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


  def update_workerreccord(self,dbsession=None):
    if (not dbsession):
      dbsession=SqlSingleton().mksession()
    l=[]
    for v in dbsession.query(YTVideo):
      t=get_dbobject(YTThreadWorkerRecord,v.yid,dbsession)
    dbsession.commit()

  def get_video_dict(self):
    dbsession=SqlSingleton().mksession()
    l=[]
    for v in dbsession.query(YTVideo):
      #print("video: "+str(v))
      if v.valid:
        l.append(v.to_dict())
    return  {'ytvlist': l}

  def get_one_video_dict(self,yid):
    dbsession=SqlSingleton().mksession()
    v=get_dbobject_if_exists(YTVideo,yid,dbsession)
    if not v: return {}
    return v.to_dict()

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
    return {}


  def refresh_all(self):
    logging.debug(type(self).__name__+".refresh_all(): START")
    do_refresh = Thread(target=self.do_refresh_all)
    do_refresh.start()
    return {}

  def do_refresh_all(self):
    logging.debug(type(self).__name__+".do_refresh_all(): START")
    dbsession=SqlSingleton().mksession()
    semaphore=Semaphore(1)
    # FIXME: there is a way to perform a single call!
    for v in dbsession.query(YTVideo):
      if not v.suspended:
        logging.debug(type(self).__name__+".do_refresh_all(): Do refresh for "+str(v.yid))
        semaphore.acquire()
        v.call_sql_task_threaded_never_give_up(10,semaphore)
    logging.debug(type(self).__name__+".do_refresh_all(): END")


  def do_refresh(self,yid):
    logging.debug(type(self).__name__+".do_refresh("+yid+"): START")
    dbsession=SqlSingleton().mksession()
    v=get_dbobject_if_exists(YTVideo,yid,dbsession)
    if not v: return
    # FIXME: some semaphore mechanism needed.
    #semaphore=Semaphore(1)
    #if not yid in semadict:
    #  semadict[yid]=Semaphore(1)
    #semadict[yid].acquire()
    # Video info refresh first
    # FIXME: bypass cache.
    v.call_sql_task_threaded(0)
    #dbsession.merge(v)
    #dbsession.commit()
    # Video comments refresh then
    #semadict[yid].acquire()

    # Only performing basic refresh of the metadata.
    logging.debug(type(self).__name__+".do_refresh("+yid+"): END")
    return
    options=Options()
    options.force_restart =True
    options.force_continue=True
    options.force_refresh =True
    options.priority=10
    ytw=get_dbobject(YTThreadWorkerRecord,yid,dbsession)
    dbsession.commit()
    if (ytw):
      ytw.call_refresh(options)
    else:
      logging.debug(type(self).__name__+".do_refresh("+yid+"): ERROR: YTThreadWorkerRecord not created")
    logging.debug(type(self).__name__+".do_refresh("+yid+"): END")
