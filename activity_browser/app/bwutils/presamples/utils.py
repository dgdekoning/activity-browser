import json
from pathlib import Path
from typing import List, Optional

import brightway2 as bw
import pandas as pd


def load_scenarios_from_file(path: str) -> pd.DataFrame:
    df = pd.read_table(path)
    return df


def save_scenarios_to_file(data: pd.DataFrame, path: str) -> None:
    data.to_csv(path_or_buf=path, sep="\t")


def find_all_package_names() -> List[str]:
    """ Peek into the presamples folder of the current project and return
     all of the package names.

    If a package name is used more than once, all following packages with
    that name will have their id returned instead.
    """
    ps_path = Path(bw.projects.dir, "presamples")
    names = set()
    for p in ps_path.glob("*/datapackage.json"):
        metadata = json.loads(p.read_text())
        name = metadata.get("name")
        exists_unique = name and name not in names
        names.add(name if exists_unique else metadata.get("id"))
    return sorted(names)


def get_package_path(name_id: str) -> Optional[Path]:
    """ Attempt to find the presamples package matching the name or id given.

    NOTE: If a non-unique name is given, it is possible the incorrect package
     is returned.
    """
    ps_path = Path(bw.projects.dir, "presamples")
    for p in ps_path.glob("*/datapackage.json"):
        metadata = json.loads(p.read_text())
        if name_id in {metadata.get("name"), metadata.get("id")}:
            return p.parent
