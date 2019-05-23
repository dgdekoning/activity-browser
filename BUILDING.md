# Building the activity-browser as a standalone executable

## PyInstaller

In order to build a functioning standalone package we currently (May 2019) need to jump through quite a few hoops:

- Create a new Conda environment with the latest activity-browser installed: `conda create -y -n abbuild activity-browser`
- Activate the new environment with: `conda activate abbuild`
- Download _only_ the dependencies for PyInstaller: `conda install -y --only-deps pyinstaller`
- Now, download the __development__ version of the PyInstaller with `pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip`
- Create two new folders either inside this repository or outside it.
- Copy the `run-activity-browser.py` script into the first folder.
- Copy the `activity_browser` folder into the second folder.
  - Make sure to remove .pyc files if these exist!
- Within the anaconda prompt, change directory to the first folder (where the script is).
- Call `pyinstaller` as follows:
  - For windows: `pyinstaller -D -n activity-browser --add-data <path_to_second_folder>;. run-activity-browser.py`
  - For linux: TODO
- PyInstaller will run and throw out some warnings, but complete the build process anyway.
- Windows note: Several Qt executables and files are not placed correctly, so this part is important.
  - Go into the newly created `dist/activity-browser` folder. This the `root` folder containing the `activity-browser.exe` executable.
  - Move the `qtwebengine_locales` folder from `PyQt5/Qt/translations` to the `root` folder.
  - Move all of the files in `PyQt5/Qt/resources` to the `root` folder.
  - Move the `QtWebEngineProcess.exe` file from `PyQt5/Qt/bin` to the `root` folder.
  - Check that everything works by running the `activity-browser.exe` file.
