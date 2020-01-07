# -*- coding: utf-8 -*-
import brightway2 as bw
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QInputDialog, QMessageBox, QWidget

from ..ui.widgets import CopyDatabaseDialog
from ..ui.wizards.db_import_wizard import DatabaseImportWizard, DefaultBiosphereDialog
from ..settings import project_settings
from ..signals import signals
from .base import BaseController
from .projects import ProjectController


class DatabaseController(BaseController):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.biosphere_importer = None
        self.copy_progress = None
        # Create widget for temporary wizard to attach to
        self.db_wizard = QWidget(parent)

    def connect_signals(self):
        signals.add_database.connect(self.add_database)
        signals.delete_database.connect(self.delete_database)
        signals.copy_database.connect(self.copy_database)
        signals.install_default_data.connect(self.install_default_data)
        signals.import_database.connect(self.import_database_wizard)

    @Slot(name="addBiosphereData")
    def install_default_data(self) -> None:
        self.biosphere_importer = DefaultBiosphereDialog()
        project_settings.add_db("biosphere3")

    @staticmethod
    @Slot(name="addBrightwayDatabase")
    def add_database() -> None:
        name, ok = QInputDialog.getText(
            None,
            "Create new database",
            "Name of new database:" + " " * 25
        )
        if ok and name:
            if name not in bw.databases:
                bw.Database(name).register()
                project_settings.add_db(name)
                signals.databases_changed.emit()
                signals.database_selected.emit(name)
            else:
                QMessageBox.information(None, "Not possible", "A database with this name already exists.")

    @Slot(str, name="copyBrightwayDatabase")
    def copy_database(self, name: str) -> None:
        new_name, ok = QInputDialog.getText(
            None,
            "Copy {}".format(name),
            "Name of new database:" + " " * 25)
        if ok and new_name:
            try:
                # Attaching the created wizard to the class avoids the copying
                # thread being prematurely destroyed.
                self.copy_progress = CopyDatabaseDialog()
                self.copy_progress.begin_copy(name, new_name)
                project_settings.add_db(new_name)
            except ValueError as e:
                QMessageBox.information(None, "Not possible", str(e))

    @Slot(str, name="deleteBrightwayDatabase")
    def delete_database(self, name: str) -> None:
        ok = QMessageBox.question(
            None,
            "Delete database?",
            "Are you sure you want to delete database '{}'? It has {} activity datasets".format(
                name, len(bw.Database(name)))
        )
        if ok == QMessageBox.Yes:
            project_settings.remove_db(name)
            del bw.databases[name]
            ProjectController.change_project(bw.projects.current, reload=True)

    @Slot(name="importDatabaseWizard")
    def import_database_wizard(self) -> None:
        """ Create a database import wizard, if it already exists, set the
        previous one to delete and recreate it.
        """
        _ = DatabaseImportWizard(self.db_wizard)
