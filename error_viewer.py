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

from center_box import CenterBox
from gettext import gettext as _

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Pango


class ErrorViewer(CenterBox):

    def __init__(self):
        CenterBox.__init__(self)

        message_box = Gtk.VBox()
        self.set_center_child(message_box)

        label = Gtk.Label(_("An error occurred."))
        label.modify_font(Pango.FontDescription("30"))
        message_box.pack_start(label, False, False, 5)

        label = Gtk.Label(_("Check the connection and try again later."))
        label.modify_font(Pango.FontDescription("18"))
        message_box.pack_start(label, False, False, 0)
