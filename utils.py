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


def get_label_name(label_id):
    if label_id in ["CATEGORY_PERSONAL"]:#, "CATEGORY_SOCIAL", "CATEGORY_FORUMS", "CATEGORY_UPDATES"]:
        return _("Received")

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

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
    month = str(months.index(month) + 1).zfill(2)

    if True:  # TODO: get format
        return "%s/%s/%s" % (day, month, year)
    else:
        return "%s/%s/%s" % (month, day, year)
