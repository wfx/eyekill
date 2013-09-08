#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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
# version: 0.2

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
    pid_list = elementary.Genlist(win)
    pid_list.callback_clicked_double_add(kill_bill)
    win.resize_object_add(pid_list)
    pid_list.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    pid_list.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    pid_list_itc = elementary.GenlistItemClass(
                        item_style="default",
                        text_get_func=pid_list_text_get,
                        content_get_func=pid_list_content_get,
                        state_get_func=pid_list_state_get)
    
    plist = psutil.get_pid_list()
    for i in plist:
        pid = psutil.Process(i)
        if (pid.uids.real == userid):
            pid_list.item_append(pid_list_itc, pid.pid, func=update_main_box)

    main_box.pack_end(pid_list)
    pid_list.show()

    
    # View: Application
    win.resize(432, 400)
    win.show()
#}}}

# - Label Process information - {{{
def update_main_box(gli, gl, *args, **kwargs):
    bill = psutil.Process(gli.data_get())
    print ("\n--- Process Information ---")
    print ("PID   : %s" % bill.pid)
    print ("Name  : %s" % bill.name)
    print ("Mem   : %s" % hbytes(bill.get_memory_info().vms))
    print ("CPU/P : %s" % bill.get_cpu_percent())
#}}}

# - Kill Bill :-) - {{{
def kill_bill(gli, gl):
    bill = gl.data_get()
    print ("Bill %s ... Gotcha" % bill)
    os.kill(bill, signal.SIGTERM)
    if (os.kill(bill, 0)):
        os.kill(bill, signal.SIGKILL)
    gli.delete()
#}}}

# - Pid List Text Get - {{{
def pid_list_text_get(obj, part, item_data):
    p = psutil.Process(item_data)
    return "%s :: %s" % (p.pid, p.name)
#}}}

# - Pid List Content Get - {{{
def pid_list_content_get(obj, part, data):
    ic = elementary.Icon(obj)
    ic.file_set("images/logo_small.png")
    ic.size_hint_aspect_set(evas.EVAS_ASPECT_CONTROL_VERTICAL, 1, 1)
    return ic
#}}}

# - Pid List State Get - {{{
def pid_list_state_get(obj, part, item_data):
    return False
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
