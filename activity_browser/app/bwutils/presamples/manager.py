# -*- coding: utf-8 -*-
import itertools
from typing import Iterable, List, Optional, Tuple

from bw2data.parameters import (ActivityParameter, DatabaseParameter,
                                ProjectParameter, get_new_symbols)
from bw2parameters import ParameterSet
from bw2parameters.errors import MissingName


class PresamplesParameterManager(object):
    """ Used to recalculate brightway parameters without editing the database

    The methods `process_project_parameters`, `process_database_parameters`,
    `process_activity_parameters` and `replace_amounts` are specifically
    used to convert the brightway parameters to simple tuples with only
    the relevant information needed for recalculation.

    The `param_values` property and `get_altered_values` method are used to
    retrieve either the whole list of prepared parameter values or a
    subset of it selected by group.

    The `recalculate_*` methods are used to perform the actual calculations
    and will read out the relevant parameters from the database. Each of the
    methods will optionally return a dictionary of the parameter names
    with their recalculated amounts.

    """
    __slots__ = 'parameter_values'

    def __init__(self):
        self.parameter_values: List[tuple] = []

    @property
    def param_values(self) -> Iterable[tuple]:
        return self.parameter_values

    @param_values.setter
    def param_values(self, values: Iterable[tuple]) -> None:
        if isinstance(values, list):
            self.parameter_values = values
        else:
            self.parameter_values = list(values)

    def get_altered_values(self, group: str) -> dict:
        """ Parses the `param_values` to extract the relevant subset of
        changed parameters.
        """
        return {k: v for k, g, v in self.param_values if g == group}

    @staticmethod
    def process_project_parameters(parameters: Iterable[ProjectParameter]) -> Iterable[tuple]:
        """ Converts ActivityParameters into tuples of the relevant values.
        """
        return ((p.name, "project", p.amount) for p in parameters)

    @staticmethod
    def process_database_parameters(parameters: Iterable[DatabaseParameter]) -> Iterable[tuple]:
        """ Converts ActivityParameters into tuples of the relevant values.
        """
        return ((p.name, p.database, p.amount) for p in parameters)

    @staticmethod
    def process_activity_parameters(parameters: Iterable[ActivityParameter]) -> Iterable[tuple]:
        """ Converts ActivityParameters into tuples of the relevant values.
        """
        return ((p.name, p.group, p.amount) for p in parameters)

    @staticmethod
    def replace_amounts(parameters: Iterable[tuple], amounts: Iterable[float]) -> Iterable[tuple]:
        """ Specifically does not check for the length of both values to
        allow the use of generators.
        """
        return (
            (n, g, amount) for ((n, g, _), amount) in zip(parameters, amounts)
        )

    @classmethod
    def construct(cls, scenario_values: Iterable[float] = None) -> 'PresamplesParameterManager':
        """ Construct an instance of itself and populate it with either the
        default parameter values or altered values.

        If altered values are given, demands that the amount of values
        is equal to the amount of parameters.
        """
        param_list = list(itertools.chain(
            cls.process_project_parameters(ProjectParameter.select()),
            cls.process_database_parameters(DatabaseParameter.select()),
            cls.process_activity_parameters(ActivityParameter.select())
        ))

        ppm = cls()
        if scenario_values:
            scenario = list(scenario_values)
            assert len(param_list) == len(scenario)
            ppm.param_values = cls.replace_amounts(param_list, scenario)
        else:
            ppm.param_values = param_list
        return ppm

    @staticmethod
    def _static(data: dict, needed: set) -> dict:
        """ Similar to the `static` method for each Parameter class where the
        ``needed`` variable is a set of the keys actually needed from ``data``.
        """
        return {k: data[k] for k in data.keys() & needed}

    @staticmethod
    def _prune_result_data(data: dict) -> dict:
        """ Takes a str->dict dictionary and extracts the amount field from
        the dictionary.
        """
        return {k: v.get("amount") for k, v in data.items()}

    def recalculate_project_parameters(self) -> Optional[dict]:
        new_values = self.get_altered_values("project")

        data = ProjectParameter.load()
        if not data:
            return

        for name, amount in new_values.items():
            data[name]["amount"] = amount

        ParameterSet(data).evaluate_and_set_amount_field()
        return self._prune_result_data(data)

    def recalculate_database_parameters(self, database: str, global_params: dict = None) -> Optional[dict]:
        new_values = self.get_altered_values(database)
        if global_params is None:
            global_params = {}

        data = DatabaseParameter.load(database)
        if not data:
            return

        for name, amount in new_values.items():
            data[name]["amount"] = amount

        new_symbols = get_new_symbols(data.values(), set(data))
        missing = new_symbols.difference(global_params)
        if missing:
            raise MissingName("The following variables aren't defined:\n{}".format("|".join(missing)))

        glo = self._static(global_params, needed=new_symbols) if new_symbols else None

        ParameterSet(data, glo).evaluate_and_set_amount_field()
        return self._prune_result_data(data)

    def recalculate_activity_parameters(self, group: str, global_params: dict = None) -> Optional[dict]:
        new_values = self.get_altered_values(group)
        if global_params is None:
            global_params = {}

        data = ActivityParameter.load(group)
        if not data:
            return

        for name, amount in new_values.items():
            data[name]["amount"] = amount

        new_symbols = get_new_symbols(data.values(), set(data))
        missing = new_symbols.difference(global_params)
        if missing:
            raise MissingName("The following variables aren't defined:\n{}".format("|".join(missing)))

        glo = self._static(global_params, needed=new_symbols) if new_symbols else None

        ParameterSet(data, glo).evaluate_and_set_amount_field()
        return self._prune_result_data(data)
