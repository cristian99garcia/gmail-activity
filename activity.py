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

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton

from canvas import GmailCanvas


class Gmail(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.make_toolbar()

        self.canvas = GmailCanvas()
        self.set_canvas(self.canvas)

        self.show_all()

    def make_toolbar(self):
        toolbarbox = ToolbarBox()
        self.set_toolbar_box(toolbarbox)

        button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(button, -1)

        toolbarbox.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)

        button = StopButton(self)
        toolbarbox.toolbar.insert(button, -1)

