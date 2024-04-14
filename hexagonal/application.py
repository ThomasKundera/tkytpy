#!/usr/bin/env python3
import unittest

class Video:
  def __init__(self,yvid):
    self.yvid=yvid


class TestVideo(unittest.TestCase):
  def test_init(self):

    v=Video('yvid')
    self.assertEqual(v.yvid,'yvid')

# --------------------------------------------------------------------------
def main():
  unittest.main()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
