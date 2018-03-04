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
  print "OPEN : ",cmd
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
      sys.stdout.write("%f%%\r"%(perc))
      sys.stdout.flush()
      counter=counter+1
    f.write(l)
    if sub>=sz:
      break
    l=con.recv(BYTES)
  print '100%\n',
  f.close()

def fetch_till_newline(con):
  d=con.recv(1)
  total=''
  while d!='\n':
    total+=d
    d=con.recv(1)          
  return total
  
def CatcopyThread(cmd,HOST,PORT,bYTES,CURRENT_CLIENT):
  global BYTES
  try:  
    PORT=int(PORT)
    BYTES=int(bYTES)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT+6))
    s.listen(1)
  
    print "LISTEN : ",HOST,PORT+6
    con, addr = s.accept()
    print "GOT : ",addr
    
    number=int(fetch_till_newline(con))
    print "NUMBER : ",number
    for i in range(0,number):
      sz=int(fetch_till_newline(con))
      print "SIZE : ",sz
      if(sz>0):
        f_name_sz=int(fetch_till_newline(con))
        f_name=''
        sub=0
        while True:
          if len(f_name)==f_name_sz:
            break 
          f_name+=con.recv(1)
        recvall(con,f_name,sz)
        con.sendall('1')
        print "Copied "
      else:
        print "No Such File"
        con.sendall('1')
  except Exception,e:
    print e
        
CatcopyThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

