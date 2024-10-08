#!/usr/bin/env python3
import time
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

from threading import  Semaphore, get_ident

from tksecrets import localsqldb_pass

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import tksingleton


# --------------------------------------------------------------------------
def get_dbsession(o):
  dbsession=Session.object_session(o)
  if not dbsession:
    dbsession=SqlSingleton().mksession()
  return (dbsession)

# --------------------------------------------------------------------------
def get_dbobject(myclass,key,dbsession=None,commit=True):
  logging.debug("get_dbobject( "+str(myclass)+" , "+str(key)+" , ) : START")
  if not (dbsession):
    dbsession=SqlSingleton().mksession()
  o=dbsession.query(myclass).get(key)
  if (not o):
    o=myclass(dbsession,key,commit)
    dbsession.add(o)
  return (o)

def get_dbobject_if_exists(myclass,key,dbsession=None):
  if not (dbsession):
    dbsession=SqlSingleton().mksession()
  o=dbsession.query(myclass).get(key)
  return (o)



class SqlSingleton(metaclass=tksingleton.SingletonMeta):
  def __init__(self,db='tkyt'):
    db_url = sqlalchemy.engine.URL.create(
      drivername="mysql+mysqlconnector",
      username="tkyt",
      password=localsqldb_pass,
      host="127.0.0.1",
      database=db,
    )
    self.engine          = sqlalchemy.create_engine(db_url, isolation_level="READ COMMITTED")#, echo=True)
    self.session_factory = sessionmaker(bind=self.engine)
    self.session_maker   = scoped_session(self.session_factory)

    self.threads_dict={}
    self.semaphore=Semaphore(1)
    super().__init__()

  def mksession(self):
    dbsession=self.session_maker()
    self.monitor_threads(dbsession)
    return (dbsession)

  def monitor_threads(self,dbsession):
    #logging.debug("SqlSingleton.monitor_threads: START")
    # This should not be run in parallel
    self.semaphore.acquire()
    current_thread=get_ident()
    if dbsession in self.threads_dict:
      if ( current_thread != self.threads_dict[dbsession]):
        logging.debug("SqlSingleton.monitor_threads(): ERROR: same session, not same thread: dbsession: "
          +str(dbsession)+" old thread: "
          +str(self.threads_dict[dbsession])+" current thread: "
          +str(current_thread))
        raise
    logging.debug("SqlSingleton.monitor_threads(): "
      +"Thread: "+str(current_thread)+" "
      +"dbsession: "+str(dbsession))
    self.threads_dict[dbsession]=current_thread
    to_del=[]
    for s in self.threads_dict:
       if not s.is_active:
         to_del.append(s)
    for s in to_del:
      del self.threads_dict[s]
    self.semaphore.release()
    #logging.debug("SqlSingleton.monitor_threads: END")


  def close(self):
     self.engine.dispose()

Base = declarative_base(bind=SqlSingleton('tkyttest').engine)


def classtest():
  from sqlalchemy.ext.declarative import declarative_base
  Base = declarative_base(bind=SqlSingleton().engine)
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  dbsession=SqlSingleton().mksession()

def directtest():
  sqlproto='mysql+mysqlconnector'
  sqluser='tkyt'
  connection_url = sqlalchemy.engine.URL.create(
    drivername="mysql+mysqlconnector",
    username="tkyt",
    password=localsqldb_pass,
    host="127.0.0.1",
    database="tkyt",
  )
  engine = sqlalchemy.create_engine(connection_url, echo=True)
  from sqlalchemy.ext.declarative import declarative_base
  Base = declarative_base(bind=engine)
  Base.metadata.create_all()

# --------------------------------------------------------------------------
def main():
  logging.debug("sqlqueue test: START")
  #directtest()
  classtest()
  logging.debug("sqlqueue test: END")

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
