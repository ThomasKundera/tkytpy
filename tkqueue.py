#!/usr/bin/env python3
import threading
import queue
import time
import datetime
from functools import total_ordering

import tksingleton

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

@total_ordering
class TkTask:
  def __init__(self,task,priority=0,semaphore=None):
    self.semaphore=semaphore
    self.priority=priority
    self.task=task

  def run(self):
    self.task()
    if (self.semaphore):
      self.semaphore.release()

  def __lt__(self,o):
    return self.priority < o.priority

  def __eq__(self,o):
    return self.priority ==  o.priority

  def __str__(self):
    return str(self.task)

class TkTaskUniq(TkTask):
  def __init__(self,tid,task,priority=0,semaphore=None):
    self.tid=tid
    super().__init__(task,priority,semaphore)

  def run(self):
    self.task()

  def __str__(self):
    return self.tid

class QueueWork(metaclass=tksingleton.SingletonMeta):

  def __init__(self):
    self.q=queue.PriorityQueue()
    threading.Thread(target=self.worker, daemon=True).start()

  def do_work(self,item):
    item.run()


  def worker(self):
    while True:
      item = self.q.get()
      logging.debug("Working on "+str(item)+". ( about "+str(self.q.qsize())+" elements remaining )")
      self.do_work(item)
      self.q.task_done()
      #time.sleep(1)

  def add(self,item):
    self.q.put(item)

  def join(self):
    self.q.join()


# This class prevents two requests having same id to be queued
class QueueWorkUniq(QueueWork):
  lastuse: datetime.datetime = None

  def __init__(self):
    self.taskdict={}
    super().__init__()

  def do_work(self,item):
    super().do_work(item)
    del self.taskdict[item.tid]

  def add(self,item):
    if item.tid in self.taskdict:
      logging.debug("Task "+str(item)+" already in queue"
                    +"about "+str(self.q.qsize())+" elements remaining"+
                    str(self.taskdict))
      if (item.semaphore):
        item.semaphore.release()
      return False
    self.taskdict[item.tid]=item.tid
    super().add(item)


def test_task():
  print("Test task")
  time.sleep(1)

# --------------------------------------------------------------------------
def main():
  t1=TkTaskUniq("toto",test_task)
  q=QueueWorkUniq()
  q.add(t1)
  q.join()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
