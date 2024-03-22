#!/usr/bin/env python3
from ytvideosspinner           import YTVideosSpinner
from ytthreadsspinner          import YTThreadsSpinner
from ytcommentsspinner         import YTCommentsSpinner
from ytthreadsevaluationthread import YTThreadsEvaluationThread

class DataSpinnersManager:
  def __init__(self,field_storage):
    self.yvs=YTVideosSpinner           (field_storage)
    self.yts=YTThreadsSpinner          (field_storage)
    self.ycs=YTCommentsSpinner         (field_storage)
    self.yet=YTThreadsEvaluationThread (field_storage)

  def run(self):
    self.yvs.run()
    self.yts.run()
    self.ycs.run()
    self.yet.run()

# --------------------------------------------------------------------------
def main():
  from fieldstorage      import FieldStorage
  from ytqueue           import YtQueue
  YtQueue(10) # This is for background download in standalone.
  field_storage = FieldStorage()
  dsm=DataSpinnersManager(field_storage)
  dsm.run()

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
