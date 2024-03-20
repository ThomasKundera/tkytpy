#!/usr/bin/env python3
import threading
from threading import Semaphore

import tksingleton
from ytqueue import YtQueue, YtTaskSemaphore

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideosSpinner:
  def __init__(self,field_storage):
    self.field_storage=field_storage
    self.semaphore=Semaphore(1)
    self.spin()


  def call_populates(self,item):
    priority=item[0]
    v=item[1]
    self.semaphore.acquire()
    task=YtTaskSemaphore('populate:'+v.yid,v.queued_populate,self.semaphore,priority)
    YtQueue().add(task)

  def spin(self):
    while True:
      vl=[]
      vd=self.field_storage.get_videos()
      for v in vd.values():
        p=v.RefreshPriority()
        vl.append((p,v))
      vls=sorted(vl, key=lambda x: x[0])
      v=vls[0][1]
      self.call_populates(vls[0])


# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yvs=YTVideosSpinner(field_storage)

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

