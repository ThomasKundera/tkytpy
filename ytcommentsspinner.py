#!/usr/bin/env python3
from sqlalchemy import or_, and_
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
    chunck_size=200 # FIXME
    ycwr=self.dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.done==False,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False)
        ).order_by(YTCommentWorkerRecord.lastwork).limit(chunck_size)
    d={}
    for o in ycwr:
      k=o.tid
      d[k]=o
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
