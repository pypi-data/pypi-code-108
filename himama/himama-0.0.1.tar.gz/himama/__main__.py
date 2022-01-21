#!/usr/bin/env python3
import logging
import os
import shutil

from six.moves import urllib_parse

try:
    import coloredlogs

    coloredlogs.install(level=logging.INFO)
except ImportError:
    logging.basicConfig(level=logging.INFO)

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.support.ui import WebDriverWait

SITE = "https://www.himama.com"
USER = os.getenv("HIMAMA_USER")
PASSWORD = os.getenv("HIMAMA_PASSWORD")
DOWNLOAD_DIR = os.getenv("HIMAMA_DOWNLOAD_DIR", "download")
MAX_JOURNALS = 200000


def getWebDriver():
    driver = None
    if not driver:
        try:
            driver = webdriver.Safari()
        except:
            pass

    if not driver:
        try:
            driver = webdriver.Firefox()
        except:
            pass

    if not driver:
        try:
            driver = webdriver.Edge()
        except:
            pass
    if not driver:
        try:
            driver = webdriver.ChromiumEdge()
        except:
            pass

    if not driver:
        try:
            driver = webdriver.Chrome()
        except:
            pass

    if not driver:
        try:
            driver = webdriver.Opera()
        except:
            pass

    if not driver:
        raise FileNotFoundError("No WebDriver Found.")

    return driver


def getAccountId(driver):
    accountsUri = driver.find_element(By.CLASS_NAME, "breadcrumb").find_element(By.TAG_NAME, "li").find_element(
        By.TAG_NAME, "a").get_attribute("href")
    return accountsUri.split("/")[-1]


def getCookies(driver):
    cookies = {}
    for cookie in driver.get_cookies():
        cookies[cookie["name"]] = cookie["value"]
    return cookies


def createKey(activity):
    activityId = activity.get("id")
    createdAt = activity.get("created_at")
    compositeKey = "{}-{}".format(createdAt.split("T")[0], activityId)
    return compositeKey


def getMediaUrls(activity):
    urlsToDownload = set()

    video = activity.get("video", {})

    if video:
        videoUrl = video.get("url")
        if videoUrl:
            urlsToDownload.add(videoUrl)

    otherVideoUrls = activity.get("video_urls", {})
    if otherVideoUrls:
        mp4VideoUrl = otherVideoUrls.get("mp4")
        if mp4VideoUrl:
            urlsToDownload.add(mp4VideoUrl)

        movVideoUrl = otherVideoUrls.get("mov")
        if movVideoUrl:
            urlsToDownload.add(movVideoUrl)

        webmVideoUrl = otherVideoUrls.get("webm")
        if webmVideoUrl:
            urlsToDownload.add(webmVideoUrl)

    image = activity.get("image", {})

    if image:
        bigImageUrl = image.get("big", {}).get("url")
        if bigImageUrl:
            urlsToDownload.add(bigImageUrl)
        else:
            imageUrl = image.get("url")
            if imageUrl:
                urlsToDownload.add(imageUrl)

    return urlsToDownload


def downloadFile(fileName, url):
    with requests.get(url, stream=True) as request:
        with open(fileName, "wb") as file:
            logging.info("Downloading: {}".format(os.path.basename(fileName)))
            shutil.copyfileobj(request.raw, file)


def downloadMediaForActivity(folderName, urlsToDownload):
    downloadFolderName = os.path.join(DOWNLOAD_DIR, folderName)
    if os.path.exists(downloadFolderName):
        logging.info("Skipping: {}".format(folderName))
        return

    tmpDownloadFolderName = downloadFolderName + "-tmp"
    if not os.path.exists(tmpDownloadFolderName):
        os.makedirs(tmpDownloadFolderName)
    for url in urlsToDownload:
        fileName = urllib_parse.urlparse(url).path.split("/")[-1]
        pathName = os.path.join(tmpDownloadFolderName, fileName)
        downloadFile(pathName, url)
    os.rename(tmpDownloadFolderName, downloadFolderName)


def downloadActivity(activity):
    downloadId = createKey(activity)
    mediaUrls = getMediaUrls(activity)
    logging.info("Activity: {}".format(downloadId))
    downloadMediaForActivity(downloadId, mediaUrls)


def downloadJournalPage(journalPageUrl, cookies):
    response = requests.get(journalPageUrl, cookies=cookies, headers={"accept": "application/json"})
    journalPage = response.json()
    downloaded = False
    for interval in journalPage.get("intervals", {}).values():
        for subInterval in interval:
            activity = subInterval.get("activity", {})
            if not activity:
                continue
            downloadActivity(activity)
            downloaded = True
    return downloaded


def downloadJournals(driver):
    cookies = getCookies(driver)
    accountId = getAccountId(driver)
    for page in range(1, MAX_JOURNALS):
        journalPageUrl = "{}/accounts/{}/journal_api?page={}".format(SITE, accountId, page)
        logging.info("Trying Page: {}".format(journalPageUrl))
        if not downloadJournalPage(journalPageUrl, cookies):
            logging.info("Stopping at: {}".format(journalPageUrl))
            break


def login(driver):
    driver.get("{}/login".format(SITE))

    elementUserName = driver.find_element(By.ID, "user_login")
    elementUserName.clear()
    elementUserName.send_keys(USER)

    elementPassword = driver.find_element(By.ID, "user_password")
    elementPassword.clear()
    elementPassword.send_keys(PASSWORD)

    elementPassword.submit()
    WebDriverWait(driver, 5).until(ExpectedConditions.url_contains("/headlines"), message="Not Logged in to Headlines.")


def main():
    logging.info("Starting ....")
    if not USER or not PASSWORD:
        raise PermissionError("No Credentials Set. Ensure you set Environment Variables.")

    logging.info("Launching Browser ....")
    driver = getWebDriver()

    logging.info("Logging In ....")
    login(driver)

    logging.info("Downloading Journals ....")
    downloadJournals(driver)

    logging.info("Closing Browser ....")
    driver.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
