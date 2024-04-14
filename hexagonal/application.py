#!/usr/bin/env python3
import unittest


class Comment:
  def __init__(self,cid):
    self.cid=cid

class CommentsThread(self,tid):
  def __init__(self,tid):
    self.tid=tid


class Video:
  def __init__(self,vid):
    self.vid=vid


class TestVideo(unittest.TestCase):
  def test_init(self):
    v=Video('vid')
    self.assertEqual(v.vid,'vid')

class TestComment(unittest.TestCase):
  def test_init(self):
    c=Comment('cid')
    self.assertEqual(c.cid,'cid')


# --------------------------------------------------------------------------
def main():
  unittest.main()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
