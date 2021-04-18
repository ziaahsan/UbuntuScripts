#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import threading
import atexit

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

from libs.screenWatcher import ScreenWatcher
from libs.sun import Sun

class App:

    ENABLE_DEBUG = True

    '''
    Setup the app and its indicator.
    '''
    def __init__(self, enable_automatic=True):
        self.identify = 'App'

        self.enable_automatic = enable_automatic

        self.sun = Sun()
        self.sun_info = self.sun.make()
        self.time_zone = self.sun.get_time_zone()

        self.screen_watcher = ScreenWatcher(self.sun_info, self.time_zone)

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.indicator = appindicator.Indicator.new(
            'Fp0GWrO43i',
            f'{self.dir_path}/icon.png',
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.__build_menu())

        self.threading_event = threading.Event()
        threading.Thread(target=self.__job_thread).start()

        
        gtk.main()
    
    '''
    Build app indicator menu.
    '''
    def __build_menu(self):
        menu = gtk.Menu()
        theme_menu = gtk.Menu()

        item_themes = gtk.ImageMenuItem(label='Day Time')
        menu.append(item_themes)
        item_themes.set_submenu(theme_menu)

        for key in self.sun_info:
            label = f'{key.capitalize()} - {self.sun_info[key]["local"].strftime("%-I:%M %p")}'
            theme_menu.append(gtk.MenuItem(label=label))

        item_quit = gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.__activate_quit)

        item_settings = gtk.MenuItem(label='Daylight Settings...')
    
        menu.append(item_quit)
        menu.append(gtk.SeparatorMenuItem())
        menu.append(item_settings)
        
        menu.show_all()
        return menu
    
    '''
    On app quit.
    '''
    def __activate_quit(self, source=''):
        gtk.main_quit()
        
        self.threading_event.set()
        
        if App.ENABLE_DEBUG:
            print (f'[{self.identify}] waiting for atexit events...')

    '''
    Sets up the jobs thread that will be used by apps.
    '''        
    def __job_thread(self):
        while not self.threading_event.isSet():
            if (self.screen_watcher.has_day_changed()):
                if App.ENABLE_DEBUG:
                    print (f'[{self.identify}] Day changed, re-initializing ScreenWatcher...')
                
                self.sun = Sun()
                self.sun_info = self.sun.make()
                self.time_zone = self.sun.get_time_zone()

                self.screen_watcher = ScreenWatcher(self.sun_info, self.time_zone)
            
            # Setting up the screen watcher
            self.screen_watcher.set_curr_wallpaper()
            
            # timeout = self.screen_watcher.next_scheduled_job()
            timeout = 30

            if App.ENABLE_DEBUG:
                print (f'[{self.identify}] waiting for {timeout} seconds...')
            
            event_is_set = self.threading_event.wait(timeout)
            if (event_is_set and App.ENABLE_DEBUG):
                print (f'[{self.identify}] event was set, terminating...')

if __name__ == '__main__':
    App()
