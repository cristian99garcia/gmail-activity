#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016, Cristian García <cristian99garcia@gmail.com>
#
# self library is free software you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation either
# version 3 of the License, or (at your option) any later version.
#
# self library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with self library if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys
import base64

from gettext import gettext as _

from utils import get_string_dict
from utils import get_string_list
from utils import unicode_to_string
from utils import make_html_from_text
from utils import get_current_date_string

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject


class Editor(Gtk.TextView):

    __gsignals__ = {
        "changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
        "update-buttons": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self, placeholder=None):
        Gtk.TextView.__init__(self)

        self.placeholder = placeholder
        self.text = ""
        self.cursor_position = 0

        if hasattr(self, "set_top_margin"):
            self.set_top_margin(5)

        if hasattr(self, "set_bottom_margin"):
            self.set_bottom_margin(5)

        self.set_left_margin(5)
        self.set_right_margin(5)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.buffer = self.get_buffer()
        self.tag_bold = self.buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tag_italic = self.buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tag_underline = self.buffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.buffer.connect("mark-set", self.__mark_set_cb)

        self.reset()

        self.connect("button-press-event", self.__button_press_cb)
        self.connect("key-release-event", self.__key_release_cb)

    def __mark_set_cb(self, widget, location, mark):
        if self.buffer.props.cursor_position != self.cursor_position:
            self.cursor_position = self.buffer.props.cursor_position
            self.emit("update-buttons")

    def __button_press_cb(self, button, event):
        if event.button == 1 and not self.edited:
            self.edited = True
            self.buffer.set_text("")

    def __key_release_cb(self, button, event):
        if not self.edited:
            self.edited = True
            self.buffer.set_text("")

        else:
            text = self.get_text()
            if self.text != text:
                self.text = text
                self.emit("changed")

    def reset(self):
        self.edited = False

        if self.placeholder is not None:
            self.buffer.set_text(self.placeholder)

    def get_text(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, False)

    def get_text_with_tags(self):
        start, end = self.buffer.get_bounds()
        text = ""
        bold = False
        italic = False
        underline = False
        for x in range(start.get_offset(), end.get_offset() + 1):
            iter = self.buffer.get_iter_at_offset(x)
            char = self.buffer.get_text(start, iter, False)
            start = iter

            text += char

            if iter.has_tag(self.tag_bold) and not bold:
                bold = True
                text += "<b>"

            elif not iter.has_tag(self.tag_bold) and bold:
                bold = False
                text += "</b>"

            if iter.has_tag(self.tag_italic) and not italic:
                italic = True
                text += "<i>"

            elif not iter.has_tag(self.tag_italic) and italic:
                italic = False
                text += "</i>"

            if iter.has_tag(self.tag_underline) and not underline:
                underline = True
                text += "<u>"

            elif not iter.has_tag(self.tag_underline) and underline:
                underline = False
                text += "</u>"

        return text

    def apply_bold(self):
        self.apply_tag(self.tag_bold)

    def remove_bold(self):
        self.remove_tag(self.tag_bold)

    def apply_italic(self):
        self.apply_tag(self.tag_italic)

    def remove_italic(self):
        self.remove_tag(self.tag_italic)

    def apply_underline(self):
        self.apply_tag(self.tag_underline)

    def remove_underline(self):
        self.remove_tag(self.tag_underline)

    def apply_tag(self, tag):
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            iter = self.buffer.get_iter_at_offset(self.buffer.props.cursor_position)
            bounds = (iter, iter)

        start, end = bounds
        self.buffer.apply_tag(tag, start, end)
        self.emit("changed")

    def remove_tag(self, tag):
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            iter = self.buffer.get_iter_at_offset(self.buffer.props.cursor_position)
            bounds = (iter, iter)

        start, end = bounds
        self.buffer.remove_tag(tag, start, end)
        self.emit("changed")

    def get_bold_at_cursor(self):
        return self.get_tag_at_cursor(self.tag_bold)

    def get_italic_at_cursor(self):
        return self.get_tag_at_cursor(self.tag_italic)

    def get_underline_at_cursor(self):
        return self.get_tag_at_cursor(self.tag_underline)

    def get_tag_at_cursor(self, tag):
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            iter = self.buffer.get_iter_at_offset(self.buffer.props.cursor_position - 1)
            return iter.has_tag(tag)

        else:
            start, end = bounds
            for x in range(start.get_offset(), end.get_offset()):
                iter = self.buffer.get_iter_at_offset(x)
                if not iter.has_tag(tag):
                    return False

            return True


