#!/usr/bin/env python3
from sqlrecord            import get_dbobject
from ytthreadworkerrecord import YTThreadWorkerRecord
from ytspinner            import YTSpinner

from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadsSpinner(YTSpinner):
  def __init__(self,field_storage):
   self.cls=YTThreadWorkerRecord
   # Creating thr table from video and filling it if not existing
   vl=field_storage.get_videos()
   dbsession=SqlSingleton().mksession()
   for v in vl.values():
     t=get_dbobject(YTThreadWorkerRecord,v.yid,dbsession)
   dbsession.commit()
   super().__init__(field_storage)



# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yts=YTThreadsSpinner(field_storage)
  from ytqueue import YtQueue
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

