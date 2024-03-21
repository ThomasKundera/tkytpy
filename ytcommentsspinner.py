#!/usr/bin/env python3
from sqlrecord              import get_dbobject
from ytcommentworkerrecord import YTCommentWorkerRecord
from ytspinner              import YTSpinner

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class YTCommentsSpinner(YTSpinner):
  def __init__(self,field_storage):
    super().__init__(field_storage,YTCommentWorkerRecord)


# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  ycs=YTCommentsSpinner(field_storage)
  ycs.run()
  from ytqueue import YtQueue
  YtQueue().join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
