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
    ERROR      = 4


class GmailCanvas(Gtk.VBox):

    __gsignals__ = {
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
        self.error_viewer = ErrorViewer()

        self.connect("realize", self.__realize_cb)

        self.show_all()

    def __realize_cb(self, widget):
        thread = threading.Thread(target=self.client.start)
        thread.start()

    def __profile_loaded_cb(self, client, profile):
        self.loading_view.set_profile(profile)

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

    def set_view(self, view_type, emit=True):
        if view_type == self.view_type:
            return

        self.view_type = view_type

        if self.view_box.get_children() != []:
            self.view_box.remove(self.view_box.get_children()[0])

        child = None
        if self.view_type == ViewType.LOADING:
            self.loading_view.start()
            child = self.loading_view

        elif self.view_type == ViewType.MAILS_LIST:
            child = self.mails_listbox
            self.loading_view.stop()

        elif self.view_type == ViewType.MAIL:
            child = self.mail_viewer
            self.loading_view.stop()

        elif self.view_type == ViewType.ERROR:
            child = self.error_viewer

        if child is not None:
            self.view_box.pack_start(child, True, True, 0)

        if emit:
            invalids = [ViewType.MAIL, ViewType.NULL, ViewType.LOADING]
            self.forward_view = ViewType.NULL if self.view_type in invalids else self.forward_view
            self.emit("history-changed")

        self.show_all()

    def can_go_back(self):
        return self.view_type in [ViewType.MAIL]

    def can_go_forward(self):
        return self.forward_view not in [ViewType.NULL, ViewType.ERROR]

    def go_back(self):
        current = self.view_type
        self.set_view(ViewType.MAILS_LIST, False)
        self.forward_view = current
        self.emit("history-changed")

    def go_forward(self):
        self.set_view(self.forward_view, False)
        self.forward_view = None
        self.emit("history-changed")
