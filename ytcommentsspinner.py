#!/usr/bin/env python3
import datetime
from sqlalchemy import or_, and_, case
from sqlalchemy.sql import func
from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytspinner              import YTSpinner
from sqlsingleton           import SqlSingleton
from ytvideorecord          import YTVideoRecord

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTCommentWorkerRecord)

  def get_items_to_process(self):
    logging.debug(type(self).__name__+"get_items_to_process.(): START")
    #dt=datetime.datetime(2024, 4, 26, 0, 31, 38).timestamp()
    #sqlv=20240426003138
    #print(dt)
    #sys.exit(0)
    chunck_size=200 # FIXME
    now=datetime.datetime.now().timestamp()
    #print(datetime.datetime.now().timestamp())
    #ycwr=self.dbsession.query(YTCommentWorkerRecord.lastwork,
    #                          func.unix_timestamp(YTCommentWorkerRecord.lastwork),
    #                          #func.timestampdiff('SECOND',func.now(),YTCommentWorkerRecord.lastwork),
    #                          now-func.unix_timestamp(YTCommentWorkerRecord.lastwork)
    #                          ).limit(chunck_size)
    #for o in ycwr:
    #  print(o)
    #sys.exit(0)
    ycwr=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.done==False,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0)
        ).order_by( case((YTCommentWorkerRecord.lastwork == None,24./YTVideoRecord.monitor),
                        else_=(now-func.unix_timestamp(YTCommentWorkerRecord.lastwork))/(3600*YTVideoRecord.monitor))).limit(chunck_size)
    d={}
    for o in ycwr:
      #print (str(o.lastwork)+" "+str(o.yid))
      k=o.tid
      d[k]=o
    #sys.exit(0)
    return d

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
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