class RemoveButton(Gtk.EventBox):

    __gsignals__ = {
        "clicked": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        image = Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        self.add(image)

        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        self.connect("realize", self.__realize_cb)
        self.connect("button-release-event", self.__button_release_cb)

    def __realize_cb(self, widget):
        win = self.get_window()
        win.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def __button_release_cb(self, widget, event):
        if event.button == 1:
            self.emit("clicked")


class AddressBox(Gtk.HBox):

    __gsignals__ = {
        "remove-me": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self, address, anchor):
        Gtk.HBox.__init__(self)

        self.address = address
        self.anchor = anchor

        self.set_margin_left(5)
        self.set_margin_right(5)

        self.label = Gtk.Label(self.address.split("@")[0])
        self.pack_start(self.label, False, False, 0)

        self.button = RemoveButton()
        self.button.connect("clicked", self.__remove_cb)
        self.pack_end(self.button, False, False, 0)

        self.show_all()

    def __remove_cb(self, button):
        self.emit("remove-me")


class EntryBox(Gtk.HBox):

    __gsignals__ = {
        "changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
        "activate": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING]),
    }

    def __init__(self, text):
        Gtk.HBox.__init__(self)

        self.label = Gtk.Label()
        self.label.set_text(text)
        self.label.set_margin_left(5)
        self.label.set_margin_right(5)
        self.label.props.xalign = 0

        self.view = Gtk.TextView()
        self.view.set_left_margin(5)
        self.view.set_right_margin(5)
        self.view.set_hexpand(True)

        if hasattr(self.view, "set_top_margin"):
            self.view.set_top_margin(5)

        if hasattr(self.view, "set_bottom_margin"):
            self.view.set_bottom_margin(5)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add(self.view)

        self.buffer = self.view.get_buffer()

    def get_text(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, 1)


class AddressEntry(EntryBox):

    def __init__(self, text):
        EntryBox.__init__(self, text)

        self.boxes = []

        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.connect("key-press-event", self.__key_press_cb)

    def __key_press_cb(self, view, event):
        start, end = self.buffer.get_bounds()
        address = self.buffer.get_text(start, end, 1).split(" ")[-1]
        pos = self.buffer.props.cursor_position

        ignore_keys = [Gdk.KEY_Return, Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Home]
        if event.keyval in ignore_keys:
            return True

        elif event.keyval in [Gdk.KEY_space, Gdk.KEY_Tab]:
            if address.strip() != "":
                for x in range(0, len(address)):
                    self.buffer.backspace(end, False, True)
                    end = self.buffer.get_end_iter()

                anchor = self.buffer.create_child_anchor(end)
                box = AddressBox(address, anchor)
                box.connect("remove-me", self.__remove_box)
                self.view.add_child_at_anchor(box, anchor)

                self.boxes.append(box)

            return True

        elif event.keyval == Gdk.KEY_BackSpace:
            if pos > 0:
                for box in self.boxes:
                    iter = self.buffer.get_iter_at_child_anchor(box.anchor)
                    if iter.get_offset() == pos - 1:
                        self.__remove_box(box)
                        return True

        elif event.keyval == Gdk.KEY_Left:
            if pos - 1 < len(self.boxes):
                return True

    def __remove_box(self, box):
        iter = self.buffer.get_iter_at_child_anchor(box.anchor)
        iter = self.buffer.get_iter_at_offset(iter.get_offset() + 1)
        self.buffer.backspace(iter, False, True)
        end = self.buffer.get_end_iter()
        self.buffer.place_cursor(end)

        self.boxes.remove(box)
        del box

    def get_text(self):
        text = ""
        for box in self.boxes:
            text += box.address + " "

        return text


