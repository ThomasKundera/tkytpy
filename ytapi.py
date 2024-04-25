#!/usr/bin/env python3
import time
import datetime
import json
import pickle

from diskcache import Cache

from tksecrets import google_api_key
from googleapiclient.discovery import build

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import tksingleton

class CachedItem:
  def __init__(self,request,answer):
    self.date=datetime.datetime.now()
    self.request=request
    self.answer=answer

class DataCache:
  def __init__(self):
    self.cache=Cache("./data")

#  def __del__(self):
#    self.cache.close()

  def answer(self,key):
    logging.debug("DataCache.answer(): START")
    res=self.cache.get(key)
    logging.debug("DataCache.answer(): cache stats: "+str(self.cache.stats()))
    if not res: return None
    ans=pickle.loads(res).answer
    return ans

  def set(self,key,request,answer):
    logging.debug("DataCache.set(): START")
    ci=CachedItem(request,answer)
    pki=pickle.dumps(ci)
    self.cache.set(key,pki)

class YtApi(metaclass=tksingleton.SingletonMeta):
  def __init__(self,wait_time=1):
    self.youtube=build('youtube','v3',
                       developerKey=google_api_key, cache_discovery=False)
    self.wait_time=wait_time
    self.lastrun=datetime.datetime.now()
    self.cache=DataCache()
    super().__init__()

  def wait_a_bit(self):
    now=datetime.datetime.now()
    Δt=now-self.lastrun
    self.lastrun=now
    st=max(self.wait_time-Δt.total_seconds(),0)
    logging.debug("YtApi.wait_a_bit(): Sleeping "+str(st)+"s")
    time.sleep(st) # This impose less than 10.000 calls per day.

  def process_request(self,request,ytr):
    logging.debug("YtApi.process_request(): START")
    key=json.loads(ytr.to_json())['uri']
    answer=self.cache.answer(key)
    if (answer): return answer
    self.wait_a_bit()
    answer=ytr.execute()
    self.cache.set(key,request,answer)
    return answer

  def process_request_commentthread_list(self,request):
    ytr=self.youtube.commentThreads().list(**request)
    return (self.process_request(request,ytr))


# --------------------------------------------------------------------------
def main():
  logging.debug("ytapi test: START")
  someid='j2GXgMIYgzU'
  yta=YtApi()
  for i in range(3):
    yta.process_request_commentthread_list({'part': 'id,snippet',
                                          'videoId': someid,
                                          'maxResults': 2,
                                          'textFormat': 'html'})
  logging.debug("tkyoutube test: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
