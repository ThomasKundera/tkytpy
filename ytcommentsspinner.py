#!/usr/bin/env python3
from math import log10
import datetime
from sqlalchemy import or_, and_, case
from sqlalchemy.sql import func
from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytspinner              import YTSpinner
from sqlsingleton           import SqlSingleton, get_dbobject_if_exists
from ytvideorecord          import YTVideoRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTCommentWorkerRecord)


  def get_item_to_process(self):
    logging.debug(type(self).__name__+"get_item_to_process.(): START")
    now=datetime.datetime.now().timestamp()

    # To add a bit of fuziness, YTVideoRecord.monitor is scrambled a bit
    # FIXME: would need floats

    ycwr=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0)
        ).order_by(
          case(
            (YTCommentWorkerRecord.lastwork == None,100./YTVideoRecord.monitor),  # Easy
          else_=(
            case(
              (YTCommentWorkerRecord.done != None, # Then it's a redo
               case((YTCommentWorkerRecord.most_recent_me == None, # I never published here
              10000*(10.-func.least(func.log10(now-func.unix_timestamp(YTCommentWorkerRecord.lastwork)),9))/YTVideoRecord.monitor), # 100 times harder than easy
               else_=(2000*(10.-func.least(func.log10(now-func.unix_timestamp(YTCommentWorkerRecord.lastwork)),9))/YTVideoRecord.monitor))), # 20 times harder than easy: we want to see new comments on known threads. # FIXME: shouldn't recent threads be more favorized?
              else_=1000*(10.-func.least(func.log10(now-func.unix_timestamp(YTCommentWorkerRecord.lastwork)),9))/YTVideoRecord.monitor) # 10 times harder than easy
              )
          )).limit(1)
    for o in ycwr:
      priority=1000
      y=get_dbobject_if_exists(YTVideoRecord,o.yid,self.dbsession)
      # FIXME: tests missing in case it changed along the way
      if (not o.lastwork):
        priority=900./y.monitor
      else:
        if (o.done):
          if (not o.most_recent_me):
            priority=10000000*(10.-min(log10(now-o.timestamp()),9))/y.monitor
          else:
            priority=100000*(10.-min(log10(now-o.lastwork.timestamp-()),9))/y.monitor
        else:
          priority=1000*(10.-min(log10(now-o.lastwork.timestamp()),9))/y.monitor
      #priority=priority
      return (priority,o)
    return None # No matching item found


# --------------------------------------------------------------------------
def main():
  from fieldstorage    import FieldStorage
  from ytqueue         import YtQueue
  field_storage = FieldStorage()
  YtQueue(1)
  ycs=YTCommentsSpinner(field_storage)
  ycs.run()
  from ytqueue import YtQueue
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
