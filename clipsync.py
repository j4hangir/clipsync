# -*- coding: UTF-8 -*-
#!/usr/bin/env python3

import os
import zmq
import pyperclip
from time import sleep
from threading import Thread

__author__ = 'Jahângir (me [at] jahangir [dAt] ninja)'

context = zmq.Context()
SELF, OTHER = None, None
PORT = 8484

if os.name == 'nt':
  SELF, OTHER = '192.168.190.1', '192.168.190.130'
elif os.name == 'posix':  # mac
  OTHER, SELF = '192.168.190.1', '192.168.190.130'
else:
  raise NotImplementedError("Undefined OS: {}".format(os.name))

SERVERS = [[OTHER, PORT],]

def receiver():
  global context, PORT
  socket = context.socket(zmq.REP)
  print("clipsync bound to: tcp://{}:{}".format(SELF, PORT))
  socket.bind("tcp://{}:{}".format(SELF, PORT))

  while True:
    #  Wait for next request from client
    cb = socket.recv_unicode()
    try: 
      pyperclip.copy(cb)
      print("set::{}{}".format(cb[:100].replace('\n', '\\n'), '...' if len(cb) > 100 else ''))
    except: pass
    #  Send reply back to client
    socket.send_unicode("1")


def sender():
  global context, SERVERS
  last = None
  while True:
    try: cb = pyperclip.paste()
    except: sleep(1); continue
    ctn = False
    if not cb or cb == last:
      ctn = True
    sleep(0.7)
    if ctn: continue
    last = cb
    
    cbex = '{}{}'.format(cb[:100].replace('\n', '\\n'), '...' if len(cb) > 100 else '')
    
    for ip, port in SERVERS:
      print("{}:{}::{}".format(ip, port, cbex))
      socket = context.socket(zmq.REQ)
      socket.connect("tcp://{}:{}".format(ip, port))
      
      socket.send_unicode(cb)
      
      #  Get the reply.
      message = socket.recv()
      # print("Received reply [ %s ]" % message)

if __name__ == '__main__':
  sthread = Thread(None, sender, daemon=True)
  rthread = Thread(None, receiver, daemon=True)
  sthread.start(); rthread.start()
  rthread.join(); sthread.join()
    
