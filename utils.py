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

import re
import time
import base64
import binascii
import unicodedata

from gettext import gettext as _

TABS = ["", "", "", "", ""]
MAIL_SPLITTERS = ["<div class=\"gmail_extra\">", "---------- Forwarded message ----------"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_label_name(label_id):
    if label_id == "CATEGORY_PERSONAL":
        return _("Principal")

    elif label_id == "CATEGORY_SOCIAL":
        return _("Social")

    elif label_id == "CATEGORY_PROMOTIONS":
        return _("Promotions")

    elif label_id == "CATEGORY_UPDATES":
        return _("Updates")

    elif label_id == "CATEGORY_FORUMS":
        return _("Forums")

    elif label_id == "STARRED":
        return _("Starred")

    elif label_id == "IMPORANT":
        return _("Important")

    elif label_id == "SENT":
        return _("Sent")

    elif label_id == "SPAM":
        return _("Spam")

    elif label_id == "TRASH":
        return _("Trash")

    else:
        return ""


def get_date_string(data):
    # data example: by 10.237.49.66 with HTTP; Wed, 14 Dec 2016 13:59:09 -0800 (PST)
    data = data.split(", ")[1]
    values = data.split(" ")
    day = values[0]
    month = values[1]
    year = values[2]
    time = values[3]

    month = str(MONTHS.index(month) + 1).zfill(2)

    if True:  # TODO: get local format
        return "%s/%s/%s" % (day, month, year)
    else:
        return "%s/%s/%s" % (month, day, year)


def get_current_date_string():
    data = time.localtime()
    date = "%s, %d %s %d %d:%d:%d -0300" % (
        DAYS[data.tm_wday],
        data.tm_mday,
        MONTHS[data.tm_mon - 1],
        data.tm_year,
        data.tm_hour,
        data.tm_min,
        data.tm_sec
    )

    # TODO: get and replace local timezone (-0300)
    return date


def decode64_string(text):
    try:
        return base64.decodestring(text)
    except binascii.Error:
        try:
            return text.decode("base64")
        except:
            return text


def unicode_to_string(unicode):
    return unicodedata.normalize("NFKD", unicode).encode("ascii", "ignore")


def get_string_dict(unicode_dict):
    new_dict = {}

    for key in unicode_dict.keys():
        value = unicode_dict[key]
        if type(key) == unicode:
            new_key = unicode_to_string(key)
        else:
            new_key = key

        if type(value) == unicode:
            new_value = unicode_to_string(value)
        else:
            new_value = value

        new_dict[new_key] = new_value

    return new_dict


def get_string_list(unicode_list):
    new_list = []

    for value in unicode_list:
        if type(value) == unicode:
            new_value = unicode_to_string(value)
        else:
            new_value = value

        new_list.append(new_value)

    return new_list


def convert_to_string(data, spacer=", "):
    text = ""
    if type(data) == list:
        max = len(data)

        for x in range(0, max):
            value = data[x]
            if type(value) == unicode:
                value = unicode_to_string(value)

            text += value
            if x < max - 1:
                text += spacer

        return text

    else:
        return data


def deep_search(data, value):
    if type(data) == dict:
        if value in data.keys():
            return data[value]
        else:
            for key in data.keys():
                found = deep_search(data[key], value)
                if found is not None:
                    return found

            return None

    elif type(data) in [list, tuple]:
        for key in data:
            found = deep_search(key, value)
            if found is not None:
                return found

        return None

    else:
        return None


def search_header(data, header_name, multiple=False, multiple_list=[]):
    def is_header_dict(value):
        if type(value) == dict:
            return "name" in value.keys() and "value" in value.keys()
        else:
            return False

    if type(data) == dict:
        if "headers" in data.keys():
            value = search_header(data["headers"], header_name, multiple, multiple_list)
            if multiple:
                multiple_list.append(value)
            else:
                return value

        elif is_header_dict(data) and data["name"] == header_name:
            if multiple:
                multiple_list.append(data["value"])
            else:
                return data["value"]

        else:
            for key in data:
                found = search_header(data[key], header_name, multiple, multiple_list)
                if found is not None:
                    if multiple:
                        multiple_list.append(found)
                    else:
                        return found

        return multiple_list if multiple else None

    elif type(data) == list:
        for value in data:
            if is_header_dict(value):
                if value["name"] == header_name:
                    if multiple:
                        multiple_list.append(value["value"])
                    else:
                        return value["value"]

            else:
                found = search_header(value, header_name)
                if found is not None:
                    if multiple:
                        multiple_list.append(found)
                    else:
                        return found

        return multiple_list if multiple else None

    else:
        return multiple_list if multiple else None



def clear_list(old_list, new_list=[]):
    while old_list in old_list:
        old_list.remove(old_list)

    while new_list in new_list:
        new_list.remove(new_list)

    for value in old_list:
        if type(value) == unicode:
            value = unicode_to_string(value)

        if type(value) == list:
            clear_list(value, new_list)

        if value not in new_list:
            new_list.append(value)

    return new_list


def get_urls(text):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)


def make_html_from_text(text):
    urls = get_urls(text)
    replaced_urls = []
    spaced_start_p = '<p style="margin-top: 15px; margin-bottom: 1px;">'
    start_p = '<p style="margin-top: 1px; margin-bottom: 1px;">'
    end_p = "</p>"

    idx = 0
    for url in urls:
        if url not in replaced_urls:
            text = text.replace(url, '<a href="###%d###">###%d###</a>' % (idx, idx))
            replaced_urls.append(url)
            idx += 1

    for x in range(0, len(replaced_urls)):
        text = text.replace(
            '<a href="###%d###">###%d###</a>' % (x, x),
            '<a href="%s">%s</a>' % (replaced_urls[x], replaced_urls[x]))

    text = text.replace('<a href="<a href="', '<a href="')
    html = text.replace("\n", end_p + start_p)
    html = html.replace(end_p + start_p + end_p + start_p, end_p + spaced_start_p)
    html = "<!DOCTYPE html><head></head><body>" + start_p + html + end_p + "</body>"
    return html


def get_message_parts(message):
    parts = []

    if "payload" in message.keys():
        if "parts" in message["payload"]:
            parts += message["payload"]["parts"]

        elif "body" in message["payload"]:
            part = {
                "body": message["payload"]["body"],
                "mimeType": message["payload"]["mimeType"],
            }

            parts.append(part)

    for part in parts:
        if "parts" in part.keys():
            parts += part["parts"]

    return parts


def load_html_data(message):
    message_html = None
    extra_html = None
    parts = get_message_parts(message)

    if parts == []:
        print "NO TIENE PARTS", message
        return

    for part in parts:
        if part["mimeType"] == "text/html":
            html = base64.urlsafe_b64decode(str(part["body"]["data"]))
            splitted = False
            for splitter in MAIL_SPLITTERS:
                if splitter in html:
                    message_html = html.split(splitter)[0]
                    extra_html = splitter + html.split(splitter, 1)[1]
                    splitted = True
                    break

            if not splitted:
                message_html = html

        elif part["mimeType"] == "text/plain":
            string = decode64_string(str(part["body"]["data"]))
            message_html = make_html_from_text(string)

        elif part["mimeType"] == "image/jpeg":
            """
            with open(part["filename"], "wb") as file:
                file.write(base64.decodestring(part["body"]["attachmentId"]))
            """

    return message_html, extra_html
