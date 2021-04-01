#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gio as gio

class Theme:

    ENABLE_DEBUG = True
    
    '''
    Setup the theme for use.
    @todo: Merge into wallpaper and a global 'org...' package handler
    '''
    def __init__(self):
        self.interface = 'org.gnome.desktop.interface'

    '''
    Get the current theme set to desktop.
    '''
    def get_theme(self):
        return gio.Settings.new(self.interface).get_string('gtk-theme')

    '''
    Sets the new theme as the desktop.
    '''
    def set_theme(self, name):
        if not name and (name != 'Yaru' or name != 'Yaru-light' or name != 'Yaru-dark'):
            return 'invalid theme...'
        
        # Sets the theme
        gio.Settings.new(self.interface).set_string('gtk-theme', name)
        #<!-- @todo: This is neccssary as a time-out
        time.sleep(2)
        #-->

        # Make sure the theme is set
        return self.get_theme() == name
