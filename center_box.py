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

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk


class CenterBox(Gtk.VBox):

    def __init__(self, child=None):
        Gtk.VBox.__init__(self)

        self.__child = child

        self.__hbox = Gtk.HBox()
        if self.__child:
            self.__hbox.pack_start(self.__child, True, False, 0)

        self.pack_start(self.__hbox, True, False, 0)

    def set_center_child(self, widget):
        if self.__child != None:
            self.__hbox.remove(self.__child)

        self.__child = widget
        if self.__child != None:
            self.__hbox.pack_start(self.__child, True, False, 0)