# -*- coding: utf-8 -*-
import brightway2 as bw
from bw2data.backends.peewee import sqlite3_lci_db
from PySide2 import QtCore, QtWidgets
import pytest

from activity_browser.app.controllers import ProjectController
from activity_browser.app.signals import signals


def test_project_indices(qtbot, ab_app, monkeypatch, capsys):
    """ Test a bit of legacy code that smoothly updates indices for databases
    """
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == 'pytest_project'
    monkeypatch.setattr(sqlite3_lci_db._database, "get_indexes", lambda *args, **kwargs: False)
    signals.project_selected.emit()
    captured = capsys.readouterr()
    assert "creating missing sqlite indices" in captured.out


@pytest.mark.parametrize(
    "proj_name, response", [
        ("", "No project name given."), ("nonexistent", "Project does not exist"),
    ]
)
def test_project_change_failure(qtbot, ab_app, capsys, proj_name, response):
    """ There are two kinds of ways the 'change_project' method can fail.
    """
    signals.change_project.emit(proj_name)
    cap = capsys.readouterr()
    assert response in cap.out


def test_project_pick_name(qtbot, monkeypatch):
    """ The user can fill out a name for a new project and either accept or
    reject it.
    """
    widget = QtWidgets.QWidget(None)
    controller = ProjectController(widget)
    qtbot.addWidget(widget)

    # Return a name from the controller method
    monkeypatch.setattr(
        QtWidgets.QInputDialog, "getText", staticmethod(lambda *args, **kwargs: ("a_name", True))
    )
    name = controller._ask_for_project_name()
    assert name == "a_name"
    monkeypatch.setattr(
        QtWidgets.QInputDialog, "getText", staticmethod(lambda *args, **kwargs: ("a_name", False))
    )
    name = controller._ask_for_project_name()
    assert name is None


def test_new_project(qtbot, ab_app):
    """ Create a new project through the project tab button.
    """
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == "pytest_project"
    assert "pytest_project_del" not in bw.projects
    controller = ab_app.controllers.project
    with qtbot.waitSignal(signals.projects_changed, timeout=500):
        controller.new_project("pytest_project_del")
    assert bw.projects.current == "pytest_project_del"


def test_project_new_project_exists(qtbot, ab_app):
    """ What happens when attempting to create a project that already exists.

    With thanks to https://stackoverflow.com/a/59148220 for showing a clean
    way of closing static QMessageBox popups.
    """
    qtbot.waitForWindowShown(ab_app.main_window)
    controller = ab_app.controllers.project

    def handle_message():
        box = QtWidgets.QApplication.activeWindow()
        assert "A project with this name already exists" in box.text()
        btn = box.button(QtWidgets.QMessageBox.Ok)
        qtbot.mouseClick(btn, QtCore.Qt.LeftButton, delay=1)

    QtCore.QTimer.singleShot(100, handle_message)
    controller.new_project("pytest_project")
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


def test_project_copy_no(qtbot, ab_app, monkeypatch):
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == "pytest_project_del"
    project_tab = ab_app.main_window.left_panel.tabs["Project"]
    monkeypatch.setattr(
        QtWidgets.QInputDialog, "getText", staticmethod(lambda *args, **kwargs: ("whoops", False))
    )

    # Do not go through with copying
    qtbot.mouseClick(
        project_tab.projects_widget.copy_project_button,
        QtCore.Qt.LeftButton
    )
    assert "whoops" not in bw.projects
    assert bw.projects.current == "pytest_project_del"


def test_project_copy_exists(qtbot, monkeypatch):
    widget = QtWidgets.QWidget(None)
    controller = ProjectController(widget)
    qtbot.addWidget(widget)

    def handle_message():
        box = QtWidgets.QApplication.activeWindow()
        assert "A project with this name already exists" in box.text()
        btn = box.button(QtWidgets.QMessageBox.Ok)
        qtbot.mouseClick(btn, QtCore.Qt.LeftButton, delay=1)

    monkeypatch.setattr(QtWidgets.QInputDialog, "getText", staticmethod(lambda *args, **kwargs: ("default", True)))
    QtCore.QTimer.singleShot(100, handle_message)
    controller.copy_project()


def test_delete_project(qtbot, monkeypatch, ab_app):
    qtbot.waitForWindowShown(ab_app.main_window)
    assert bw.projects.current == 'pytest_project_del'
    monkeypatch.setattr(QtWidgets.QMessageBox, 'question', staticmethod(lambda *args: QtWidgets.QMessageBox.Yes))
    # project_tab = ab_app.main_window.left_panel.tabs['Project']
    with qtbot.waitSignal(signals.projects_changed, timeout=500):
        # qtbot.mouseClick(
        #     project_tab.projects_widget.delete_project_button,
        #     QtCore.Qt.LeftButton
        # )
        ab_app.controllers.project.delete_project()
    assert bw.projects.current == 'default'


def test_project_copy_success(qtbot, monkeypatch, bw2test):
    widget = QtWidgets.QWidget(None)
    controller = ProjectController(widget)
    qtbot.addWidget(widget)

    # Create a copy
    monkeypatch.setattr(QtWidgets.QInputDialog, "getText", staticmethod(lambda *args, **kwargs: ("pytest_copy", True)))
    with qtbot.waitSignal(signals.projects_changed, timeout=500):
        controller.copy_project()
    assert bw.projects.current == "pytest_copy"


def test_project_delete_last_fails(qtbot, bw2test):
    """ A special error message is given if the user attempts to delete the
    last project.
    """
    widget = QtWidgets.QWidget(None)
    controller = ProjectController(widget)
    qtbot.addWidget(widget)

    def handle_message():
        box = QtWidgets.QApplication.activeWindow()
        assert "Can't delete last project." in box.text()
        btn = box.button(QtWidgets.QMessageBox.Ok)
        qtbot.mouseClick(btn, QtCore.Qt.LeftButton, delay=1)

    QtCore.QTimer.singleShot(100, handle_message)
    controller.delete_project()
