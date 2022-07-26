from __future__ import print_function, unicode_literals
import os
import socket, pickle, sys, win32gui
import time
import shutil
import tempfile as tfutils
import colorama as pcolor
from tkinter import filedialog as fd
from alive_progress import alive_bar
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from tqdm import tqdm
from natsort import natsorted, ns
from cryptography.fernet import Fernet
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform

def clearConsole():
      if os.name == 'nt':
            os.system('cls')
      else:
            os.system('clear')
            
clearConsole()

print(os.getcwd())
print("Welcome to sRFS - Simple Remote File System")
print('Loading...')

class DebugPrint:
      def connOpen(message):
            print(pcolor.Fore.GREEN + pcolor.Style.BRIGHT + '[+] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)
      def connMessage(message):
            print(pcolor.Fore.CYAN + pcolor.Style.BRIGHT + '[/] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)
      def connClose(message):
            print(pcolor.Fore.RED + pcolor.Style.BRIGHT + '[-] ' + pcolor.Style.RESET_ALL + pcolor.Fore.BLUE + message + pcolor.Style.RESET_ALL)

def getPrivateIp():
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      privateIp = s.getsockname()[0]
      s.close()
      return privateIp

class settings:
      serverAddr = (0, 9876)
      ftsAddr = (0, 9877)
      txtformat = 'utf-8'
      ftspacketsize = 1024
      
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
      
class Env:
      current_dir = '.'
      if platform.system().lower() == 'windows':
            localpathseparator = "\\"
      else:
            localpathseparator = "/"
      temp_dir = tfutils.gettempdir() + '\\rfs\\'
      

class dirEntry:
      def __init__(self, type, name):
            self.name = name
            self.type = type

def sendFile(filename):
      global fts
      ftc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      ftc.connect(settings.ftsAddr)
      try: os.mkdir("." + Env.pathseparator + ".tempsrfs" + Env.pathseparator)
      except: pass
      tempfile = "." + Env.localpathseparator + ".tempsrfs" + Env.localpathseparator + filename.split(Env.localpathseparator)[-1]
      
      with open(filename, 'rb') as f:
            with open(tempfile, "wb") as f2:
                  f2.write(crypto.encrypt(f.read()))
                  
      with open(tempfile, 'rb') as f:
            data = f.read()
            size = sys.getsizeof(data)
            
      ftc.send(crypto.encrypt(str(size).encode('utf-8')))
      ftc.recv(1024)
      
      with open(tempfile, 'rb') as f:
            while True:
                  packet = f.read(1024)
                  
                  if not packet:
                        break
                  
                  ftc.send(packet)
                  pass
                  
def rcvFile(filename):
      global crypto
      ftc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      while True:
            try:
                  ftc.connect(settings.ftsAddr)
                  break
            except ConnectionRefusedError:
                  pass
      size = int(crypto.decrypt(ftc.recv(1024)))
      ftc.send(crypto.encrypt('ready'.encode('utf-8')))
      downloadedbytes = 0
      try:
            os.remove(filename)
      except FileNotFoundError:
            pass
      packet = bytes()
      encdata = bytes()
      with tqdm(total=size/1000000) as bar:
            with open(filename + ".temp", 'ab') as f:
                  while downloadedbytes < size:   
                        packet = ftc.recv(1024)
                        if sys.getsizeof(packet) == 33:
                              break
                        f.write(packet)
                        bar.update(sys.getsizeof(packet)/1000000)
                        

      with open(filename + ".temp", 'rb') as f: encdata = f.read()
      with open(filename, 'wb') as f: f.write(crypto.decrypt(encdata))
            
      
            
      ftc.close()
      
def choiceMenu(options, commands=None):
      style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#ff6673 bold',  # default
            Token.Pointer: '#0ae7ff bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
      })
      
      selectorlist = [
            {
            'type': 'list',
            'message': 'sRFS ' + str(settings.serverAddr) + f'({Env.current_dir})',
            'name': 'choice',
            'validate': lambda answer: 'You must choose at least one topping.' \
                  if len(answer) == 0 else True,
            'choices': []
            }
      ]
            
      if commands != None:
            selectorlist[0]['choices'].append(Separator())
            
            for command in commands:
                  selectorlist[0]['choices'].append({'name': command})
                  
            selectorlist[0]['choices'].append(Separator())
            
      for entry in options:
            selectorlist[0]['choices'].append({'name': entry.name})
            
      answer = prompt(selectorlist, style=style)
      
      answer = answer['choice']
      
      return answer
      
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
                  'message': 'Password:',
                  'name': 'password',
            }
      ]

      answer = prompt(properties, style=style)
      return answer['password']

