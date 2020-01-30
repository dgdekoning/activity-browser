# -*- coding: utf-8 -*-
from brightway2 import projects
from PySide2 import QtWidgets
from PySide2.QtCore import Slot

from ..signals import signals


class Statusbar(QtWidgets.QStatusBar):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

        self.status_message_left = QtWidgets.QLabel('Welcome')
        self.status_message_right = QtWidgets.QLabel('Database')
        self.status_message_center = QtWidgets.QLabel('Project')

        self.addWidget(self.status_message_left, 1)
        self.addWidget(self.status_message_center, 2)
        self.addWidget(self.status_message_right, 0)

        self.connect_signals()

    def connect_signals(self):
        signals.new_statusbar_message.connect(self.left)
        signals.project_selected.connect(self.update_project)
        signals.database_selected.connect(self.set_database)

    @Slot(str, name="setNewLeftMessage")
    def left(self, message):
        print(message)  # for console output
        self.status_message_left.setText(message)

    def center(self, message):
        self.status_message_center.setText(message)

    def right(self, message):
        self.status_message_right.setText(message)

    @Slot(str, name="setCurrentProjectName")
    def update_project(self):
        self.center("Project: {}".format(projects.current))
        self.right("Database: None")

    @Slot(str, name="setDatabaseName")
    def set_database(self, name):
        self.right("Database: {}".format(name))
