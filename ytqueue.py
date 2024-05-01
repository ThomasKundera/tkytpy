#!/usr/bin/env python3
import time
import datetime

from tkqueue import QueueWorkUniq
from sqltask import SqlTaskUniq
from ytapi import YtApi

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# FIXME: should the design here not mix SQL/YT and only care about
# fetching the data?
class YtTask(SqlTaskUniq):
  def __init__(self,tid,cls,oid,priority=0,semaphore=None ,options=None):
    self.options=options
    super().__init__(tid,cls,oid,priority,semaphore)

  def do_run(self,youtube):
    logging.debug(type(self).__name__+".do_run(): START ("+str(self)+")")
    if (self.options):
      self.o.sql_task_threaded(self.dbsession,youtube,self.options)
    else:
      self.o.sql_task_threaded(self.dbsession,youtube)

  def run(self,youtube):
    logging.debug(type(self).__name__+".run(): START ("+str(self)+")")
    self.pre_run()
    self.do_run(youtube)
    self.post_run()

# There will only be one instance of this,
# as it derivates from SingletonMeta
# Thus, we can queue googleapi requests here,
# without worrying of multitheads (hoppefully)
class YtQueue(QueueWorkUniq):
  def __init__(self,wait_time=10):
    self.youtube=YtApi()
    super().__init__()

  def do_work(self,item):
    item.run(self.youtube)
    del self.taskdict[item.tid]

# --------------------------------------------------------------------------
def main():
  logging.debug("ytqueue test: START")
  from sqltestrecord import TestRecord
  from sqlsingleton import SqlSingleton, Base
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  t=TestRecord(dbsession,1)
  t.call_sql_task_threaded()
  YtQueue().join()
  time.sleep(2)
  print(YtQueue().q.qsize())
  logging.debug("ytqueue test: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
