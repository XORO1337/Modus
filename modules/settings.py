import json
import os
from utils.vpn import connect_vpn, disconnect_vpn

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

from fabric.utils.helpers import get_relative_path

CONFIG_FILE = get_relative_path("../config/assets/config.json")

VPN_STATUSES = ["Disconnected", "Connecting", "Connected"]

CATEGORIES = [
    ("General", "🔧"),
    ("Appearance", "🎨"),
    ("Wallpaper", "🖼"),
    ("Panel", "📊"),
    ("Dock", "🚢"),
    ("Notifications", "🔔"),
    ("VPN", "🔒"),
]

DOCK_POSITIONS = ["Bottom", "Top", "Left", "Right"]
CLOCK_FORMATS = ["12-hour", "24-hour"]
_DESCRIPTION_MAX_WIDTH = 55

_DEFAULTS = {
    "terminal_command": "kitty -e",
    "window_switcher_items_per_row": 10,
    "hide_special_workspace": True,
    "wallpapers_dir": "~/Pictures/Wallpapers/",
    "matugen_enabled": True,
    "panel_clock_format": "12-hour",
    "dock_position": "Bottom",
    "dock_enabled": True,
    "dock_auto_hide": True,
    "dock_always_occluded": False,
    "dock_icon_size": 52,
    "dock_hide_special_workspace_apps": True,
    "dock_preview_apps": False,
    "notification_timeout": "5s",
    "notification_ignored_apps_history": ["Hyprshot"],
    "notification_limited_apps_history": ["Spotify"],
}


def _load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Settings: failed to load config: {e}")
    return {}


def _save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Settings: failed to save config: {e}")


