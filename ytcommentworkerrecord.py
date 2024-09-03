#!/usr/bin/env python3
import unittest
import datetime
from sqlalchemy.sql import func
import sqlalchemy

from sqlalchemy import or_, and_
from ytcommentworkerrecord0  import YTCommentWorkerRecord0
from ytcommentrecord        import YTCommentRecord
from ytauthorrecord         import YTAuthorRecord
from sqlrecord              import SqlRecord
from ytvideorecord          import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentWorkerRecord(YTCommentWorkerRecord0):
  def __init__(self,dbsession,tid,commit=None):
    logging.debug("YTCommentWorkerRecord.__init__("+str(tid)+"): START")
    super().__init__(dbsession,tid,commit)

  def get_comment_list(self,dbsession,with_tlc=False):
    print("GARP: "+str(dbsession))
    #with_tlc=False
    if (with_tlc):
      return dbsession.query(YTCommentRecord).filter(
        or_((YTCommentRecord.parent == self.tid) , (YTCommentRecord.cid == self.tid))
        ).order_by(YTCommentRecord.updated)
    return dbsession.query(YTCommentRecord).filter(YTCommentRecord.parent == self.tid).order_by(YTCommentRecord.updated)

  def delete(self,dbsession):
    logging.debug("YTCommentWorkerRecord.delete(): START: FIXME")
    # not doing it #FIXME
    return
    comments=self.get_comment_list(dbsession,True)
    dbsession.delete(comments)

  def i_posted_there(self,dbsession):
    comments=self.get_comment_list(dbsession,True)
    print(comments)
    for c in comments:
      print("GARP: "+str(c))
      if (c.from_me(dbsession)):
        return True
    return False

  def compute_interest(self,dbsession,do_set=False):
    logging.debug("YTCommentWorkerRecord.compute_interest: START")
    comments=self.get_comment_list(dbsession,True)
    has_me=0
    from_me=0
    has_me_after=0
    replies_after=0
    most_recent_me=datetime.datetime(2000, 1, 1)
    most_recent_reply=datetime.datetime(2000, 1, 1)
    ignore_before=self.ignore_before
    if ignore_before ==  None:
      ignore_before=datetime.datetime(2000, 1, 1)

    for c in comments:
      if (c.from_me(dbsession)):
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

    if (do_set):
      self.interest_level=interest_level
      self.most_recent_me=most_recent_me
      if (most_recent_me):
        if (not self.ignore_before):
          self.ignore_before=most_recent_me
        elif (most_recent_me>self.ignore_before):
          self.ignore_before=most_recent_me
        self.most_recent_reply=most_recent_reply
      self.lastcompute=datetime.datetime.now()
      # dealing with video mostrecentme:
      if (most_recent_me):
        v=get_dbobject_if_exists(YTVideoRecord,self.yid,dbsession)
        # FIXME: if not v? (shouldn't be)
        if (v.mostrecentme):
          if (most_recent_me>v.mostrecentme):
            v.mostrecentme=most_recent_me
        else:
          v.mostrecentme=most_recent_me
    return interest_level

  def set_interest(self,dbsession,commit=True):
    logging.debug("YTCommentWorkerRecord.set_interest(): START")
    self.compute_interest(dbsession,True)
    #cwr=get_dbobject_if_exists(YTCommentWorkerRecord,self.tid,dbsession)
    #self.compute_interest(cwr)
    #self.interest_level=level
    logging.debug("YTCommentWorkerRecord.set_interest(): interest_level = "+str(self.interest_level))
    if (commit):
      dbsession.commit()

  def completed(self,dbsession):
    logging.debug("YTCommentWorkerRecord.completed(): START")
    self.done=True
    self.nextcmtpagetoken=None
    self.lastwork=datetime.datetime.now()
    self.set_interest(dbsession,False)
    logging.debug("YTCommentWorkerRecord.completed(): 2")
    if ((not self.most_recent_me) and (not self.most_recent_reply)):
      logging.debug("YTCommentWorkerRecord.completed(): Erasing comments")
      self.delete(dbsession)
    logging.debug("YTCommentWorkerRecord.completed(): END")

  def to_dict(self,dbsession):
    d={}
    cwr=get_dbobject_if_exists(YTCommentRecord,self.tid,dbsession)
    if not cwr:
      return {}
    tlc=cwr.to_dict()
    d={'tlc': tlc}
    cl=[]
    cml=self.get_comment_list(dbsession)
    for c in cml:
      cl.append(c.to_dict())
    d['clist']=cl
    return d

# --------------------------------------------------------------------------
def main():
  import time
  from ytqueue        import YtQueue
  from ytvideo import get_video_ids_from_file
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  YtQueue(1)
  vidlist=get_video_ids_from_file('yturls.txt')
  ycwlist=[]
  for yid in vidlist:
    ycwl=dbsession.query(YTCommentWorkerRecord).filter( YTCommentWorkerRecord.yid == yid )
    if (not ycwl): continue
    ycwlist.append(ycwl)

  for ycwl in ycwlist:
    for ycw in ycwl:
      ycw.call_sql_task_threaded()
    time.sleep(1)
  YtQueue().join()
  dbsession.commit()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
