#!/usr/bin/env python3
import datetime

from ytcommentworkerrecord  import YTCommentWorkerRecord
from sqlrecord              import SqlRecord, get_dbsession, get_dbobject, get_dbobject_if_exists

from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentThread():
  def __init__(self,tid):
    self.tid=tid

  def compute_interest(self):
    return 0


  def set_interest(self):
    interest_level=self.compute_interest()
    dbsession=SqlSingleton().mksession()
    cwr=get_dbobject_if_exists(YTCommentWorkerRecord,self.tid,dbsession)
    cwr.interest_level=interest_level
    cwr.lastcompute=datetime.datetime.now()
    dbsession.commit()


# --------------------------------------------------------------------------
def main():
  yct=YTCommentThread('Ugw-0kWl9ROhXGJe_cR4AaABAg')
  yct.set_interest()
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
