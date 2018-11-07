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
from browser import Browser

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

import re


class LoginScreen(Gtk.VBox):

    __gsignals__ = {
        "send-code": (
            GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]
        ),
    }

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.browser = Browser()
        self.browser.browser.connect("web-process-terminated", self._web_process_terminated_cb)
        self.pack_start(self.browser, True, True, 10)

    def _load_finished_cb(self, browser, html):
        if "<title>Success code=" in html:
            code = re.search(r"<title>Success code=(.+)</title>", html).group(1)
            self.emit("send-code", code)

    def set_url(self, url):
        self.browser.browser.load_uri(url)
