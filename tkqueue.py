#!/usr/bin/env python3
from random import random
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

  def __str__(self):
    return self.tid+" ("+str(self.priority)+")"

class QueueWork(metaclass=tksingleton.SingletonMeta):

  def __init__(self):
    self.q=queue.PriorityQueue()
    self.meanpriority=0.
    threading.Thread(target=self.worker, daemon=True).start()

  def do_work(self,item):
    item.run()


  def worker(self):
    while True:
      item = self.q.get()
      logging.debug("QueueWork.worker(): Working on: "+str(item)+". ( about "+str(self.q.qsize())+" elements remaining )")
      self.do_work(item)
      self.q.task_done()
      #time.sleep(1)

  def add(self,item):
    if (self.meanpriority>item.priority):
      self.meanpriority=item.priority
    else:
      self.meanpriority=(4*self.meanpriority+item.priority)/5.
    if (item.priority>self.meanpriority*(1+random())):
      logging.debug("QueueWork.worker(): "
        +str(item)+" too high priority to run ("+str(self.meanpriority)+")")
      if (item.semaphore):
        logging.debug(type(self).__name__
                    +".add(): Semaphore release ("+str(item))
        item.semaphore.release()
      return False
    self.q.put(item)
    logging.debug(type(self).__name__+
                  ".add("+str(item)+"): added ("+str(self.meanpriority)+")")
    return True

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
      logging.debug(type(self).__name__+".add("+str(item)+"): already in queue"
                    +" about "+str(self.q.qsize())+" elements remaining"+
                      self.strtaskdict())
      if (item.semaphore):
        logging.debug(type(self).__name__
                    +".add(): Semaphore release ("+str(self))
        item.semaphore.release()
      return False
    if (not super().add(item)):
      return False
    self.taskdict[item.tid]=item
    return True

  def strtaskdict(self):
    s=""
    for v in self.taskdict.values():
      s+=" "+str(v)
    return s



def test_task1():
  print("Test task1")
  time.sleep(5)

def test_task2():
  print("Test task2")
  time.sleep(5)

def test_task3():
  print("Test task3")
  time.sleep(5)

# --------------------------------------------------------------------------
def main():
  t1=TkTaskUniq("toto",test_task1,1000)
  t2=TkTaskUniq("titi",test_task2,3000)
  t3=TkTaskUniq("tutu",test_task3,40000)
  q=QueueWorkUniq()
  for i in range(10):
    for t in [t1,t2,t3]:
      q.add(t)
      time.sleep(1)
  q.join()
  q.join()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
