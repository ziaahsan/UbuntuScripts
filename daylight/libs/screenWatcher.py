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

        self.sun_info = sun_info
        self.time_zone = time_zone

        self.enable_theme = enable_theme
        self.enable_wallaper = enable_wallaper

        self.wallpaper = Wallpaper()

        self.root_dir_path = Path(os.path.realpath(__file__)).parent.parent
        
        self.jobs = []
        self.make_jobs()

        atexit.register(self.clear_jobs)

    '''
    Makes jobs based on the sun info provided through the constructor.
    '''
    def make_jobs(self):
        # Always clear jobs before making
        self.clear_jobs()

        if type(self.sun_info) != dict: raise Exception('sun info is not valid...')

        # Sequence jobs
        for val in self.sun_info:
            seqs = self.sun_info[val]['seq'].keys()
            for seq in seqs:
                job_time = self.sun_info[val]['seq'][seq].strftime("%H:%M:%S")
                self.jobs.append(\
                    schedule
                        .every()
                        .day
                        .at(job_time)
                        .do(self.__set_wallpaper, seq)
                )

                if ScreenWatcher.ENABLE_DEBUG:
                    print (f'[{self.identify}] job created for: {job_time}...')

        # set current wallpaper
        self.__set_curr_wallpaper()
        
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
    Set the current wallpaper that should be active based on the seq.
    '''
    def __set_curr_wallpaper(self):
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
        
        if ScreenWatcher.ENABLE_DEBUG:
            print (f'[{self.identify}] Setting wallpaper uri...')
        
        self.wallpaper.set_uri(uri)
