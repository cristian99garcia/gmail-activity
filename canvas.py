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

import threading

from client import Client
from redactor import Redactor
from mail_viewer import MailViewer
from error_viewer import ErrorViewer
from loading_view import LoadingView
from mails_listbox import MailsListBox

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject


class ViewType:
    NULL       = 0
    LOADING    = 1
    MAILS_LIST = 2
    MAIL       = 3
    REDACT     = 4
    ERROR      = 5


class GmailCanvas(Gtk.VBox):

    __gsignals__ = {
        "update-buttons": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
        "history-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.view_type = ViewType.NULL
        self.forward_view = ViewType.NULL

        self.client = Client()
        self.client.connect("profile-loaded", self.__profile_loaded_cb)
        self.client.connect("loading", self.__start_load)
        self.client.connect("loaded", self.__end_load)
        self.client.connect("thread-loaded", self.__thread_loaded_cb)
        self.client.connect("error", self.__error_cb)

        self.view_box = Gtk.VBox()
        self.pack_start(self.view_box, True, True, 0)

        self.loading_view = LoadingView()

        self.mails_listbox = MailsListBox()
        self.mails_listbox.connect("label-selected", self.__label_selected_cb)
        self.mails_listbox.connect("thread-selected", self.__thread_selected_cb)

        self.mail_viewer = MailViewer()
        self.redactor = Redactor()
        self.error_viewer = ErrorViewer()

        self.viewers = {
            ViewType.LOADING: self.loading_view,
            ViewType.MAILS_LIST: self.mails_listbox,
            ViewType.MAIL: self.mail_viewer,
            ViewType.REDACT: self.redactor,
            ViewType.ERROR: self.error_viewer,
        }

        self.connect("realize", self.__realize_cb)

        self.show_all()

    def __realize_cb(self, widget):
        thread = threading.Thread(target=self.client.start)
        thread.start()

    def __profile_loaded_cb(self, client, profile):
        self.loading_view.set_profile(profile)
        self.mail_viewer.set_profile(profile)

    def __start_load(self, client):
        self.set_view(ViewType.LOADING)

    def __end_load(self, client, threads, labels):
        self.loading_view.stop()
        self.set_view(ViewType.MAILS_LIST)

        GLib.idle_add(self.mails_listbox.set_threads, threads)
        GLib.idle_add(self.mails_listbox.set_labels, labels)

    def __thread_loaded_cb(self, client, thread):
        self.mail_viewer.set_thread(thread)
        self.set_view(ViewType.MAIL)

    def __error_cb(self, client):
        self.set_view(ViewType.ERROR)

    def __label_selected_cb(self, view, labelid):
        print "LABEL SELECTED", labelid

    def __thread_selected_cb(self, view, threadid):
        #thread = threading.Thread(target=self.client.request_thread, args=(threadid,))
        #thread.start()
        self.client.request_thread(threadid)

    def __update_buttons(self):
        invalids = [ViewType.NULL, ViewType.LOADING]
        self.forward_view = ViewType.NULL if self.view_type in invalids else self.forward_view
        print self.forward_view

        data = {
            "back": self.view_type in [ViewType.MAIL, ViewType.REDACT],
            "forward": self.forward_view not in [ViewType.NULL, ViewType.ERROR],
            "redact": self.view_type == ViewType.MAILS_LIST
        }

        self.emit("update-buttons", data)

    def show_redactor(self):
        self.set_view(ViewType.REDACT, False)
        self.forward_view = ViewType.NULL
        self.__update_buttons()

    def set_view(self, view_type, emit=True):
        if view_type == self.view_type:
            return

        self.view_type = view_type

        if self.view_box.get_children() != []:
            self.view_box.remove(self.view_box.get_children()[0])

        child = None
        if self.view_type in self.viewers.keys():
            child = self.viewers[self.view_type]

        if self.view_type == ViewType.LOADING:
            self.loading_view.start()
        else:
            self.loading_view.stop()

        if child is not None:
            self.view_box.pack_start(child, True, True, 0)

        if emit:
            self.__update_buttons()

        self.show_all()

    def go_back(self):
        current = self.view_type
        self.set_view(ViewType.MAILS_LIST, False)
        self.forward_view = current

        self.__update_buttons()

    def go_forward(self):
        self.set_view(self.forward_view)
        self.forward_view = ViewType.NULL

        self.__update_buttons()
