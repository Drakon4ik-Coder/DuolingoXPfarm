import pickle
import time

import keyboard
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait


def login():
    # wait for 2 minutes for user to login
    WebDriverWait(driver, 120).until(lambda driver: driver.current_url == "https://www.duolingo.com/learn")


# return kanji in passed string
def kanji(text):
    if "田中" in text:
        return "田中"
    elif "中山" in text:
        return "中山"
    elif "山口" in text:
        return "山口"
    return None


# translation from kanji to hiragana and romanji
hiragana = {"田中": "たなか", "中山": "なかやま", "山口": "やまぐち"}
romanji = {"田中": "Tanaka", "中山": "Nakayama", "山口": "Yamaguchi"}


# go to the next task
def go_next_task():
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Check')]").click()
    except:
        pass
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Continue')]").click()
    except:
        pass

# wait for text to be present on page
def wait_for_text(text):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '{}')]".format(text))))
        time.sleep(1)
    except:
        return False
    return True


# check whether text is present on page
def check_for_text(text):
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(text))
    except NoSuchElementException:
        return False
    return True


# begin session
def start_session():
    try:
        # load cookies
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    except FileNotFoundError:
        # login and save cookies
        login()
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))


def first_task():
    if not wait_for_text("Select the pronunciation for"):
        return False
    header = driver.find_element(By.XPATH, "//*[contains(text(), 'Select the pronunciation for')]")
    kanjiWord1 = kanji(header.text)
    if kanjiWord1 is None:
        return False
    answer = driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(hiragana[kanjiWord1]))
    answer.click()
    go_next_task()
    return True


def second_task():
    if not wait_for_text("Select the meaning for"):
        return False
    header = driver.find_element(By.XPATH, "//*[contains(text(), 'Select the meaning for')]")
    kanjiWord2 = kanji(header.text)
    if kanjiWord2 is None:
        return False
    answer = driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(romanji[kanjiWord2]))
    answer.click()
    go_next_task()
    return True


def third_task():
    if not wait_for_text("What sound does this make"):
        return False
    header = driver.find_element(By.XPATH, "//span[@lang='ja']")
    kanjiWord3 = kanji(header.text)

    driver.find_element(By.XPATH, "//input").send_keys(romanji[kanjiWord3])
    go_next_task()
    return True


def draw_kanji():
    while not check_for_text("Continue"):
        action = ActionChains(driver)
        canvas = driver.find_elements(By.TAG_NAME, "svg")[1]
        try:
            start = canvas.find_elements(By.TAG_NAME, "circle")[1]
            end = canvas.find_element(By.TAG_NAME, "image")
            if end.get_attribute("height") != "18":
                raise Exception("No end")
            action.move_to_element(start)
            action.click_and_hold()
            action.move_to_element(end)
            action.release()
            try:
                action.perform()
            except:
                pass
        except IndexError:
            action.click(canvas.find_element(By.TAG_NAME, "path"))
            action.perform()
            action.click(canvas.find_element(By.TAG_NAME, "path"))
            action.perform()
        except:
            action.click(canvas.find_element(By.TAG_NAME, "path"))
            action.perform()
        time.sleep(0.1)
    go_next_task()


if __name__ == '__main__':
    # mute chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")

    driver = webdriver.Chrome(chrome_options)

    driver.get('https://www.duolingo.com/')

    start_session()

    # do kanji
    while True:
        driver.get('https://www.duolingo.com/alphabets/ja/kanji/group/4')
        time.sleep(3)
        if not first_task():
            continue
        if not second_task():
            continue
        if not third_task():
            continue
        # do kanji drawing
        while not check_for_text("Total XP"):
            time.sleep(1)
            draw_kanji()
        # finish lesson
        go_next_task()
        time.sleep(1)
