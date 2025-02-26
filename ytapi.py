#!/usr/bin/env python3
import os
import time
import datetime
import json
import pickle

from diskcache import Cache

from tksecrets import google_api_key
from googleapiclient.discovery import build
from googleapiclient.errors    import HttpError

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class CachedItem:
  def __init__(self,request,answer):
    self.date=datetime.datetime.now()
    self.request=request
    self.answer=answer

class DataCache:
  def __init__(self):
    self.cache=Cache("./data")

  def answer(self,key):
    logging.debug("DataCache.answer(): START")
    res=self.cache.get(key)
    logging.debug("DataCache.answer(): cache stats: "+str(self.cache.stats()))
    if not res:
      logging.debug("DataCache.answer(): Cache miss")
      return None
    ans=pickle.loads(res).answer
    logging.debug("DataCache.answer(): Cache hit")
    return ans

  def set(self,key,request,answer):
    logging.debug("DataCache.set(): START")
    ci=CachedItem(request,answer)
    pki=pickle.dumps(ci)
    self.cache.set(key,pki)

# Built  to mimick youtube API so that we don't have to change the rest of the code at all
# Likely overcomplex, but works.

class YtApiExecute:
  def __init__(self,what,args):
    self.what=what
    self.args=args

  def execute(self,force=None):
    retry=0
    while (retry<10):
      retry+=1
      try:
        return self.what(force,self.args)
      except HttpError as err:
        logging.debug("YtApiExecute.execute(): ERROR ( "+str(err.code)+" )")
        if (err.code == 403):
            # This usually means we exceeded quota.
            # We abort the whole thing
            os._exit(-1)
        time.sleep(30)
    return None

class YtApiWork:
  def __init__(self,ytapi):
    self.ytapi=ytapi

class YtApicommentThreads(YtApiWork):
  def  __init__(self,ytapi):
    super().__init__(ytapi)

  def list(self,**kwargs):
    return YtApiExecute(self.ytapi.execute_commentthread_list,kwargs)

class YtApicomments(YtApiWork):
  def  __init__(self,ytapi):
    super().__init__(ytapi)

  def list(self,**kwargs):
    return YtApiExecute(self.ytapi.execute_comments_list,kwargs)

class YtApivideos(YtApiWork):
  def  __init__(self,ytapi):
    super().__init__(ytapi)

  def list(self,**kwargs):
    return YtApiExecute(self.ytapi.execute_videos_list,kwargs)

# metaclass=tksingleton.SingletonMeta ? Would be nice
# but can't be nested in ytqueue which is also Singleton
# So be simple and clear:
# YtApi should just never be called directly, but only through YtQueue
class YtApi:
  def __init__(self,wait_time=10):
    self.youtube=build('youtube','v3',
                       developerKey=google_api_key, cache_discovery=False)
    self.wait_time=wait_time
    self.lastrun=datetime.datetime.now()
    self.cache=DataCache()
    self.ytacommentThreads=YtApicommentThreads(self)
    self.ytacomments=YtApicomments(self)
    self.ytavideos=YtApivideos(self)
    super().__init__()

  def wait_a_bit(self):
    now=datetime.datetime.now()
    Δt=now-self.lastrun
    st=max(self.wait_time-Δt.total_seconds(),0)
    logging.debug("YtApi.wait_a_bit(): Sleeping "+str(st)+"s ( Δt= "+str(Δt.total_seconds())+"s )")
    time.sleep(st) # This impose less than 10.000 calls per day.


  def do_process_request(self,force,request,ytr,key):
    self.wait_a_bit()
    answer=ytr.execute()
    self.lastrun=datetime.datetime.now()
    self.cache.set(key,request,answer)
    return answer

  def process_request(self,force,request,ytr):
    logging.debug("YtApi.process_request(): START")
    key=json.loads(ytr.to_json())['uri']
    if not force:
      answer=self.cache.answer(key)
      if (answer): return answer
    retry=0
    while retry <10:
      try:
        answer=self.do_process_request(force,request,ytr,key)
        return answer
      except TimeoutError:
        logging.debug("YtApi.process_request(): Timeout")
        time.sleep(30) # When self.wait_time is low, it's usefull to anyway wait some time.
      retry+=1
    raise # No answer,better to kill the thread.

  def execute_commentthread_list(self,force,request):
    ytr=self.youtube.commentThreads().list(**request)
    return (self.process_request(force,request,ytr))

  def execute_comments_list(self,force,request):
    ytr=self.youtube.comments().list(**request)
    return (self.process_request(force,request,ytr))

  def execute_videos_list(self,force,request):
    ytr=self.youtube.videos().list(**request)
    return (self.process_request(force,request,ytr))

  def commentThreads(self):
    return self.ytacommentThreads

  def comments(self):
    return self.ytacomments

  def videos(self):
    return self.ytavideos


def teststuff():
  uri="https://youtube.googleapis.com/youtube/v3/commentThreads?part=id%2Csnippet%2Creplies&videoId=xPksF_JFNEI&pageToken=Z2V0X25ld2VzdF9maXJzdC0tQ2dnSWdBUVZGN2ZST0JJRkNJZ2dHQUFTQlFpb0lCZ0FFZ1VJaVNBWUFCSUZDSjBnR0FFU0JRaUhJQmdBR0FBaURnb01DT080d01RRkVJQ3c3S2NC&maxResults=100&key=AIzaSyBehkZDTzG8E4dnVHKRzCN_nGPU6gt83Hk&alt=json"
  cache=DataCache()
  key=uri
  answer=cache.answer(key)
  npt=answer['nextPageToken']
  print(npt)
  uri2="https://youtube.googleapis.com/youtube/v3/commentThreads?part=id%2Csnippet%2Creplies&videoId=xPksF_JFNEI&pageToken="+npt+"&maxResults=100&key=AIzaSyBehkZDTzG8E4dnVHKRzCN_nGPU6gt83Hk&alt=json"
  print (uri2)

# --------------------------------------------------------------------------
def main():
  logging.debug("ytapi test: START")
  teststuff()
  return
  someid='iphcyNWFD10'
  yta=YtApi()
  for i in range(3):
    request=yta.commentThreads().list(part='id,snippet',videoId=someid,maxResults=2,textFormat='html')
    print(request.execute())
  print(request.execute(True))
  logging.debug("tkyoutube test: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
