# -*- coding: utf-8 -*-
import brightway2 as bw
from PySide2 import QtCore, QtWidgets


def test_open_db_wizard(qtbot, ab_app):
    assert bw.projects.current == 'pytest_project'
    qtbot.waitForWindowShown(ab_app.main_window)
    project_tab = ab_app.main_window.left_panel.tabs['Project']

    def handle_message():
        box = QtWidgets.QApplication.activeWindow()
        btn = box.button(QtWidgets.QWizard.CancelButton)
        qtbot.mouseClick(btn, QtCore.Qt.LeftButton, delay=1)

    QtCore.QTimer.singleShot(100, handle_message)
    qtbot.mouseClick(
        project_tab.databases_widget.import_database_button,
        QtCore.Qt.LeftButton
    )
