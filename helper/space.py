import sys
f=open(sys.argv[1],'rb')
f1=open(sys.argv[1]+"UP",'wb')
space=int(sys.argv[2])
line=f.readline()
while line:
  f1.write(line[space:])
  line=f.readline()
f1.close()
f.close()
