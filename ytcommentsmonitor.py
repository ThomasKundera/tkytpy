#!/usr/bin/env python3
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import tksingleton

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentsMonitor(metaclass=tksingleton.SingletonMeta):
  def __init__(self,v):
    self.yids={}
    return

  def add(self,yid):
    if yid in self.yids: return
    self.yids[yid]=None

