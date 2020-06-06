# Test
from . import config
from typing import List
from aqt.qt import *
from anki.httpclient import HttpClient
import aqt
from aqt import addons

def prompt_to_update(
    parent: QWidget,
    mgr: addons.AddonManager,
    client: HttpClient,
    ids: List[int],
    on_done: Callable[[List[addons.DownloadLogEntry]], None],
) -> None:
    def _iter_listwidget(l):
        for i in range(l.count()):
            yield l.item(i)

    def _iter_checked_listwidget(l):
        toWrite = config.getUserOption()
        for item in _iter_listwidget(l):
            checked = item.checkState() == Qt.Checked
            toWrite["_addons_info"][item.text()] = {"update": checked}
            config.writeConfig()
            if checked:
                yield item.text()

    def _select_addons_to_update(ids):
        messagebox = QMessageBox(
            QMessageBox.Question,
            "Addon update",
            "The following add-ons have updates available. Install them now?",
            QMessageBox.Cancel | QMessageBox.Ok
        )
        selected_ids = QListWidget()
        messagebox.layout().addWidget(selected_ids, 1, 2)
        selected_ids.addItems([str(i) for i in ids])
        for item in _iter_listwidget(selected_ids):
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            isChecked = config.getUserOption(["_addons_info", item.text(), "update"], default=False)
            item.setCheckState(Qt.Checked if isChecked else Qt.Unchecked)

        if messagebox.exec() == QMessageBox.Ok:
            return list(_iter_checked_listwidget(selected_ids))
        else:
            return []

    addons.download_addons(parent, mgr, _select_addons_to_update(ids), on_done, client)

aqt.addons.prompt_to_update = prompt_to_update
