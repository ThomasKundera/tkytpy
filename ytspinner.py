#!/usr/bin/env python3
import time
import threading
from threading import Thread, Semaphore

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTSpinner:
  def __init__(self,field_storage,cls):
    logging.debug("YTSpinner.__init__(): START")
    self.field_storage=field_storage
    self.cls=cls
    self.semaphore=Semaphore(1)

  def run(self):
    logging.debug("YTSpinner.run(): START")
    self.spint = Thread(target=self.spin)
    self.spint.start()
    logging.debug("YTSpinner.run: END")

  def call_populate(self,item):
    logging.debug("YTSpinner.call_populate: START")
    priority=item[0]
    t=item[1]
    self.semaphore.acquire()
    # Using priority here needs a careful evaluation.
    # So, we'll just give everything same for now.
    t.call_populate(1000,self.semaphore)
    logging.debug("YTSpinner.call_populate: END")

  def queued_populate(self,youtube):
    logging.debug("YTSpinner.queued_populate: START")
    time.sleep(10) # Just for tests

  def do_spin(self):
    logging.debug("YTSpinner.do_spin(): START")
    ol=[]
    od=self.field_storage.get_dict(self.cls)
    for o in od.values():
      p=o.get_priority()
      ol.append((p,o))
    ols=sorted(ol, key=lambda x: x[0])
    if (len(ols) and ols[0][0] < 1000000): # FIXME
      logging.debug("YTSpinner.do_spin(): selected "+str(ols[0]))
      self.call_populate(ols[0])
    else:
      time.sleep(20) # FIXME
    logging.debug("YTSpinner.do_spin(): END")

  def spin(self):
    logging.debug("YTSpinner.spin: START")
    if (not self.field_storage):
      return # For tests, mostly
    while True:
      time.sleep(1)
      self.do_spin()

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  from sqltestrecord import TestRecord
  field_storage = FieldStorage()
  field_storage
  ys=YTSpinner(field_storage,TestRecord)
  ys.run()
  ys.spint.join()
  return
# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

