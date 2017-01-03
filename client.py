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

import os
import httplib2
import threading

from constants import TABS

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import gi
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk
from gi.repository import GObject

SCOPES = "https://mail.google.com/"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Sugar Gmail"
CREDENTIALS_FILE = os.path.expanduser("~/.gmail-credentials.json")


class Client(GObject.GObject):

    __gsignals__ = {
        "profile-loaded": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
        "loading": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
        "loaded": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT]),
        "thread-loaded": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
        "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.credentials = None
        self.service = None

    def __load(self):
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build("gmail", "v1", http=http)
        
        profile = self.service.users().getProfile(userId="me").execute()
        self.emit("profile-loaded", profile)

        threads = {}
        for tab in TABS:
            results = self.service.users().threads().list(userId="me", labelIds=tab, maxResults=25).execute()
            threads[tab] = results.get("threads", [])

        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get("labels", [])

        self.emit("loaded", threads, labels)

    def request_thread(self, threadid):
        if self.service is None:
            return

        self.emit("loading")

        thread = self.service.users().threads().get(userId="me", id=threadid).execute()
        self.emit("thread-loaded", thread)

    def start(self):
        self.emit("loading")

        if self.credentials is None:
            try:
                self.credentials = self.get_credentials()
            except:
                self.emit("error")

        try:
            self.__load()
        except:
            self.emit("error")

    def send(self, mail):
        if self.service is None:
            return

        new_data = self.service.users().messages().send(userId="me", body=mail).execute()

    def get_credentials(self):
        store = Storage(CREDENTIALS_FILE)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
        
        return credentials
