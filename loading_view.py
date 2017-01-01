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
from center_box import CenterBox

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject


class LoadingView(CenterBox):

    def __init__(self):
        CenterBox.__init__(self)

        self._tid = None

        vbox = Gtk.VBox()
        self.set_center_child(vbox)

        self.bar = Gtk.ProgressBar()
        self.bar.set_size_request(300, 3)
        vbox.pack_start(self.bar, False, False, 20)

        self.adress_label = Gtk.Label(_("Loading"))
        vbox.pack_start(self.adress_label, False, False, 0)

        self.show_all()

    def __advance(self):
        self.bar.pulse()
        return True

    def start(self):
        self._tid = GObject.timeout_add(200, self.__advance)

    def stop(self):
        if self._tid is not None:
            GObject.source_remove(self._tid)
            self._tid = None

    def set_profile(self, profile):
        self.profile = profile
        self.adress_label.set_text(self.profile["emailAddress"])
