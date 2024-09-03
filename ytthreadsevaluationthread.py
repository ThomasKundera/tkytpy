#!/usr/bin/env python3
import time
import datetime
from threading import Thread, Semaphore
#from sqlalchemy import nulls_first
from sqlalchemy import case, or_, and_

from ytcommentworkerrecord  import YTCommentWorkerRecord
from ytvideorecord          import YTVideoRecord
from sqlsingleton import SqlSingleton, Base, get_dbobject, get_dbsession

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

  def default_chunk(self,dbsession,chunck_size):
    return dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0,
             YTCommentWorkerRecord.done==True)
        ).order_by(
          (YTCommentWorkerRecord.lastcompute-YTCommentWorkerRecord.lastwork)/YTVideoRecord.monitor).limit(chunck_size)

  def value_thread_chunck(self,dbsession,chunck_size):
    return dbsession.query(YTCommentWorkerRecord).join(
      YTVideoRecord,YTVideoRecord.yid==YTCommentWorkerRecord.yid).filter(
        and_(YTCommentWorkerRecord.done==True,
             YTCommentWorkerRecord.interest_level>0,
             YTVideoRecord.valid == True,
             YTVideoRecord.suspended ==False,
             YTVideoRecord.monitor>0)
        ).order_by(
          (YTCommentWorkerRecord.lastcompute-YTCommentWorkerRecord.lastwork)/YTVideoRecord.monitor).limit(chunck_size)

  def do_spin(self,dbsession,chunck_size):
    startdate=datetime.datetime.now()
    chunck_size=100
    tteval=self.value_thread_chunck(dbsession,chunck_size)
    count=0
    # FIXME: date at which recompute is meaningful
    lastcompute=tteval[0].lastcompute
    if (lastcompute):
      print("SHOULD NOT BE NONE: "+str(lastcompute)+" "+str(tteval[0].lastcompute))
      Δt=(datetime.datetime.now()-lastcompute).total_seconds()
      if (Δt < 10*60): # FIXME
        # Useless to recompute so often, waiting a bit and leaving
        time.sleep(30)
        return
    for t in tteval:
      if ( (t.lastcompute) and (t.lastcompute>t.lastwork)): # FIXME: forced recompute should be done when function changed
        continue
      logging.debug("YTThreadsEvaluationThread.do_spin(): lastcompute: "+str(t.lastcompute))
      # We have to commit, otherwise we risks conflicts.
      t.set_interest(dbsession)
      count+=1
    if (count):
      Δt=(datetime.datetime.now()-startdate).total_seconds()
      logging.debug("YTThreadsEvaluationThread.do_spin(): Processed: "+str(count)+" items in "+str(Δt)+" seconds ("+str(Δt/(count))+" seconds per item")
    dbsession.commit()

  def spin(self):
    logging.debug("YTThreadsEvaluationThread.spin: START")
    if (not self.field_storage):
      return # For tests, mostly
    # dbsession for this thread
    dbsession=SqlSingleton().mksession()
    while True:
      time.sleep(10)
      self.do_spin(dbsession,100)

# --------------------------------------------------------------------------
def main():
  from fieldstorage    import FieldStorage
  from ytqueue         import YtQueue
  YtQueue(1)
  field_storage = FieldStorage()
  yte=YTThreadsEvaluationThread(field_storage)
  yte.run()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

