#Source code: https://github.com/sharat910/selenium-youtube

import random
import time
from youtube import YouTube
from config_parser import get_config
from resolutions import get_playable_resolutions
import json


from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_video_list(config):
    with open(config['youtube']['video_list'],"r") as f:
        urls = [x.strip() for x in f.readlines()]
    return urls

def get_video_list_json(config):
    with open(config['video_list']) as f:
        videos = json.load(f)
    return videos

def play_with_res(video,res,config,d):
    print("Launching browser...")
    y = YouTube(video,res, d, config['youtube'])
    y.play()
    time.sleep(2)

def play_one_video_all_resolutions(config, video):
    d = webdriver.Chrome()
    resolutions = get_playable_resolutions(config,video['url'],d)
    print("Playing %s in" % (video['title']),resolutions)
    for res in resolutions:
        play_with_res(video,res,config,d)

if __name__ == '__main__':
    time.sleep(5)
    config = get_config()
    videos = get_video_list_json(config)
    d = webdriver.Chrome()
    n = min(len(videos),config['no_of_videos'])
    s = min(len(videos),config['starting_index'])
    for video in videos[s:n]:
        # play_one_video_all_resolutions(config, video)
        play_with_res(video,"Auto",config,d)