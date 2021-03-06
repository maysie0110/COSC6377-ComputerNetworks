#https://github.com/sharat910/selenium-youtube/blob/master/youtube.py

import os
import time
from datetime import datetime
import logging
import random
import requests
from pprint import pprint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# from decorators import retry

DIVS = [1,2,3,4,5,9,10,11,12,15]
DIV_TO_KEY = {}
INTERVAL = 0.5

class YouTube(object):
    """docstring for YouTube"""
    def __init__(self, video, resolution, driver, config,flowfetch):
        self.url = video['url']
        self.playback_seconds = self.get_sec_from_time_str(video['length'])
        self.resolution = resolution
        self.config = config
        self.flowfetch = flowfetch
        self.driver = driver
        
    def get_video_id(self):
        return self.url.split("=")[1]
    
    def get_sec_from_time_str(self,time_str):
        return sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time_str.split(":"))))

    def load_video(self):
        print("Loading url...")
        self.driver.get(self.url)
        return True

    @retry
    def select_resolution(self):
        # Don't bother selecting resolution for Auto
        if self.resolution == 'Auto':
            print("Playing in Auto resolution.")
            return True
        
        print("Selecting resolution...")
        time.sleep(0.2)
        sb = self.driver.find_element_by_css_selector('.ytp-button.ytp-settings-button')
        sb.click()
        time.sleep(0.3)
        try:
            elem = self.driver.find_element_by_css_selector('div.ytp-menuitem:nth-child(5) > div:nth-child(1)')
            elem.click()
        except:
            elem = self.driver.find_element_by_css_selector('div.ytp-menuitem:nth-child(4) > div:nth-child(1)')
            elem.click()
        time.sleep(1)
        res = self.driver.find_elements_by_class_name("ytp-menuitem-label")
        for item in res:
            #print(item.text)
            if item.text == self.resolution:
                item.click()
                print("Selected", self.resolution)
                return True
        return False

    @retry
    def enable_stats(self):
        movie_player = self.driver.find_element_by_id('movie_player')
        self.hover = ActionChains(self.driver).move_to_element(movie_player)
        self.hover.perform()
        ActionChains(self.driver).context_click(movie_player).perform()
        options = self.driver.find_elements_by_class_name('ytp-menuitem')
        for option in options:
            option_child = option.find_element_by_class_name('ytp-menuitem-label')
            if option_child.text == 'Stats for nerds':
                option_child.click()
                print("Enabled stats collection.")
                return True
        return False 

    def get_stats(self,stat_dict):
        stat_dict['Timestamp'] = str(datetime.now())
        stat_dict['Current Seek'] = self.get_current_seek()
        for div_id in DIVS:
            elem = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > span:nth-child(2)"%div_id)
            stat_dict[DIV_TO_KEY[div_id]] = elem.text

    def collect_stats(self):
        try:
            stat_dict = self.create_new_stat_dict()
            n = min(2*self.playback_seconds, self.config['number_of_data_points'])
            print("Started collecting... it'll take %d seconds." % (n/2))
            for i in range(n):
                start = time.time()
                if i % 2 == 0:
                    self.hover.perform()
                self.get_stats(stat_dict)
                stat_dict['Ad'] = False
                self.flowfetch.post_video_stat(stat_dict)
                time_taken = time.time()-start
                #print("Time taken",time_taken)
                time.sleep(max(0,INTERVAL - time_taken))
            return True
        except Exception as e:
            print("Ecountered error while collecting stats", e)
            return False

    def collect_stats_for_ad(self):
        try:
            print("Collecting stats for ads...")
            stat_dict = self.create_new_stat_dict()
            i = 0
            while(self.ad_present()):
                start = time.time()
                if i % 2 == 0:
                    self.hover.perform()
                self.get_stats(stat_dict)
                stat_dict['Ad'] = True
                self.flowfetch.post_video_stat(stat_dict)
                time_taken = time.time()-start
                time.sleep(max(0,INTERVAL - time_taken))
                i += 1
        except Exception as e:
            print("Unable to collect stats for ads")
            print(e)
            return False

    def get_current_seek(self):
        elem = self.driver.find_element_by_css_selector(".ytp-time-current")
        return elem.text

    def create_new_stat_dict(self):
        stat = {}
        stat['Timestamp'] = None
        stat['Current Seek'] = None
        print("\nCollecting following stats...")
        for div_id in DIVS:
            key = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > div:nth-child(1)"%div_id).text
            stat[key] = None
            print(div_id,key)
            #Populate DIV_TO_KEY dict
            DIV_TO_KEY[div_id] = key
        return stat

    def get_content_metadata(self):
        c = {
            'agent': self.config['agent'],
            'tag': self.config['tag'],
            'content_id': self.get_video_id(),
            'content_provider': self.config['content_provider'],
            'content_resolution': self.resolution,
            'session_id': self.driver.session_id
        }
        return c

    def play(self):
        print("Starting flowfetch...")
        self.flowfetch.start(self.get_content_metadata())
        time.sleep(2)
        if not self.load_video():
            self.stop(False)
            return

        if not self.enable_stats():
            self.stop(False)
            return

        #Ads load a little late in chrome
        if self.config['agent'] == 'chrome':
            time.sleep(1)

        if self.ad_present():
            print("Ad playing...")
            self.collect_stats_for_ad()

        if not self.select_resolution():
            self.stop(False)
            return
        
        if self.collect_stats():    
            self.stop(True)
        else:
            self.stop(False)

    def stop(self,success):
        print("Closing driver...")
        self.driver.close()
        print("Stopping flowfetch...")
        self.flowfetch.stop(success)
        print("Done\n\n")

    def ad_present(self):
        try:
            self.driver.find_element_by_class_name("videoAdUi")
            return True
        except Exception as e:
            return False