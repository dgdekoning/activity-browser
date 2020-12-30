# -*- coding: utf-8 -*-
import json
from pathlib import Path
import shutil
from typing import Iterator, Optional

import appdirs
import brightway2 as bw

from ... import PACKAGE_DIRECTORY


class BaseSettings(object):
    """ Base Class for handling JSON settings files.
    """
    def __init__(self, directory: str, filename: str = None):
        self.data_dir: Path = Path(directory)
        self.filename: str = filename or "default_settings.json"
        self.settings_file: Path = self.data_dir.joinpath(self.filename)
        self.settings: Optional[dict] = None
        self.initialize_settings()

    @classmethod
    def get_default_settings(cls) -> dict:
        """ Returns dictionary containing the default settings for the file
        """
        raise NotImplementedError

    def restore_default_settings(self) -> None:
        """ Undo all user settings and return to original state.
        """
        self.settings = self.get_default_settings()
        self.write_settings()

    def initialize_settings(self) -> None:
        """ Attempt to find and read the settings_file, creates a default
        if not found
        """
        if self.settings_file.is_file():
            self.load_settings()
        else:
            self.settings = self.get_default_settings()
            self.write_settings()

    def load_settings(self) -> None:
        with self.settings_file.open() as infile:
            self.settings = json.load(infile)

    def write_settings(self) -> None:
        with self.settings_file.open("w") as outfile:
            json.dump(self.settings, outfile, indent=4, sort_keys=True)


class ABSettings(BaseSettings):
    """ Interface to the json settings file. Will create a userdata directory
    via appdirs if not already present.
    """
    def __init__(self, filename: str):
        ab_dir = appdirs.AppDirs("ActivityBrowser", "ActivityBrowser")
        user_dir = Path(ab_dir.user_data_dir)
        if not user_dir.is_dir():
            user_dir.mkdir(parents=True, exist_ok=True)
        self.move_old_settings(user_dir, filename)

        super().__init__(ab_dir.user_data_dir, filename)

    @staticmethod
    def move_old_settings(directory: Path, filename: str) -> None:
        """ legacy code: This function is only required for compatibility
        with the old settings file and can be removed in a future release
        """
        file = directory.joinpath(filename)
        if not file.exists():
            old_settings = Path(PACKAGE_DIRECTORY).joinpath("ABsettings.json")
            if old_settings.exists():
                shutil.copyfile(old_settings, file)

    @classmethod
    def get_default_settings(cls) -> dict:
        """ Using methods from the commontasks file to set default settings
        """
        return {
            "custom_bw_dir": cls.get_default_directory(),
            "startup_project": cls.get_default_project_name(),
        }

    @property
    def custom_bw_dir(self) -> Path:
        """ Returns the custom brightway directory, or the default
        """
        directory = self.settings.get("custom_bw_dir", self.get_default_directory())
        return Path(directory)

    @custom_bw_dir.setter
    def custom_bw_dir(self, directory: str) -> None:
        """ Sets the custom brightway directory to `directory`
        """
        self.settings.update({"custom_bw_dir": str(directory)})

    @property
    def startup_project(self) -> str:
        """ Get the startup project from the settings, or the default
        """
        project = self.settings.get(
            "startup_project", self.get_default_project_name()
        )
        if project not in bw.projects:
            project = self.get_default_project_name()
        return project

    @startup_project.setter
    def startup_project(self, project: str) -> None:
        """ Sets the startup project to `project`
        """
        self.settings.update({"startup_project": project})

    @staticmethod
    def get_default_directory() -> str:
        """ Returns the default brightway application directory
        """
        data_dir, logs_dir = bw.projects._get_base_directories()
        return data_dir

    @staticmethod
    def get_default_project_name() -> Optional[str]:
        """ Returns the default project name.
        """
        if "default" in bw.projects:
            return "default"
        elif len(bw.projects):
            return next(iter(bw.projects)).name
        else:
            return None


class ProjectSettings(BaseSettings):
    """
    Handles user settings which are specific to projects. Created initially to handle read-only/writable database status
    Code based on ABSettings class, if more different types of settings are needed, could inherit from a base class

    structure: singleton, loaded dependent on which project is selected.
        Persisted on disc, Stored in the BW2 projects data folder for each project
        a dictionary1 of dictionaries2
        Dictionary1 keys are settings names (currently just 'read-only-databases'), values are dictionary2s
        Dictionary2 keys are database names, values are bools

    For now, decided to not include saving writable-activities to settings.
    As activities are identified by tuples, and saving them to json requires extra code
    https://stackoverflow.com/questions/15721363/preserve-python-tuples-with-json
    This is currently not worth the effort but could be returned to later

    """
    def __init__(self, filename: str):
        # on selection of a project (signal?), find the settings file for that project if it exists
        # it can be a custom location, based on ABsettings. So check that, and if not, use default?
        # once found, load the settings or just an empty dict.
        super().__init__(bw.projects.dir, filename)

        # https://github.com/LCA-ActivityBrowser/activity-browser/issues/235
        # Fix empty settings file and populate with currently active databases
        if "read-only-databases" not in self.settings:
            self.settings.update(self.process_brightway_databases())
            self.write_settings()

    @classmethod
    def get_default_settings(cls) -> dict:
        """ Return default empty settings dictionary.
        """
        return cls.process_brightway_databases()

    @staticmethod
    def process_brightway_databases() -> dict:
        """ Process brightway database list and return new settings dictionary.

        NOTE: This ignores the existing database read-only settings.
        """
        return {
            "read-only-databases": {name: True for name in bw.databases.list}
        }

    def reset_for_project_selection(self) -> None:
        """ On switching project, attempt to read the settings for the new
        project.
        """
        print("Reset project settings directory to:", bw.projects.dir)
        self.settings_file = Path(bw.projects.dir).joinpath(self.filename)
        self.initialize_settings()

    def add_db(self, db_name: str, read_only: bool = True) -> None:
        """ Store new databases and relevant settings here when created/imported
        """
        self.settings["read-only-databases"].setdefault(db_name, read_only)
        self.write_settings()

    def modify_db(self, db_name: str, read_only: bool) -> None:
        """ Update write-rules for the given database
        """
        self.settings["read-only-databases"].update({db_name: read_only})
        self.write_settings()

    def remove_db(self, db_name: str) -> None:
        """ When a database is deleted from a project, the settings are also deleted.
        """
        self.settings["read-only-databases"].pop(db_name, None)
        self.write_settings()

    def db_is_readonly(self, db_name: str) -> bool:
        """ Check if given database is read-only, defaults to yes.
        """
        return self.settings["read-only-databases"].get(db_name, True)

    def get_editable_databases(self) -> Iterator[str]:
        """ Return list of database names where read-only is false

        NOTE: discards the biosphere3 database based on name.
        """
        iterator = self.settings.get("read-only-databases", {}).items()
        return (name for name, ro in iterator if not ro and name != "biosphere3")


# Initialize settings classes
ab_settings = ABSettings("ABsettings.json")
project_settings = ProjectSettings("AB_project_settings.json")
