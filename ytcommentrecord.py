#!/usr/bin/env python3
from ytauthorrecord    import YTAuthorRecord
from ytcommentrecord0  import YTCommentRecord0

from sqlsingleton   import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class YTCommentRecord(YTCommentRecord0):
  def __init__(self,dbsession,cid,commit=True):
    super().__init__(dbsession,cid,commit)

  def from_me(self,dbsession=None):
    a=get_dbobject_if_exists(YTAuthorRecord,self.author,dbsession)
    if not a:
      # FIXME: reload author, which likely means reloading the thread
      logging.debug("WARNING: YTComment.from_me: author "+str(self.author)+" does not exists")
      return False
    return (a.me)

  def has_me(self):
    me=['kundera', 'kuntera' 'cuntera']
    for k in me:
      if (k in self.text.lower()):
        return True
    return False

  def from_friends(self,dbsession=None):
    a=get_dbobject_if_exists(YTAuthorRecord,self.author,dbsession)
    return (a.friend)

def main():
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
