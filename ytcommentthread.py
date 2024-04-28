#!/usr/bin/env python3
import unittest
import datetime
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


class YTComment(YTCommentRecord):
  def __init__(self,dbsession,cid,commit=True):
    self.cid=cid
    super().__init__(dbsession,commit)

  def from_me(self,dbsession=None):
    a=get_dbobject_if_exists(YTAuthorRecord,self.author,dbsession)
    if not a:
      logging.debug("WARNING: YTComment.from_me: author "+str(self.author)+" does not exists")
      return False
    return (a.me)

  def has_me(self):
    me=['kundera', 'kuntera' 'cuntera']
    for k in me:
      if (k in self.text.lower()):
        return True
    return False

  def from_friends(self,dbsession=None):
    a=get_dbobject_if_exists(YTAuthorRecord,self.author,dbsession)
    return (a.friend)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentThread():
  def __init__(self,tid,dbsession=None):
    self.tid=tid
    if not dbsession:
      self.dbsession=SqlSingleton().mksession()
    else:
      self.dbsession=dbsession

  def get_comment_list(self,with_tlc=False):
    #with_tlc=False
    if (with_tlc):
      return self.dbsession.query(YTComment).filter(
        or_((YTComment.parent == self.tid) , (YTComment.cid == self.tid))
        ).order_by(YTComment.updated)
    return self.dbsession.query(YTComment).filter(YTComment.parent == self.tid).order_by(YTComment.updated)


  def i_posted_there(self):
    comments=self.get_comment_list(True)
    print(comments)
    for c in comments:
      print("GARP: "+str(c))
      if (c.from_me(self.dbsession)):
        return True
    return False

  def compute_interest(self,cwr=None):
    #logging.debug("YTCommentThread.compute_interest: START")
    comments=self.get_comment_list(True)
    has_me=0
    from_me=0
    has_me_after=0
    replies_after=0
    most_recent_me=datetime.datetime(2000, 1, 1)
    most_recent_reply=datetime.datetime(2000, 1, 1)
    ignore_before=None
    if (cwr):
      ignore_before=cwr.ignore_before
    if ignore_before ==  None:
      ignore_before=datetime.datetime(2000, 1, 1)

    for c in comments:
      if (c.from_me(self.dbsession)):
        from_me+=1
        replies_after=0
        has_me_after=0
        if (c.updated > most_recent_me):
          most_recent_me=c.updated
      else:
        if (c.updated <= ignore_before):
          continue
        if (from_me>0):
          replies_after+=1
          if (c.has_me()):
            has_me_after+=1
        if (c.updated > most_recent_reply):
          most_recent_reply=c.updated
    interest_level=(from_me)*(replies_after+has_me_after*10)

    if (most_recent_me < datetime.datetime(2001, 1, 1)):
      most_recent_me = None
    if (most_recent_reply < datetime.datetime(2001, 1, 1)):
      most_recent_reply = None

    if (cwr):
      cwr.interest_level=interest_level
      cwr.most_recent_me=most_recent_me
      if (most_recent_me):
        if (not cwr.ignore_before):
           cwr.ignore_before=most_recent_me
        elif (most_recent_me>cwr.ignore_before):
          cwr.ignore_before=most_recent_me
      cwr.most_recent_reply=most_recent_reply
    return interest_level

  def set_interest(self,commit=True):
    cwr=get_dbobject_if_exists(YTCommentWorkerRecord,self.tid,self.dbsession)
    self.compute_interest(cwr)
    cwr.lastcompute=datetime.datetime.now()
    if (commit):
      self.dbsession.commit()

  def to_dict(self):
    d={}
    cwr=get_dbobject_if_exists(YTComment,self.tid,self.dbsession)
    if not cwr:
      return {}
    tlc=cwr.to_dict()
    d={'tlc': tlc}
    cl=[]
    cml=self.get_comment_list()
    for c in cml:
      cl.append(c.to_dict())
    d['clist']=cl
    return d




# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentThreadList():
  def __init__(self):
    self.dbsession=SqlSingleton().mksession()
    return

  def get_oldest_thread_of_interest(self):
    threads=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.interest_level != 0 ,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.most_recent_me).limit(1)
    if (threads.count()==0):
      return None
    t=YTCommentThread(threads[0].tid)
    return t

  def get_newest_thread_of_interest(self):
    threads=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.interest_level != 0,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.most_recent_reply.desc()).limit(1)
    if (threads.count()==0):
      return None
    t=YTCommentThread(threads[0].tid)
    return t

  def get_thread(self,tid):
    t=YTCommentThread(tid)
    return t

  def force_refresh_thread(self,tid):
    t=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
    if t:
      t.call_sql_task_threaded(0) # FIXME FIXME FIXME: semaphore!



  def set_ignore_from_comment(self,cid):
    cmt=get_dbobject_if_exists(YTCommentRecord,cid,self.dbsession)
    if (cmt):
      tid=cmt.parent
      if (tid == None):
        tid=cmt.cid
      tcwr=get_dbobject_if_exists(YTCommentWorkerRecord,tid,self.dbsession)
      tcwr.ignore_before=cmt.updated
      self.dbsession.commit()
      yct=YTCommentThread(tid,self.dbsession)
      yct.set_interest()

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
    ytct=YTCommentThread("Ugz84TKRQZboOin1LXJ4AaABAg",dbsession)
    if (ytct):
      print("GARP: "+str(ytct.compute_interest()))


def simple_test():
  dbsession=SqlSingleton().mksession()
  ytct=YTCommentThread("Ugz2eqcV5SC1sFC6FB14AaABAg",dbsession)
  print(ytct.compute_interest())
  ytct=YTCommentThread("UgjWCKGV7tqcM3gCoAEC",dbsession)
  ytct.set_interest()

# --------------------------------------------------------------------------
def main():
  simple_test()
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
