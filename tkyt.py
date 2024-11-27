#!/usr/bin/env python3
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import tksingleton

from ytvideolist           import YTVideoList
from ytcommentthreadlist   import YTCommentThreadList

class TkYt(metaclass=tksingleton.SingletonMeta):
  def __init__(self,field_storage):
    self.field_storage=field_storage
    return

  def setup(self):
    self.videos           =YTVideoList(self.field_storage)
    self.commentthreadlist=YTCommentThreadList()

  def add_video(self,yid):
    yid=yid.strip()
    if (len(yid)>11):
      yid=yid.split('?')
      if (len(yid)>1):
        yid=yid[1].split('=')
        if (len(yid)>1):
           yid=yid[1][0:11]
    if (yid):
      self.videos.add_from_yid(yid)

  def get_video(self,yid):
    vd=self.videos.get_one_video_dict(yid)
    ccount=self.commentthreadlist.get_commentcount_for_video(yid)
    vd['recordedcommentcount']=ccount
    return vd


  def get_video_list(self):
    vl=self.videos.get_video_dict()
    ccount=self.commentthreadlist.get_commentcount_per_video()
    for v in vl['ytvlist']:
      if v['yid'] in ccount:
        v['recordedcommentcount']=ccount[v['yid']]
      else:
        v['recordedcommentcount']=0
    return vl

  def video_checkbox_action(self,action,yid,checked):
    return self.videos.checkbox_action(action,yid,checked)

  def video_monitor_action(self,yid,value):
    return self.videos.set_monitor(yid,value)

  def video_refresh_action(self,yid):
    #print("video_refresh_action")
    #return {}
    return self.videos.refresh(yid)

  def video_refresh_all_action(self):
    return self.videos.refresh_all()

  def get_number_of_threads_of_interest(self):
    return self.commentthreadlist.get_number_of_threads_of_interest()


  def get_newest_threads_of_interest(self,nb=1):
    return self.commentthreadlist.get_newest_threads_of_interest_as_dict(nb)

  def get_oldest_threads_of_interest(self,nb=1):
    return self.commentthreadlist.get_oldest_threads_of_interest_as_dict(nb)

  def get_thread(self,tid):
    return self.commentthreadlist.get_thread_dict(tid)

  def force_refresh_thread(self,tid):
    self.commentthreadlist.force_refresh_thread(tid)

  def get_unseen_new_threads(self):
    return {}

  def set_ignore_from_comment(self,cid):
    if (not cid): return
    self.commentthreadlist.set_ignore_from_comment(cid)
    return {}


# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  tk=TkYt(field_storage)
  tk.setup()
  #tk.add_video("https://www.youtube.com/watch?v=LaVip3J__8Y")
  #return
  
  tk.force_refresh_thread('UgxJPjS09BYJeA6ucnV4AaABAg')

  return
  print(tk.get_oldest_thread_of_interest())
  print(tk.get_newest_thread_of_interest())

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
