import os
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from gi.repository import GLib
from utils.vpn import connect_vpn, disconnect_vpn
from modules.settings import _load_config, _save_config, VPN_STATUSES

class VPNWidget(Box):
    def __init__(self):
        config = _load_config()
        self.server = config.get("vpn_server", "")
        self.status = config.get("vpn_status", "Disconnected")
        self.label = Label(label=f"VPN: {self.status}", name="vpn-widget-label", h_align="start")
        super().__init__(
            name="vpn-widget",
            orientation="h",
            children=[
                Button(
                    name="vpn-connect-button",
                    child=Label(label="Connect"),
                    on_clicked=self.connect_vpn,
                ),
                Button(
                    name="vpn-disconnect-button",
                    child=Label(label="Disconnect"),
                    on_clicked=self.disconnect_vpn,
                ),
                self.label,
            ],
        )

    def connect_vpn(self, *_):
        config = _load_config()
        server = config.get("vpn_server", "")
        username = config.get("vpn_username", "")
        password = config.get("vpn_password", "")
        success, msg = connect_vpn(server, username, password)
        if success:
            config["vpn_status"] = "Connected"
            self.label.set_text("VPN: Connected")
        else:
            config["vpn_status"] = "Disconnected"
            self.label.set_text(f"VPN: Failed ({msg})")
        _save_config(config)

    def disconnect_vpn(self, *_):
        config = _load_config()
        server = config.get("vpn_server", "")
        success, msg = disconnect_vpn(server)
        config["vpn_status"] = "Disconnected"
        if success:
            self.label.set_text("VPN: Disconnected")
        else:
            self.label.set_text(f"VPN: Failed ({msg})")
        _save_config(config)
