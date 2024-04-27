#!/usr/bin/env python3

"""Main entry point to tkyt Youtube Comment manager.
This script runs both UI (as http interface) and data spinners.
"""

from filestorage        import FileStorage
from fieldstorage       import FieldStorage
from cmdnview           import CmdNView
from tkyt               import TkYt
from dataspinnermanager import DataSpinnersManager


class Manager:
  """
  Manage and run all subclasses
  """
  def __init__(self):
    """
    Initialize inteface and data instance and connect them.
    """
    self.file_storage  = FileStorage ()
    self.field_storage = FieldStorage()
    self.dsm           = DataSpinnersManager(self.field_storage)
    self.tkyt          = TkYt(self.field_storage)
    self.tkyt.setup()
    self.cmd_n_view    = CmdNView    (self.tkyt)

  def run(self):
    """
    Run inteface and data instance, as separated threads
    """
    self.dsm.run()
    self.cmd_n_view.run()

# --------------------------------------------------------------------------
def main():
  """Starts all"""
  manager=Manager()
  manager.run()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
