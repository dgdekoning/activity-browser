# -*- coding: utf-8 -*-
from typing import Union
import uuid

import brightway2 as bw
from bw2data.backends.peewee import ExchangeDataset
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QInputDialog, QMessageBox

from ..bwutils import AB_metadata, commontasks as bc
from ..settings import project_settings
from ..signals import signals
from .base import BaseController


class ActivityController(BaseController):
    def connect_signals(self):
        signals.duplicate_activity.connect(self.duplicate_activity)
        signals.activity_modified.connect(self.modify_activity)
        signals.new_activity.connect(self.new_activity)
        signals.delete_activity.connect(self.delete_activity)
        signals.duplicate_activity_to_db.connect(self.copy_activity)
        signals.show_duplicate_to_db_interface.connect(self.duplicate_activity_to_db)

    @staticmethod
    @Slot(str, name="createActivity")
    def new_activity(database_name: str) -> None:
        # TODO: let user define product
        name, ok = QInputDialog.getText(
            None,
            "Create new technosphere activity",
            "Please specify an activity name:" + " " * 10,
        )
        if ok and name:
            new_act = bw.Database(database_name).new_activity(
                code=uuid.uuid4().hex,
                name=name,
                unit="unit",
                type="process",
            )
            new_act.save()
            production_exchange = new_act.new_exchange(amount=1, type="production")
            production_exchange.input = new_act
            production_exchange.save()
            signals.open_activity_tab.emit(new_act.key)
            signals.metadata_changed.emit(new_act.key)
            signals.database_changed.emit(database_name)
            signals.databases_changed.emit()

    @staticmethod
    @Slot(tuple, name="removeActivity")
    def delete_activity(key: tuple) -> None:
        act = bw.get_activity(key)
        nu = len(act.upstream())
        if nu:
            text = "activities consume" if nu > 1 else "activity consumes"
            QMessageBox.information(
                None,
                "Not possible.",
                """Can't delete {}. {} upstream {} its reference product.
                Upstream exchanges must be modified or deleted.""".format(act, nu, text)
            )
        else:
            act.delete()
            signals.metadata_changed.emit(act.key)
            signals.database_changed.emit(act['database'])
            signals.databases_changed.emit()
            signals.calculation_setup_changed.emit()

    @staticmethod
    def generate_copy_code(key: tuple) -> str:
        db, code = key
        metadata = AB_metadata.get_database_metadata(db)
        if '_copy' in code:
            code = code.split('_copy')[0]
        copies = metadata["key"].apply(
            lambda x: x[1] if code in x[1] and "_copy" in x[1] else None
        ).dropna().to_list() if not metadata.empty else []
        if not copies:
            return "{}_copy1".format(code)
        n = max((int(c.split('_copy')[1]) for c in copies))
        return "{}_copy{}".format(code, n+1)

    @staticmethod
    @Slot(tuple, name="duplicateActivity")
    def duplicate_activity(key: tuple) -> None:
        """duplicates the selected activity in the same db, with a new BW code
        for creating a copy in a different db, use copy_to_db"""
        # todo: add "copy of" (or similar) to name of activity for easy identification in new db
        # todo: some interface feedback so user knows the copy has succeeded
        act = bw.get_activity(key)
        new_code = ActivityController.generate_copy_code(key)
        new_act = act.copy(new_code)
        # Update production exchanges
        for exc in new_act.production():
            if exc.input.key == key:
                exc.input = new_act
                exc.save()
        # Update 'products'
        for product in new_act.get('products', []):
            if product.get('input') == key:
                product['input'] = new_act.key
        new_act.save()
        signals.metadata_changed.emit(new_act.key)
        signals.database_changed.emit(act['database'])
        signals.databases_changed.emit()
        signals.open_activity_tab.emit(new_act.key)

    @staticmethod
    @Slot(tuple, name="copyActivity")
    def copy_activity(key: tuple) -> None:
        origin_db = key[0]
        activity = bw.get_activity(key)

        available_target_dbs = list(project_settings.get_editable_databases())
        if origin_db in available_target_dbs:
            available_target_dbs.remove(origin_db)
        if not available_target_dbs:
            QMessageBox.information(
                None, "No target database",
                "No valid target databases available. Create a new database or set one to writable (not read-only)."
            )
            return
        target_db, ok = QInputDialog.getItem(
            None, "Copy activity to database", "Target database:",
            available_target_dbs, 0, False
        )
        if ok:
            ActivityController.duplicate_activity_to_db(target_db, activity)

    @staticmethod
    def duplicate_activity_to_db(target_db: str, activity) -> None:
        new_code = ActivityController.generate_copy_code((target_db, activity['code']))
        new_act_key = (target_db, new_code)
        activity.copy(code=new_code, database=target_db)
        # only process database immediately if small
        if len(bw.Database(target_db)) < 50:
            bw.databases.clean()
        signals.metadata_changed.emit(new_act_key)
        signals.database_changed.emit(target_db)
        signals.open_activity_tab.emit(new_act_key)
        signals.databases_changed.emit()

    @staticmethod
    @Slot(tuple, str, object, name="editActivity")
    def modify_activity(key: tuple, field: str, value: Union[str, float]) -> None:
        activity = bw.get_activity(key)
        activity[field] = value
        activity.save()
        signals.metadata_changed.emit(key)
        signals.database_changed.emit(key[0])


class ExchangeController(BaseController):
    def connect_signals(self):
        signals.exchanges_deleted.connect(self.delete_exchanges)
        signals.exchanges_add.connect(self.add_exchanges)
        signals.exchange_modified.connect(self.modify_exchange)

    @staticmethod
    @Slot(list, tuple, name="addExchangesToActivity")
    def add_exchanges(from_keys: list, to_key: tuple) -> None:
        activity = bw.get_activity(to_key)
        for key in from_keys:
            technosphere_db = bc.is_technosphere_db(key[0])
            exc = activity.new_exchange(input=key, amount=1)
            if key == to_key:
                exc['type'] = 'production'
            elif technosphere_db is True:
                exc['type'] = 'technosphere'
            elif technosphere_db is False:
                exc['type'] = 'biosphere'
            else:
                exc['type'] = 'unknown'
            exc.save()
        signals.metadata_changed.emit(to_key)
        signals.database_changed.emit(to_key[0])

    @staticmethod
    @Slot(list, name="deleteMultipleExchanges")
    def delete_exchanges(exchanges: list):
        db_changed = set()
        for exc in exchanges:
            db_changed.add(exc['output'][0])
            exc._document.delete_instance()
        for db in db_changed:
            # signals.metadata_changed.emit(to_key)
            signals.database_changed.emit(db)

    @staticmethod
    @Slot(object, str, object, name="modifyExchangeDataset")
    def modify_exchange(exchange: ExchangeDataset, field: str, value: Union[str, float]):
        # The formula field needs special handling.
        if field == "formula":
            if field in exchange and (value == "" or value is None):
                # Remove formula entirely.
                del exchange[field]
                if "original_amount" in exchange:
                    # Restore the original amount, if possible
                    exchange["amount"] = exchange["original_amount"]
                    del exchange["original_amount"]
            if value:
                # At least set the formula, possibly also store the amount
                if field not in exchange:
                    exchange["original_amount"] = exchange["amount"]
                exchange[field] = value
        else:
            exchange[field] = value
        exchange.save()
        if field == "formula":
            # If a formula was set, removed or changed, recalculate exchanges
            signals.exchange_formula_changed.emit(exchange["output"])
        signals.database_changed.emit(exchange['output'][0])
