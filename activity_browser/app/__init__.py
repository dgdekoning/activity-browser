# -*- coding: utf-8 -*-
import sys
import traceback

from .application import Application


def run_activity_browser():
    print("Python version:", sys.version)
    qapp = Application(sys.argv)
    qapp.main_window.showMaximized()

    def exception_hook(*args):
        print(''.join(traceback.format_exception(*args)))

    sys.excepthook = exception_hook
    sys.exit(qapp.exec_())
