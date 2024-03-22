#!/usr/bin/env python3
import time
from threading import Thread, Semaphore

from sqlrecord              import get_dbobject, get_dbsession
from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytcommentthread        import YTCommentThread
from sqlsingleton import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTThreadsEvaluationThread:
  def __init__(self,field_storage):
    self.field_storage=field_storage

  def run(self):
    logging.debug("YTThreadsEvaluationThread.run(): START")
    self.spint = Thread(target=self.spin)
    self.spint.start()
    logging.debug("YTThreadsEvaluationThread.run: END")

  def do_spin(self,chunck_size):
    tteval=self.dbsession.query(YTCommentWorkerRecord).filter(YTCommentWorkerRecord.lastcompute==None).limit(chunck_size) # FIXME: We could only get tid, here.
    # FIXME: as at many other places this will only work once.
    # Updates are not handled
    count=0
    for t in tteval:
      #time.sleep(0.1) # FIXME This is to let time to other threads as there is
      #                # no thread priority available
      YTCommentThread(t.tid,self.dbsession).set_interest(False)
      count+=1
    self.dbsession.commit()
    logging.debug("YTThreadsEvaluationThread.do_spin: END: processed "+str(count)+" items")

  def spin(self):
    logging.debug("YTThreadsEvaluationThread.spin: START")
    if (not self.field_storage):
      return # For tests, mostly
    self.dbsession=SqlSingleton().mksession()
    while True:
      time.sleep(1)
      self.do_spin(100)




# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  yte=YTThreadsEvaluationThread(field_storage)
  yte.run()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

