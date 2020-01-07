# -*- coding: utf-8 -*-
from collections import namedtuple

from .controllers import *
from .ui.main import MainWindow


Controllers = namedtuple(
    "controllers",
    (
        "project", "database", "activity", "exchange", "calculation",
        "metadata", "settings",
    )
)


class Application(object):
    def __init__(self):
        self.main_window = MainWindow()
        self.controllers = Controllers(
            ProjectController(),
            DatabaseController(),
            ActivityController(),
            ExchangeController(),
            CalculationSetupController(),
            MetadataController(),
            SettingController(),
        )

    def show(self):
        self.main_window.showMaximized()

    def close(self):
        self.main_window.close()

    def deleteLater(self):
        self.main_window.deleteLater()
