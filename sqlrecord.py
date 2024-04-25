#!/usr/bin/env python3
import datetime
import json
import sqlalchemy
from sqlalchemy.orm import class_mapper
from ytqueue        import YtQueue, YtTask

from sqlsingleton   import SqlSingleton, Base


import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class SqlRecord:
  def __init__(self,dbsession,commit=True):
    self.populate_default()
    if (commit):
      dbsession.commit()

  def get_id(self):
    mapper = class_mapper(type(self))
    return (getattr(self,mapper.primary_key[0].key))

  def copy_from(self,o):
    #r = inspect(self.myclass).columns
    mapper = class_mapper(type(o))
    prim = set([c.key for c in mapper.primary_key])
    for k in [p.key for p in mapper.iterate_properties if p.key not in prim]:
      value = getattr(o, k)
      setattr(self, k, value)

  def call_sql_task_threaded(self,priority=0,semaphore=None):
    logging.debug(type(self).__name__+".call_sql_task_threaded(): START")
    task=YtTask('populate: '+type(self).__name__
                +" - "+str(self.get_id()),type(self),self.get_id(),priority,semaphore)
    YtQueue().add(task)
    logging.debug(type(self).__name__+".call_sql_task_threaded(): END")

  def get_priority(self):
    logging.debug(type(self).__name__+".get_priority(): START")
    # Lower the more prioritized, number should roughlt reflects
    # time (in second) before next update would be nice.
    # Refresh priority should depends heavily on interractive accesses
    # but we don't have that metric yet (FIXME)
    return sys.maxsize

  def __str__(self):
    s=str(type(self).__name__)+" (id= "+str(self.get_id())+" )"
    return s

  def to_dict(self):
    d={}
    mapper = class_mapper(type(self))
    for k in [p.key for p in mapper.iterate_properties]:
      value = getattr(self, k)
      d[str(k)]=str(value)
    return d

  def sql_task_threaded(self,dbsession,youtube):
    raise # Must be implemented
    return

  def populate_default(self):
    return

# --------------------------------------------------------------------------
def main():
  from sqltestrecord import TestRecord
  Base.metadata.create_all()
  tr1=get_dbobject(TestRecord,'toto')
  tr2=get_dbobject(TestRecord,'tutu')
  tr3=get_dbobject(TestRecord,'titi')
  tr4=get_dbobject(TestRecord,'tata')
  dbsession=get_dbsession(tr1)
  dbsession.commit()
  print(tr1.to_dict())

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()

