#!/usr/bin/env python3
import datetime
from sqlalchemy import or_, and_, case
from sqlalchemy.sql import func
from ytspinner            import YTSpinner
from ytvideorecord        import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbobject_if_exists, get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideosSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTVideoRecord)

  def get_item_to_process(self):
    logging.debug(type(self).__name__+".get_item_to_process.(): START")
    now=datetime.datetime.now().timestamp()

    yvr=self.dbsession.query(YTVideoRecord).filter(
        and_(YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0)
        ).order_by(
          case(
            (YTVideoRecord.lastrefreshed == None,100./YTVideoRecord.monitor),
          else_=1000*(10.-func.least(func.log10(now-func.unix_timestamp(YTVideoRecord.lastrefreshed)),9))/YTVideoRecord.monitor
              )
          ).limit(1)
    for o in yvr:
      priority=100./(0.01+o.monitor)
      if (o.populated): # It's a redo
        priority=10000000./(0.01+o.monitor)
      #yvpriority=get_dbobject_if_exists(YTVideoRecord,o.yid,self.dbsession)
      return (priority,o)
    return None # No matching item found

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yvs=YTVideosSpinner(field_storage)
  yvs.run()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

