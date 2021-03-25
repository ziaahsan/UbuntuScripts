#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, datetime, time, signal
import json, imghdr, threading,  pytz
import schedule, atexit

TODAY = datetime.date.today()
TIME_ZONE = 'America/Toronto'

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from dateutil import tz
from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from astral.sun import sun
from astral.geocoder import database, lookup

APPINDICATOR_ID = 'Fp0GWrO43i'

ENABLE_DEBUG = True
ENABLE_AUTOMATIC = True
ENABLE_WALLPAPER_CHANGE = True
ENABLE_THEME_CHANGE = False

SCHEDULED_JOBS = []

scheduler_thread = None
job_thread = None
wallpaper_thread = None
theme_thread = None

def main():
    global scheduler_thread

    if ENABLE_DEBUG:
        print('Starting main ...')
    
    if ENABLE_AUTOMATIC:
        # Schedule jobs to be executed
        SCHEDULED_JOBS.append(schedule.every(60).seconds.do(set_automatic))
        
        if scheduler_thread is None:
            if ENABLE_DEBUG:
                print('Enabling scheduler thread ...')
            scheduler_thread = threading.Thread(target=run_scheduled_jobs)
            scheduler_thread.start()

    indicator = appindicator.Indicator.new(
        APPINDICATOR_ID,
        f'{DIR_PATH}/icon.png',
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    
    gtk.main()


def build_menu():
    menu = gtk.Menu()
    theme_menu = gtk.Menu()

    item_themes = gtk.ImageMenuItem(label='Theme Style')

    item_dawn = gtk.MenuItem(label='Dawn')
    item_dawn.connect('activate', activate_dawn_wallpaper)

    item_sun_rise = gtk.MenuItem(label='Sun Rise')
    item_sun_rise.connect('activate', activate_sunrise_wallpaper)

    item_noon = gtk.MenuItem(label='Noon')
    item_noon.connect('activate', activate_noon_wallpaper)

    item_sun_set = gtk.MenuItem(label='Sun Set')
    item_sun_set.connect('activate', activate_sunset_wallpaper)

    item_dusk = gtk.MenuItem(label='Dusk')
    item_dusk.connect('activate', activate_dusk_wallpaper)

    item_quit = gtk.MenuItem(label='Quit')
    item_quit.connect('activate', activate_quit)

    item_settings = gtk.MenuItem(label='Daylight Settings...')
    
    menu.append(item_themes)
    item_themes.set_submenu(theme_menu)

    theme_menu.append(item_dawn)
    theme_menu.append(item_sun_rise)
    theme_menu.append(item_noon)
    theme_menu.append(item_sun_set)
    theme_menu.append(item_dusk)

    menu.append(item_quit)
    
    menu.append(gtk.SeparatorMenuItem())
    menu.append(item_settings)
    
    menu.show_all()
    return menu

def run_scheduled_jobs():
    global job_thread

    while len(SCHEDULED_JOBS) > 0:
        if ENABLE_AUTOMATIC and job_thread is None:
            if ENABLE_DEBUG:
                print('Enabling job thread ...')
            job_thread = threading.Thread(target=schedule.run_pending())
            job_thread.start()
        
        if job_thread != None:
            job_thread.join() # Wait for job thread to finish
            if ENABLE_DEBUG:
                print('Disable job thread ...')
            job_thread = None
        
        # Disable the enabling of the job thread for x seconds
        #<--@todo: Fix this will cause the x seconds wait upon quit...
        time.sleep(10)
        #-->

def activate_dawn_wallpaper(source=''):
    uri = f'{DIR_PATH}/screen'
    for i in os.listdir(uri):
        if 'dawn' in i:
            uri = f'{uri}/{i}'
            break
    
    apply_changes(uri, 'Yaru')

def activate_sunrise_wallpaper(source=''):
    uri = f'{DIR_PATH}/screen'
    for i in os.listdir(uri):
        if 'sunrise' in i:
            uri = f'{uri}/{i}'
            break
    
    apply_changes(uri, 'Yaru')

def activate_noon_wallpaper(source=''):
    uri = f'{DIR_PATH}/screen'
    for i in os.listdir(uri):
        if 'noon' in i:
            uri = f'{uri}/{i}'
            break
    
    apply_changes(uri, 'Yaru')

def activate_sunset_wallpaper(source=''):
    uri = f'{DIR_PATH}/screen'
    for i in os.listdir(uri):
        if 'sunset' in i:
            uri = f'{uri}/{i}'
            break
    
    apply_changes(uri, 'Yaru-dark')

def activate_dusk_wallpaper(source=''):
    uri = f'{DIR_PATH}/screen'
    for i in os.listdir(uri):
        if 'dusk' in i:
            uri = f'{uri}/{i}'
            break
    
    apply_changes(uri, 'Yaru-dark')

def activate_quit(source=''):
    if ENABLE_DEBUG:
        print('Quitting ...')      
   
    for job in SCHEDULED_JOBS:
        schedule.cancel_job(job)
        SCHEDULED_JOBS.remove(job)
    
    # Clear all jobs
    schedule.clear()

    # Before quitting wait for threads in progress to end
    wait_for_threads()

    if ENABLE_DEBUG:
        print (f'\
            Jobs: {SCHEDULED_JOBS}\n\
            #of Threads: {threading.active_count()}\n\
            Scheduler Thread: {scheduler_thread}\n\
            Job Thread: {job_thread}\n\
            Wallpaper Thread: {wallpaper_thread}\n\
            Theme Thread: {theme_thread}\n\
        ')
    gtk.main_quit()
    print ("[App] Closed gracefully.")

def is_image(uri):
    return imghdr.what(uri)

def set_automatic():
    now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    now_local = now_utc.astimezone(tz.gettz(TIME_ZONE))
    sun_info = sun(
        lookup('Toronto', database()).observer,
        date=datetime.date(TODAY.year, TODAY.month, TODAY.day)
    )
    
    for val in sun_info:
        sun_info[val] = {
            'utc': sun_info[val],
            'local': sun_info[val].replace(tzinfo=pytz.UTC).astimezone(tz.gettz(TIME_ZONE))
        }
    
    if now_local >= sun_info['dusk']['local']:
        activate_dusk_wallpaper()
    elif now_local >= sun_info['sunset']['local']:
        activate_sunset_wallpaper()
    elif now_local >= sun_info['noon']['local']:
        activate_noon_wallpaper()
    elif now_local >= sun_info['sunrise']['local']:
        activate_sunrise_wallpaper()
    elif now_local >= sun_info['dawn']['local']:
        activate_dawn_wallpaper()

def get_wallpaper_uri():
    settings = gio.Settings.new('org.gnome.desktop.background')
    return settings.get_string('picture-uri')

def set_wallpaper(uri):
    if not uri.startswith('/'):
        return 'invalid resource location...'

    if not is_image(uri):
        return 'not a valid image...'

    settings = gio.Settings.new('org.gnome.desktop.background')
    settings.set_string('picture-uri', f'file://{uri}')
    
    return get_wallpaper_uri() == uri

def get_theme():
    settings = gio.Settings.new('org.gnome.desktop.interface')
    return settings.get_string('gtk-theme')

def set_theme(name):
    if not name and (name != 'Yaru' or name != 'Yaru-light' or name != 'Yaru-dark'):
        return 'invalid theme...'
    
    settings = gio.Settings.new('org.gnome.desktop.interface')
    settings.set_string('gtk-theme', name)
    return get_theme() == name

def apply_changes(uri, theme_name):
    global wallpaper_thread, theme_thread
    if ENABLE_WALLPAPER_CHANGE and wallpaper_thread is None:
        if ENABLE_DEBUG:
            print('Enabling wallpaper thread ...')
        wallpaper_thread = threading.Thread(target=set_wallpaper, args=[uri])
        wallpaper_thread.start()
    
    if ENABLE_THEME_CHANGE and theme_thread is None:
        if ENABLE_DEBUG:
            print('Enabling theme thread ...')
        theme_thread = threading.Thread(target=set_theme, args=[theme_name])
        theme_thread.start()
    
    #<--@todo: Change this to a callback so we don't halt process
    if wallpaper_thread != None:
        if wallpaper_thread.is_alive():
            wallpaper_thread.join()
    if theme_thread != None:
        if theme_thread.is_alive():
            theme_thread.join()
    #-->
    if ENABLE_DEBUG:
        print('Disable Wallpaper and Theme thread ...')
    
    wallpaper_thread = None
    theme_thread = None

def wait_for_threads():
    global scheduler_thread, job_thread, wallpaper_thread, theme_thread

    if scheduler_thread != None:
        scheduler_thread.join()
        scheduler_thread = None
    
    if job_thread != None:
        job_thread.join()
        job_thread = None
    
    if wallpaper_thread != None:
        wallpaper_thread.join()
        wallpaper_thread = None
    
    if theme_thread != None:
        theme_thread.join()
        theme_thread = None

if __name__ == '__main__':
    main()