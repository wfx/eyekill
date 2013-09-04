#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Wolfgang Morawetz.
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# version: 0.1

import os
import signal
import psutil
import elementary
import edje
import ecore
import evas


def application(userid = os.getuid()):

    app_win = elementary.StandardWindow("Main", "Eye Kill")
    app_win.callback_delete_request_add(lambda o: elementary.exit())

    process_list = elementary.List(app_win)
    app_win.resize_object_add(process_list)
    process_list.size_hint_weight_set(evas.EVAS_HINT_EXPAND,evas.EVAS_HINT_EXPAND)
    update_process_list(process_list, userid)
    process_list.show()

    app_win.resize(420,426)
    app_win.show()


def update_process_list(process_list, userid):
    pid_list = psutil.get_pid_list()
    for i in pid_list:
        pid = psutil.Process(i)
        if (pid.uids.real == userid):
            process_list.item_append(pid.name, callback = process_list_menu, cb_data = pid)


def process_list_menu(li, it, cb_data):
    popup = elementary.Ctxpopup(li)
    #popup.item_append("Info", func = process_info, cb_data = cb_data)
    popup.item_append("Kill", func = process_kill, cb_data = cb_data)
    (x, y) = li.evas.pointer_canvas_xy_get()
    popup.move(x, y)
    popup.show()


def process_info(li, it, cb_data):
    pass


def process_kill(li, it, cb_data):
    os.kill(cb_data.pid, signal.SIGTERM)
    if (os.kill(cb_data.pid, 0)):
        os.kill(cb_data.pid, signal.SIGKILL)

if __name__ == "__main__":

    elementary.init()
    application()

    elementary.run()
    elementary.shutdown()
    
