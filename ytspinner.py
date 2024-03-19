#!/usr/bin/env python3
import time
import threading
from threading import Semaphore

import tksingleton
from ytqueue import YtQueue, YtTaskSemaphore

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTSpinner:
  def __init__(self,field_storage):
    self.field_storage=field_storage
    self.semaphore=Semaphore(1)
    self.spin()

  def call_populates(self,item):
    priority=item[0]
    t=item[1]
    yid=t.get_id()
    yid=t.get_id()
    self.semaphore.acquire()
    task=YtTaskSemaphore('populate:'+type(t).__name__+"-"+yid,t.queued_populate,self.semaphore,priority)
    YtQueue().add(task)

  def queued_populate(self,youtube):
    time.sleep(10) # Just for tests

  def spin(self):
    if (not self.field_storage):
      return # For tests, mostly
    while True:
      ol=[]
      od=self.field_storage.get_dict(self.cls)
      for o in od.values():
        p=o.RefreshPriority()
        ol.append((p,o))
      ols=sorted(ol, key=lambda x: x[0])
      self.call_populates(ols[0])


# --------------------------------------------------------------------------
def main():
  ys=YTSpinner(None)
  print(type(ys).__name__)
  return
# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

