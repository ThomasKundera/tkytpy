#!/usr/bin/env python3
import tksingleton

from ytvideolist       import YTVideoList

class TkYt(metaclass=tksingleton.SingletonMeta):
  def __init__(self,field_storage):
    self.field_storage=field_storage
    return

  def setup(self):
    self.videos=YTVideoList(self.field_storage)

  def add_video(self,yid):
    self.videos.add_from_yid(yid.strip())

  def get_video_list(self):
    return self.videos.get_video_dict()

  def get_newest_thread_of_interest(self):
    return {}

  def get_oldest_thread_of_interest(self):
    return {}

  def get_unseen_new_threads(self):
    return {}

