#!/usr/bin/python3

import os
import sys
import threading
import time
from file_time_func import *
import gi

# reference
# https://github.com/Taiko2k/GTK4PythonTutorial/blob/main/README.md
# https://github.com/timlau/gtk4-python.git

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, GObject, Gio, Adw

# https://github.com/natorsc/gui-python-gtk/blob/main/src/gtk4/file-chooser-dialog-folder/MainWindow.py
class SelectDir(Gtk.FileChooserDialog):
    def __init__(self, title, widget, parent):
        Gtk.FileChooserDialog.__init__(self)
        self.set_action(action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.label = widget.get_label()
        self.set_title(title)
        self.set_transient_for(parent)
        self.set_default_size(600, 400)
        self.set_modal(True)
        self.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
    def get_label(self):
        return self.label

class Window(Gtk.ApplicationWindow):
    def __init__(self, title, width, height, **kwargs):
        super(Window, self).__init__(**kwargs)
        self.set_default_size(width, height)
        self.headerbar = Gtk.HeaderBar()
        self.set_titlebar(self.headerbar)
        label = Gtk.Label()
        label.set_text(title)
        self.headerbar.set_title_widget(label)

    def on_start_copy_clicked(self, widget):
        # dictionary
        copy_info = {}
        
        copy_info["lb_in_path"] = self.lb_in_path.get_text()
        copy_info["lb_out_path"] = self.lb_out_path.get_text()
        
        self.thread_running = True
        thread = threading.Thread(target=self.on_thread_working, args=(copy_info, ))
        thread.daemon = True
        thread.start()
        print("thread start")

    def on_update_status(self, args):
        self.lb_process.set_text(args['n_file'])
        self.lb_ing_count.set_text(str(args['copy_count']) + " / " + str(args['all_count']))

    def on_thread_working(self, copy_info):
        in_file_list = get_dir_list(copy_info["lb_in_path"])
        
        all_count = len(in_file_list)
        copy_count = 0
        GLib.idle_add(self.on_update_status, {'copy_count':copy_count, 'all_count':all_count, 'n_file':""})
        # time.sleep(0.2)
        for i in range(all_count):
            n_file = in_file_list[i]
            n_date = str_to_datetime(in_file_list[i])
            
            # date 변환 실패할경우 pass
            if not n_date:
                print("copy error => " + n_file)
                continue

            #str_date = n_date.strftime("%Y %m %d %H:%M:%S")
            #tmp_path = self.lb_out_path.get_text() + "/" + n_date.strftime("%Y/%m/%d/")
            # 2020/2020년8월
            tmp_path = copy_info["lb_out_path"] + "/" + n_date.strftime("%Y/%Y년%m월/")
            if not os.path.isdir(tmp_path):
                os.makedirs(tmp_path)

            # exist check
            if os.path.isfile(tmp_path + n_file):
                continue

            #print("copy => " + n_file)
            file_copy(copy_info["lb_in_path"] + "/" + n_file, tmp_path + n_file)
            copy_count = copy_count + 1
            GLib.idle_add(self.on_update_status, {'copy_count':copy_count, 'all_count':all_count, 'n_file':n_file})
            # time.sleep(0.2)
        print("copy end")
        self.thread_running = False

    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.show()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            print("btn label: " + widget.get_label())
            if widget.get_label() == "Input(DIR)":
                self.lb_in_path.set_text(dialog.get_filename())
                print("input label")
            elif widget.get_label() == "Output(DIR)":
                self.lb_out_path.set_text(dialog.get_filename())
                print("output label")

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def evnet_msg(self, event, pdata):
        print("click")
        return True
	
    def btn_click(self, btn):
        print("btn click")
        return True
	
    def destroy(self, win):
        print("win destroy")
        Gtk.main_quit()

    def on_activate(self, app):
        win = Gtk.ApplicationWindow(application=app)
        btn = Gtk.Button(label="Hello, World!")
        btn.connect('clicked', lambda x: win.close())
        win.set_child(btn)
        win.present()

    def on_start(self):
        app = Gtk.Application(application_id='org.gtk.image_sort')
        app.connect('activate', self.on_activate)
        app.run(None)

class MyWindow(Window):
    def __init__(self, title, width, height, **kwargs):
        super(MyWindow, self).__init__(title, width, height, **kwargs)
        
        self.in_path = ""
        self.out_path = "/tmp"

        content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        content.set_halign(Gtk.Align.CENTER)
        content.set_margin_top(20)
        content.set_spacing(10)
        content_sub1 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        content_sub1.set_margin_top(20)
        content_sub1.set_spacing(10)
        content2_l = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        content2_l.set_spacing(10)
        content2_r = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        content2_r.set_spacing(10)
        content_sub1.append(content2_l)
        content_sub1.append(content2_r)
        
        label = Gtk.Label()
        label.set_text('Image copy tool')
        content.append(label)
        content.append(content_sub1)

        self.lb_in_path = Gtk.Entry()
        self.lb_out_path = Gtk.Entry()
        self.lb_in_path.set_text(self.in_path)
        self.lb_out_path.set_text(self.out_path)
        self.lb_in_path.set_halign(Gtk.Align.START)
        self.lb_out_path.set_halign(Gtk.Align.START)
        content2_l.append(self.lb_in_path)
        content2_r.append(self.lb_out_path)
        
        button = Gtk.Button()
        button.set_label('in path')
        button.set_halign(Gtk.Align.CENTER)
        button.connect('clicked', self.on_dir_clicked)
        content2_l.append(button)

        button = Gtk.Button()
        button.set_label('out path')
        button.set_halign(Gtk.Align.CENTER)
        button.connect('clicked', self.on_dir_clicked)
        content2_r.append(button)

        self.lb_process = Gtk.Label()
        self.lb_process.set_text('')
        content.append(self.lb_process)
        self.lb_ing_count = Gtk.Label()
        self.lb_ing_count.set_text('')
        content.append(self.lb_ing_count)

        button = Gtk.Button()
        button.set_label('Start')
        button.connect("clicked", self.on_start_copy_clicked)
        content.append(button)
        self.thread_running = False
        self.set_child(content)

    def on_dir_clicked(self, widget):
        """
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_transient_for(self)
        dialog.set_default_size(600, 400)
        dialog.set_modal(True)
        dialog.connect('response', self.on_dialog_response)
        dialog.show()
        """
        dialog = SelectDir("Please choose a folder", widget, self)
        dialog.connect('response', self.on_dialog_response)
        dialog.show()
        
    def on_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            glocalfile = dialog.get_file()
            print("Folder selected: " + glocalfile.get_basename())
            print("Folder selected: " + glocalfile.get_path())
            label = dialog.get_label()
            path = glocalfile.get_path()
            
            print("btn label: " + label)
            if label == "in path":
                self.lb_in_path.set_text(path)
            elif label == "out path":
                self.lb_out_path.set_text(path)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

class Application(Adw.Application):
    """ Main Application class """

    def __init__(self):
        super().__init__(application_id='seo.utils.image',
                        flags=Gio.ApplicationFlags.FLAGS_NONE)

    def print_gtk_version(self):
        print("Gtk Version: ", Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION, Gtk.MICRO_VERSION)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MyWindow("Image copy & sort(GTK4+Adwaita)", 500, 300, application=self)
        self.print_gtk_version()
        win.present()

def main():
    """ Run the main application"""
    app = Application()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()
    #app = gtk_img_copy()
    #app.on_start()

