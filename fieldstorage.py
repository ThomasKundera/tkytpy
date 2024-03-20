#!/usr/bin/env python3
from sqlsingleton import SqlSingleton, Base

from ytvideo import YTVideo

class FieldStorage:
  def __init__(self):
    Base.metadata.create_all()
    return


  def get_dict(self,cls):
    dbsession=SqlSingleton().mksession()
    d={}
    for o in dbsession.query(cls):
      k=o.get_id()
      d[k]=o
    return d

  def get_videos(self):
    dbsession=SqlSingleton().mksession()
    vd={}
    for v in dbsession.query(YTVideo):
      vd[v.yid]=v
    return vd

  def get_theads(self):
    dbsession=SqlSingleton().mksession()
    td={}
    for d in dbsession.query(YTVideo):
      dl[v.yid]=v
    return vl




# --------------------------------------------------------------------------
def main():
  from ytthreadrecord import YTThreadRecord
  fs=FieldStorage()
  vl=fs.get_dict(YTThreadRecord)
  print(vl)


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
