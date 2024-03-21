#!/usr/bin/env python3
#from ytvideosspinner          import YTVideosSpinner
from ytthreadsspinner        import YTThreadsSpinner
from ytcommentsspinner       import YTCommentsSpinner


class DataSpinnersManager:
  def __init__(self,field_storage):
    #self.yvs=YTVideosSpinner()
    self.yts=YTThreadsSpinner (field_storage)
    self.ycs=YTCommentsSpinner(field_storage)

  def run(self):
    #self.yvs.run()
    self.yts.run()
    self.ycs.run()

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  field_storage = FieldStorage()
  dsm=DataSpinnersManager(field_storage)

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
