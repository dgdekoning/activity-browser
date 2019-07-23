# -*- coding: utf-8 -*-
import brightway2 as bw
from PyQt5 import QtCore, QtTest
from bw2data.parameters import DatabaseParameter, ProjectParameter

from activity_browser.app.signals import signals


def get_parameters_tab(window):
    """ Helper method: return the correct tab """
    return window.right_panel.tabs["Parameters"].tabs["Variables"]


def test_create_project_param(qtbot, ab_app):
    """ Create a single Project parameter.
    """
    assert bw.projects.current == "pytest_project"
    assert ProjectParameter.select().count() == 0
    qtbot.waitForWindowShown(ab_app.main_window)

    project_db_tab = get_parameters_tab(ab_app.main_window)
    proj_table = project_db_tab.project_table

    with qtbot.waitSignal(proj_table.new_parameter, timeout=1000):
        # qtbot.mouseClick(project_db_tab.new_project_param, QtCore.Qt.LeftButton)
        # Since mouseClick doesn't work, shortcircuit by emitting clicked event
        project_db_tab.new_project_param.clicked.emit()

    # Fill with variables
    assert proj_table.dataframe.shape[0] == 1
    proj_table.dataframe.loc[0, ] = {
        "name": "test_project", "amount": 2.5, "formula": ""
    }

    with qtbot.waitSignal(signals.parameters_changed, timeout=1000):
        # qtbot.mouseClick(project_db_tab.save_project_btn, QtCore.Qt.LeftButton)
        # Since mouseClick doesn't work, shortcircuit by emitting clicked event
        project_db_tab.save_project_btn.clicked.emit()

    assert ProjectParameter.select().count() == 1
    assert ProjectParameter.select().where(ProjectParameter.name == "test_project").count() == 1


def test_create_database_params(qtbot, ab_app):
    """ Create two database parameters, one dependent on the above
    project parameter and one dependent on the first database parameter.
    """
    assert DatabaseParameter.select().count() == 0

    project_db_tab = get_parameters_tab(ab_app.main_window)
    db_table = project_db_tab.database_table

    with qtbot.waitSignals([db_table.new_parameter, db_table.new_parameter], timeout=1000):
        project_db_tab.new_database_param.clicked.emit()
        project_db_tab.new_database_param.clicked.emit()

    assert db_table.dataframe.shape[0] == 2
    db_table.dataframe.loc[0, ] = {
        "database"
    }
    # project_db_tab.project_table.dataframe.iloc[0, 0] = "test_project"
    # project_db_tab.project_table.dataframe.iloc[0, 1] = "2.5"
    # project_db_tab.project_table.dataframe.iloc[0, 2] = ""


