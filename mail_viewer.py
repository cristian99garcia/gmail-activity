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

from gettext import gettext as _

from redactor import Redactor
from utils import deep_search
from utils import load_html_data
from utils import get_date_string

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit", "3.0")

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import WebKit
from gi.repository import GObject


class ThreadHeaderBox(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.subject_label = Gtk.Label()
        self.subject_label.modify_font(Pango.FontDescription("20"))
        self.subject_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.pack_start(self.subject_label, False, False, 0)

        self.important_button = Gtk.CheckButton()
        self.pack_start(self.important_button, False, False, 0)

    def set_data(self, data):
        self.subject_label.set_label("")
        messages = data["messages"]

        for message in messages:
            for header in message["payload"]["headers"]:
                if header["name"] == "Subject":
                    self.subject_label.set_label(header["value"])
                    self.subject_label.set_tooltip_text(header["value"])
                    return

        # self.important_button.set_active("IMPORTANT" in mail["labelIds"])


class MailBox(Gtk.VBox):

    def __init__(self, mail):
        Gtk.VBox.__init__(self)

        self.mail = mail
        self.views = {}
        self.message_html = None
        self.extra_html = None

        self.set_size_request(1, 100)
        self.set_margin_top(5)
        self.set_margin_bottom(10)
        self.set_margin_left(20)
        self.set_margin_right(20)

        self.pack_end(Gtk.VSeparator(), False, False, 20)

        self.message_html, self.extra_html = load_html_data(self.mail)
        self.make_headerbox()
        self.make_mailbox()
        self.make_extrabox()

    def make_headerbox(self):
        self.headerbox = Gtk.HBox()
        self.headerbox.set_margin_bottom(5)
        self.pack_start(self.headerbox, False, False, 0)

        data = {
            "From": "",
            "To": "",
            "Date": "",
        }

        for header in self.mail["payload"]["headers"]:
            if header["name"] in data.keys():
                data[header["name"]] = header["value"]

        vbox = Gtk.VBox()
        self.headerbox.pack_start(vbox, False, False, 0)

        from_label = Gtk.Label(data["From"])
        from_label.props.xalign = 0  # #set_xalign(Gtk.Align.START)
        vbox.pack_start(from_label, False, False, 0)

        to_label = Gtk.Label(_("To ") + data["To"])
        to_label.props.xalign = 0  # set_xalign(Gtk.Align.START)
        to_label.set_ellipsize(Pango.EllipsizeMode.END)
        vbox.pack_start(to_label, False, False, 0)

        tooltip = ""
        for to in data["To"].split(", "):
            tooltip += to + "\n"

        to_label.set_tooltip_text(tooltip[:-1])

        time_label = Gtk.Label(get_date_string(data["Date"]))
        self.headerbox.pack_end(time_label, False, False, 0)

        self.headerbox.show_all()

    def make_mailbox(self):
        self.mailbox = Gtk.VBox()
        self.pack_start(self.mailbox, False, False, 0)

        view = WebKit.WebView()
        self.mailbox.pack_start(view, False, False, 0)

        if self.message_html is not None:
            view.load_html_string(self.message_html, "file:///")

        self.mailbox.show_all()

    def make_extrabox(self):
        self.extrabox = Gtk.VBox()
        self.pack_end(self.extrabox, False, False, 0)

        if self.extra_html is not None:
            extra_expander = Gtk.Expander()
            extra_expander.set_label("...")
            self.extrabox.pack_start(extra_expander, False, False, 0)

            view = WebKit.WebView()
            view.set_size_request(1, 1)
            view.load_html_string(self.extra_html, "file:///")
            extra_expander.add(view)

            extra_expander.set_expanded(False)


class MailViewer(Gtk.ScrolledWindow):

    __gsignals__ = {
        "send": (
            GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]
        ),
    }

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.mailboxes = []
        self.thread = None
        self.threadid = None

        self.canvas = Gtk.VBox()
        self.canvas.set_margin_top(20)
        self.canvas.set_margin_bottom(20)
        self.canvas.set_margin_left(20)
        self.canvas.set_margin_right(20)
        self.add(self.canvas)

        self.headerbox = ThreadHeaderBox()
        self.canvas.pack_start(self.headerbox, False, False, 0)

        self.mailboxes_canvas = Gtk.VBox()
        self.canvas.pack_start(self.mailboxes_canvas, True, True, 0)

        self.redactor = Redactor()
        self.redactor.connect("send", self.__send_cb)
        self.canvas.pack_end(self.redactor, False, False, 0)

        self.show_all()

    def __send_cb(self, redactor, data):
        self.emit("send", data)

    def __add_messages(self, thread):
        def add_mail(message):
            box = MailBox(message)
            self.mailboxes.append(box)
            self.mailboxes_canvas.pack_start(box, False, False, 0)

        for message in thread["messages"]:
            add = True
            for box in self.mailboxes:
                if box.mail == message:
                    add = False
                    break

            if add:
                add_mail(message)

    def set_thread(self, thread):
        if self.threadid is not None:
            new_thread = deep_search(thread, "threadId")
            if new_thread == self.threadid:
                self.__add_messages(thread)
                self.redactor.reset()

        else:
            if self.mailboxes != []:
                self.clear()

            self.thread = thread
            self.threadid = deep_search(self.thread, "threadId")

            self.headerbox.set_data(thread)
            self.redactor.set_thread(thread)
            self.__add_messages(thread)

            self.show_all()

    def set_profile(self, profile):
        self.redactor.set_profile(profile)

    def clear(self):
        while self.mailboxes != []:
            box = self.mailboxes[0]
            self.mailboxes_canvas.remove(box)
            self.mailboxes.remove(box)
            del box

        del self.mailboxes
        self.mailboxes = []

        del self.thread
        self.thread = None

        del self.threadid
        self.threadid = None
