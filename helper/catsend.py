#!/usr/bin/python
from __future__ import division
import socket
import sys
import getpass
import os
import time
import pyaudio
import pygame.camera
import pygame.image
import wave
import cv2
import numpy
import subprocess
import pyscreenshot as ImageGrab
import re
from threading import Thread

def fetch_till_newline(con):
  d=con.recv(1)
  total=''
  while d!='\n':
    total+=d
    d=con.recv(1)          
  return total
  
def CatsendThread(cmd,HOST,PORT,bYTES,CURRENT_CLIENT):
  global BYTES
  try:  
    PORT=int(PORT)
    BYTES=int(bYTES)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT+7))
    s.listen(1)
  
    print "LISTEN : ",HOST,PORT+7
    con, addr = s.accept()
    print "GOT : ",addr
    dest=re.sub(r"catsend *","",cmd)
    files=[]
    if dest=='*':
      for (dirpath, dirnames, filenames) in os.walk('.'):
        files.extend(filenames)
        break
    else:
      files.append(dest)
    print "NUMBER : ",str(len(files))
    con.sendall(str(len(files))+'\n')
    for i in range(0,len(files)):
      print "Sending File : ",files[i]
      if os.path.isfile(files[i]):
        total=str(os.path.getsize(files[i]))
      else:
        total='0'
      con.sendall(str(total)+'\n')
      con.sendall(str(len(files[i]))+'\n')
      con.sendall(files[i])
      f=open(files[i],'rb')
      sub=0
      total=int(total)
      perc=float(0)
      counter=float(1)
      l=f.read(BYTES)
      while (l):
        con.send(l)
        sub+=len(l)
        perc=float(sub)*100/total
        if perc>=counter:
          sys.stdout.write("%f%%\r"%(perc))
          sys.stdout.flush()
          counter=counter+1
        l=f.read(BYTES)
      f.close()
      con.recv(1)
    con.close()
  except Exception,e:
    print e
        
CatsendThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

