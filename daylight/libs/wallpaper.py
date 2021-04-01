#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import imghdr

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gio as gio

class Wallpaper:
    
    ENABLE_DEBUG = True

    '''
    Setup the wallpaper for use.
    @todo: Merge into theme and a global 'org...' package handler
    '''
    def __init__(self):
        self.backgorund = 'org.gnome.desktop.background'
    '''
    Checks if uri is an image.
    '''
    def is_image(self, uri):
        return imghdr.what(uri)
    
    '''
    Get the current wallpaper set to desktop.
    '''
    def get_uri(self):
        return gio.Settings.new(self.backgorund).get_string('picture-uri')

    '''
    Sets the new uri as the wallpaper.
    '''
    def set_uri(self, uri):
        if not uri.startswith('/'):
            raise Exception('invalid resource location...')

        if not self.is_image(uri):
             raise Exception('not a valid image...')

        uri = f'file://{uri}'

        # Sets the wallpaper
        gio.Settings.new(self.backgorund).set_string('picture-uri', uri)
        #<!-- @todo: This is neccssary as a time-out
        time.sleep(2)
        #-->

        if self.get_uri() != uri:
            raise Exception('something went wrong when \
                setting up the wallpaper...')
