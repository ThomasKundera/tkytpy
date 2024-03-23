#!/usr/bin/env python3
from ytthreadworkerrecord import YTThreadWorkerRecord
from ytspinner            import YTSpinner
from ytvideorecord        import YTVideoRecord

from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbsession

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTVideosSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTVideoRecord)

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yvs=YTVideosSpinner(field_storage)
  yvs.run()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

