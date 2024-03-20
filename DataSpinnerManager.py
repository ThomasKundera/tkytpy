#!/usr/bin/env python3
from ytvideospinner          import YTVideosSpinner
from ytthreadsspinner        import YTThreadsSpinner
from ytcommentsspinner       import YTCommentsSpinner


class DataSpinnersManager:
  def __init__(self):
    self.yvs=YTVideosSpinner()
    self.yts=YTThreadsSpinner()
    self.ycs=YTCommentsSpinner()

# --------------------------------------------------------------------------
def main():
  dsm=DataSpinnersManager()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
