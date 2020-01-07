# -*- coding: utf-8 -*-
import os

import brightway2 as bw
from bw2data.project import ProjectDataset, SubstitutableDatabase
from PySide2.QtCore import Slot

from ..bwutils import AB_metadata
from ..settings import ab_settings
from ..signals import signals
from .base import BaseController
from .projects import ProjectController


class MetadataController(BaseController):
    def connect_signals(self):
        signals.project_selected.connect(self.reset_metadata)
        signals.metadata_changed.connect(self.update_metadata)
        signals.edit_activity.connect(self.print_convenience_information)

    @staticmethod
    @Slot(name="triggerMetadataReset")
    def reset_metadata() -> None:
        AB_metadata.reset_metadata()

    @staticmethod
    @Slot(tuple, name="updateMetadataActivity")
    def update_metadata(key: tuple) -> None:
        AB_metadata.update_metadata(key)

    @staticmethod
    @Slot(str, name="printDatabaseInformation")
    def print_convenience_information(db_name: str) -> None:
        AB_metadata.print_convenience_information(db_name)


class SettingController(BaseController):
    def __init__(self, parent=None):
        super().__init__(parent)
        if ab_settings.settings:
            print("Loading user settings:")
            self.switch_brightway2_dir_path(dirpath=ab_settings.custom_bw_dir)
            ProjectController.change_project(ab_settings.startup_project)

    def connect_signals(self):
        signals.switch_bw2_dir_path.connect(self.switch_brightway2_dir_path)

    @staticmethod
    @Slot(str, name="switchBrightwayDirectory")
    def switch_brightway2_dir_path(dirpath: str) -> None:
        if dirpath == bw.projects._base_data_dir:
            return  # dirpath is already loaded
        try:
            assert os.path.isdir(dirpath)
            bw.projects._base_data_dir = dirpath
            bw.projects._base_logs_dir = os.path.join(dirpath, "logs")
            # create folder if it does not yet exist
            if not os.path.isdir(bw.projects._base_logs_dir):
                os.mkdir(bw.projects._base_logs_dir)
            # load new brightway directory
            bw.projects.db = SubstitutableDatabase(
                os.path.join(bw.projects._base_data_dir, "projects.db"),
                [ProjectDataset]
            )
            print('Loaded brightway2 data directory: {}'.format(bw.projects._base_data_dir))
            ProjectController.change_project(ab_settings.startup_project, reload=True)
            signals.databases_changed.emit()
        except AssertionError:
            print('Could not access BW_DIR as specified in settings.py')
