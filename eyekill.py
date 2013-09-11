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
# TODO: - Testing
#       o Code cleanup
#       x Filter for all or Elementary processes
#       x Paint a application icon
#
#


import os
import signal
import psutil
import elementary
import edje
import ecore
import evas


class Application(object):


    def __init__(self, parent_pid = None):
        self.userid = os.getuid()
        self.parent_pid = parent_pid

        self.win = elementary.Window("my app", elementary.ELM_WIN_BASIC)
        self.win.title_set("eye kill")
        self.win.callback_delete_request_add(self.destroy)

        self.bg = elementary.Background(self.win)
        self.win.resize_object_add(self.bg)
        self.bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.bg.show()

        self.main_box = elementary.Box(self.win)
        self.main_box.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.win.resize_object_add(self.main_box)
        self.main_box.show()
        self.info_frame = elementary.Frame(self.win)
        self.info_frame.text_set("Information")
        self.main_box.pack_end(self.info_frame)
        self.info_frame.show()
        self.lb = elementary.Label(self.win)
        self.lb.text_set('<b>Kill process with a double click</b>')
        self.info_frame.content_set(self.lb)
        self.lb.show()

        self.ps_list = elementary.List(self.win)
        self.ps_list.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.ps_list.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.ps_list.callback_clicked_double_add(self.kill_bill)

        self.update_list()

        self.main_box.pack_end(self.ps_list)
        self.ps_list.go()
        self.ps_list.show()
    
        self.win.resize(320, 384)
        self.win.show()


    def destroy(self, obj):
        elementary.exit()


    def update_list(self):
        if self.parent_pid is None:
            pl = psutil.get_pid_list()
            for p in pl:
                p = psutil.Process(p)
                if p.uids.real == self.userid:
                    short_info = '%s / %s / %s' % (p.pid, p.name, p.status)
                    self.ps_list.item_append(label = short_info, callback = self.update_info, p = p)
        else:
            ps = psutil.Process(self.parent_pid)
            pl = ps.get_children(self.parent_pid)
            for p in pl:
                if p.uids.real == self.userid:
                    short_info = '%s / %s / %s' % (p.pid, p.name, p.status)
                    self.ps_list.item_append(label = short_info, callback = self.update_info, p = p)


    def update_info(self,li , it, p):
        info = ("PID %i STAT %s TIME %s<br/> MEM %s COMMAND %s" % \
                (p.pid, p.status, p.get_cpu_times().user, hbytes(p.get_memory_info().rss), p.name))
        self.lb.text_set(info)


    def kill_bill(self, obj, cb_data):
        bill = cb_data.data_get()[1]['p'].pid
        print ("Bill %s ... Gotcha" % bill)
        os.kill(bill, signal.SIGTERM)
        if (os.kill(bill, 0)):
            os.kill(bill, signal.SIGKILL)
        item = obj.selected_item_get()
        item.disabled_set(True)


def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.2f%s" % (num, x)
        num /= 1024.0
    return "%3.2f%s" % (num, 'TB')

def get_de():
    de = None
    p = psutil.get_process_list()
    for i in p:
        if (i.name == 'enlightenment'):
            de = i.pid
            print "found enlightenment"
    return de


if __name__ == "__main__":
    elementary.init()

    Application(get_de())
    
    elementary.run()
    elementary.shutdown()

# vim:foldmethod=marker 
