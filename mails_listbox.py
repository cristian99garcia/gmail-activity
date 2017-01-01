#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016, Cristian García <cristian99garcia@gmail.com>
#
# This library is free software you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from utils import get_label_name

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject


class TreeView(Gtk.ScrolledWindow):

    __gsignals__ = {
        "selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
    }

    def __init__(self, model, data_id):
        Gtk.ScrolledWindow.__init__(self)

        self.model = model
        self.data_id = data_id

        self.view = Gtk.TreeView()
        self.view.set_model(self.model)
        self.add(self.view)

        selection = self.view.get_selection()
        selection.connect("changed", self.__selection_changed_cb)

    def __selection_changed_cb(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self.emit("selected", model[treeiter][self.data_id])


class LabelsListBox(TreeView):

    def __init__(self):
        # label, id
        TreeView.__init__(self, Gtk.ListStore(str, str), 1)

        width = 200
        height = self.get_preferred_height_for_width(width)[0]  # Evit Gtk warning spam
        self.set_size_request(width, height)

        self.labels = ["CATEGORY_PERSONAL", "STARRED", "IMPORANT", "SENT", "SPAM", "TRASH"]

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Label", renderer_text, text=0)
        self.view.append_column(column_text)

    def set_labels(self, labels):
        def add_label(label):
            self.model.append([get_label_name(label), label])

        for label in self.labels:
            GObject.idle_add(add_label, label)

        self.show_all()


class ThreadsListBox(TreeView):

    def __init__(self):
        # important, text, id, history id
        TreeView.__init__(self, Gtk.ListStore(bool, str, str, str), 2)

        self.set_size_request(300, 1)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.__important_setted)
        column_toggle = Gtk.TreeViewColumn("Important", renderer_toggle, active=0)
        self.view.append_column(column_toggle)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Mail", renderer_text, text=1)
        self.view.append_column(column_text)

    def __important_setted(self, widget, path):
        self.model[path][0] = not self.model[path][0]

    def set_threads(self, threads):
        """
        def add_thread(idx):
            thread = threads[idx]
            self.model.append([False, thread["snippet"], thread["id"], thread["historyId"]])
            idx += 1
            if idx < len(threads):
                GObject.idle_add(add_thread, idx)

        GObject.idle_add(add_thread, 0)
        """
        for thread in threads:
            self.model.append([False, thread["snippet"], thread["id"], thread["historyId"]])

        self.show_all()


class MailsListBox(Gtk.HBox):

    __gsignals__ = {
        "label-selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
        "thread-selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
    }

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.labels_view = LabelsListBox()
        self.labels_view.connect("selected", self.__label_selected_cb)
        self.pack_start(self.labels_view, False, False, 0)

        self.threads_listbox = ThreadsListBox()
        self.threads_listbox.connect("selected", self.__thread_selected_cb)
        self.pack_start(self.threads_listbox, True, True, 0)

        self.show_all()

    def set_threads(self, threads):
        self.threads_listbox.set_threads(threads)

    def set_labels(self, labels):
        self.labels_view.set_labels(labels)

    def __label_selected_cb(self, listbox, labelid):
        self.emit("label-selected", labelid)

    def __thread_selected_cb(self, listbox, threadid):
        self.emit("thread-selected", threadid)
