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

from client import Client
from mail_viewer import MailViewer
from loading_view import LoadingView
from mails_listbox import MailsListBox

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject


class ViewType:
    LOADING = 0
    MAILS_LIST = 1
    MAIL = 2


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.view_type = None

        self.set_title("Client")
        self.set_default_size(680, 480)
        self.maximize()
        self.connect("destroy", Gtk.main_quit)

        self.client = Client()
        self.client.connect("profile-loaded", self.__profile_loaded_cb)
        self.client.connect("loading", self.__start_load)
        self.client.connect("loaded", self.__end_load)
        self.client.connect("thread-loaded", self.__thread_loaded_cb)
        self.client.connect("message-loaded", self.__message_loaded_cb)

        hbox = Gtk.HBox()
        self.add(hbox)

        self.view_box = Gtk.VBox()
        hbox.pack_start(self.view_box, True, True, 0)

        self.loading_view = LoadingView()

        self.mails_listbox = MailsListBox()
        self.mails_listbox.connect("label-selected", self.__label_selected_cb)
        self.mails_listbox.connect("thread-selected", self.__thread_selected_cb)

        self.mail_viewer = MailViewer()

        self.client.start()

        self.show_all()

    def __profile_loaded_cb(self, client):
        self.loading_view.set_profile(self.client.get_profile())

    def __start_load(self, client):
        self.set_view(ViewType.LOADING)

    def __end_load(self, client):
        def load_data():
            self.mails_listbox.set_threads(self.client.get_threads())
            self.mails_listbox.set_labels(self.client.get_labels())

        self.loading_view.stop()
        self.set_view(ViewType.MAILS_LIST)
        GObject.idle_add(load_data)

    def __thread_loaded_cb(self, client, threadid):
        thread = self.client.get_thread(threadid)
        self.mail_viewer.set_thread(thread)
        self.set_view(ViewType.MAIL)

    def __message_loaded_cb(self, client, messageid):
        message = self.client.get_message(messageid)
        print messageid, message

    def __label_selected_cb(self, view, labelid):
        print "LABEL SELECTED", labelid

    def __thread_selected_cb(self, view, threadid):
        self.set_view(ViewType.LOADING)
        self.client.request_thread(threadid)

    def set_view(self, view_type):
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

        elif self.view_type == ViewType.MAIL:
            child = self.mail_viewer

        if child is not None:
            self.view_box.pack_start(child, True, True, 0)

        self.show_all()


if __name__ == "__main__":
    win = Window()
    Gtk.main()