class Redactor(Gtk.VBox):

    __gsignals__ = {
        "send": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
    }

    def __init__(self, thread=None):
        Gtk.VBox.__init__(self)

        self.thread = None
        self.profile = None
        self.__change_style = True

        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_left(8)
        self.set_margin_right(8)

        self.to_entry = AddressEntry(_("To:"))
        self.cc_entry = AddressEntry(_("Cc:"))
        self.cco_entry = AddressEntry(_("Cco:"))
        self.subject_entry = EntryBox(_("Subject:"))

        self.grid = Gtk.Grid()
        self.pack_start(self.grid, False, False, 0)

        if self.thread is None:
            self.grid.attach(self.to_entry.label,  0, 0, 1, 1)
            self.grid.attach(self.to_entry.scroll, 1, 0, 1, 1)

            self.grid.attach(self.cc_entry.label,  0, 1, 1, 1)
            self.grid.attach(self.cc_entry.scroll, 1, 1, 1, 1)

            self.grid.attach(self.cco_entry.label,  0, 2, 1, 1)
            self.grid.attach(self.cco_entry.scroll, 1, 2, 1, 1)

            self.grid.attach(self.subject_entry.label,   0, 3, 1, 1)
            self.grid.attach(self.subject_entry.scroll,  1, 3, 1, 1)

        self.editorbox = Gtk.VBox()
        self.pack_start(self.editorbox, True, True, 5)

        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(100, 200)
        self.editorbox.pack_start(scroll, True, True, 0)

        self.editor = Editor()
        self.editor.connect("update-buttons", self.__update_buttons_cb)
        scroll.add(self.editor)

        self.make_toolbar()

        self.show_all()

    def __update_buttons_cb(self, editor):
        self.__change_style = False
        self.button_bold.set_active(self.editor.get_bold_at_cursor())
        self.button_italic.set_active(self.editor.get_italic_at_cursor())
        self.button_underline.set_active(self.editor.get_underline_at_cursor())
        self.__change_style = True

    def make_toolbar(self):
        toolbar = Gtk.Toolbar()
        self.editorbox.pack_end(toolbar, False, False, 0)

        self.button_bold = Gtk.ToggleToolButton()
        self.button_bold.set_tooltip_text(_("Bold"))
        self.button_bold.set_icon_name("format-text-bold-symbolic")
        self.button_bold.connect("toggled", self._toggle_bold)
        toolbar.insert(self.button_bold, -1)

        self.button_italic = Gtk.ToggleToolButton()
        self.button_italic.set_tooltip_text(_("Italic"))
        self.button_italic.set_icon_name("format-text-italic-symbolic")
        self.button_italic.connect("toggled", self._toggle_italic)
        toolbar.insert(self.button_italic, -1)

        self.button_underline = Gtk.ToggleToolButton()
        self.button_underline.set_tooltip_text(_("Underline"))
        self.button_underline.set_icon_name("format-text-underline-symbolic")
        self.button_underline.connect("toggled", self._toggle_underline)
        toolbar.insert(self.button_underline, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar.insert(separator, -1)

        self.button_send = Gtk.ToolButton()
        self.button_send.set_icon_name("mail-send-symbolic")
        self.button_send.set_tooltip_text(_("Send"))
        self.button_send.connect("clicked", self._send_cb)
        toolbar.insert(self.button_send, -1)

    def set_profile(self, profile):
        del self.profile
        self.profile = get_string_dict(profile)

    def set_thread(self, thread, remove_entries=True):
        del self.thread
        self.thread = thread
        self.editor.placeholder = _("Click here if you want reply or forward the message")
        self.editor.reset()

        if remove_entries and self.grid.get_parent() == self:
            self.remove(self.grid)

    def get_data(self):
        html = make_html_from_text(self.editor.get_text_with_tags())
        encoded = base64.urlsafe_b64encode(html)
        threadid = None
        address = None
        labels = ["SENT"]

        if self.thread is not None:
            threadid = unicode_to_string(self.thread["payload"]["threadId"])
            labels = get_string_list(self.thread["payload"]["labelIds"])

        if self.profile is not None:
            address = self.profile["emailAddress"]

        body = {
            "data": encoded,
            "size": sys.getsizeof(encoded),
        }

        headers = [
            {
                "name": "MIME-Version",
                "value": "1.0"
            },
            {
                "name": "Date",
                "value": get_current_date_string()
            },
            {
                "name": "Subject",
                "value": self.subject_entry.get_text()
            },
            {
                "name": "Content-Type",
                "value": "text/html; charset=UTF-8"
            }
        ]

        if address is not None:
            headers.append({ "name": "From", "value": address })

        if self.to_entry.get_text().strip() != "":
            recipients = self.to_entry.get_text().split(" ")
            headers.append({ "name": "To", "value": recipients[0] })  # TODO: send to all

        message = {
            "payload": {
                "body": body,
                "mimeType": "text/html",
                "partId": "0",
                "filename": "",
                "headers": headers,
                "parts": [],
            },
            "snippet": self.editor.get_text().replace("\n", " ")[:100],
            "sizeEstimate": sys.getsizeof(encoded),
            "labelIds": labels,
        }

        if threadid is not None:
            message["threadId"] = threadid

        return message

    def _toggle_bold(self, button):
        if self.__change_style:
            if button.get_active():
                self.editor.apply_bold()
            else:
                self.editor.remove_bold()

    def _toggle_italic(self, button):
        if self.__change_style:
            if button.get_active():
                self.editor.apply_italic()
            else:
                self.editor.remove_italic()

    def _toggle_underline(self, button):
        if self.__change_style:
            if button.get_active():
                self.editor.apply_underline()
            else:
                self.editor.remove_underline()

    def _send_cb(self, button):
        data = self.get_data()
        self.emit("send", data)


class Window(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.view_type = None

        self.set_default_size(680, 480)
        self.connect("destroy", Gtk.main_quit)

        box = Gtk.VBox()
        self.add(box)

        self.redactor = Redactor()
        self.redactor.connect("send", self._send_cb)
        box.pack_start(self.redactor, True, True, 0)

        self.show_all()

    def _send_cb(self, redactor, data):
        print data


if __name__ == "__main__":
    win = Window()
    Gtk.main()
