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
import base64

from gettext import gettext as _

TABS = ["", "", "", "", ""]


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

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month = str(months.index(month) + 1).zfill(2)

    if True:  # TODO: get format
        return "%s/%s/%s" % (day, month, year)
    else:
        return "%s/%s/%s" % (month, day, year)


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
        if not url in replaced_urls:
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

    splitter = "<div class=\"gmail_extra\">"

    if parts == []:
        print "NO TIENE PARTS", message
        return

    for part in parts:
        if part["mimeType"] == "text/html":
            html = base64.urlsafe_b64decode(str(part["body"]["data"]))
            if splitter in html:
                message_html = html.split(splitter)[0]
                extra_html = splitter + html.split(splitter, 1)[1]
            else:
                message_html = html

        elif part["mimeType"] == "text/plain":
            message_html = make_html_from_text(base64.decodestring(str(part["body"]["data"])))

        elif part["mimeType"] == "image/jpeg":
            """
            with open(part["filename"], "wb") as file:
                file.write(base64.decodestring(part["body"]["attachmentId"]))
            """

    return message_html, extra_html
