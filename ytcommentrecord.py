#!/usr/bin/env python3
import datetime
import json
import sqlalchemy

from sqlrecord      import SqlRecord

from sqlsingleton   import SqlSingleton, Base, get_dbsession, get_dbobject, get_dbobject_if_exists

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class YTCommentRecord(SqlRecord,Base):
  __tablename__ = 'ytcomment0_4'
  cid               = sqlalchemy.Column(sqlalchemy.Unicode(100),primary_key=True)
  yid               = sqlalchemy.Column(sqlalchemy.Unicode(50))
  parent            = sqlalchemy.Column(sqlalchemy.Unicode(50))
  author            = sqlalchemy.Column(sqlalchemy.Unicode(100))
  text              = sqlalchemy.Column(sqlalchemy.Unicode(11000)) #FIXME: 12000?
  published         = sqlalchemy.Column(sqlalchemy.DateTime)
  updated           = sqlalchemy.Column(sqlalchemy.DateTime)
  liked             = sqlalchemy.Column(sqlalchemy.Integer)

  def __init__(self,dbsession,cid,commit=True):
    self.cid=cid
    super().__init__(dbsession,commit)

  def fill_from_json(self,jscomment,commit=True):
    if (commit):
      dbsession=SqlSingleton().mksession()
    self.cid =jscomment['id']
    snippet  =jscomment['snippet']

    self.yid =snippet['videoId']
    self.text=snippet['textDisplay'][:10000] # FIXME
    #print("TEXT LENGTH: "+str(len(self.text)))
    #print(self.text)
    self.author=snippet['authorDisplayName']

    if ('parentId' in snippet):
      self.parent=snippet['parentId']
    self.published=datetime.datetime.strptime(snippet['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
    self.updated  =datetime.datetime.strptime(snippet['updatedAt'],"%Y-%m-%dT%H:%M:%SZ")
    if (snippet['viewerRating'] == 'like'):
      self.liked    = 1
    else:
      self.liked    = 0
    # Waiting for the day dislikes will be returned...
    if (commit):
      dbsession.commit()

  def populate_default(self):
    # Wasn't kept in previous version
    self.liked        = None
# --------------------------------------------------------------------------
def main():
  Base.metadata.create_all()
  dbsession=SqlSingleton().mksession()
  #res=dbsession.query(YTCommentRecord.yid, #func.count(YTCommentRecord.yid)).group_by(YTCommentRecord.yid).all()
  #print(res)
  return

  ycr=get_dbobject(YTCommentRecord,"UgzMZr8oiZeLFE-IGqB4AaABAg")

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
