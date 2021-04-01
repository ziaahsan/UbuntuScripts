#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pytz
import datetime

from dateutil import tz

from astral.sun import sun
from astral.geocoder import database, lookup

'''
Simply class for sun location through out the day using astral.
'''
class Sun:

    ENABLE_DEBUG = True
    
    '''
    Setup the new sun.
    '''
    def __init__(self, with_date=datetime.date.today(), time_zone='America/Toronto', look_up='Toronto'):
        self.with_date = with_date
        self.time_zone = time_zone
        self.look_up = look_up
        self.info = None

        self.wallpaper_seq = {
            'dawn': [0, 1],
            'sunrise': [2, 3, 4, 5],
            'noon': [6, 7],
            'sunset': [8, 9, 10, 11],
            'dusk': [12, 13, 14, 15]
        }
    
    '''
    Get the time zone used in this sun
    '''
    def get_time_zone(self):
        return self.time_zone

    '''
    Makes the sun info to be used.
    '''
    def make(self):
        self.info = sun(
            lookup(self.look_up, database()).observer,
            date=datetime.date(self.with_date.year,self.with_date.month,self.with_date.day)
        )

        if type(self.info) != dict: return
        
        for val in self.info:
            self.info[val] = {
                'utc': self.info[val],
                'local': self.info[val].astimezone(tz.gettz(self.time_zone))
            }

        self.__create_wallpaper_time_slots()
        return self.info

    '''
    Add the self.wallpaper_seq to the assosicates time slots through out the day.
    '''
    def __create_wallpaper_time_slots(self):
        keys = ['dawn', 'sunrise', 'noon', 'sunset', 'dusk']
        
        seq = 0
        for keys_indx in range(0, len(keys)):
            if keys_indx+1 is len(keys):
                end_of_day = datetime.datetime(\
                        self.with_date.year,
                        self.with_date.month,
                        self.with_date.day, 23, 59, 59, 0
                    ).astimezone(tz.gettz(self.time_zone))
                diff = end_of_day - self.info[keys[keys_indx]]['local']
            else:
                diff = self.info[keys[keys_indx + 1]]['local'] - self.info[keys[keys_indx]]['local']
            
            avg = diff / len(self.wallpaper_seq [keys[keys_indx]])

            start_at = self.info[keys[keys_indx]]['local']
            self.info[keys[keys_indx]]['seq'] = {}

            wall_seq_index = 0
            while wall_seq_index < len(self.wallpaper_seq [keys[keys_indx]]):
                self.info[keys[keys_indx]]['seq'][seq] = start_at
                start_at = start_at + avg
                seq+=1
                wall_seq_index +=1

