#!/usr/bin/env python3
import threading
from threading import Semaphore

import tksingleton
from ytqueue import YtQueue, YtTask
from ytcommentsworkerrecord import YTCommentsWorkerRecord


import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentsWorker(YTCommentsWorkerRecord):
  def __init__(self,yid):
    super().__init__(yid)

  def run(self):
    self.semaphore=Semaphore(1)
    while  (self.infulldownload): # FIXME: actual condition is more complex
      self.semaphore.acquire()
      self.call_download_chunck()

  def call_download_chunck(self):
    task=YtTask('populate:'+self.yid,self.download_chunck)
    YtQueue().add(task)

def comments_monitor(yid):
  cm=YTCommentsWorker(yid)
  cm.run()

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentsMonitor(metaclass=tksingleton.SingletonMeta):
  def __init__(self):
    self.threads={}
    return

  def add(self,yid):
    logging.debug("YTCommentsMonitor.add(): START")
    if yid in self.threads: return
    self.threads[yid]=threading.Thread(target=comments_monitor, args=(yid,))
    self.threads[yid].start()
