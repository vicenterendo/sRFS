from __future__ import print_function, unicode_literals
from multiprocessing import Event
import os
from re import L
import subprocess
from telnetlib import ENCRYPT

def clearConsole():
      if os.name == 'nt':
            os.system('cls')
      else:
            os.system('clear')
clearConsole()

import sys
import socket
import pickle
import shutil
import tempfile as tfutils
from pathlib import Path
import colorama as pcolor
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from natsort import natsorted, ns
import platform
from cryptography.fernet import Fernet
import time


class Prompt:
      def connOpen(message):
            print(pcolor.Fore.GREEN + pcolor.Style.BRIGHT + '[+] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)
      def connMessage(message):
            print(pcolor.Fore.CYAN + pcolor.Style.BRIGHT + '[/] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)
      def connClose(message):
            print(pcolor.Fore.RED + pcolor.Style.BRIGHT + '[-] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)

class EventID:
      CLOSECONN = -1
      LISTFILES = 0
      GETFILE = 1
      WRITEFILE = 2
      DELETEFILE = 3
      DOWNLOADFOLDER = 4
      COPYFILE = 5
      PASTEFILE = 6
      CHECKPATH = 7
      GETCWD = 8
      GETPLATFORM = 9
      RUNCMD = 10
      ISFOLDER = 11
      
class dirEntry:
      def __init__(self, type, name):
            self.name = name
            self.type = type
            
class Env:
      if platform.system().lower() == 'windows':
            pathseparator = "\\"
      else:
            pathseparator = "/"
      
      temp_dir = tfutils.gettempdir() + pathseparator + 'rfsServer' + pathseparator


try:
      os.mkdir(Env.temp_dir)
except:
      pass

def getPrivateIp():
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      privateIp = s.getsockname()[0]
      s.close()
      return privateIp

def passwordPrompt():
      style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: ''
      })

      properties = [
            {
                  'type': 'password',
                  'message': 'Set a password:',
                  'name': 'password',
            }
      ]

      answer = prompt(properties, style=style)
      return answer['password']

if not os.path.exists("./key.srfskey"):
      key = Fernet.generate_key()
      print(pcolor.Fore.BLUE + pcolor.Style.BRIGHT + "Generating encryption key...")
      with open("./key.srfskey", "wb") as f:
            f.write(pickle.dumps(key))
      print(pcolor.Fore.GREEN + f"Key saved on{pcolor.Style.BRIGHT} key.srfskey" + pcolor.Style.RESET_ALL)

Env.key = pickle.loads(open("./key.srfskey", "rb").read())
crypto = Fernet(Env.key)

os.chdir(str(Path.home()))
try: os.mkdir("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator)
except: pass
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((getPrivateIp(), 9876))


fts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fts.bind((getPrivateIp(), 9877))

def rcvFile():
      global fts
      filename = "." + Env.pathseparator + ".tempsrfs" + Env.pathseparator + str(time.time())
      fts.listen()
      ftc, addr = fts.accept()

      size = int(crypto.decrypt(ftc.recv(1024)))
      ftc.send(crypto.encrypt('ready'.encode('utf-8')))
      downloadedbytes = 0
      try:
            os.remove(filename)
      except FileNotFoundError:
            pass
      packet = bytes()
      encdata = bytes()
      with open(filename + ".temp", 'ab') as f:
            while downloadedbytes < size:   
                  packet = ftc.recv(1024)
                  if sys.getsizeof(packet) == 33:
                        break
                  f.write(packet)
                        
      
      with open(filename + ".temp", 'rb') as f: encdata = f.read()
      ftc.close()
      
      return crypto.decrypt(encdata)

def sendFile(filename):
      global fts
      fts.listen()
      ftc, addr = fts.accept()
      
      try: os.mkdir("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator)
      except: pass
      
      
      with open(filename, 'rb') as f:
            with open("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator + filename.split(Env.pathseparator)[-1], "wb") as f2:
                  f2.write(crypto.encrypt(f.read()))
                  
      with open("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator + filename.split(Env.pathseparator)[-1], 'rb') as f:
            data = f.read()
            size = sys.getsizeof(data)
            
      ftc.send(crypto.encrypt(str(size).encode('utf-8')))
      ftc.recv(1024)
      
      with open("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator + filename.split(Env.pathseparator)[-1], 'rb') as f:
            while True:
                  packet = f.read(1024)
                  
                  if not packet:
                        break
                  
                  ftc.send(packet)
                  pass
                  
                        


if platform.system().upper() == 'WINDOWS':
      Env.pathseparator = '\\'
else:
      Env.pathseparator = '/'

while True:
      server.listen()
      conn, addr = server.accept()
      
      Prompt.connOpen('Connected to ' + str(addr[0]))
      while True:
            try:
                  conn.settimeout(3)
                  while True:
                        try: 
                              rawEntry = conn.recv(2048)
                              rawEntry = crypto.decrypt(rawEntry)
                              break
                        except TimeoutError: pass
                  conn.settimeout(None)
                        
                  try:
                        jsonEntry = pickle.loads(rawEntry)
                  except EOFError:
                        pass
                  
                  action = jsonEntry['action']
                  
                  Prompt.connMessage("Request received: " + str(jsonEntry))
                  
                  if action == EventID.GETPLATFORM:
                        conn.send(crypto.encrypt(platform.system().encode('utf-8')))

                  if action == EventID.GETCWD:
                        conn.send(crypto.encrypt(os.getcwd().encode('utf-8')))
                        
                  
                  if action == EventID.CLOSECONN:
                        try: conn.close() 
                        except: pass
                        Prompt.connClose('Connection closed successfully')

                        break
                  
                  if action == EventID.LISTFILES:
                        #list files
                        dirList = os.listdir(jsonEntry['details']['path'])
                        for i, entry in enumerate(dirList):
                              if os.path.isdir(jsonEntry['details']['path'] + '/' + entry):
                                    dirList[i] = dirEntry(1, entry)
                              else:
                                    dirList[i] = dirEntry(0, entry)
                        conn.send(crypto.encrypt(pickle.dumps(dirList)))
                        
                  if action == EventID.GETFILE:
                        path = jsonEntry['details']['path']
                        sendFile(path)
                        
                        
                  if action == EventID.WRITEFILE:
                        path = jsonEntry['details']['path']
                        with open(path, 'wb') as f:
                              f.write(rcvFile())
                              
                  if action == EventID.DELETEFILE:
                        path = jsonEntry['details']['path']
                        if os.path.isdir(path):
                              shutil.rmtree(path)
                        else:
                              os.remove(path)
                              
                  if action == EventID.DOWNLOADFOLDER:
                        path = jsonEntry['details']['path']
                        shutil.make_archive(Env.temp_dir + str(time.time()), 'zip', path)
                        sendFile(Env.temp_dir + str(time.time()) + '.zip')
                        
                  if action == EventID.CHECKPATH:
                        path = jsonEntry['details']['path']
                        if os.path.exists(path):
                              conn.send(crypto.encrypt(pickle.dumps(True)))
                        else:
                              conn.send(crypto.encrypt(pickle.dumps(False)))

                  if action == EventID.RUNCMD:
                        fullcommand = jsonEntry['details']['command']
                        command = jsonEntry['details']['command'].split()[0]
                        parameters = fullcommand.strip(jsonEntry['details']['command'].split()[0])
                        commandoutput = None
                        commandoutput = subprocess.check_output(fullcommand, shell=True)
                        
                        conn.send(crypto.encrypt(pickle.dumps(commandoutput)))

                  if action == EventID.ISFOLDER:
                        path = jsonEntry['details']['path']
                        conn.send(crypto.encrypt(pickle.dumps(os.path.isdir(path))))
                  
                        
            except ConnectionAbortedError:
                  Prompt.connClose('Connection Lost')
                  break
            except ConnectionResetError:
                  Prompt.connClose('Connection Lost')
                  break
            except BrokenPipeError:
                  try: conn.close()
                  except: pass
                  Prompt.connClose('Connection Lost: Broken Pipe')
                  break
            
            #except Exception as e:
            #      print(pcolor.Fore.RED + pcolor.Style.BRIGHT + str(e) + pcolor.Style.RESET_ALL)