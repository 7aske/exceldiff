bin=./node_modules/.bin

default_recipe: build

build: install build-react build-electron build-python
	echo build

install:
	python3 -m venv venv
	. venv/bin/activate
	python3 -m pip install -r requirements.txt
	$(bin)/yarn install

build-react: src/index.tsx
	$(bin)/react-scripts build

build-electron:
	$(bin)/tsc --build src/electron/tsconfig.json
	cp src/electron/preload.js build/
	$(bin)/electron-packager ./build exceldiff --out=./dist --platform=win32 --arch=x64 --overwrite --ignore=./build/exceldiff

build-python: exceldiff/exceldiff.py
	. venv/bin/activate
	venv/bin/pyinstaller --onefile -y exceldiff/exceldiff.py --distpath dist/exceldiff-win32-x64/exceldiff/
