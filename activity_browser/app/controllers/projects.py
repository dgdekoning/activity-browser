# -*- coding: utf-8 -*-
from typing import Optional

import brightway2 as bw
from bw2data.backends.peewee import sqlite3_lci_db
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QInputDialog, QMessageBox

from ..settings import ab_settings
from ..signals import signals
from .base import BaseController


class ProjectController(BaseController):
    def connect_signals(self):
        signals.project_selected.connect(self.ensure_sqlite_indices)
        signals.new_project.connect(self.new_project)
        signals.change_project.connect(self.change_project)
        signals.copy_project.connect(self.copy_project)
        signals.delete_project.connect(self.delete_project)
        print('Brightway2 data directory: {}'.format(bw.projects._base_data_dir))
        print('Brightway2 active project: {}'.format(bw.projects.current))
        signals.project_selected.emit()

    @staticmethod
    @Slot(name="ensureSqliteIndices")
    def ensure_sqlite_indices() -> None:
        """
        - fix for https://github.com/LCA-ActivityBrowser/activity-browser/issues/189
        - also see bw2data issue: https://bitbucket.org/cmutel/brightway2-data/issues/60/massive-sqlite-query-performance-decrease
        @LegacyCode?
        """
        if bw.databases and not sqlite3_lci_db._database.get_indexes('activitydataset'):
            print('creating missing sqlite indices')
            bw.Database(list(bw.databases)[-1])._add_indices()

    @staticmethod
    @Slot(str, name="changeBrightwayProject")
    def change_project(name: str = None, reload: bool = False) -> None:
        # TODO: what should happen if a new project is opened? (all activities, etc. closed?)
        # self.clear_database_wizard()
        if not name:
            print("No project name given.")
            return
        elif name not in bw.projects:
            print("Project does not exist: {}".format(name))
            return
        if name != bw.projects.current or reload:
            bw.projects.set_current(name)
            signals.project_selected.emit()
            print("Loaded project:", name)

    @staticmethod
    def _ask_for_project_name() -> Optional[str]:
        name, ok = QInputDialog.getText(
            None,
            "Create new project",
            "Name of new project:" + " " * 25
        )
        return name if ok else None

    @staticmethod
    @Slot(name="newBrightwayProject")
    def new_project(name: str = None) -> None:
        name = name or ProjectController._ask_for_project_name()
        if name and name not in bw.projects:
            bw.projects.set_current(name)
            ProjectController.change_project(name, reload=True)
            signals.projects_changed.emit()
        elif name in bw.projects:
            QMessageBox.information(None, "Not possible.", "A project with this name already exists.")

    @staticmethod
    @Slot(name="copyBrightwayProject")
    def copy_project() -> None:
        name, ok = QInputDialog.getText(
            None,
            "Copy current project",
            "Copy current project ({}) to new name:".format(bw.projects.current) + " " * 10
        )
        if ok and name:
            if name not in bw.projects:
                bw.projects.copy_project(name, switch=True)
                ProjectController.change_project(name)
                signals.projects_changed.emit()
            else:
                QMessageBox.information(None, "Not possible.", "A project with this name already exists.")

    @staticmethod
    def _confirm_project_deletion() -> QMessageBox.StandardButton:
        return QMessageBox.question(
            None,
            "Confirm project deletion",
            ("Are you sure you want to delete project '{}'? It has {} databases" +
             " and {} LCI methods").format(
                bw.projects.current,
                len(bw.databases),
                len(bw.methods)
            )
        )

    @staticmethod
    @Slot(name="deleteBrightwayProject")
    def delete_project() -> None:
        if len(bw.projects) == 1:
            QMessageBox.information(None, "Not possible.", "Can't delete last project.")
            return
        response = ProjectController._confirm_project_deletion()
        if response == QMessageBox.Yes:
            bw.projects.delete_project(bw.projects.current, delete_dir=False)
            ProjectController.change_project(ab_settings.startup_project, reload=True)
            signals.projects_changed.emit()


class CalculationSetupController(BaseController):
    def connect_signals(self):
        signals.new_calculation_setup.connect(self.new_calculation_setup)
        signals.rename_calculation_setup.connect(self.rename_calculation_setup)
        signals.delete_calculation_setup.connect(self.delete_calculation_setup)

    @staticmethod
    @Slot(name="createCalculationSetup")
    def new_calculation_setup() -> None:
        name, ok = QInputDialog.getText(
            None,
            "Create new calculation setup",
            "Name of new calculation setup:" + " " * 10
        )
        if ok and name:
            if name not in bw.calculation_setups.keys():
                bw.calculation_setups[name] = {'inv': [], 'ia': []}
                signals.calculation_setup_selected.emit(name)
                print("New calculation setup: {}".format(name))
            else:
                QMessageBox.information(None, "Not possible", "A calculation setup with this name already exists.")

    @staticmethod
    @Slot(str, name="deleteCalculationSetup")
    def delete_calculation_setup(name: str) -> None:
        del bw.calculation_setups[name]
        signals.set_default_calculation_setup.emit()
        print("Deleted calculation setup: {}".format(name))

    @staticmethod
    @Slot(str, name="renameCalculationSetup")
    def rename_calculation_setup(current: str) -> None:
        new_name, ok = QInputDialog.getText(
            None,
            "Rename '{}'".format(current),
            "New name of this calculation setup:" + " " * 10
        )
        if ok and new_name:
            bw.calculation_setups[new_name] = bw.calculation_setups[current].copy()
            del bw.calculation_setups[current]
            signals.calculation_setup_selected.emit(new_name)
            print("Renamed calculation setup from {} to {}".format(current, new_name))
