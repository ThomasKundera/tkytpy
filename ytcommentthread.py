#!/usr/bin/env python3
import datetime
import sqlalchemy

from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytcommentrecord        import YTCommentRecord
from ytauthorrecord         import YTAuthorRecord
from sqlrecord              import SqlRecord

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


class YTThreadOfInterest(SqlRecord,Base):
  __tablename__            = 'ytthreadofinterest0_1'
  tid                      = sqlalchemy.Column(sqlalchemy.Unicode(50),primary_key=True)
  yid                      = sqlalchemy.Column(sqlalchemy.Unicode(50))
  interest_level           = sqlalchemy.Column(sqlalchemy.Integer)
  lastcompute              = sqlalchemy.Column(sqlalchemy.DateTime)

  def __init__(self,dbsession,tid,commit=True):
    self.tid=tid
    super().__init__(dbsession,commit)



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
    if (with_tlc):
      return self.dbsession.query(YTComment).filter(YTComment.parent == self.tid or YTComment.cid == self.tid).order_by(YTComment.updated)
    return self.dbsession.query(YTComment).filter(YTComment.parent == self.tid).order_by(YTComment.updated)

  def compute_interest(self):
    logging.debug("YTCommentThread.compute_interest: START")
    comments=self.get_comment_list(True)
    has_me=0
    from_me=0
    has_me_after=0
    replies_after=0
    most_recent_reply_after=datetime.datetime(2000, 1, 1)
    from_me=False
    for c in comments:
      if (c.from_me(self.dbsession)):
        from_me+=1
      if (not from_me):
        replies_after+=1
        if (c.has_me()):
           has_me_after+=1
        if (c.updated > most_recent_reply_after):
          most_recent_reply_after=c.updated
    if (from_me):
      Δt=(datetime.datetime.now()-most_recent_reply_after).total_seconds()
      Δt=min(1,Δt) # As we want the inverse
      τ=365.*24*3600./Δt # Will be 1 or less if comment older than one year
      # As we are for now working with integers only,
      # we'll convert <1 values to negative integers
      if (τ<1):
        τ=-1/τ
      value=from_me*(replies_after+has_me_after*has_me_after)*τ
      return int(value)
    return 0

  def set_interest(self,commit=True):
    interest_level=self.compute_interest()
    cwr=get_dbobject_if_exists(YTCommentWorkerRecord,self.tid,self.dbsession)
    cwr.interest_level=interest_level
    cwr.lastcompute=datetime.datetime.now()
    if (commit):
      self.dbsession.commit()

  def to_dict(self):
    d={}
    cwr=get_dbobject_if_exists(YTComment,self.tid,self.dbsession)
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
    threads=self.dbsession.query(YTCommentWorkerRecord).filter(YTCommentWorkerRecord.interest_level != 0).order_by(YTCommentWorkerRecord.interest_level.desc()).limit(1)
    if (threads.count()==0):
      return None
    t=YTCommentThread(threads[0].tid)
    return t

  def get_newest_thread_of_interest(self):
    threads=self.dbsession.query(YTCommentWorkerRecord).filter(YTCommentWorkerRecord.interest_level != 0).order_by(YTCommentWorkerRecord.interest_level).limit(1)
    if (threads.count()==0):
      return None
    t=YTCommentThread(threads[0].tid)
    return t

# --------------------------------------------------------------------------
def main():
  #yct=YTCommentThread('Ugz-g04lVUjL5K8Sv0h4AaABAg')
  #yct.set_interest()
  #return

  ytl=YTCommentThreadList()
  print(ytl.get_oldest_thread_of_interest())
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
