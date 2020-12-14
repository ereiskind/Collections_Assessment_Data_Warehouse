#! /usr/local/bin/python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from pathlib import Path

# function to take care of downloading file
def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

# instantiate a chrome options object so you can set the size and headless preference
# some of these chrome options might be unnecessary but I just used a boilerplate
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "Downloads",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')

# executable_path needs to be on PATH environmental variable--how should this be handled?
Path_to_ChromeDriver = Path()
#ToDo: Fill in parameters for Path()
driver = webdriver.Chrome(options=chrome_options, executable_path=Path_to_ChromeDriver)

# This is the path that the file needs to be read from
File_Path = Path()
#ToDo: Fill in parameters for Path()
# There's no apparent way to get the name of the file that gets downloaded, so this file path will need to be just for the downloaded file and hold one file at a time

# function to handle setting up headless download
enable_download_headless(driver, File_Path)

# get request to target the site selenium is active on
#ToDo: Put the SUSHI URL in the method below
driver.get()

#ToDo: Get name of only file File_Path
#ToDo: Read that JSON file into memory as Python object
#ToDo: Delete the JSON file