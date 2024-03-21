#!/usr/bin/env python3
from filestorage        import FileStorage
from fieldstorage       import FieldStorage
from cmdnview           import CmdNView
from tkyt               import TkYt
from dataspinnermanager import DataSpinnersManager


class Manager:
  def __init__(self):
    self.file_storage  = FileStorage ()
    self.field_storage = FieldStorage()
    self.dsm           = DataSpinnersManager(self.field_storage)
    self.tkyt          = TkYt(self.field_storage)
    self.tkyt.setup()
    self.cmd_n_view    = CmdNView    (self.tkyt)

  def run(self):
    self.dsm.run()
    self.cmd_n_view.run()
    return

# --------------------------------------------------------------------------
def main():
  manager=Manager()
  manager.run()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
