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

from gi.repository import GObject

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

except ImportError:
    flags = None


SCOPES = "https://mail.google.com/"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Sugar Gmail"
CREDENTIALS_FILE = os.path.expanduser("~/.gmail-credentials.json")


class Client(GObject.GObject):

    __gsignals__ = {
        "profile-loaded": (GObject.SIGNAL_RUN_LAST, None, []),
        "loading": (GObject.SIGNAL_RUN_LAST, None, []),
        "loaded": (GObject.SIGNAL_RUN_LAST, None, []),
        "thread-loaded": (GObject.SIGNAL_RUN_LAST, None, [str]),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.credentials = None
        self.service = None
        self.profile = {}
        self.threads = {}
        self.loaded_threads = {}
        self.labels = {}
        self.thread = {}

    def __load(self):
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build("gmail", "v1", http=http)
        
        self.profile = self.service.users().getProfile(userId="me").execute()
        self.emit("profile-loaded")

        for tab in TABS:
            results = self.service.users().threads().list(userId="me", labelIds=tab, maxResults=25).execute()
            self.threads[tab] = results.get("threads", [])

        results = self.service.users().labels().list(userId='me').execute()
        self.labels = results.get("labels", [])

        self.emit("loaded")

    def __load_thread(self, threadid):
        if self.service is None:
            return

        thread = self.service.users().threads().get(userId="me", id=threadid).execute()
        self.loaded_threads[threadid] = thread
        self.emit("thread-loaded", threadid)

    def start(self):
        self.load()

    def load(self):
        self.emit("loading")

        if self.credentials is None:
            self.credentials = self.get_credentials()

        thread = threading.Thread(target=self.__load)
        thread.start()

    def get_profile(self):
        return self.profile

    def get_threads(self):
        return self.threads

    def get_labels(self):
        return self.labels

    def get_thread(self, threadid):
        if threadid in self.loaded_threads:
            return self.loaded_threads[threadid]

    def get_credentials(self):
        store = Storage(CREDENTIALS_FILE)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME

            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                credentials = tools.run(flow, store)
        
        return credentials

    def request_thread(self, threadid):
        thread = threading.Thread(target=self.__load_thread, args=(threadid,))
        thread.run()
