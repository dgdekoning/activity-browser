# -*- coding: utf-8 -*-
import brightway2 as bw
from PySide2 import QtCore, QtWidgets

from activity_browser.app.controllers import ProjectController
from activity_browser.app.signals import signals


def test_new_project(qtbot, mocker, ab_app):
    qtbot.waitForWindowShown(ab_app.main_window)
    mocker.patch.object(
        ProjectController, '_ask_for_project_name', return_value='pytest_project_del'
    )
    project_tab = ab_app.main_window.left_panel.tabs['Project']
    with qtbot.waitSignal(signals.projects_changed, timeout=500):
        qtbot.mouseClick(
            project_tab.projects_widget.new_project_button,
            QtCore.Qt.LeftButton
        )
    assert bw.projects.current == 'pytest_project_del'


def test_change_project(qtbot, ab_app):
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == 'pytest_project_del'
    project_tab = ab_app.main_window.left_panel.tabs['Project']
    combobox = project_tab.projects_widget.projects_list
    assert 'default' in bw.projects
    assert 'default' in combobox.project_names
    combobox.activated.emit(combobox.project_names.index('default'))
    assert bw.projects.current == 'default'
    combobox.activated.emit(combobox.project_names.index('pytest_project_del'))
    assert bw.projects.current == 'pytest_project_del'


def test_delete_project(qtbot, mocker, ab_app):
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == 'pytest_project_del'
    mocker.patch.object(ProjectController, '_confirm_project_deletion',
                        return_value=QtWidgets.QMessageBox.Yes)
    project_tab = ab_app.main_window.left_panel.tabs['Project']
    with qtbot.waitSignal(signals.projects_changed, timeout=500):
        qtbot.mouseClick(
            project_tab.projects_widget.delete_project_button,
            QtCore.Qt.LeftButton
        )
    assert bw.projects.current == 'default'
