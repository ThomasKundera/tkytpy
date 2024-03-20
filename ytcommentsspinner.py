#!/usr/bin/env python3
from sqlrecord              import get_dbobject
from ytcommentsworkerrecord import YTCommentsWorkerRecord
from ytspinner              import YTSpinner


import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentsSpinner(YTSpinner):
  def __init__(self,field_storage):
    self.cls=YTCommentsWorkerRecord
    super().__init__(field_storage)


# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  ycs=YTCommentsSpinner(field_storage)
  yts.run()
  from ytqueue import YtQueue
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
