#!/usr/bin/env python3
import http.server
import socketserver
import json

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import tksingleton

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
class HttpHandler(http.server.SimpleHTTPRequestHandler):
  DIRECTORY = "/var/tkweb"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=HttpHandler.DIRECTORY, **kwargs)

  def do_GET(self):
    super().do_GET()

  def do_POST(self):
    logging.debug("HttpHandle:do_POST: START: "+self.path)
    content_length = int(self.headers['Content-Length'])
    post_data_bytes = self.rfile.read(content_length)
    logging.debug("HttpHandle:do_POST: Received data:\n"+str(post_data_bytes))
    post_data_str = post_data_bytes.decode("UTF-8")
    js=json.loads(post_data_str)
    #js2=json.loads(js) # FIXME: Why?

    response=json.dumps(EventHandler().answer(js))

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()

    #print(response)

    self.wfile.write(response.encode(encoding='utf_8'))
    logging.debug("HttpHandle:do_POST: END")



class EventHandler(metaclass=tksingleton.SingletonMeta):
  def __init__(self,tkyt=None):
    self.tkyt=tkyt
    return

  def answer(self,js):
    cmd=js['command']
    if cmd == 'get_video_list':
      return self.get_video_list()
    if cmd == 'add_video':
      return self.add_video(js['ytid']) # FIXME: yid
    if cmd == 'video_action':
      return self.video_action(js)
    if cmd == 'get_main_stuff':
      return self.get_main_stuff()
    if cmd == 'get_oldest_thread_of_interest':
      return self.get_oldest_thread_of_interest()
    if cmd == 'get_newest_thread_of_interest':
      return self.get_newest_thread_of_interest()
    if cmd == 'get_thread':
      return self.get_thread(js['tid'])
    if cmd == 'set_ignore_from_comment':
      return self.set_ignore_from_comment(js['cid'])


  def add_video(self,yid):
    self.tkyt.add_video(yid)
    return { 'status': 'OK' }

  def get_video_list(self):
    return self.tkyt.get_video_list()

  def video_action(self,js):
    action=js['action']
    yid=js['yid']
    if action == 'suspended':
      checked=js['checked']
      return self.tkyt.video_checkbox_action(action,yid,checked)
    if action == 'monitor':
      value=int(js['value'])
      return self.tkyt.video_monitor_action(yid,value)
    return {}

  def get_oldest_thread_of_interest(self):
    return self.tkyt.get_oldest_thread_of_interest()

  def get_newest_thread_of_interest(self):
    return self.tkyt.get_newest_thread_of_interest()

  def get_thread(self,tid):
    return self.tkyt.get_thread(tid)

  def set_ignore_from_comment(self,cid):
    return self.tkyt.set_ignore_from_comment(cid)


class HttpServer:
  def __init__(self,tkyt):
    EventHandler(tkyt)

  def run(self):
    PORT = 8000
    with socketserver.TCPServer(("", PORT), HttpHandler) as httpd:
      logging.debug("serving at port: "+str(PORT))
      try:
        httpd.serve_forever()
      except KeyboardInterrupt:
        logging.debug("Stopping server...")
        httpd.shutdown()



# --------------------------------------------------------------------------
def main():
  return

# --------------------------------------------------------------------------
if __name__ == '__main__':
  main()
        
