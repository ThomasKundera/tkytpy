#!/usr/bin/env python3
import tksingleton

from ytvideolist       import YTVideoList
from ytcommentthread   import YTCommentThreadList

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

  def get_video_list(self):
    return self.videos.get_video_dict()

  def get_newest_thread_of_interest(self):
    yth=self.commentthreadlist.get_newest_thread_of_interest()
    return yth.to_dict()

  def get_oldest_thread_of_interest(self):
    yth=self.commentthreadlist.get_oldest_thread_of_interest()
    return yth.to_dict()

  def get_unseen_new_threads(self):
    return {}


# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  tk=TkYt(field_storage)
  tk.setup()
  tk.add_video("https://www.youtube.com/watch?v=LaVip3J__8Y")
  return
  print(tk.get_oldest_thread_of_interest())
  print(tk.get_newest_thread_of_interest())

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
