# OpenLWR-Server

Serverside component of OpenLWR, handles communication with clients and runs the simulation calculations.\
very big thanks to Goosey (fluff.goose on discord) for writing the original reactor physics in lua

# How to run
## Step 1: Installing python3.12

<details>
  <summary>Windows</summary>
  
Install python3.12 via the microsoft store\
Can also be installed from the python website, however please make sure you check the option to set the PATH variable in the installer
</details>
<br>
<details>
  <summary>macOS</summary>
  
NOTE: macOS 13 "Ventura" or later is required to install python\
Install [brew.sh](https://brew.sh/) via the following command:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then, install python via homebrew:
```
brew install python@3.12
```
</details>
<br>
<details>
  <summary>Linux</summary>
  <br>

<details>
  
  <summary>Ubuntu/Debian</summary>
  
NOTE: python3.12 is not available on debian stable, in this case, you must build python3.12 yourself in order to run the server. This process will not be covered by this guide.
```
sudo apt install python3.12 python3-pip
```
</details>
<details>
  <summary>Fedora/RHEL</summary>
  
```
sudo dnf install python3.12 python3.12-pip
```
</details>
<details>
  <summary>Arch</summary>
  
```
sudo pacman -S python python-pip
```
</details>
<details>
  <summary>Gentoo</summary>
  
```
sudo emerge --ask dev-lang/python:3.12 dev-python/pip
```
</details>
</details>
<br>
<details>
  <summary>FreeBSD</summary>
  
NOTE: python3.12 is not available, you must build python3.12 yourself in order to run the server. This process will not be covered by this guide.\
Once python3.12 is installed, you may install pip using the following command.
```
python3.12 -m ensurepip --upgrade
```
</details>

## Step 2: Installing python dependencies
cd into the directory where the server files are, then run the following command:
```
python3.12 -m pip install -r requirements.txt
```

In some cases, pip may throw an error telling you to create a venv, if pip runs successfully, you may skip this step, however, if this occurrs, you can resolve this with the following:
```
python3.12 -m venv .

# Please note that you will need to run this to activate the venv every time you want to start the server
source bin/activate

# Now run pip again
python3.12 -m pip install -r requirements.txt
```


## Step 3: Running the server
In the server directory, run the following command:
```
python3.12 main.py
```
