# Building the activity-browser as a standalone executable

## PyInstaller

In order to build a functioning standalone package we need to do the following:

- Create a new Conda environment with the latest activity-browser installed AND a version of pyinstaller greater than 3.4: `conda create -y -n abbuild python=3.7 activity-browser pyinstaller>3.4`
- Activate the new environment with: `conda activate abbuild`
- Create two new folders either inside this repository or outside it.
- Copy the `run-activity-browser.py` script into the first folder.
- Within the anaconda prompt, change directory to the first folder (where the script is).
- Create a `.spec` file (see [here](https://pythonhosted.org/PyInstaller/spec-files.html#using-spec-files) for explanations) with the following command: `pyi-makespec -D -n activity-browser .\run-activity-browser.py`
- Now open the new file and paste the following between the first and third lines:
```python
import os
import importlib

ab_root = os.path.dirname(importlib.import_module('activity_browser').__file__)
bw2io_root = os.path.dirname(importlib.import_module('bw2io').__file__)

data_files = [
    (os.path.join(ab_root, 'icons'), 'activity_browser\\icons'),
    (os.path.join(ab_root, 'app\\ui\\web'), 'activity_browser\\app\\ui\\web'),
    (os.path.join(bw2io_root, 'data'), 'bw2io\\data')
]
```
- Inside the `a = Analysis` code, change the `datas=[]` to `datas=data_files`.
- Congrats! You can now call pyinstaller to start the build process: `pyinstaller activity-browser.spec`
- PyInstaller will run and throw out some warnings, but complete the build process anyway.
- Windows note: Several Qt executables and files are not placed correctly, so this part is important.
  - Go into the newly created `dist/activity-browser` folder. This the `root` folder containing the `activity-browser.exe` executable.
  - Move the `qtwebengine_locales` folder from `PyQt5/Qt/translations` to the `root` folder.
  - Move all of the files in `PyQt5/Qt/resources` to the `root` folder.
  - Move the `QtWebEngineProcess.exe` and `opengl32sw.dll` files from `PyQt5/Qt/bin` to the `root` folder.
  - Go to the anaconda environment folder for the environment used to build the executable. There, look in the `Library/bin` folder for the `libGLESv2.dll` and `libEGL.dll` files. Copy these over as well.
  - Check that everything works by running the `activity-browser.exe` file.
