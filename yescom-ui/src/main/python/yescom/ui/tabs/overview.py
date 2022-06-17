#!/usr/bin/env python3

import datetime
import math
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from ..widgets.players import OnlinePlayersTree

from ez.pogdog.yescom.api import Logging

logger = Logging.getLogger("yescom.ui.tabs.overview")


class OverviewTab(QWidget):
    """
    Provides an overview of the server's information.
    """

    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent)

        self.main_window = parent

        self._last_update = time.time()

        self._setup_tab()

        self.main_window.tick.connect(self._on_tick)

    def __repr__(self) -> str:
        return "<OverviewTab() at %x>" % id(self)

    def _setup_tab(self) -> None:
        logger.finer("Setting up overview tab...")

        main_layout = QHBoxLayout(self)

        info_layout = QVBoxLayout()

        self.address_label = QLabel(self)
        self.address_label.setText("Address: (no server)")
        self.address_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.address_label)

        self.tickrate_label = QLabel(self)
        self.tickrate_label.setText("Tickrate: 0.0tps")
        self.tickrate_label.setToolTip("The current server tickrate.")
        # self.tickrate_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.tickrate_label)

        self.ping_label = QLabel(self)
        self.ping_label.setText("Ping: 0ms")
        self.ping_label.setToolTip("The average ping across all connected accounts.")
        # self.ping_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.ping_label)

        self.tslp_label = QLabel(self)
        self.tslp_label.setText("TSLP: 0ms")
        self.tslp_label.setToolTip("The minimum time since last packet across all connected accounts.")
        # self.tslp_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.tslp_label)

        self.uptime_label = QLabel(self)
        self.uptime_label.setText("Uptime: 00:00:00")
        self.uptime_label.setToolTip("How long we've been connected to this server for.")
        # self.uptime_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.uptime_label)

        self.render_dist_label = QLabel(self)
        self.render_dist_label.setText("Render distance: 0 / 0 (0 chunks)")
        self.render_dist_label.setToolTip("Estimated server render distance.")
        self.render_dist_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.render_dist_label)

        self.queryrate_label = QLabel(self)
        self.queryrate_label.setText("Queryrate: 0.0qps")
        self.queryrate_label.setToolTip("The current rate of queries being sent to the server.")
        # self.queryrate_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        info_layout.addWidget(self.queryrate_label)

        info_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # TODO: More information (trackers, etc)
        # TODO: Current (in game) time?

        main_layout.addLayout(info_layout)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        online_layout = QVBoxLayout()

        online_players_list = OnlinePlayersTree(self)
        online_layout.addWidget(online_players_list)

        buttons_layout = QHBoxLayout()

        self.remove_button = QPushButton(self)
        self.remove_button.setEnabled(self.main_window.current_server is not None)
        self.remove_button.setText("Remove server")
        buttons_layout.addWidget(self.remove_button)

        self.disconnect_all_button = QPushButton(self)
        self.disconnect_all_button.setEnabled(
            self.main_window.current_server is not None and self.main_window.current_server.isConnected()
        )
        self.disconnect_all_button.setText("Disconnect all")
        self.disconnect_all_button.setToolTip("Disconnects all currently online players and disables auto reconnecting.")
        self.disconnect_all_button.clicked.connect(lambda checked: self.main_window.disconnect_all())
        buttons_layout.addWidget(self.disconnect_all_button)

        online_layout.addLayout(buttons_layout)
        main_layout.addLayout(online_layout)

        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 10)

    # ------------------------------ Events ------------------------------ #

    def _on_tick(self) -> None:
        if time.time() - self._last_update < .1:  # Don't want it to update too fast
            return
        self._last_update = time.time()
        current = self.main_window.current_server

        address = "(no server)"
        tickrate = 0.0
        ping = 0.0
        tslp = "0"
        uptime = "0:00:00"
        render_distance = 0
        queryrate = 0.0

        if current is not None:
            address = "%s:%i" % (current.hostname, current.port)
            if current.isConnected():
                tickrate = current.getTPS()
                ping = current.getPing()
                tslp = max(1, current.getTSLP())
                if tslp > current.HIGH_TSLP.value:
                    tslp = str(tslp)
                else:
                    tslp = "<%i" % (math.ceil(tslp / 50) * 50)
                uptime = str(datetime.timedelta(seconds=current.getConnectionTime()))
                queryrate = current.getQPS()

            render_distance = current.getRenderDistance()

        self.address_label.setText("Address: %s" % address)
        self.tickrate_label.setText("Tickrate: %.1ftps" % tickrate)
        self.ping_label.setText("Ping: %.1fms" % ping)
        self.tslp_label.setText("TSLP: %sms" % tslp)
        self.uptime_label.setText("Uptime: %s" % uptime)
        self.render_dist_label.setText("Render distance: %i / %i (%i chunks)" % (
            max(0, (render_distance - 1) // 2), render_distance, render_distance ** 2,
        ))
        self.queryrate_label.setText("Queryrate: %.1fqps" % queryrate)

        self.disconnect_all_button.setEnabled(current is not None and current.isConnected())


from ..main import MainWindow
