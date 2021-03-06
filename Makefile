bin=./node_modules/.bin

UNAME=""
ifeq ($(OS),Windows_NT)
    UNAME = WIN32
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        UNAME = LINUX
    endif
    ifeq ($(UNAME_S),Darwin)
        UNAME = OSX
    endif
endif

default_recipe: build

build: install build-react build-electron build-python
	

install:
ifeq ($(UNAME),WIN32)
	python.exe -m venv venv
	.\venv\Scripts\activate.bat
	python.exe -m pip install -r requirements.txt
	yarn install
else
	python3 -m venv venv
	. venv/bin/activate
	python3 -m pip install -r requirements.txt
	yarn install
endif


build-react: src/index.tsx
	npm run build-react

build-electron:
ifeq ($(UNAME),WIN32)
	npm run build-electron-windows
	npm run package-electron-windows
else
	npm run build-electron-linux
	npm run package-electron-linux	
endif

build-python: exceldiff/exceldiff.py
ifeq ($(UNAME),WIN32)
	.\venv\Scripts\activate.bat
	pyinstaller --onefile -y exceldiff\exceldiff.py --distpath dist\exceldiff-win32-x64\bin
else
	. venv/bin/activate
	venv/bin/pyinstaller --onefile -y exceldiff/exceldiff.py --distpath dist/exceldiff-linux-x64/bin/
endif

