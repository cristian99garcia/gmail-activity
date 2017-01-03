#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016, Cristian García <cristian99garcia@gmail.com>
#
# self library is free software you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation either
# version 3 of the License, or (at your option) any later version.
#
# self library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with self library if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys
import base64

from gettext import gettext as _

from utils import make_html_from_text
from utils import get_current_date_string

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class Editor(Gtk.TextView):

    def __init__(self):
        Gtk.TextView.__init__(self)

        self.placeholder = _("Click here if you want reply or forward the message")
        self.buffer = self.get_buffer()

        if hasattr(self, "set_top_margin"):
            self.set_top_margin(5)

        if hasattr(self, "set_bottom_margin"):
            self.set_bottom_margin(5)

        self.set_left_margin(5)
        self.set_right_margin(5)

        self.reset()

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.__button_press_cb)

    def __button_press_cb(self, button, event):
        if event.button == 1 and not self.edited:
            self.edited = True
            self.buffer.set_text("")

    def reset(self):
        self.edited = False
        self.buffer.set_text(self.placeholder)

    def get_text(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, 1)


class RemoveButton(Gtk.EventBox):

    __gsignals__ = {
        "clicked": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        image = Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        self.add(image)

        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        self.connect("realize", self.__realize_cb)
        self.connect("button-release-event", self.__button_release_cb)

    def __realize_cb(self, widget):
        win = self.get_window()
        win.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def __button_release_cb(self, widget, event):
        if event.button == 1:
            self.emit("clicked")


class AddressBox(Gtk.HBox):

    __gsignals__ = {
        "remove-me": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self, address, anchor):
        Gtk.HBox.__init__(self)

        self.address = address
        self.anchor = anchor

        self.set_margin_left(5)
        self.set_margin_right(5)

        self.label = Gtk.Label(self.address.split("@")[0])
        self.pack_start(self.label, False, False, 0)

        self.button = RemoveButton()
        self.button.connect("clicked", self.__remove_cb)
        self.pack_end(self.button, False, False, 0)

        self.show_all()

    def __remove_cb(self, button):
        self.emit("remove-me")


class EntryBox(Gtk.HBox):

    __gsignals__ = {
        "changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
        "activate": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
    }

    def __init__(self, text):
        Gtk.HBox.__init__(self)

        self.label = Gtk.Label()
        self.label.set_text(text)
        self.label.set_margin_left(5)
        self.label.set_margin_right(5)
        self.label.props.xalign = 0

        self.view = Gtk.TextView()
        self.view.set_left_margin(5)
        self.view.set_right_margin(5)
        self.view.set_hexpand(True)

        if hasattr(self.view, "set_top_margin"):
            self.view.set_top_margin(5)

        if hasattr(self.view, "set_bottom_margin"):
            self.view.set_bottom_margin(5)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.view)

        self.buffer = self.view.get_buffer()

    def get_text(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, 1)


class AddressEntry(EntryBox):

    def __init__(self, text):
        EntryBox.__init__(self, text)

        self.boxes = []

        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.connect("key-press-event", self.__key_press_cb)

    def __key_press_cb(self, view, event):
        start, end = self.buffer.get_bounds()
        address = self.buffer.get_text(start, end, 1).split(" ")[-1]
        pos = self.buffer.props.cursor_position

        ignore_keys = [Gdk.KEY_Return, Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Home]
        if event.keyval in ignore_keys:
            return True

        elif event.keyval in [Gdk.KEY_space, Gdk.KEY_Tab]:
            if address.strip() != "":
                for x in range(0, len(address)):
                    self.buffer.backspace(end, False, True)
                    end = self.buffer.get_end_iter()

                anchor = self.buffer.create_child_anchor(end)
                box = AddressBox(address, anchor)
                box.connect("remove-me", self.__remove_box)
                self.view.add_child_at_anchor(box, anchor)

                self.boxes.append(box)

            return True

        elif event.keyval == Gdk.KEY_BackSpace:
            if pos > 0:
                for box in self.boxes:
                    iter = self.buffer.get_iter_at_child_anchor(box.anchor)
                    if iter.get_offset() == pos - 1:
                        self.__remove_box(box)
                        return True

        elif event.keyval == Gdk.KEY_Left:
            if pos - 1 < len(self.boxes):
                return True

    def __remove_box(self, box):
        iter = self.buffer.get_iter_at_child_anchor(box.anchor)
        iter = self.buffer.get_iter_at_offset(iter.get_offset() + 1)
        self.buffer.backspace(iter, False, True)
        end = self.buffer.get_end_iter()
        self.buffer.place_cursor(end)

        self.boxes.remove(box)
        del box

    def get_text(self):
        text = ""
        for box in self.boxes:
            text += box.address + " "

        return text