def normalPrompt(message):
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
                  'type': 'input',
                  'message': message,
                  'name': 'input',
            }
      ]

      answer = prompt(properties, style=style)
      return answer['input']

def findFileInList(filelist, query):
      foundAt = None
      for i, file in enumerate(filelist):
            if file.name == query:
                  foundAt = i
      return foundAt

def isdir(path):
      client.send(crypto.encrypt(pickle.dumps({'action': EventID.ISFOLDER, 'details': {'path': path}})))
      isDir = pickle.loads(crypto.decrypt(client.recv(1024)))
      return isDir

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if not os.path.exists('lastIp.txt'):
      open('lastIp.txt', 'w').close()

f = open('lastIp.txt', 'r+')
lastIp = f.read()



if lastIp != '':
      addrInput = normalPrompt('Server Adress (empty for last):')
      if addrInput == '':
            settings.serverAddr = (lastIp, settings.serverAddr[1])
            settings.ftsAddr = (lastIp, settings.ftsAddr[1])
      else:
            settings.serverAddr = (addrInput, settings.serverAddr[1])
            settings.ftsAddr = (addrInput, settings.ftsAddr[1])
            with open('lastIp.txt', 'w') as f:
                  f.write(addrInput)

else: 
      addrInput = normalPrompt('Server Adress:')
      if addrInput == '':
            print('Insert Something')
            sys.exit()
      else:
            settings.serverAddr = (addrInput, settings.serverAddr[1])
            settings.ftsAddr = (addrInput, settings.ftsAddr[1])
            with open('lastIp.txt', 'w') as f:
                  f.write(addrInput)


f.close()
      



print(f"Connecting to server {settings.serverAddr[0]}...")

# Connect to server
while True:
      try:
            client.connect(tuple(settings.serverAddr))
            break
      except ConnectionRefusedError:
            print("Connection timed out, trying again...")
            pass

if not os.path.exists("./key.srfskey"):
      currcwd = os.getcwd()
      print(pcolor.Fore.RED + pcolor.Style.BRIGHT + "No \"key.srfskey\" file found on the current directory, press enter to select a file...")
      input()
      filename, customfilter, flags=win32gui.GetOpenFileNameW()
      shutil.copy(filename, currcwd + Env.localpathseparator + "key.srfskey")

with open("./key.srfskey", 'rb') as f:
      crypto = Fernet(pickle.loads(f.read()))
      


toSend = crypto.encrypt(pickle.dumps({'action': EventID.GETCWD})) 
client.send(toSend)

Env.current_dir = crypto.decrypt(client.recv(65535)).decode('utf-8')

client.send(crypto.encrypt(pickle.dumps({'action': EventID.GETPLATFORM})))
Env.serverplatform = crypto.decrypt(client.recv(65535)).decode('utf-8')
if Env.serverplatform.upper() == 'WINDOWS':
      Env.pathseparator = '\\'
else:
      Env.pathseparator = '/'

