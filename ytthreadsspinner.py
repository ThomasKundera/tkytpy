#!/usr/bin/env python3
import time
import datetime
from sqlalchemy import or_, and_, case
from sqlalchemy.sql import func
from ytthreadworkerrecord import YTThreadWorkerRecord
from ytspinner            import YTSpinner
from ytvideorecord        import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTThreadWorkerRecord)

  def update_from_videos(self):
    # Creating the table from video and filling it if not existing
    vl=self.field_storage.get_videos()
    for v in vl.values():
      t=get_dbobject(YTThreadWorkerRecord,v.yid,self.dbsession)
    self.dbsession.commit()

  def do_spin(self):
    self.update_from_videos()
    super().do_spin_new()

  def get_item_to_process(self):
    logging.debug(type(self).__name__+"get_item_to_process.(): START")
    now=datetime.datetime.now().timestamp()
    # if Δt=now-lastwork
    # Δt between 0 and 10⁸, about.
    # log10(Δt) between 1 and 9, about
    # min(log10(Δt),9) between 1 and 9
    # 10-min(log10(Δt),9) between 1 and 10
    # None should be 1.
    # Then divide by monitor
    # For monitor=1 None: 1 : wins against any Δt
    # For monitor=2 None: 1 : wins against Δt<10⁸
    # For monitor=3 None: 1 : wins against Δt<10⁷
    # ...
    # For monitor=10 None: 1 : always loose
    ycwr=self.dbsession.query(YTThreadWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTThreadWorkerRecord.yid).filter(
        and_(YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0)
        ).order_by(
          case(
            (YTThreadWorkerRecord.lastwork == None,100./YTVideoRecord.monitor),  # Easy
          else_=(
            case(
              (YTThreadWorkerRecord.nexttreadpagetoken == None, # It's a redo
                    10000*(10.-func.least(func.log10(now-func.unix_timestamp(YTThreadWorkerRecord.lastwork)),9))/YTVideoRecord.monitor), # 100 times harder than easy
              else_=1000*(10.-func.least(func.log10(now-func.unix_timestamp(YTThreadWorkerRecord.lastwork)),9))/YTVideoRecord.monitor) # 10 times harder than easy
              )
          )).limit(1)
    for o in ycwr:
      priority=1000
      if (o.lastwork and (not o.nexttreadpagetoken)): # It's a redo
        time.sleep(10) # FIXME crude deprioritisation
        print("Really trying!!!")
        priority=10000
      return (priority,o)
    return None # No matching item found

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yts=YTThreadsSpinner(field_storage)
  yts.run()
  from ytqueue import YtQueue
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

