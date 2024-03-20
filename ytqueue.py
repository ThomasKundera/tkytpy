#!/usr/bin/env python3
import time

from tksecrets import google_api_key
from googleapiclient.discovery import build

import tkqueue

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YtTask(tkqueue.TkTaskUniq):
  def run(self,youtube):
    self.task(youtube)
    if (self.semaphore):
      self.semaphore.release()

# There will only be one instance of this,
# as it derivates from SingletonMeta
# Thus, we can queue googleapi requests here,
# without worrying of multitheads (hoppefully)
class YtQueue(tkqueue.QueueWorkUniq):
  def __init__(self):
    self.youtube=build('youtube','v3',
                       developerKey=google_api_key, cache_discovery=False)
    super().__init__()

  def do_work(self,item):
    time.sleep(10) # This impose less than 10.000 calls per day.
    # FIXME: using etags in headers is a must.
    item.run(self.youtube)
    del self.taskdict[item.tid]

class TestClass:
  def __init__(self,yid):
    self.yid=yid
    time.sleep(1)
    task=YtTask('populate:'+self.yid,self.populate)
    YtQueue().add(task)

  def populate(self,youtube):
    request=youtube.commentThreads().list(part='snippet',videoId=self.yid,maxResults=100,textFormat='html')
    print("\n-----------------\n")
    print(request.execute())
    print("\n-----------------\n")

# --------------------------------------------------------------------------
def main():
  logging.debug("tkyoutube test: START")
  t1=TestClass('j2GXgMIYgzU')
  #t1=TestClass('iphcyNWFD10')
  #t1=TestClass('aBr2kKAHN6M')
  #t1=TestClass('aBr2kKAHN6M')

  YtQueue().join()
  logging.debug("tkyoutube test: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
