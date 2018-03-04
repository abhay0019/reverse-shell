#!/usr/bin/python
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

def VideoThread(HOST,PORT,BYTES,CURRENT_CLIENT):
  PORT=int(PORT)
  BYTES=int(BYTES)
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((HOST, PORT+1))
  s.listen(1)
  print "LISTEN : ",HOST,PORT+1
  con, addr = s.accept()
  print "GOT : ",addr
  fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
  total=''
  d=con.recv(1)
  WH=''
  while d!='\n':
    WH+=d
    d=con.recv(1)
  V=WH.split(' ')
  width=int(V[0])
  height=int(V[1])
  FILENAME=CURRENT_CLIENT+" "+time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())+".avi"
  vid = cv2.VideoWriter(FILENAME,fourcc,8,(width,height),True)       
  while True:
    d=con.recv(1)
    total=''
    while d!='\n':
      total+=d
      d=con.recv(1)
    sub=0
    total=int(total)
    d=''
    while True:
      d += con.recv(BYTES)
      if(len(d)>=total):
        break
    img_np = numpy.fromstring(d,dtype='uint8')
    decimg = cv2.imdecode(img_np,1)
    vid.write(decimg)
    cv2.imshow('server',decimg)
    key=cv2.waitKey(1)
    if key==27:
      break
    con.send('1')
  vid.release()
  con.send('0')
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  cmd=raw_input('Wanna Keep Recording?(y/n)')
  if(cmd=='n'):
    cmd=subprocess.Popen("rm '"+FILENAME+"'",shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    output=cmd.stdout.read()+cmd.stderr.read()
    print output
  print "Closed"
  con.close()
try:
  VideoThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
  print sys.argv
except Exception,e:
  print e
