#!/usr/bin/env python3
import unittest
import datetime
from sqlalchemy.sql import func
import sqlalchemy

from sqlalchemy import or_, and_
from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytcommentrecord        import YTCommentRecord
from ytauthorrecord         import YTAuthorRecord
from sqlrecord              import SqlRecord
from ytvideorecord          import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentThreadList():
  def __init__(self):
    self.dbsession=SqlSingleton().mksession()
    return

  def get_number_of_threads_of_interest(self):
    nb=self.dbsession.query(YTCommentWorkerRecord).filter(YTCommentWorkerRecord.interest_level != 0).count()
    return {'nb': nb}

  def get_oldest_threads_of_interest_old(self,nb=1):
    now=datetime.datetime.now()
    threads=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.interest_level != 0 ,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.most_recent_me).limit(nb)
    if (threads.count()==0):
      return None
    return threads

  def get_oldest_threads_of_interest(self,nb=1):
    now=datetime.datetime.now()
    threads=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.interest_level != 0 ,
             or_ (YTCommentWorkerRecord.ignore_until == None,
                  YTCommentWorkerRecord.ignore_until < now),
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.most_recent_me).limit(nb)
    if (threads.count()==0):
      return None
    return threads


  def get_newest_threads_of_interest(self,nb=1):
    threads=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.interest_level != 0,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.most_recent_reply.desc()).limit(nb)
    if (threads.count()==0):
      return None
    return threads

  def get_thread_from_ytcw(self,ytcw):
    if (ytcw):
      return ytcw.to_dict(self.dbsession)
    return {}
  
  def convert_threadlist_to_dict(self,tl):
    d={}
    lst=[]
    for t in tl:
      lst.append(self.get_thread_from_ytcw(t))
    d['tlist']=lst
    return d

  def get_thread(self,tid):
    t=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
    return t

  def get_thread_dict(self,tid):
    t=self.get_thread(tid)
    return self.get_thread_from_ytcw(t)

  def get_oldest_threads_of_interest_as_dict(self,nb=1):
    tl=self.get_oldest_threads_of_interest(nb)
    return self.convert_threadlist_to_dict(tl)

  def get_newest_threads_of_interest_as_dict(self,nb=1):
    tl=self.get_newest_threads_of_interest(nb)
    return self.convert_threadlist_to_dict(tl)

  def force_refresh_thread(self,tid):
    t=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
    if t:
      t.call_sql_task_threaded(0,options=True) # This should be safe, after looking.
      # Only annoying case is if exact same task is queued, it will
      # be discarded even if the other one has lower priority.
      # FIXME time.sleep(10) # This to have the thread updated.
      self.dbsession.merge(t) # FIXME: I have to better understand
      t.set_interest(self.dbsession)
      # A commit would be needed after the command ran.
      # A callback would be nice
    return True
  
  def suspend_thread(self,tid,duration):
    t=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
    if t:
      t.suspend(self.dbsession,duration)
      self.dbsession.merge(t)
    return True

  def get_commentcount_for_video(self,yid):
    d=self.dbsession.query(YTCommentRecord).filter(YTCommentRecord.yid == yid).count()
    return d

  def get_commentcount_per_video(self):
    res=self.dbsession.query(YTCommentRecord.yid, func.count(YTCommentRecord.yid)).group_by(YTCommentRecord.yid).all()
    d={}
    for v in res:
      d[v[0]]=v[1]
    return d


  def set_ignore_from_comment(self,cid):
    logging.debug(type(self).__name__+".set_ignore_from_comment( "+str(cid)+" : START")
    cmt=get_dbobject_if_exists(YTCommentRecord,cid,self.dbsession)
    if (cmt):
      logging.debug(type(self).__name__+".set_ignore_from_comment() : 2")
      tid=cmt.parent
      if (tid == None):
        tid=cmt.cid
      tcwr=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
      tcwr.ignore_before=cmt.updated
      tcwr.set_interest(self.dbsession)

class TestYTComment(unittest.TestCase):
  def test_from(self):
    dbsession=SqlSingleton().mksession()
    ytc=get_dbobject_if_exists(YTComment,"UgxKkhejRlOem0a9MZd4AaABAg.9m9BVs9jpHh9mR5LDy3jc1",dbsession)
    self.assertEqual(ytc.from_me(),False)
    self.assertEqual(ytc.has_me() ,True)
    ytc=get_dbobject_if_exists(YTComment,"UgxKkhejRlOem0a9MZd4AaABAg.9m9BVs9jpHh9mYKCAJxsPB",dbsession)
    self.assertEqual(ytc.from_me(),True)


class TestYTCommentThread(unittest.TestCase):
  def test_comment_list(self):
    dbsession=SqlSingleton().mksession()
    ytct=YTCommentThread("Ugz2eqcV5SC1sFC6FB14AaABAg",dbsession)
    print(ytct.get_comment_list(True))


  def test_I_posted(self):
    dbsession=SqlSingleton().mksession()
    ytct=YTCommentThread("Ugz84TKRQZboOin1LXJ4AaABAg",dbsession)
    self.assertEqual(ytct.i_posted_there(),True)
    #self.assertEqual(ytc.has_me() ,True)


  def test_compute_interest(self):
    dbsession=SqlSingleton().mksession()
    ytct=YTCommentThread("UgzlZaj_4k12sLhUVPx4AaABA",dbsession)
    if (ytct):
      print("GARP: "+str(ytct.compute_interest()))


def simple_test():
  dbsession=SqlSingleton().mksession()
  ytct=get_dbobject_if_exists(YTCommentWorkerRecord,"Ugz2eqcV5SC1sFC6FB14AaABAg",dbsession)
  #print(ytct.compute_interest()
  for i in range(10):
    ytct.set_interest(dbsession,False)
  dbsession.commit()
  return
  #ytct=YTCommentThread("UgjWCKGV7tqcM3gCoAEC",dbsession)
  ytct.set_interest()
  return
  ytl=YTCommentThreadList()
  ytl.force_refresh_thread("UgzlZaj_4k12sLhUVPx4AaABAg")


# --------------------------------------------------------------------------
def main():
  import cProfile
  cProfile.run('simple_test()','runstats.dat')
  return
  from ytqueue import YtQueue
  YtQueue().join()
  return
  unittest.main()
  return
  #yct=YTCommentThread('Ugz-g04lVUjL5K8Sv0h4AaABAg')
  #yct.set_interest()
  #return

  ytl=YTCommentThreadList()
  print(ytl.get_oldest_thread_of_interest())
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
