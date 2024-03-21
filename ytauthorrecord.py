#!/usr/bin/env python3
import datetime
import json
import sqlalchemy

from sqlsingleton import SqlSingleton, Base
from sqlrecord    import SqlRecord, get_dbsession, get_dbobject

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTAuthorRecord(SqlRecord,Base):
  __tablename__ = 'ytauthor0_1'
  name              = sqlalchemy.Column(sqlalchemy.Unicode(100),primary_key=True)
  pp                = sqlalchemy.Column(sqlalchemy.Unicode(200))
  me                = sqlalchemy.Column(sqlalchemy.Boolean)
  follow            = sqlalchemy.Column(sqlalchemy.Boolean)
  friend            = sqlalchemy.Column(sqlalchemy.Boolean)
  ignore            = sqlalchemy.Column(sqlalchemy.Boolean)


  def __init__(self,dbsession,name,commit=True):
    self.name=name
    super().__init__(dbsession,commit)

  def fill_from_json(self,jscomment,commit=True):
    if (commit):
      dbsession=SqlSingleton().mksession()
    snippet  =jscomment['snippet']
    self.pp =snippet['authorProfileImageUrl']
    if (commit):
      dbsession.commit()


  def populate_default(self):
    self.pp                = None
    self.me                = False
    self.follow            = False
    self.friend            = False
    self.ignore            = False



    # --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  ycr=get_dbobject(YTAuthorRecord,"@bhromur")

  jsc={'kind': 'youtube#comment',
        'etag': '0dpXYZIyrl835yGrlcf0-Jy1IjA',
        'id': 'UgzMZr8oiZeLFE-IGqB4AaABAg',
        'snippet': {
          'channelId': 'UCmmS_FihQnPgNm0eZGa5TZg',
          'videoId': 'j2GXgMIYgzU',
          'textDisplay': 'TEST',
          'authorDisplayName': '@bhromur',
          'authorProfileImageUrl': 'https://yt3.ggpht.com/ytc/AIdro_kxVy1R1IqrIs82Kgct-UZAtBxzMvZOBxoxIIQW=s48-c-k-c0x00ffffff-no-rj',
          'authorChannelUrl': 'http://www.youtube.com/@bhromur',
          'authorChannelId': {'value': 'UCcAB9d5riTvNrcUqTMvwNnA'},
          'canRate': True,
          'viewerRating': 'none',
          'likeCount': 158,
          'publishedAt': '2022-07-10T12:24:05Z',
          'updatedAt': '2022-07-10T12:24:05Z'}}

  ycr.fill_from_json(jsc)

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()


