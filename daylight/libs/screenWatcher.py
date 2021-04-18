#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import math
import pytz
import datetime
import unittest
import importlib
import schedule
import atexit

from dateutil import tz
from pathlib import Path

from . import Wallpaper

class ScreenWatcher:

    ENABLE_DEBUG = True

    '''
    Setup the screen watcher.
    '''
    def __init__(self, sun_info, time_zone, enable_theme=False, enable_wallaper=True):
        self.identify = 'ScreenWatcher'

        self.init_date = datetime.date.today()

        self.sun_info = sun_info
        self.time_zone = time_zone

        self.enable_theme = enable_theme
        self.enable_wallaper = enable_wallaper

        self.wallpaper = Wallpaper()

        self.root_dir_path = Path(os.path.realpath(__file__)).parent.parent
        
        self.jobs = []

        atexit.register(self.clear_jobs)

    '''
    Makes jobs based on the sun info provided through the constructor.
    '''
    def make_jobs(self):
        # Always clear jobs before making
        # self.clear_jobs()
        pass
        
    '''
    Runs the scheduled jobs
    '''
    def run_scheduled_jobs(self):
        if ScreenWatcher.ENABLE_DEBUG:
            print (f'[{self.identify}] Trying to run scheduled jobs if any...')
        schedule.run_pending()
    
    '''
    Get the next job time.
    '''
    def next_scheduled_job(self):
        return schedule.idle_seconds()
    
    '''
    Clears the jobs, and scheduler.
    '''
    def clear_jobs(self):
        if ScreenWatcher.ENABLE_DEBUG:
            print (f'[{self.identify}] clearing {len(self.jobs)} jobs...')

        for job in self.jobs:
            schedule.cancel_job(job)
        
        schedule.clear()
        self.jobs.clear()

        if ScreenWatcher.ENABLE_DEBUG:
            print (f'[{self.identify}] active {len(self.jobs)} jobs...')
    

    '''
    Check if date has changed since the initialized date
    '''
    def has_day_changed(self):
        return self.init_date < datetime.date.today()
    
    '''
    Set the current wallpaper that should be active based on the seq.
    '''
    def set_curr_wallpaper(self):
        now = datetime.datetime.now().astimezone(tz.gettz(self.time_zone))

        if (ScreenWatcher.ENABLE_DEBUG):
            print (f'[{self.identify}] looking for seq with time >= {now}')
        
        for key in self.sun_info:
            seqs = self.sun_info[key]['seq']
            if type(seqs) != dict:
                continue
            
            found_seq = False

            for seq in seqs:
                seq_time = seqs[seq]
                if (now < seq_time):
                    if (ScreenWatcher.ENABLE_DEBUG):
                        print (f'[{self.identify}] found seq: {seq}')
                    self.__set_wallpaper(seq)
                    found_seq = True
                    break
            
            if found_seq:
                break

    '''
    Set the wallpaper based on the sequence (filename) provided.
    '''
    def __set_wallpaper(self, seq):
        if type(seq) != int: raise Exception('provided wallpaper seq is not an integer...')
        if  seq < 0: raise Exception('wallpaper seq cannot be negative...')

        uri = f'{self.root_dir_path}/screen'
        for file_name in os.listdir(uri):
            if str(seq) == os.path.splitext(file_name)[0]:
                uri = f'{uri}/{file_name}'
                break
        
        if self.wallpaper.get_uri() != f'file://{uri}':
            if ScreenWatcher.ENABLE_DEBUG:
                print (f'[{self.identify}] Setting wallpaper uri...')
            self.wallpaper.set_uri(uri)
