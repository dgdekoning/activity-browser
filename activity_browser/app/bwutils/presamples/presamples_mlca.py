# -*- coding: utf-8 -*-
import brightway2 as bw
import presamples as ps

from ..multilca import MLCA


class PresamplesMLCA(MLCA):
    """ Subclass of the `MLCA` class which adds another dimension in the form
     of scenarios / presamples arrays.

    The initial calculation will take use the first presamples array.
    After this, each call to `calculate_scenario` will update the inventory
     matrices and recalculate the results.
    """
    def __init__(self, cs_name: str, ps_name: str):
        self.resource = ps.PresampleResource.get_or_none(name=ps_name)
        if not self.resource:
            raise ValueError("Presamples resource with name '{}' not found.".format(ps_name))
        super().__init__(cs_name)
        idx = next(iter(self.lca.presamples.matrix_indexer))
        self.scenario_count = idx.ncols

    def _construct_lca(self) -> bw.LCA:
        return bw.LCA(
            demand=self.func_units_dict, method=self.methods[0],
            presamples=[self.resource.path]
        )

    def calculate_scenario(self, skip: int = None) -> None:
        """ Update the LCA matrices with the presamples arrays and redo
         the calculations.

        Setting a `skip` value allows us to avoid running all the calculations
         if we only want to look at (for example) the 1st and 5th scenarios.
        """
        steps = range(skip + 1) if skip else range(1)
        # Iterate through the alternate matrices until the correct
        # one is reached
        for _ in steps:
            self.lca.presamples.update_matrices(self.lca)
        # Recalculate everything, replacing all of the LCA data
        self._perform_calculations()
