<h1 align=center> sRFS - Simple Remote File System </h1>

<p align="center">
  <img src="https://user-images.githubusercontent.com/76400414/180086374-fad46b2e-2d54-4d30-a0e1-2ca39e554da4.png" />
</p>
<h3 align="center" > sRFS (Simple Remote File System) is a quick and easy platform to manage another device's storage.
Made to be used on personal computers as well as remote access to servers, sRFS is an open source program to help you delete, upload, download, copy and paste files, as well as running some basic shell commands. </h3>

<hr>
<br><br>

  
<h4 align="center" style="color:orange">⚠️ Your antivirus program might flag the executable files as virus, as these are not signed. Do not worry, I guarantee this is not any kind of malware and if you do not feel safe with it, just run the .py files instead, where you can check the source code running ⚠️</h4>

<br>

<h1 align=center> Quick Start </h1> 

## Server QuickStart

### 1. Setting up port forwarding

  - In your router's settings forward the ports according <br>
  to the following table: 
  
  | Port | Protocol    |
  |------|-------------| 
  | 9877 | `TCP` `UDP` | 
  | 9876 | `TCP` `UDP` |
  

### 2. Setting up the file
 - Drag and drop the `server.exe` file on it's own, clean, folder 
 - Make sure that it is in a safe folder and that it isnt being used for another purpose
 
## 3. Choosing a password
 - On the first execution, the server will prompt you to enter a password. This password will be stored in a `password.txt` file on the same folder as the executable.
 - To change the password, edit it the password.txt file.
 


<br><br>
## Client QuickStart 

⚠️ As of yet, the client only works on **Windows** ⚠️

### 1. Grabbing the server's address 
 - After the server is runnning, you have to get it's address. For that, search `Whats my ipv4` on google or click [this link](https://www.google.com/search?q=whats+my+ipv4&oq=whats+my+ipv4).

### 2. Connecting to the server
 - Once you have got the server's IP address, enter it in the first prompt (`Server Address`)
 
### 3. Logging in
 - As soon as a connection to the server is established, the program will prompt you to insert a password. Enter the same password you set on the server's side. If the password is correct, it should enter the browsing mode right away and you should be good to go, enjoy!

  
<h1 align=center> TODO List </h1> 
<br> 


- [ ] Add a gui
- [ ] Encrypted connection
- [x] Solve [issues](https://github.com/vicenterendo/sRFS/issues) 


