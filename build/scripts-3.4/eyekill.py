#!/usr/bin/python
# encoding: utf-8
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


__author__ = "Wolfgang Morawetz"
__copyright__ = "Copyright (C) 2014 Wolfgang Morawetz"
__version__ = "0.2014.08.16"
__description__ = 'A tiny taskkiller'
__github__ = 'https://github.com/wfx/eyekill'
__source__ = 'Source code and bug reports: {0}'.format(__github__)
PY_EFL = "https://git.enlightenment.org/bindings/python/python-efl.git/"


import os
import sys
import getopt
import signal
#psutil > 2.0 !!!
import psutil

try:
    from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
    from efl import elementary
    from efl.elementary.window import StandardWindow
    from efl.elementary.box import Box
    from efl.elementary.frame import Frame
    from efl.elementary.label import Label
    from efl.elementary.list import List
    from efl.elementary.button import Button
    from efl.elementary.panel import Panel, ELM_PANEL_ORIENT_LEFT
except ImportError:
    printErr("ImportError: Please install Python-EFL:\n ", PY_EFL)
    exit(1)

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

#   EyeKill
class Application(object):
    def __init__(self):
        self.cfg = ConfigOption()
        self.userid = os.getuid()
        self.win = None
        self.bg = None
        self.main_box = None
        self.info_frame = None
        self.lb = None
        self.ps_list = None

        self.win = StandardWindow("my app", "eyekill", size=(320, 384))
        self.win.title_set("eye kill")
        self.win.callback_delete_request_add(self.destroy)

        self.main_box = Box(self.win)
        self.main_box.size_hint_weight = EXPAND_BOTH
        self.win.resize_object_add(self.main_box)
        self.main_box.show()

        self.info_frame = Frame(self.win)
        self.info_frame.text_set("Information")
        self.main_box.pack_end(self.info_frame)
        self.info_frame.show()

        self.lb = Label(self.win)
        self.lb.text_set('<b>Kill process with a double click</b>')
        self.info_frame.content_set(self.lb)
        self.lb.show()

        self.ps_list = List(self.win)
        self.ps_list.size_hint_weight = EXPAND_BOTH
        self.ps_list.size_hint_align = FILL_BOTH
        self.ps_list.callback_clicked_double_add(self.kill_bill)

        self.update_list()

        self.main_box.pack_end(self.ps_list)
        self.ps_list.go()
        self.ps_list.show()
    
        self.win.resize(320, 384)
        self.win.show()


    def destroy(self, obj):
        # FIXME: but here self.cfg.save()???
        elementary.exit()


    def update_list(self):

        if bool(self.cfg.get_desktop()):
            for de in self.cfg.get_desktop():
                ps = psutil.Process(get_pid_by_name(de))
                pl = ps.children()
                for p in pl:
                    if p.uids().real == self.userid:
                        if p.name not in self.cfg.get_process():
                            short_info = '%s / %s / %s' % (p.pid, p.name(), p.status())
                            self.ps_list.item_append(label = short_info, callback = self.update_info, p = p)
        else:
            pl = psutil.get_pid_list()
            for p in pl:
                p = psutil.Process(p)
                if p.uids().real == self.userid:
                    if p.name() not in self.cfg.get_process():
                        short_info = '%s / %s / %s' % (p.pid, p.name(), p.status())
                        self.ps_list.item_append(label = short_info, callback = self.update_info, p = p)


    def update_info(self,li , it, p):
        info = ("PID %i STAT %s TIME %s<br/>MEM %s CPU %s COMMAND %s" % \
               (p.pid,\
                p.status(),\
                p.get_cpu_times().user,\
                hbytes(p.get_memory_info().rss),\
                p.get_cpu_percent(interval=0),\
                p.name()))
        self.lb.text_set(info)


    def kill_bill(self, obj, cb_data):
        bill = cb_data.data_get()[1]['p'].pid
        print ("%s ... Gotcha" % bill)
        os.kill(bill, signal.SIGTERM)
        if (os.kill(bill, 0)):
            os.kill(bill, signal.SIGKILL)
        item = obj.selected_item_get()
        item.disabled_set(True)

