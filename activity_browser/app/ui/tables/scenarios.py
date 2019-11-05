# -*- coding: utf-8 -*-
import itertools

from bw2data.parameters import ActivityParameter, DatabaseParameter, ProjectParameter
import pandas as pd

from ...bwutils.presamples import ppm
from .delegates import FloatDelegate, ViewOnlyDelegate
from .views import ABDataFrameEdit, dataframe_sync


class ScenarioTable(ABDataFrameEdit):
    """ Constructs an infinitely (horizontally) expandable table that is
    used to set specific amount for user-defined parameters.

    The two required columns in the dataframe for the table are 'Name',
    and 'Type'. all other columns are seen as scenarios containing N floats,
    where N is the number of rows found in the Name column.

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(FloatDelegate(self))
        self.setItemDelegateForColumn(0, ViewOnlyDelegate(self))

    @dataframe_sync
    def sync(self, df: pd.DataFrame = None) -> None:
        if df is not None:
            required = {"Name", "Group"}
            if not required.issubset(df.columns):
                raise ValueError(
                    "The given dataframe does not contain required columns: {}".format(required.difference(df.columns))
                )
            assert df.columns.get_loc("Group") == 1
            self.dataframe = df.set_index("Name")
            return
        data = itertools.chain(
            ppm.process_project_parameters(ProjectParameter.select()),
            ppm.process_database_parameters(DatabaseParameter.select()),
            ppm.process_activity_parameters(ActivityParameter.select())
        )
        self.dataframe = pd.DataFrame(data, columns=["Name", "Group", "default"])
        self.dataframe.set_index("Name", inplace=True)
