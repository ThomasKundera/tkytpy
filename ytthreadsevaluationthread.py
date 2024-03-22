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

  def do_spin(self):
    logging.debug("YTThreadsEvaluationThread.do_spin(): START")
    ol=[]

    for o in od.values():
      p=o.get_priority()
      ol.append((p,o))
    ols=sorted(ol, key=lambda x: x[0])
    if (len(ols) and ols[0][0] < 1000000): # FIXME
      logging.debug("YTThreadsEvaluationThread.do_spin(): selected "+str(ols[0]))
      self.call_populate(ols[0])
    else:
      logging.debug("YTThreadsEvaluationThread.do_spin(): Nothing to do")
      time.sleep(1)
    logging.debug("YTThreadsEvaluationThread.do_spin(): END")


  def do_spin(self,chunck_size):
    tteval=self.dbsession.query(YTCommentWorkerRecord).filter(YTCommentWorkerRecord.lastcompute==None).limit(chunck_size) # FIXME: We could only get tid, here.
    # FIXME: as at many other places this will only work once.
    # Updates are not handled
    for t in tteval:
      #time.sleep(0.1) # FIXME This is to let time to other threads as there is
      #                # no thread priority available
      YTCommentThread(t.tid,self.dbsession).set_interest(False)
    self.dbsession.commit()

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