#   hbytes :
#   Recalculate byte's into a more readable format
def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.2f%s" % (num, x)
        num /= 1024.0
    return "%3.2f%s" % (num, 'TB')

#   get_pid_by_name :
#   Return False or PID by name
def get_pid_by_name(value):
    p = psutil.get_process_list()
    for i in p:
        if (i.name() == value):
            return i.pid
    return False

#   ConfigOption
class ConfigOption(object):
   
    def __init__(self):
        self.fname = "%s/.config/eyekill.conf" % os.environ['HOME']
        self.desktop = []
        self.process = []
        self.verbose = False
        self.load()
        self.cmdline_apply()

        
        if self.verbose:
            xy = self.get_desktop()
            print ("Desktop: item's: ",xy," True?: ",bool(xy)," Type: ",type(xy))
            xy = self.get_process()
            print ("process: item's: ",xy," True?: ",bool(xy)," Type: ",type(xy))

        self.desktop_cleanup()

        if self.verbose:
            xy = self.get_desktop()
            print ("Desktop cleaup: item's: ",xy," True?: ",bool(xy)," Type: ",type(xy))
        


    def load(self):
        try:
            with open(self.fname, "r") as p:
                for c in p:
                    c = self.str_cleanup(c)
                    param, value = c.split("=",1)
                    if param == 'process' and bool(value):
                        if bool(value) or value == 'None':
                            self.process = value.split(",")
                    elif param == 'desktop' and bool(value):
                        if not 'False' in value or value == '':
                            self.desktop = value.split(",")
        except IOError:
            pass
    

    def desktop_cleanup(self):
        for de in self.get_desktop():
            if not get_pid_by_name(de):
                print ("Warning: please remove desktop option: %s !" % de)
                self.del_desktop(de)


    def str_cleanup(self, value):
        value = value.replace(" ","")
        value = value.replace("\n","")
        value = value.replace("'","")
        value = value.replace("\"","")
        return value
    

    def cmdline_apply(self):
        (cmd_desktop, cmd_process,cmd_verbose) = cmdline()
        if bool(cmd_desktop):
            self.desktop = []
            cmd_desktop = self.str_cleanup(cmd_desktop)
            cmd_desktop = cmd_desktop.split(",")
            self.set_desktop(cmd_desktop)

        if bool(cmd_process):
            self.procees = []
            cmd_process = self.str_cleanup(cmd_process)
            cmd_process = cmd_process.split(",")
            self.set_process(cmd_process)
            
        self.verbose = cmd_verbose


    def set_desktop(self, value = None):
        for d in value:
            if not d in self.desktop:
                self.desktop.append(d)


    def get_desktop(self,index = False):
        if index:
            return self.desktop[index]
        else:
            return self.desktop


    def del_desktop(self, value = None):
        if value in self.desktop:
            self.desktop.remove(value)
        else:
            return False


    def set_process(self, value = None):
        for d in value:
            if not d in self.desktop:
                self.process.append(d)


    def get_process(self,index = False):
        if index:
            return self.process[index]
        else:
            return self.process


    def del_process(self, value = None):
        if value in self.process:
            self.process.remove(value)

#   cmdline :
#   Return False or Commandline option application's main mode <enlightenment>
def cmdline(argv = sys.argv[1:]):
    desktop = ''
    process = ''
    verbose = False
    help_msg = "\
eyekill %s\n\neyekill [option] [value, ..] as comma seperated list\n\
Options:\n\
-d                Desktop's\n\
--desktop         Desktop's\n\
-p                Process(es)\n\
--process         Process(es)" % __version__

    try:
        opts, args = getopt.gnu_getopt(argv,"h:d:p:v",["help", "desktop=", "process="])
    except getopt.GetoptError:
        print (help_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-v':
            verbose = True
        elif opt == '-h':
            print (help_msg)
            sys.exit()
        elif opt in ("-d", "--desktop"):
            desktop = arg
        elif opt in ("-p", "--process"):
            process = arg

    return (desktop,process,verbose)

if __name__ == "__main__":

    elementary.init()
    eyekill = Application()  
    elementary.run()
    elementary.shutdown()