while True:
      try:
            if not Env.current_dir.endswith(Env.pathseparator):
                  Env.current_dir += Env.pathseparator
            clearConsole()
            client.send(crypto.encrypt(pickle.dumps({'action': EventID.LISTFILES, 'details': {'path': Env.current_dir}})))
            data = b""
            #currtimeout = 0.1
            while True:
                  packet = client.recv(4096)
                  if not packet: break
                  data += packet
                  try: 
                        _data = crypto.decrypt(data)
                        dir_list = pickle.loads(_data) 
                        break
                  except:
                        continue
            
                  
                  
            #client.settimeout(None)
            
            dir_list = natsorted(dir_list, key=lambda x: x.name)
            modifiedDirList = dir_list
            modifiedDirList.insert(0, dirEntry(1, '..'))
            nameOnlyDirList = list()
            
            commands = [
                  '/upload',
                  '/delete',
                  '/goto',
                  '/download',
                  '/command'
            ]
            
            
            for entry in dir_list:
                  nameOnlyDirList.append(entry.name)         
            
            userinput = choiceMenu(modifiedDirList, commands)
            
            
            if userinput.startswith('/'):           
                  if userinput.startswith('/goto'):
                        custompath = input('Path >  ').replace('/', Env.pathseparator).replace('.' + Env.pathseparator, Env.current_dir)
                         
                        if Env.serverplatform.lower() == 'windows':
                              if not custompath[1] == ":":
                                    custompath = Env.current_dir + custompath

                        else:
                              if not custompath[0] == "/":
                                    custompath = Env.current_dir + custompath
                              
                        fname = custompath.split(Env.pathseparator)[-1]
                        client.send(crypto.encrypt(pickle.dumps({'action': EventID.CHECKPATH, 'details': {'path': custompath}})))
                        isPath = pickle.loads(crypto.decrypt(client.recv(1024)))
                        if isPath:
                              if isdir(custompath) == 0: 
                                    if len(custompath) == 2 and custompath.endswith(":"):
                                          custompath += Env.pathseparator      
                                    currunix = '{' + str(time.time()) + '}'
                                    client.send(crypto.encrypt(pickle.dumps({'action': EventID.GETFILE, 'details': {'path': custompath}})))
                                    tempfile = Env.temp_dir + currunix + Env.pathseparator + fname
            
                                    if 'rfs' not in os.listdir(tfutils.gettempdir()): os.mkdir(Env.temp_dir)

                                    try: os.mkdir(Env.temp_dir + currunix)
                                    except: pass
                                          
                                    
                                    rcvFile(tempfile)
                                    os.startfile(tempfile)
                              else: Env.current_dir = custompath
                              
                        else: Env.current_dir = custompath
                                    
                                    
                        if not Env.current_dir.endswith(Env.pathseparator):
                              Env.current_dir += Env.pathseparator
                        
                  if userinput.startswith('/upload'):
                        filename, customfilter, flags=win32gui.GetOpenFileNameW()
                        client.send(crypto.encrypt(pickle.dumps({'action': EventID.WRITEFILE, 'details': {'path': Env.current_dir + input('Save as >  ')}})))
                        sendFile(filename)
                  
                  if userinput.startswith('/delete'):
                        filetodel = Env.current_dir + choiceMenu(dir_list)
                        client.send(crypto.encrypt(pickle.dumps({'action': EventID.DELETEFILE, 'details': {'path': filetodel}})))
                  
                  if userinput.startswith('/download'):
                        currunix = '{' + str(time.time()) + '}'
                        filename = choiceMenu(dir_list)
                        if dir_list[findFileInList(dir_list, filename)].type == 1:   
                              filetodownload = Env.current_dir + filename
                              tempfile = Env.temp_dir + currunix + '.zip'
                              client.send(crypto.encrypt(pickle.dumps({'action': EventID.DOWNLOADFOLDER, 'details': {'path': filetodownload}})))
                              try: os.mkdir(Env.temp_dir + currunix)  
                              except: pass
                              rcvFile(tempfile)
                              shutil.unpack_archive(tempfile, Env.temp_dir + currunix  + Env.pathseparator + filename, 'zip')
                              os.system('start ' + Env.temp_dir + currunix + Env.pathseparator + filename)
                        else:
                              filetodownload = Env.current_dir + filename
                              tempfolder = Env.temp_dir + currunix
                              client.send(crypto.encrypt(pickle.dumps({'action': EventID.GETFILE, 'details': {'path': filetodownload}})))
                              try: os.mkdir(tempfolder)
                              except: pass
                                    
                              rcvFile(tempfolder + Env.pathseparator + filename)
                              
                              os.startfile(tempfolder + Env.pathseparator + filename)
                              
                  if userinput.startswith('/command'):
                        command = normalPrompt('Bash command: ')
                        client.send(crypto.encrypt(pickle.dumps({'action': EventID.RUNCMD, 'details': {'command': command}})))
                        received = pickle.loads(crypto.decrypt(client.recv(65535)))
                        print(str(received)[2:-1].replace('\\n', '\n').replace('\\r', '\r'))
                        print('---------- [END OF OUTPUT] ----------')
                        input('Press enter to continue...')
                        del received
                        
                  
                  
                  continue
            
            else:
                  currentry = dir_list[findFileInList(dir_list, userinput)]
                  
                  if currentry.type == 0: 
                        currunix = '{' + str(time.time()) + '}'
                        tempfolder = Env.temp_dir + currunix
                        client.send(crypto.encrypt(pickle.dumps({'action': EventID.GETFILE, 'details': {'path': Env.current_dir + currentry.name}})))
                        tempfile = Env.temp_dir + currunix + Env.pathseparator + currentry.name
                        
                        if 'rfs' not in os.listdir(tfutils.gettempdir()): os.mkdir(Env.temp_dir)
                        
                        try: os.mkdir(tempfolder) 
                        except: pass
                              
                        rcvFile(tempfile)
                        try: os.startfile(tempfile)
                        except: pass
                        
                  elif currentry.name == '..':

                        if not Env.current_dir.endswith(':'):
                              cutDir = Env.current_dir.split(Env.pathseparator)[:-2]
                              Env.current_dir = ''
                              for dir in cutDir:
                                    Env.current_dir += dir + Env.pathseparator
                  
                  else:
                        Env.current_dir += currentry.name
      
      except ConnectionResetError:
            pass
      
      except KeyError:
            
            try: 
                  client.send(crypto.encrypt(pickle.dumps({'action': EventID.CLOSECONN})))
                  client.close()
            except: pass
            sys.exit()