class Settings(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Settings")
        self.set_default_size(820, 580)
        self.set_size_request(820, 580)
        self.set_resizable(False)
        self.set_name("settings-window")
        self.set_visible(False)

        # --- Outer vertical box: title bar + content ---
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_name("settings-outer")

        # --- macOS-style title bar ---
        title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_bar.set_name("settings-titlebar")

        # Traffic-light close button
        close_btn = Gtk.Button()
        close_btn.set_name("settings-titlebar-close")
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", lambda *_: self.hide())
        title_bar.pack_start(close_btn, False, False, 12)

        # Reload config icon button
        reload_btn = Gtk.Button()
        reload_btn.set_name("settings-titlebar-reload")
        reload_btn.set_relief(Gtk.ReliefStyle.NONE)
        reload_btn.set_tooltip_text("Reload config")
        reload_icon = Gtk.Label(label="⟳")  # Unicode reload icon
        reload_icon.set_name("settings-titlebar-reload-icon")
        reload_btn.add(reload_icon)
        reload_btn.connect("clicked", self._on_reload_config)
        title_bar.pack_start(reload_btn, False, False, 8)

        title_lbl = Gtk.Label(label="System Settings")
        title_lbl.set_name("settings-titlebar-label")
        title_lbl.set_hexpand(True)
        title_bar.pack_start(title_lbl, True, True, 0)

        # Spacer to balance the close button and reload button
        spacer = Gtk.Box()
        spacer.set_size_request(32, 1)
        title_bar.pack_end(spacer, False, False, 12)
    def _on_reload_config(self, button):
        config = _load_config()
        # Update all widgets with the latest config values
        # General
        self._widgets["terminal_command"].set_text(config.get("terminal_command", _DEFAULTS["terminal_command"]))
        self._widgets["window_switcher_items_per_row"].set_value(config.get("window_switcher_items_per_row", _DEFAULTS["window_switcher_items_per_row"]))
        self._widgets["hide_special_workspace"].set_active(config.get("hide_special_workspace", _DEFAULTS["hide_special_workspace"]))
        # Appearance
        self._widgets["matugen_enabled"].set_active(config.get("matugen_enabled", _DEFAULTS["matugen_enabled"]))
        # Wallpaper
        self._widgets["wallpapers_dir"].set_text(config.get("wallpapers_dir", _DEFAULTS["wallpapers_dir"]))
        # Panel
        fmt = config.get("panel_clock_format", _DEFAULTS["panel_clock_format"])
        self._widgets["panel_clock_format"].set_active(CLOCK_FORMATS.index(fmt) if fmt in CLOCK_FORMATS else 0)
        # Dock
        pos = config.get("dock_position", _DEFAULTS["dock_position"])
        self._widgets["dock_position"].set_active(DOCK_POSITIONS.index(pos) if pos in DOCK_POSITIONS else 0)
        self._widgets["dock_enabled"].set_active(config.get("dock_enabled", _DEFAULTS["dock_enabled"]))
        self._widgets["dock_auto_hide"].set_active(config.get("dock_auto_hide", _DEFAULTS["dock_auto_hide"]))
        self._widgets["dock_always_occluded"].set_active(config.get("dock_always_occluded", _DEFAULTS["dock_always_occluded"]))
        self._widgets["dock_icon_size"].set_value(config.get("dock_icon_size", _DEFAULTS["dock_icon_size"]))
        self._widgets["dock_preview_apps"].set_active(config.get("dock_preview_apps", _DEFAULTS["dock_preview_apps"]))
        self._widgets["dock_hide_special_workspace_apps"].set_active(config.get("dock_hide_special_workspace_apps", _DEFAULTS["dock_hide_special_workspace_apps"]))
        # Notifications
        self._widgets["notification_timeout"].set_text(config.get("notification_timeout", _DEFAULTS["notification_timeout"]))
        ignored_val = config.get("notification_ignored_apps_history", _DEFAULTS["notification_ignored_apps_history"])
        self._widgets["notification_ignored_apps_history"].set_text(", ".join(ignored_val) if ignored_val else "")
        limited_val = config.get("notification_limited_apps_history", _DEFAULTS["notification_limited_apps_history"])
        self._widgets["notification_limited_apps_history"].set_text(", ".join(limited_val) if limited_val else "")
        self._status_label.set_text("Config reloaded ✓")

        outer.pack_start(title_bar, False, False, 0)

        title_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        title_sep.set_name("settings-title-separator")
        outer.pack_start(title_sep, False, False, 0)

        # --- root layout: sidebar | content ---
        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        root.set_name("settings-root")

        # --- Sidebar ---
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar.set_name("settings-sidebar")

        # Search entry
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_name("settings-search")
        self._search_entry.set_placeholder_text("Search…")
        self._search_entry.set_margin_top(12)
        self._search_entry.set_margin_bottom(8)
        self._search_entry.set_margin_start(10)
        self._search_entry.set_margin_end(10)
        self._search_entry.connect("search-changed", self._on_search_changed)
        sidebar.pack_start(self._search_entry, False, False, 0)

        # Nav buttons container (scrollable for many categories)
        self._nav_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._nav_box.set_margin_start(10)
        self._nav_box.set_margin_end(10)
        self._nav_box.set_margin_bottom(10)
        sidebar.pack_start(self._nav_box, True, True, 0)

        # --- Content stack ---
        self._stack = Gtk.Stack()
        self._stack.set_name("settings-stack")
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.set_transition_duration(150)
        self._stack.set_hexpand(True)
        self._stack.set_vexpand(True)

        # --- Sidebar buttons ---
        self._sidebar_buttons = []
        for name, icon in CATEGORIES:
            btn = Gtk.Button()
            btn.set_name("settings-nav-button")
            btn.set_relief(Gtk.ReliefStyle.NONE)
            inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            icon_label = Gtk.Label(label=icon)
            icon_label.set_name("settings-nav-icon")
            text_label = Gtk.Label(label=name)
            text_label.set_name("settings-nav-label")
            text_label.set_halign(Gtk.Align.START)
            inner.pack_start(icon_label, False, False, 0)
            inner.pack_start(text_label, True, True, 0)
            btn.add(inner)
            btn.connect("clicked", self._on_nav_clicked, name)
            self._nav_box.pack_start(btn, False, False, 0)
            self._sidebar_buttons.append((name, btn))

        # Build content pages
        config = _load_config()
        self._widgets = {}

        self._stack.add_named(self._build_general_page(config), "General")
        self._stack.add_named(self._build_appearance_page(config), "Appearance")
        self._stack.add_named(self._build_wallpaper_page(config), "Wallpaper")
        self._stack.add_named(self._build_panel_page(config), "Panel")
        self._stack.add_named(self._build_dock_page(config), "Dock")
        self._stack.add_named(self._build_notifications_page(config), "Notifications")
        self._stack.add_named(self._build_vpn_page(config), "VPN")
    def _build_vpn_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("VPN Settings"), False, False, 0)

        vpn_server_entry = Gtk.Entry()
        vpn_server_entry.set_name("settings-entry")
        vpn_server_entry.set_text(config.get("vpn_server", ""))
        vpn_server_entry.set_width_chars(32)
        self._widgets["vpn_server"] = vpn_server_entry
        box.pack_start(
            self._row(
                "VPN Server",
                vpn_server_entry,
                "Enter the VPN server address (e.g. vpn.example.com)",
            ),
            False, False, 0,
        )

        vpn_username_entry = Gtk.Entry()
        vpn_username_entry.set_name("settings-entry")
        vpn_username_entry.set_text(config.get("vpn_username", ""))
        vpn_username_entry.set_width_chars(24)
        self._widgets["vpn_username"] = vpn_username_entry
        box.pack_start(
            self._row(
                "Username",
                vpn_username_entry,
                "VPN login username",
            ),
            False, False, 0,
        )

        vpn_password_entry = Gtk.Entry()
        vpn_password_entry.set_name("settings-entry")
        vpn_password_entry.set_visibility(False)
        vpn_password_entry.set_text(config.get("vpn_password", ""))
        vpn_password_entry.set_width_chars(24)
        self._widgets["vpn_password"] = vpn_password_entry
        box.pack_start(
            self._row(
                "Password",
                vpn_password_entry,
                "VPN login password",
            ),
            False, False, 0,
        )

        vpn_status_combo = Gtk.ComboBoxText()
        vpn_status_combo.set_name("settings-combo")
        for status in VPN_STATUSES:
            vpn_status_combo.append_text(status)
        current_status = config.get("vpn_status", "Disconnected")
        vpn_status_combo.set_active(
            VPN_STATUSES.index(current_status) if current_status in VPN_STATUSES else 0
        )
        self._widgets["vpn_status"] = vpn_status_combo
        box.pack_start(
            self._row(
                "VPN Status",
                vpn_status_combo,
                "Current VPN connection status",
            ),
            False, False, 0,
        )

        connect_btn = Gtk.Button(label="Connect")
        connect_btn.set_name("settings-vpn-connect-button")
        connect_btn.connect("clicked", self._on_vpn_connect)
        box.pack_start(connect_btn, False, False, 8)

        disconnect_btn = Gtk.Button(label="Disconnect")
        disconnect_btn.set_name("settings-vpn-disconnect-button")
        disconnect_btn.connect("clicked", self._on_vpn_disconnect)
        box.pack_start(disconnect_btn, False, False, 8)

        return self._make_scrolled_page(box)

    def _on_vpn_connect(self, button):
        config = _load_config()
        server = self._widgets["vpn_server"].get_text().strip()
        username = self._widgets["vpn_username"].get_text().strip()
        password = self._widgets["vpn_password"].get_text().strip()
        config["vpn_server"] = server
        config["vpn_username"] = username
        config["vpn_password"] = password
        config["vpn_status"] = "Connecting"
        _save_config(config)
        self._widgets["vpn_status"].set_active(VPN_STATUSES.index("Connecting"))
        self._status_label.set_text("Connecting to VPN…")
        success, msg = connect_vpn(server, username, password)
        if success:
            config["vpn_status"] = "Connected"
            self._widgets["vpn_status"].set_active(VPN_STATUSES.index("Connected"))
            self._status_label.set_text("VPN connected ✓")
        else:
            config["vpn_status"] = "Disconnected"
            self._widgets["vpn_status"].set_active(VPN_STATUSES.index("Disconnected"))
            self._status_label.set_text(f"VPN connect failed: {msg}")
        _save_config(config)

    def _on_vpn_disconnect(self, button):
        config = _load_config()
        server = self._widgets["vpn_server"].get_text().strip()
        success, msg = disconnect_vpn(server)
        config["vpn_status"] = "Disconnected"
        _save_config(config)
        self._widgets["vpn_status"].set_active(VPN_STATUSES.index("Disconnected"))
        if success:
            self._status_label.set_text("VPN disconnected ✓")
        else:
            self._status_label.set_text(f"VPN disconnect failed: {msg}")

        # --- Save / Apply bar ---
        action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        action_bar.set_name("settings-action-bar")
        action_bar.set_margin_top(0)
        action_bar.set_margin_bottom(12)
        action_bar.set_margin_start(16)
        action_bar.set_margin_end(16)

        self._status_label = Gtk.Label(label="")
        self._status_label.set_name("settings-status-label")

        reset_btn = Gtk.Button(label="Reset to Defaults")
        reset_btn.set_name("settings-reset-button")
        reset_btn.connect("clicked", self._on_reset)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.set_name("settings-cancel-button")
        cancel_btn.connect("clicked", lambda *_: self.hide())

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.set_name("settings-apply-button")
        apply_btn.connect("clicked", self._on_apply)

        action_bar.pack_start(self._status_label, False, False, 0)
        action_bar.pack_start(reset_btn, False, False, 0)
        action_bar.pack_end(apply_btn, False, False, 0)
        action_bar.pack_end(cancel_btn, False, False, 0)

        # Content wrapper: stack + action bar
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_name("settings-content-box")
        content_box.pack_start(self._stack, True, True, 0)

        action_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        action_sep.set_name("settings-action-separator")
        content_box.pack_start(action_sep, False, False, 0)
        content_box.pack_start(action_bar, False, False, 0)

        root.pack_start(sidebar, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.set_name("settings-separator")
        root.pack_start(separator, False, False, 0)

        root.pack_start(content_box, True, True, 0)

        outer.pack_start(root, True, True, 0)
        self.add(outer)

        # Select first category
        self._select_category("General")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_nav_clicked(self, button, name):
        self._select_category(name)

    def _select_category(self, name):
        self._stack.set_visible_child_name(name)
        for cat_name, btn in self._sidebar_buttons:
            ctx = btn.get_style_context()
            if cat_name == name:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
        self._status_label.set_text("")

    def _on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        for cat_name, btn in self._sidebar_buttons:
            btn.set_visible(not query or query in cat_name.lower())

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _make_scrolled_page(self, inner_box):
        """Wrap a Gtk.Box in a ScrolledWindow for long content."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(inner_box)
        return scroll

    def _section_label(self, text):
        lbl = Gtk.Label(label=text)
        lbl.set_name("settings-section-label")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_margin_top(12)
        lbl.set_margin_bottom(4)
        return lbl

    def _row(self, label_text, widget, description=None):
        """Return a labelled settings row."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.set_name("settings-row")
        row.set_margin_start(8)
        row.set_margin_end(8)
        row.set_margin_top(4)
        row.set_margin_bottom(4)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl = Gtk.Label(label=label_text)
        lbl.set_name("settings-row-label")
        lbl.set_halign(Gtk.Align.START)
        left.pack_start(lbl, False, False, 0)
        if description:
            desc = Gtk.Label(label=description)
            desc.set_name("settings-row-description")
            desc.set_halign(Gtk.Align.START)
            desc.set_line_wrap(True)
            desc.set_max_width_chars(_DESCRIPTION_MAX_WIDTH)
            left.pack_start(desc, False, False, 0)

        row.pack_start(left, True, True, 0)
        row.pack_end(widget, False, False, 0)
        return row

    # --- General ---
    def _build_general_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("System"), False, False, 0)

        terminal_entry = Gtk.Entry()
        terminal_entry.set_name("settings-entry")
        terminal_entry.set_text(config.get("terminal_command", _DEFAULTS["terminal_command"]))
        terminal_entry.set_width_chars(20)
        self._widgets["terminal_command"] = terminal_entry
        box.pack_start(
            self._row(
                "Terminal command",
                terminal_entry,
                "Command used to open a terminal (e.g. kitty -e)",
            ),
            False, False, 0,
        )

        box.pack_start(self._section_label("Window Switcher"), False, False, 0)

        switcher_spin = Gtk.SpinButton()
        switcher_spin.set_name("settings-spinbutton")
        adj = Gtk.Adjustment(
            value=config.get("window_switcher_items_per_row", _DEFAULTS["window_switcher_items_per_row"]),
            lower=1, upper=20, step_increment=1, page_increment=5,
        )
        switcher_spin.set_adjustment(adj)
        self._widgets["window_switcher_items_per_row"] = switcher_spin
        box.pack_start(
            self._row(
                "Items per row",
                switcher_spin,
                "Number of windows shown per row in Alt+Tab switcher",
            ),
            False, False, 0,
        )

        box.pack_start(self._section_label("Workspaces"), False, False, 0)

        special_ws_switch = Gtk.Switch()
        special_ws_switch.set_active(config.get("hide_special_workspace", _DEFAULTS["hide_special_workspace"]))
        self._widgets["hide_special_workspace"] = special_ws_switch
        box.pack_start(
            self._row(
                "Hide special workspace",
                special_ws_switch,
                "Hide the Hyprland special workspace from the workspace bar",
            ),
            False, False, 0,
        )

        return self._make_scrolled_page(box)

    # --- Appearance ---
    def _build_appearance_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("Dynamic Colors"), False, False, 0)

        matugen_switch = Gtk.Switch()
        matugen_switch.set_active(config.get("matugen_enabled", _DEFAULTS["matugen_enabled"]))
        self._widgets["matugen_enabled"] = matugen_switch
        box.pack_start(
            self._row(
                "Matugen color extraction",
                matugen_switch,
                "Automatically generate a color scheme from the current wallpaper",
            ),
            False, False, 0,
        )

        return self._make_scrolled_page(box)

    # --- Wallpaper ---
    def _build_wallpaper_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("Wallpaper Source"), False, False, 0)

        wallpaper_entry = Gtk.Entry()
        wallpaper_entry.set_name("settings-entry")
        wallpaper_entry.set_text(
            config.get("wallpapers_dir", _DEFAULTS["wallpapers_dir"])
        )
        wallpaper_entry.set_width_chars(26)
        self._widgets["wallpapers_dir"] = wallpaper_entry

        browse_btn = Gtk.Button(label="Browse…")
        browse_btn.set_name("settings-browse-button")
        browse_btn.connect("clicked", self._on_browse_wallpapers, wallpaper_entry)

        dir_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        dir_row.set_name("settings-row")
        dir_row.set_margin_start(8)
        dir_row.set_margin_end(8)
        dir_row.set_margin_top(4)
        dir_row.set_margin_bottom(4)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl = Gtk.Label(label="Wallpapers directory")
        lbl.set_name("settings-row-label")
        lbl.set_halign(Gtk.Align.START)
        desc = Gtk.Label(label="Directory scanned for wallpaper images")
        desc.set_name("settings-row-description")
        desc.set_halign(Gtk.Align.START)
        left.pack_start(lbl, False, False, 0)
        left.pack_start(desc, False, False, 0)

        dir_row.pack_start(left, True, True, 0)
        dir_row.pack_end(browse_btn, False, False, 0)
        dir_row.pack_end(wallpaper_entry, False, False, 0)

        box.pack_start(dir_row, False, False, 0)

        # --- mpvpaper video wallpaper option ---
        box.pack_start(self._section_label("Video Wallpaper (mpvpaper)"), False, False, 12)

        video_entry = Gtk.Entry()
        video_entry.set_name("settings-entry")
        video_entry.set_text(config.get("video_wallpaper", ""))
        video_entry.set_width_chars(32)
        self._widgets["video_wallpaper"] = video_entry
        box.pack_start(
            self._row(
                "Video file path",
                video_entry,
                "Set a video file to use as wallpaper (requires mpvpaper)",
            ),
            False, False, 0,
        )

        mpvpaper_btn = Gtk.Button(label="Set Video Wallpaper")
        mpvpaper_btn.set_name("settings-mpvpaper-button")
        mpvpaper_btn.connect("clicked", self._on_set_video_wallpaper)
        box.pack_start(mpvpaper_btn, False, False, 8)

        return self._make_scrolled_page(box)

    def _on_set_video_wallpaper(self, button):
        video_path = self._widgets["video_wallpaper"].get_text().strip()
        if not video_path:
            self._status_label.set_text("Please enter a video file path.")
            return
        # Save to config
        config = _load_config()
        config["video_wallpaper"] = video_path
        _save_config(config)
        # Launch mpvpaper
        import subprocess
        try:
            subprocess.Popen(["mpvpaper", "eDP-1", video_path])
            self._status_label.set_text("Video wallpaper set ✓")
        except Exception as e:
            self._status_label.set_text(f"Failed to set video wallpaper: {e}")

    def _on_browse_wallpapers(self, button, entry):
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpapers Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        current = entry.get_text()
        if current:
            dialog.set_current_folder(os.path.expanduser(current))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()

    # --- Panel ---
    def _build_panel_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("Clock"), False, False, 0)

        clock_combo = Gtk.ComboBoxText()
        clock_combo.set_name("settings-combo")
        for fmt in CLOCK_FORMATS:
            clock_combo.append_text(fmt)
        current_fmt = config.get("panel_clock_format", _DEFAULTS["panel_clock_format"])
        clock_combo.set_active(
            CLOCK_FORMATS.index(current_fmt) if current_fmt in CLOCK_FORMATS else 0
        )
        self._widgets["panel_clock_format"] = clock_combo
        box.pack_start(
            self._row(
                "Clock format",
                clock_combo,
                "Display time in 12-hour (AM/PM) or 24-hour format",
            ),
            False, False, 0,
        )

        return self._make_scrolled_page(box)

    # --- Dock ---
    def _build_dock_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("Position & Visibility"), False, False, 0)

        position_combo = Gtk.ComboBoxText()
        position_combo.set_name("settings-combo")
        for pos in DOCK_POSITIONS:
            position_combo.append_text(pos)
        current_pos = config.get("dock_position", _DEFAULTS["dock_position"])
        position_combo.set_active(
            DOCK_POSITIONS.index(current_pos) if current_pos in DOCK_POSITIONS else 0
        )
        self._widgets["dock_position"] = position_combo
        box.pack_start(
            self._row("Dock position", position_combo), False, False, 0
        )

        enabled_switch = Gtk.Switch()
        enabled_switch.set_active(config.get("dock_enabled", _DEFAULTS["dock_enabled"]))
        self._widgets["dock_enabled"] = enabled_switch
        box.pack_start(
            self._row("Show Dock", enabled_switch, "Display the application dock"),
            False, False, 0,
        )

        autohide_switch = Gtk.Switch()
        autohide_switch.set_active(config.get("dock_auto_hide", _DEFAULTS["dock_auto_hide"]))
        self._widgets["dock_auto_hide"] = autohide_switch
        box.pack_start(
            self._row(
                "Auto-hide Dock",
                autohide_switch,
                "Automatically hide the dock when a window overlaps it",
            ),
            False, False, 0,
        )

        occluded_switch = Gtk.Switch()
        occluded_switch.set_active(config.get("dock_always_occluded", _DEFAULTS["dock_always_occluded"]))
        self._widgets["dock_always_occluded"] = occluded_switch
        box.pack_start(
            self._row(
                "Always consider dock occluded",
                occluded_switch,
                "Treat dock as always hidden regardless of window overlap",
            ),
            False, False, 0,
        )

        box.pack_start(self._section_label("Appearance"), False, False, 0)

        icon_spin = Gtk.SpinButton()
        icon_spin.set_name("settings-spinbutton")
        adj = Gtk.Adjustment(
            value=config.get("dock_icon_size", _DEFAULTS["dock_icon_size"]),
            lower=24, upper=128, step_increment=4, page_increment=16,
        )
        icon_spin.set_adjustment(adj)
        self._widgets["dock_icon_size"] = icon_spin
        box.pack_start(
            self._row("Icon size (px)", icon_spin, "Size of icons in the dock"),
            False, False, 0,
        )

        box.pack_start(self._section_label("Behaviour"), False, False, 0)

        preview_switch = Gtk.Switch()
        preview_switch.set_active(config.get("dock_preview_apps", _DEFAULTS["dock_preview_apps"]))
        self._widgets["dock_preview_apps"] = preview_switch
        box.pack_start(
            self._row(
                "Preview app windows",
                preview_switch,
                "Show a preview of open windows when hovering a dock icon",
            ),
            False, False, 0,
        )

        box.pack_start(self._section_label("Workspaces"), False, False, 0)

        hide_special_switch = Gtk.Switch()
        hide_special_switch.set_active(
            config.get("dock_hide_special_workspace_apps", _DEFAULTS["dock_hide_special_workspace_apps"])
        )
        self._widgets["dock_hide_special_workspace_apps"] = hide_special_switch
        box.pack_start(
            self._row(
                "Hide special-workspace apps",
                hide_special_switch,
                "Don't show apps from the special workspace in the dock",
            ),
            False, False, 0,
        )

        return self._make_scrolled_page(box)

    # --- Notifications ---
    def _build_notifications_page(self, config):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_name("settings-page")
        box.set_margin_top(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        box.pack_start(self._section_label("Timing"), False, False, 0)

        timeout_entry = Gtk.Entry()
        timeout_entry.set_name("settings-entry")
        timeout_entry.set_text(config.get("notification_timeout", _DEFAULTS["notification_timeout"]))
        timeout_entry.set_width_chars(8)
        self._widgets["notification_timeout"] = timeout_entry
        box.pack_start(
            self._row(
                "Default timeout",
                timeout_entry,
                "Duration before a notification auto-dismisses (e.g. 5s, 1m)",
            ),
            False, False, 0,
        )

        box.pack_start(self._section_label("App Filtering"), False, False, 0)

        ignored_entry = Gtk.Entry()
        ignored_entry.set_name("settings-entry")
        ignored_val = config.get("notification_ignored_apps_history", _DEFAULTS["notification_ignored_apps_history"])
        ignored_entry.set_text(", ".join(ignored_val) if ignored_val else "")
        ignored_entry.set_width_chars(26)
        self._widgets["notification_ignored_apps_history"] = ignored_entry
        box.pack_start(
            self._row(
                "Ignored apps (history)",
                ignored_entry,
                "Comma-separated list of apps whose notifications are not stored",
            ),
            False, False, 0,
        )

        limited_entry = Gtk.Entry()
        limited_entry.set_name("settings-entry")
        limited_val = config.get("notification_limited_apps_history", _DEFAULTS["notification_limited_apps_history"])
        limited_entry.set_text(", ".join(limited_val) if limited_val else "")
        limited_entry.set_width_chars(26)
        self._widgets["notification_limited_apps_history"] = limited_entry
        box.pack_start(
            self._row(
                "Limited-history apps",
                limited_entry,
                "Comma-separated list of apps with limited notification history",
            ),
            False, False, 0,
        )

        return self._make_scrolled_page(box)

    # ------------------------------------------------------------------
    # Save / Reset
    # ------------------------------------------------------------------

    def _on_apply(self, button):
        config = _load_config()

        # General
        config["terminal_command"] = self._widgets["terminal_command"].get_text().strip()
        config["window_switcher_items_per_row"] = int(
            self._widgets["window_switcher_items_per_row"].get_value()
        )
        config["hide_special_workspace"] = self._widgets["hide_special_workspace"].get_active()

        # Appearance
        config["matugen_enabled"] = self._widgets["matugen_enabled"].get_active()

        # Wallpaper
        config["wallpapers_dir"] = self._widgets["wallpapers_dir"].get_text().strip()

        # Panel
        config["panel_clock_format"] = self._widgets["panel_clock_format"].get_active_text()

        # Dock
        config["dock_position"] = self._widgets["dock_position"].get_active_text()
        config["dock_enabled"] = self._widgets["dock_enabled"].get_active()
        config["dock_auto_hide"] = self._widgets["dock_auto_hide"].get_active()
        config["dock_always_occluded"] = self._widgets["dock_always_occluded"].get_active()
        config["dock_icon_size"] = int(self._widgets["dock_icon_size"].get_value())
        config["dock_preview_apps"] = self._widgets["dock_preview_apps"].get_active()
        config["dock_hide_special_workspace_apps"] = self._widgets[
            "dock_hide_special_workspace_apps"
        ].get_active()

        # Notifications
        config["notification_timeout"] = self._widgets["notification_timeout"].get_text().strip()

        def _parse_list(text):
            return [s.strip() for s in text.split(",") if s.strip()]

        config["notification_ignored_apps_history"] = _parse_list(
            self._widgets["notification_ignored_apps_history"].get_text()
        )
        # Keep legacy key in sync for compatibility
        config["notification_ignored_apps"] = config["notification_ignored_apps_history"]
        config["notification_limited_apps_history"] = _parse_list(
            self._widgets["notification_limited_apps_history"].get_text()
        )

        _save_config(config)
        self._status_label.set_text("Settings saved ✓")

    def _on_reset(self, button):
        """Reset all widgets to default values."""
        d = _DEFAULTS
        self._widgets["terminal_command"].set_text(d["terminal_command"])
        self._widgets["window_switcher_items_per_row"].set_value(d["window_switcher_items_per_row"])
        self._widgets["hide_special_workspace"].set_active(d["hide_special_workspace"])

        self._widgets["matugen_enabled"].set_active(d["matugen_enabled"])
        self._widgets["wallpapers_dir"].set_text(d["wallpapers_dir"])

        fmt = d["panel_clock_format"]
        self._widgets["panel_clock_format"].set_active(
            CLOCK_FORMATS.index(fmt) if fmt in CLOCK_FORMATS else 0
        )

        pos = d["dock_position"]
        self._widgets["dock_position"].set_active(
            DOCK_POSITIONS.index(pos) if pos in DOCK_POSITIONS else 0
        )
        self._widgets["dock_enabled"].set_active(d["dock_enabled"])
        self._widgets["dock_auto_hide"].set_active(d["dock_auto_hide"])
        self._widgets["dock_always_occluded"].set_active(d["dock_always_occluded"])
        self._widgets["dock_icon_size"].set_value(d["dock_icon_size"])
        self._widgets["dock_preview_apps"].set_active(d["dock_preview_apps"])
        self._widgets["dock_hide_special_workspace_apps"].set_active(d["dock_hide_special_workspace_apps"])

        self._widgets["notification_timeout"].set_text(d["notification_timeout"])
        self._widgets["notification_ignored_apps_history"].set_text(
            ", ".join(d["notification_ignored_apps_history"])
        )
        self._widgets["notification_limited_apps_history"].set_text(
            ", ".join(d["notification_limited_apps_history"])
        )

        self._status_label.set_text("Defaults restored – click Apply to save")

    # ------------------------------------------------------------------
    # Toggle visibility
    # ------------------------------------------------------------------

    def toggle(self, _=None):
        if self.get_visible():
            self.hide()
        else:
            self.show_all()
