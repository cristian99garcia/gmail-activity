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

from constants import TABS
from constants import CATEGORIES
from utils import get_label_name
from utils import unicode_to_string

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject

from sugar3.graphics.icon import CellRendererIcon
from sugar3 import profile

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
        self.view.set_headers_visible(False)
        self.view.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.view.connect("button-press-event", self.__button_press_cb)
        self.add(self.view)

        selection = self.view.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.connect("changed", self.__selection_changed_cb)

    def __selection_changed_cb(self, selection):
        # model, treeiter = selection.get_selected()
        # if treeiter is not None:
        #     self.emit("selected", model[treeiter][self.data_id])
        pass

    def __button_press_cb(self, widget, event):
        if event.button != 1:
            return

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            path = self.view.get_path_at_pos(event.x, event.y)
            if path is not None:
                path = path[0]
                iter = self.model.get_iter(path)
                value = self.model.get_value(iter, self.data_id)
                self.emit("selected", value)


class LabelsListBox(TreeView):

    def __init__(self):
        # label, id
        TreeView.__init__(self, Gtk.ListStore(str, str), 1)

        self.set_size_request(200, 1)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Label", renderer_text, text=0)
        self.view.append_column(column_text)

        for label in CATEGORIES:
            self.model.append([get_label_name(label), label])

        self.show_all()

    def set_labels(self, labels):
        pass


class ThreadsListBox(TreeView):

    __gsignals__ = {
        "favorited": (GObject.SIGNAL_RUN_LAST, None, [str, bool]),
    }

    def __init__(self, category):
        # important, starred, text, id, history id, background color
        TreeView.__init__(self, Gtk.ListStore(bool, bool, str, str, str, str), 3)
        self.category = category
        self.set_size_request(300, 1)
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.__important_setted)
        column_toggle = Gtk.TreeViewColumn("Important", renderer_toggle, active=0)
        self.view.append_column(column_toggle)


        cell_favorite = CellRendererFavourite()
        cell_favorite.connect('clicked', self.__favourite_clicked)
        self._fav_column = Gtk.TreeViewColumn("Starred", cell_favorite)
        self._fav_column.set_cell_data_func(
            cell_favorite, self.__favorite_set_data)
        self.view.append_column(self._fav_column)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("ellipsize", Pango.EllipsizeMode.END)
        column_text = Gtk.TreeViewColumn("Mail", renderer_text, text=2, background=5)
        self.view.append_column(column_text)


    def __important_setted(self, widget, path):
        self.model[path][0] = not self.model[path][0]

    def __favourite_clicked(self, cell, path):
        self.model[path][1] = not self.model[path][1]
        self.emit("favorited", self.model[path][3], self.model[path][1])

    def __favorite_set_data(self, column, cell, tree_model,
                               tree_iter, data):
        favorite = tree_model[tree_iter][1]
        if favorite:
            cell.props.xo_color = profile.get_color()
        else:
            cell.props.xo_color = None

    def set_threads(self, threads):
        for thread in threads:
            snippet = unicode_to_string(thread["snippet"])
            id = unicode_to_string(thread["id"])
            historyid = unicode_to_string(thread["historyId"])

            background_color = '#EEEEEE'
            if not thread["read"]:
                background_color = 'white'

            starred = False
            if thread["STARRED"]:
                starred = True
            self.model.append([False, starred, snippet, id, historyid, background_color])

        self.show_all()


class ThreadsNotebook(Gtk.Notebook):

    __gsignals__ = {
        "thread-selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
        "favorite-clicked": (GObject.SIGNAL_RUN_LAST, None, [str, bool]),
    }

    def __init__(self):
        Gtk.Notebook.__init__(self)

        self.listboxes = {}

        for tab in TABS:
            label = Gtk.Label(get_label_name(tab))
            listbox = ThreadsListBox(tab)
            listbox.connect("selected", self.__thread_selected_cb)
            listbox.connect("favorited", self.__favorite_clicked_cb)
            self.append_page(listbox, label)
            self.child_set_property(listbox, "tab-expand", True)

            self.listboxes[tab] = listbox

        self.show_all()

    def __thread_selected_cb(self, listbox, threadid):
        self.emit("thread-selected", threadid)

    def __favorite_clicked_cb(self, listbox, threadid, starred):
        self.emit("favorite-clicked", threadid, starred)


class MailsListBox(Gtk.HBox):

    __gsignals__ = {
        "label-selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
        "thread-selected": (GObject.SIGNAL_RUN_LAST, None, [str]),
        "favorite-clicked": (GObject.SIGNAL_RUN_LAST, None, [str, bool]),
    }

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.labels_view = LabelsListBox()
        self.labels_view.connect("selected", self.__label_selected_cb)
        self.pack_start(self.labels_view, False, False, 0)

        self.threads_notebook = ThreadsNotebook()
        self.threads_notebook.connect("thread-selected", self.__thread_selected_cb)
        self.threads_notebook.connect("favorite-clicked", self.__favorite_clicked_cb)
        self.pack_start(self.threads_notebook, True, True, 0)

        self.show_all()

    def set_threads(self, threads):
        for tab in threads.keys():
            self.threads_notebook.listboxes[tab].set_threads(threads[tab])

    def set_labels(self, labels):
        self.labels_view.set_labels(labels)

    def __label_selected_cb(self, listbox, labelid):
        self.emit("label-selected", labelid)

    def __thread_selected_cb(self, notebook, threadid):
        self.emit("thread-selected", threadid)

    def __favorite_clicked_cb(self, notebook, threadid, starred):
        self.emit("favorite-clicked", threadid, starred)


class CellRendererFavourite(CellRendererIcon):
    __gtype_name__ = "CellRendererFavourite"

    def __init__(self):
        CellRendererIcon.__init__(self)

        self.props.width = self.props.height = self.props.size = 25
        self.props.icon_name = 'emblem-favorite'

        self.props.mode = Gtk.CellRendererMode.ACTIVATABLE

    def do_activate(self, event, widget, path, background_area, cell_area, flags):
        self.emit("clicked", path)

from gi.repository import Gtk

class CellRendererPixbufWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="CellRendererPixbuf Example")

        self.set_default_size(200, 200)

        self.liststore = Gtk.ListStore(str, str)
        self.liststore.append(["Item 1", DESACTIVATED])
        self.liststore.append(["Item 2", DESACTIVATED])
        self.liststore.append(["Item 3", ACTIVATED])

        treeview = Gtk.TreeView(model=self.liststore)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Text", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_pixbuf = CellRendererPixbuf()
        renderer_pixbuf.connect("clicked", self._clicked_cb)

        column_pixbuf = Gtk.TreeViewColumn("Image", renderer_pixbuf, icon_name=1)
        treeview.append_column(column_pixbuf)

        self.add(treeview)

    def _clicked_cb(self, cell, path):
        state = self.liststore[path][1]
        if state == ACTIVATED:
            self.liststore[path][1] = DESACTIVATED

        else:
            self.liststore[path][1] = ACTIVATED


win = CellRendererPixbufWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

