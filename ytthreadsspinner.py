#!/usr/bin/env python3
from math import log10
import time
import datetime
from sqlalchemy import or_, and_, case
from sqlalchemy.sql import func
from ytthreadworkerrecord import YTThreadWorkerRecord, Options
from ytspinner            import YTSpinner
from ytvideorecord        import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbobject_if_exists,get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTThreadWorkerRecord)
    # FIXME: temporary hack
    return
    #options=Options()
    #options.force_restart =True
    #options.force_continue=True
    #options.force_refresh =False
    #options.priority=10
    #ytw=get_dbobject_if_exists(YTThreadWorkerRecord,'TW6hgO#c3wuI')
    #ytw.call_refresh(options)

  def update_from_videos(self):
    # Creating the table from video and filling it if not existing
    vl=self.field_storage.get_videos()
    for v in vl.values():
      t=get_dbobject(YTThreadWorkerRecord,v.yid,self.dbsession)
    self.dbsession.commit()

  def do_spin_new(self):
    #time.sleep(30)
    #return
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
                    5000*(10.-func.least(func.log10(now-func.unix_timestamp(YTThreadWorkerRecord.lastwork)),9))/YTVideoRecord.monitor), # 100 times harder than easy
              else_=1000*(10.-func.least(func.log10(now-func.unix_timestamp(YTThreadWorkerRecord.lastwork)),9))/YTVideoRecord.monitor) # 10 times harder than easy
              )
          )).limit(1)
    for o in ycwr:
      priority=1000
      y=get_dbobject_if_exists(YTVideoRecord,o.yid,self.dbsession)
      # FIXME: tests missing in case it changed along the way
      if (not o.lastwork):
        prority=100./y.monitor
      else:
        if (not o.nexttreadpagetoken):
          priority=10000000*(10.-min(log10(now-o.lastwork.timestamp()),9))/y.monitor
        else:
          priority=1000*(10.-min(log10(now-o.lastwork.timestamp()),9))/y.monitor
      return (priority,o)
    return None # No matching item found

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  from ytqueue import YtQueue
  field_storage = FieldStorage()
  YtQueue().meanpriority=10000
  yts=YTThreadsSpinner(field_storage)
  yts.run()
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

