#!/usr/bin/env python3
from tkqueue import TkTask
from sqlsingleton import SqlSingleton, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class SqlTask(TkTask):
  def __init__(self,cls,oid,priority=0,semaphore=None):
    self.cls=cls
    self.oid=oid
    super().__init__(None,priority,semaphore)

  def pre_run(self):
    # We are now in out new thread
    # lets create a session we will work in
    # and instantiate an object that belongs to it
    # before actually doing sql stuff.
    self.dbsession=SqlSingleton().mksession()
    self.o=get_dbobject_if_exists(self.cls,self.oid,self.dbsession)

  def do_run(self):
    self.o.sql_task_threaded(self.dbsession)

  def post_run(self):
    self. dbsession.commit()
    self.dbsession.merge(self.o)
    if (self.semaphore):
      self.semaphore.release()

  def run(self):
    self.pref_run()
    self.do_run()
    self.post_run()

  def __lt__(self,o):
    return self.priority < o.priority

  def __eq__(self,o):
    return self.priority ==  o.priority

  def __str__(self):
    return str(self.cls)+"-"+str(self.oid)

class SqlTaskUniq(SqlTask):
  def __init__(self,tid,cls,oid,priority=0,semaphore=None):
    self.tid=tid
    super().__init__(cls,oid,priority,semaphore)

  def __str__(self):
    return self.tid



# --------------------------------------------------------------------------
def main():
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
