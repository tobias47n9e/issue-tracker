#!/usr/bin/env python3

#
# Copyright (C) 2016 Tobias Schönber <tobias47n9e@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import gi
gi.require_version('Ide', '1.0')
from gi.repository import Ide
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
import bugzilla
import threading
import time


class MainPlugin(GObject.Object, Ide.WorkbenchAddin):

    """
    Main class of the plugin.

    Handles the loading, unloading of the plugin.
    """

    def do_load(self, workbench):
        self.workbench = workbench
        context = self.workbench.props.context
        self.perspective = IssueTrackerPerspective(visible=True)
        self.workbench.add_perspective(self.perspective)

    def do_unload(self, app):
        self.workbench = None


class IssueTrackerPerspective(Gtk.Box, Ide.Perspective):

    """
    Creates the perspective containing the issue tracker information

    Sets up the widgets, queries the remote issue tracker and displays
    the information.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Main container
        self.main_box = Gtk.Box(visible=True,
                                orientation=Gtk.Orientation.VERTICAL)

        # Header
        header = Gtk.Label(visible=True, expand=True)
        header.set_markup("<big>Remote Repository Stats</big>")
        self.main_box.pack_start(header, False, True, 0)
        tracker_label = Gtk.Label(label="Issue Tracker:", visible=True)
        tracker_link = Gtk.LinkButton(uri="https://bugzilla.gnome.org",
                                      label="https://bugzilla.gnome.org",
                                      visible=True)
        tracker_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                              visible=True)
        tracker_box.pack_start(tracker_label, False, True, 0)
        tracker_box.pack_start(tracker_link, True, True, 0)
        self.main_box.pack_start(tracker_box, False, True, 0)
        header_line = Gtk.Separator(visible=True)
        self.main_box.pack_start(header_line, False, True, 10)

        # Summar containers
        grid = Gtk.Grid(visible=True)
        self.main_box.add(grid)

        total_label = Gtk.Label(label="Total Issues:", visible=True)
        self.total_box = Gtk.Box(visible=True)
        self.total_spinner = Gtk.Spinner(active=True, visible=True)
        self.total_box.pack_start(self.total_spinner, True, True, 0)
        open_label = Gtk.Label(label="Open Issues:", visible=True)
        self.open_box = Gtk.Box(visible=True)
        self.open_spinner = Gtk.Spinner(active=True, visible=True)
        self.open_box.pack_start(self.open_spinner, True, True, 0)
        closed_label = Gtk.Label(label="Closed Issues:", visible=True)
        self.closed_box = Gtk.Box(visible=True)
        self.closed_spinner = Gtk.Spinner(active=True, visible=True)
        self.closed_box.pack_start(self.closed_spinner, True, True, 0)

        grid.attach(total_label, 0, 0, 1, 1)
        grid.attach(self.total_box, 1, 0, 1, 1)
        grid.attach(open_label, 0, 1, 1, 1)
        grid.attach(self.open_box, 1, 1, 1, 1)
        grid.attach(closed_label, 0, 2, 1, 1)
        grid.attach(self.closed_box, 1, 2, 1, 1)

        # Set up Workbench
        self.add(self.main_box)
        self.titlebar = Ide.WorkbenchHeaderBar(visible=True)

        # Get Remote Tracker Information
        thread = threading.Thread(target=self.query_bugzilla)
        thread.daemon = True
        thread.start()

    def query_bugzilla(self):
        """
        Async: Query bugzilla for all the project information

		The request is slow, the information is added once it
		is loaded.
        """
        label_list = Gtk.Label(expand=True, visible=True)
        label_list.set_markup("<big>Issues</big>")
        self.main_box.pack_start(label_list, False, True, 0)

        scroll_window = Gtk.ScrolledWindow(visible=True)
        listbox = Gtk.ListBox(visible=True)
        scroll_window.add(listbox)

        # FIXME: Get project name and tracker
        gnome_bugz = bugzilla.Bugzilla("https://bugzilla.gnome.org")
        bugs = gnome_bugz.query({"product": "gnome-builder"})
        bugs_total = 0
        bugs_open = 0
        bugs_closed = 0

        for bug in bugs:
            bugs_total += 1
            if bug.is_open == True:
                bugs_open += 1
                lbl_status = Gtk.Label(label="Open", visible=True)
            else:
                bugs_closed += 1
                lbl_status = Gtk.Label(label="Closed", visible=True)

            row = Gtk.ListBoxRow(visible=True)
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                           visible=True, spacing=50)
            lbl = Gtk.Label(label=bug.summary, visible=True)
            box.pack_start(lbl, True, True, 0)
            box.pack_start(lbl_status, True, True, 0)
            row.add(box)
            listbox.add(row)

        total_label = Gtk.Label(label=bugs_total, visible=True)
        open_label = Gtk.Label(label=bugs_open, visible=True)
        closed_label = Gtk.Label(label=bugs_closed, visible=True)
        self.total_box.remove(self.total_spinner)
        self.total_box.pack_start(total_label, True, True, 0)
        self.open_box.remove(self.open_spinner)
        self.open_box.pack_start(open_label, True, True, 0)
        self.closed_box.remove(self.closed_spinner)
        self.closed_box.pack_start(closed_label, True, True, 0)


        self.main_box.pack_start(scroll_window, True, True, 0)

    def do_get_id(self):
        return 'hello-world2'

    def do_get_title(self):
        return 'Hello'

    def do_get_priority(self):
        return 10000

    def do_get_icon_name(self):
        return "folder-publicshare-symbolic"

    def do_get_titlebar(self):
        return self.titlebar

