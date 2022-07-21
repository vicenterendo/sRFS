from __future__ import print_function, unicode_literals
from multiprocessing import Event
import os
from re import L
import subprocess

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
import colorama
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from natsort import natsorted, ns
import platform


class Prompt:
      def connOpen(message):
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT + '[+] ' + colorama.Style.RESET_ALL + colorama.Fore.BLUE + message + colorama.Style.RESET_ALL)
      def connMessage(message):
            print(colorama.Fore.CYAN + colorama.Style.BRIGHT + '[/] ' + colorama.Style.RESET_ALL + colorama.Fore.BLUE + message + colorama.Style.RESET_ALL)
      def connClose(message):
            print(colorama.Fore.RED + colorama.Style.BRIGHT + '[-] ' + colorama.Style.RESET_ALL + colorama.Fore.BLUE + message + colorama.Style.RESET_ALL)

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
      
class dirEntry:
      def __init__(self, type, name):
            self.name = name
            self.type = type
            
class Env:
      temp_dir = tfutils.gettempdir() + '\\rfsServer\\'

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


if 'password.txt' in os.listdir():
      password = open('./password.txt', 'r').read()
else:
      print(colorama.Fore.RED + colorama.Style.BRIGHT + 'No password.txt detected on user\'s home directory.' + colorama.Style.RESET_ALL)
      password = passwordPrompt()
      open('password.txt', 'w').write(password)
      print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 'Password has been set and saved on password.txt.' + colorama.Style.RESET_ALL)


os.chdir(str(Path.home()))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((getPrivateIp(), 9876))


fts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fts.bind((getPrivateIp(), 9877))

def rcvFile():
      global fts
      fts.listen()
      ftc, addr = fts.accept()
      size = int(ftc.recv(1024))
      ftc.send('ready'.encode('utf-8'))
      filedata = bytes()
      while sys.getsizeof(filedata) < size:
            filedata += ftc.recv(1024)
      ftc.close()
            
      return filedata

def sendFile(filename):
      global fts
      fts.listen()
      ftc, addr = fts.accept()
      with open(filename, 'rb') as f:
            data = f.read()
            size = sys.getsizeof(data)
            
      ftc.send(str(size).encode('utf-8'))
      ftc.recv(1024)
      
      with open(filename, 'rb') as f:
            while True:
                  packet = f.read(1024)
                  
                  if not packet:
                        break
                  
                  ftc.send(packet)
      
      


while True:
      server.listen()
      conn, addr = server.accept()
      
      while True:
            insertedpassword = pickle.loads(conn.recv(1024))
            if insertedpassword == password:
                  conn.send(pickle.dumps(True))
                  break
            else:
                  conn.send(pickle.dumps(False))
                  
      
      Prompt.connOpen('Connected to ' + str(addr[0]))
      while True:
            try:
                  conn.settimeout(15)
                  while True:
                        try: 
                              rawEntry = conn.recv(2048)
                              break
                        except: pass
                  conn.settimeout(None)
                        
                  try:
                        jsonEntry = pickle.loads(rawEntry)
                  except EOFError:
                        pass
                  
                  action = jsonEntry['action']
                  
                  Prompt.connMessage("Request received: " + str(jsonEntry))
                  
                  if action == EventID.GETPLATFORM:
                        conn.send(platform.system().encode('utf-8'))

                  if action == EventID.GETCWD:
                        conn.send(os.getcwd().encode('utf-8'))
                        
                  
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
                        conn.send(pickle.dumps(dirList))
                        
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
                        shutil.make_archive(Env.temp_dir + path.split('/')[-1], 'zip', path)
                        sendFile(Env.temp_dir + path.split('/')[-1] + '.zip')
                        
                  if action == EventID.CHECKPATH:
                        path = jsonEntry['details']['path']
                        if os.path.exists(path):
                              conn.send(pickle.dumps(True))
                        else:
                              conn.send(pickle.dumps(False))

                  if action == EventID.RUNCMD:
                        fullcommand = jsonEntry['details']['command']
                        command = jsonEntry['details']['command'].split()[0]
                        parameters = fullcommand.strip(jsonEntry['details']['command'].split()[0])
                        conn.send(subprocess.check_output([command]))

                  
                        
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
            
            except Exception as e:
                  print(colorama.Fore.RED + colorama.Style.BRIGHT + str(e) + colorama.Style.RESET_ALL)