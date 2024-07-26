# OpenLWR-Server

Serverside component of OpenLWR, handles communication with clients and runs the simulation calculations.\
very big thanks to Goosey (fluff.goose on discord) for writing the original reactor physics in lua

# How to run
## Installing python3.12

<details>
  <summary>Windows</summary>
  
Install python3.12 via the microsoft store\
Can also be installed from the python website, however please make sure you check the option to set the PATH variable in the installer
</details>
<br>
<details>
  <summary>macOS</summary>
  
NOTE: This requires version 12.7.5 "Monterey" or later\
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
  
NOTE: On stable releases of Debian, python3.12 is not available, you can either build 3.12 from source, or you can install python3.11 through apt (though 3.11 is not supported and may cause issues)
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
  
NOTE: python3.12 is not available, you can either build 3.12 from source, or you can install python 3.11 (though 3.11 is not supported and may cause issues)
```
sudo pkg install python311
python3.11 -m ensurepip --upgrade
```
</details>

## Installing python dependencies
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


## Running the server
In the server directory, run the following command:
```
python3.12 main.py
```
