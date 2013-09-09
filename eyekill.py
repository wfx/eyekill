#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Wolfgang Morawetz.
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Thank's to: 
# kuuko,and davemds from e/irc.
# hbytes 99.99% based on the code from http://www.guguncube.com
#
#
# version: 0.9 (bug hunt)
#
# TODO: Testing
#       Code cleanup
#       Paint a application icon
#
#


import os
import signal
import psutil
import elementary
import edje
import ecore
import evas

def destroy(obj):
    elementary.exit()

# - Application - {{{
def app(userid = os.getuid()):
    # Main Window
    global win, main_box
    win = elementary.Window("my app", elementary.ELM_WIN_BASIC)
    win.title_set("eye kill")
    win.callback_delete_request_add(destroy)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    # View: Information(PID)
    #       Box
    main_box = elementary.Box(win)
    main_box.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    win.resize_object_add(main_box)
    main_box.show()
    #       Box -> Frame
    info_frame = elementary.Frame(win)
    info_frame.text_set("Information")
    main_box.pack_end(info_frame)
    info_frame.show()
    #       Box -> Frame -> Label (default Information)
    lb = elementary.Label(win)
    lb.text_set('<b>Kill process with a double klick</b>')
    info_frame.content_set(lb)
    lb.show()

    # View: PID List
    #       Box -> GenList
    ps_list = elementary.List(win)
    ps_list.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    ps_list.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    ps_list.callback_clicked_double_add(kill_bill)
    pid_list = psutil.get_pid_list()
    for i in pid_list:
        ps = psutil.Process(i)
        if (ps.uids.real == userid):
            short_info = '%s / %s / %s' % (ps.pid, ps.name, ps.status)
            ps_list.item_append(label = short_info, callback = update_info, ps=ps, lb=lb)

    main_box.pack_end(ps_list)
    ps_list.go()
    ps_list.show()
    
    # View: Application
    win.resize(320, 384)
    win.show()
#}}}

# - Label Process information - {{{
def update_info(li, it, lb, ps):
    info = \
        ("<b>PID: <i>%i</i></b>, <b>Name :<i>%s</i></b></br><b>Memory (vms) :<i>%s</i><b>, <b>CPU: <i>%s</i><b>, <b>State: <i>%s</i><b>" % \
        (ps.pid, ps.name, hbytes(ps.get_memory_info().vms), ps.get_cpu_percent(interval=.1), ps.status ))
    lb.text_set(info)
#}}}

# - Kill Bill :-) - {{{
def kill_bill(obj, cb_data):
    bill = cb_data.data_get()[1]['ps'].pid
    print ("Bill %s ... Gotcha" % bill)
    os.kill(bill, signal.SIGTERM)
    if (os.kill(bill, 0)):
        os.kill(bill, signal.SIGKILL)
    item = obj.selected_item_get()
    item.disabled_set(True)
#}}}


# - Human Bytes from Guguncube - {{{
def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.2f%s" % (num, x)
        num /= 1024.0
    return "%3.2f%s" % (num, 'TB')
#}}}


if __name__ == "__main__":
    elementary.init()
    app()
    elementary.run()
    elementary.shutdown()

# vim:foldmethod=marker 
