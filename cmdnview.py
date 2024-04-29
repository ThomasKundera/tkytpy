#!/usr/bin/env python3
"""Independently starts the inteactive part of tkyt.
"""

from httpserver import HttpServer

class CmdNView:
  """
  Manage the webserver
  """
  def __init__(self,tkyt):
    self.server=HttpServer(tkyt)

  def run(self):
    self.server.run()

# --------------------------------------------------------------------------
def main():
  from fieldstorage       import FieldStorage
  from tkyt               import TkYt
  field_storage = FieldStorage()
  tkyt          = TkYt(field_storage)
  tkyt.setup()
  cmd=CmdNView(tkyt)
  cmd.run()


# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
