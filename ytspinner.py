#!/usr/bin/env python3
import time
from threading import Thread, Semaphore

from sqlsingleton    import SqlSingleton, Base

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTSpinner:
  def __init__(self,field_storage,cls):
    logging.debug(type(self).__name__+".__init__(): START")
    self.field_storage=field_storage
    self.cls=cls
    self.semaphore=Semaphore(1)
    self.modified_item=None

  def run(self):
    logging.debug(type(self).__name__+".run(): START")
    self.spint = Thread(target=self.spin)
    self.spint.start()
    logging.debug(type(self).__name__+".run: END")

  def call_populate(self,item):
    logging.debug(type(self).__name__+".call_populate: START")
    SqlSingleton().monitor_threads(self.dbsession)
    # FIXME: this is some way to recover the data
    # that were not saved.
    if (self.modified_item):
      self.dbsession.merge(self.modified_item)
      self.dbsession.commit()
    priority=item[0]
    t=item[1]
    logging.debug(type(self).__name__
                  +".call_populate(): Semaphore request ("+t.get_id()+")")
    self.semaphore.acquire()
    self.modified_item=t # Trying to solve the multithread issue
    # Using priority here needs a careful evaluation. But may works now.
    t.call_sql_task_threaded(priority,self.semaphore)
    logging.debug(type(self).__name__+".call_populate: END")


  def do_spin_new(self):
    logging.debug(type(self).__name__+".do_spin_new(): START")
    item=self.get_item_to_process()
    if item:
      self.call_populate(item)
    else:
      logging.debug(type(self).__name__+".do_spin_new(): Nothing to do")
      time.sleep(10)
    logging.debug(type(self).__name__+".do_spin_new(): END")



  def spin(self):
    logging.debug(type(self).__name__+".spin: START")
    if (not self.field_storage):
      return # For tests, mostly
    # Now in main thread, time to create the dbsession.
    self.dbsession=SqlSingleton().mksession()
    while True:
      time.sleep(1)
      self.do_spin_new()

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  from sqltestrecord import TestRecord
  from ytqueue        import YtQueue
  field_storage = FieldStorage()
  field_storage
  YtQueue(1)
  ys=YTSpinner(field_storage,TestRecord)
  ys.run()
  ys.spint.join()
  return
# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