class Redacter(Gtk.VBox):

    def __init__(self, threadid=None, address=None):
        Gtk.VBox.__init__(self)

        self.threadid = threadid
        self.address = address

        self.set_margin_top(3)
        self.set_margin_bottom(8)
        self.set_margin_left(8)
        self.set_margin_right(8)

        self.to_entry = AddressEntry(_("To:"))
        self.cc_entry = AddressEntry(_("Cc:"))
        self.cco_entry = AddressEntry(_("Cco:"))
        self.subject_entry = EntryBox(_("Subject:"))

        grid = Gtk.Grid()
        self.pack_start(grid, False, False, 5)

        if self.threadid is None:
            grid.attach(self.to_entry.label,  0, 0, 1, 1)
            grid.attach(self.to_entry.scroll, 1, 0, 1, 1)

            grid.attach(self.cc_entry.label,  0, 1, 1, 1)
            grid.attach(self.cc_entry.scroll, 1, 1, 1, 1)

            grid.attach(self.cco_entry.label,  0, 2, 1, 1)
            grid.attach(self.cco_entry.scroll, 1, 2, 1, 1)

            grid.attach(self.subject_entry.label,   0, 3, 1, 1)
            grid.attach(self.subject_entry.scroll,  1, 3, 1, 1)

        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(100, 200)
        self.pack_start(scroll, True, True, 5)

        self.editor = Editor()
        scroll.add(self.editor)

        self.show_all()

    def get_data(self):
        html = make_html_from_text(self.editor.get_text())
        encoded = base64.urlsafe_b64encode(html)
        recipients = self.to_entry.get_text().split(" ")

        body = {
            "data": encoded,
            "attachmentId": "REPLACEME",
            "size": sys.getsizeof(encoded),
        }

        headers = [
            {
                "name": "MIME-Version",
                "value": "1.0"
            },
            {
                "name": "Date",
                "value": get_current_date_string()
            },
            {
                "name": "Message-ID",
                "value": "REPLACEME"
            },
            {
                "name": "Subject",
                "value": self.subject_entry.get_text()
            },
            {
                "name": "From",
                "value": self.address  # TODO: get name too
            },
            {
                "name": "To",
                "value": recipients[0]  # TODO: send to all
            },
            {
                "name": "Content-Type",
                "value": "text/html; charset=UTF-8"
            }
        ]

        message = {
            "internalDate": "REPLACEME",
            "historyId": "REPLACEME",
            "payload": {
                "body": body,
                "mimeType": "text/html",
                "partId": "0",
                "filename": "",
                "headers": headers,
                "parts": [
                ],
            },
            "snippet": self.editor.get_text().replace("\n", " ")[:100],
            "sizeEstimate": sys.getsizeof(encoded),
            "threadId": self.threadid,
            "labelIds": [
                "REPLACEME",
            ],
            "id": "REPLACEME",
        }

        return message


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.view_type = None

        self.set_default_size(680, 480)
        self.connect("destroy", Gtk.main_quit)

        box = Gtk.VBox()
        self.add(box)

        self.redacter = Redacter()
        box.pack_start(self.redacter, True, True, 0)

        b = Gtk.Button("check")
        b.connect("clicked", self.__check)
        box.pack_end(b, False, False, 0)

        self.show_all()

    def __check(self, button):
        print self.redacter.get_data()


if __name__ == "__main__":
    win = Window()
    Gtk.main()
