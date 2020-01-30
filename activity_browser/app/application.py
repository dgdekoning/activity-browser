# -*- coding: utf-8 -*-
from PySide2.QtCore import __version__ as qt_version
from PySide2.QtWidgets import QApplication

from .controller import Controller
from .ui.main import MainWindow


class Application(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        print("Qt Version:", qt_version)
        self.main_window = MainWindow()
        self.controller = Controller()
