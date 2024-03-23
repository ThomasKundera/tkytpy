#!/usr/bin/env python3
from ytthreadworkerrecord import YTThreadWorkerRecord
from ytspinner            import YTSpinner

from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTThreadWorkerRecord)
    self.update_from_videos()

  def update_from_videos(self):
    # Creating the table from video and filling it if not existing
    vl=self.field_storage.get_videos()
    for v in vl.values():
      t=get_dbobject(YTThreadWorkerRecord,v.yid,self.dbsession)
    self.dbsession.commit()

  def do_spin(self):
    self.update_from_videos()
    super().do_spin()


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

