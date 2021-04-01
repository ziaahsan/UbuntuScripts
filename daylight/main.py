#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, datetime, time, signal, math
import imghdr, threading, pytz
import schedule

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gio as gio
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

from config import Config

INDICATOR = None

def main():
    build_sun_info()

    if Config.ENABLE_DEBUG:
        print('Starting main ...')
    
    if Config.ENABLE_AUTOMATIC:
        do_automatic()
        # Schedule jobs to be executed
        Config.SCHEDULED_JOBS.append(schedule.every(10).seconds.do(do_automatic))
        
        if Config.SCH_THREAD is None:
            if Config.ENABLE_DEBUG:
                print('Enabling scheduler thread ...')
            Config.SCH_THREAD = threading.Thread(target=run_scheduled_jobs)
            Config.SCH_THREAD.start()

    INDICATOR = appindicator.Indicator.new(
        Config.APPINDICATOR_ID,
        f'{DIR_PATH}/icon.png',
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    INDICATOR.set_status(appindicator.IndicatorStatus.ACTIVE)
    INDICATOR.set_menu(build_menu())
    
    gtk.main()


def build_menu():
    menu = gtk.Menu()
    theme_menu = gtk.Menu()

    item_themes = gtk.ImageMenuItem(label='Theme Style')

    dawn_label = f"Dawn - {Config.SUN_INFO['dawn']['local_str']}" if Config.ENABLE_AUTOMATIC else 'Dawn'
    item_dawn = gtk.MenuItem(label=dawn_label)
    item_dawn.connect('activate', activate_dawn_wallpaper)

    sunrise_label = f"Sun Rise - {Config.SUN_INFO['sunrise']['local_str']}" if Config.ENABLE_AUTOMATIC else 'Sun Rise'
    item_sun_rise = gtk.MenuItem(label=sunrise_label)
    item_sun_rise.connect('activate', activate_sunrise_wallpaper)

    noon_label = f"Noon - {Config.SUN_INFO['noon']['local_str']}" if Config.ENABLE_AUTOMATIC else 'Noon'
    item_noon = gtk.MenuItem(label=noon_label)
    item_noon.connect('activate', activate_noon_wallpaper)

    sunset_label = f"Sun Set - {Config.SUN_INFO['sunset']['local_str']}" if Config.ENABLE_AUTOMATIC else 'Sun Set'
    item_sun_set = gtk.MenuItem(label=sunset_label)
    item_sun_set.connect('activate', activate_sunset_wallpaper)

    dusk_label = f"Dusk - {Config.SUN_INFO['dusk']['local_str']}" if Config.ENABLE_AUTOMATIC else 'Dusk'
    item_dusk = gtk.MenuItem(label=dusk_label)
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
    while len(Config.SCHEDULED_JOBS) > 0:
        if Config.ENABLE_AUTOMATIC and Config.JOB_THREAD is None:
            if Config.ENABLE_DEBUG:
                print('Enabling job thread ...')
            Config.JOB_THREAD = threading.Thread(target=schedule.run_pending())
            Config.JOB_THREAD.start()
        
        if Config.JOB_THREAD != None:
            Config.JOB_THREAD.join() # Wait for job thread to finish
            if Config.ENABLE_DEBUG:
                print('Disable job thread ...')
            Config.JOB_THREAD = None
        
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
    if Config.ENABLE_DEBUG:
        print('Quitting ...')      
   
    for job in Config.SCHEDULED_JOBS:
        schedule.cancel_job(job)
        Config.SCHEDULED_JOBS.remove(job)
    
    # Clear all jobs
    schedule.clear()

    # Before quitting wait for threads in progress to end
    wait_for_threads()

    if Config.ENABLE_DEBUG:
        print (f'\
            Jobs: {Config.SCHEDULED_JOBS}\n\
            #of Threads: {threading.active_count()}\n\
            Scheduler Thread: {Config.SCH_THREAD}\n\
            Job Thread: {Config.JOB_THREAD}\n\
            Wallpaper Thread: {Config.WALLPAPER_THREAD}\n\
            Theme Thread: {Config.THEME_THREAD}\n\
        ')
    gtk.main_quit()
    print ("[App] Closed gracefully.")

def set_automatic(seq):
    if seq is None or seq < 0: return

    uri = f'{DIR_PATH}/screen'
    for file_name in os.listdir(uri):
        if str(seq) == os.path.splitext(file_name)[0]:
            uri = f'{uri}/{file_name}'
            break
    
    print(uri)
    apply_changes(uri, 'Yaru-dark')

def do_automatic():
    global Config.SUN_INFO

    if not Config.SUN_INFO:
        if Config.ENABLE_DEBUG:
            print ("Invalid sun info...")
        return 

    # now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    # now_local = now_utc.astimezone(tz.gettz(TIME_ZONE))

    global local_time
    now_local = local_time.astimezone(tz.gettz(TIME_ZONE))
    print(now_local)
    print(Config.SUN_INFO['dawn']['local'], now_local >= Config.SUN_INFO['dawn']['local'])

    seq = -1
    
    def calculate_seq(moveTo, moveFrom):
        diff = Config.SUN_INFO[moveTo]['local'] - Config.SUN_INFO[moveFrom]['local']
        avg = diff / len(Config.SUN_WALLPAPER_SEQ[moveFrom])
        seq_val = math.floor(len(Config.SUN_WALLPAPER_SEQ[moveFrom]) - ((Config.SUN_INFO[moveTo]['local'] - now_local) / avg))
        print(moveTo, moveFrom, seq_val)
        return seq_val
    
    if now_local >= Config.SUN_INFO['dusk']['local']:
        pass
    elif now_local >= Config.SUN_INFO['sunset']['local']:
        seq = calculate_seq('dusk', 'sunset')
    elif now_local >= Config.SUN_INFO['noon']['local']:
        seq = calculate_seq('sunset', 'noon')
    elif now_local >= Config.SUN_INFO['sunrise']['local']:
        seq = calculate_seq('noon', 'sunrise')
    elif now_local >= Config.SUN_INFO['dawn']['local']:
        seq = calculate_seq('sunrise', 'dawn')
    
    set_automatic(seq)
    local_time = datetime.timedelta(minutes=30)

def apply_changes(uri, theme_name):
    global Config.WALLPAPER_THREAD, Config.THEME_THREAD
    if Config.ENABLE_WALLPAPER_CHANGE and Config.WALLPAPER_THREAD is None:
        if Config.ENABLE_DEBUG:
            print('Enabling wallpaper thread ...')
        Config.WALLPAPER_THREAD = threading.Thread(target=set_wallpaper, args=[uri])
        Config.WALLPAPER_THREAD.start()
    
    if Config.ENABLE_THEME_CHANGE and Config.THEME_THREAD is None:
        if Config.ENABLE_DEBUG:
            print('Enabling theme thread ...')
        Config.THEME_THREAD = threading.Thread(target=set_theme, args=[theme_name])
        Config.THEME_THREAD.start()
    
    #<--@todo: Change this to a callback so we don't halt process
    if Config.WALLPAPER_THREAD != None:
        if Config.WALLPAPER_THREAD.is_alive():
            Config.WALLPAPER_THREAD.join()
    if Config.THEME_THREAD != None:
        if Config.THEME_THREAD.is_alive():
            Config.THEME_THREAD.join()
    #-->
    if Config.ENABLE_DEBUG:
        print('Disable Wallpaper and Theme thread ...')
    
    Config.WALLPAPER_THREAD = None
    Config.THEME_THREAD = None

def wait_for_threads():
    global Config.SCH_THREAD, Config.JOB_THREAD, Config.WALLPAPER_THREAD, Config.THEME_THREAD

    if Config.SCH_THREAD != None:
        Config.SCH_THREAD.join()
        Config.SCH_THREAD = None
    
    if Config.JOB_THREAD != None:
        Config.JOB_THREAD.join()
        Config.JOB_THREAD = None
    
    if Config.WALLPAPER_THREAD != None:
        Config.WALLPAPER_THREAD.join()
        Config.WALLPAPER_THREAD = None
    
    if Config.THEME_THREAD != None:
        Config.THEME_THREAD.join()
        Config.THEME_THREAD = None

if __name__ == '__main__':
    main()