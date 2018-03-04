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

def ScreenThread(cmd,HOST,PORT,BYTES,CURRENT_CLIENT):
  PORT=int(PORT)
  BYTES=int(BYTES)
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((HOST, PORT+2))
  s.listen(1)
  print "LISTEN : ",HOST,PORT+2
  con, addr = s.accept()
  print "GOT : ",addr
        
  iscolor=True
  cmd=str.encode(cmd)
  cmd=re.sub(r"screenrecord *","",cmd)
  print "CMD : ",cmd,len(cmd)
  if(len(cmd)>0):
    vect=cmd.split(' ')
  else:
    vect=[]
  print "VECT : ",len(vect)
  print vect,len(vect),"1"
  if(len(vect)==1 and vect[0][0]=='c'):
    iscolor=False
  if(len(vect)==5 and vect[4][0]=='c'):
    iscolor=False  
  print "2"
  total=''
  fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
  d=con.recv(1)
  WH=''
  while d!='\n':
    WH+=d
    d=con.recv(1)
  print "33"
  V=WH.split(' ')
  width=int(V[0])
  height=int(V[1])
  print V
  FILENAME=CURRENT_CLIENT+" "+time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())+".avi"
  vid = cv2.VideoWriter(FILENAME,fourcc,8,(width,height),True)
  while True:
    d=con.recv(1)
    shape=''
    while d!='\n':
      shape+=d
      d=con.recv(1)
    shapes=shape.split(' ')
    d=con.recv(1)
    total=''
    while d!='\n':
      total+=d
      d=con.recv(1)
    sub=0
    total=int(total)
    d=''
    print "Total : ",total
    while True:
      d += con.recv(BYTES)
      if(len(d)>=total):
        break
    if(len(shapes)==3):
      img_np = numpy.fromstring(d,dtype='uint8').reshape(int(shapes[0]),int(shapes[1]),int(shapes[2]))
    else:
      img_np = numpy.fromstring(d,dtype='uint8').reshape(int(shapes[0]),int(shapes[1]))
      ret = numpy.empty((img_np.shape[0], img_np.shape[1], 3), dtype=numpy.uint8)
      ret[:,:,0]=img_np
      ret[:,:,1]=img_np
      ret[:,:,2]=img_np
      img_np=ret
    print "MATCHE : ",img_np.shape
    vid.write(img_np)
    cv2.imshow('server',img_np)
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
try:
  ScreenThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
  print sys.argv
except Exception,e:
  print e
