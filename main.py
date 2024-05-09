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


def calc_dot(path):
    edge_cords = [path]
    if "C" in path:
        edge_cords = path.split("C")
    ret = []
    for x in edge_cords:
        line = [i.replace("M", "").replace(" ", "") for i in x.split("L")]
        first_dot = [float(i) for i in line[0].split(",")][0:2]
        second_dot = [float(i) for i in line[1].split(",")]
        ret.append([round(j - i) for i, j in zip(first_dot, second_dot)])

    return ret


def draw_kanji():
    while not check_for_text("Continue"):
        action = ActionChains(driver)
        canvas = driver.find_elements(By.TAG_NAME, "svg")[1]
        path = canvas.find_element(By.TAG_NAME, "g").find_elements(By.TAG_NAME, "path")
        path = [i for i in path if not "pathLength" in i.get_attribute("outerHTML")][0]
        path_cords = path.get_attribute("d")
        action.move_to_element(path)
        res = calc_dot(path_cords)
        if len(res) == 2:
            action.move_by_offset(-(res[0][0] + res[1][0]), -(res[0][1] + res[1][1]))
        else:
            action.move_by_offset(-res[0][0], -res[0][1])
        action.click_and_hold()
        for cord in res:
            action.move_by_offset(2 * cord[0], 2 * cord[1])
        action.release()
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
    counter = 0
    timeSum = 0
    lastTime = time.time()
    # do kanji
    while True:
        try:
            driver.get('https://www.duolingo.com/alphabets/ja/kanji/group/9')
            time.sleep(3)
            if not first_task():
                continue
            if not second_task():
                continue
            if not third_task():
                continue
            time.sleep(1)
            # do kanji drawing
            while not check_for_text("Total XP") and not check_for_text("Bonus"):
                draw_kanji()
                time.sleep(1)
            counter += 1
            endTime = time.time()
            timeSum += endTime - lastTime
            print("Finished lessons:", counter, "\nLast finished in:", round(endTime - lastTime), "sec, average:", round(timeSum / counter), "sec")
            lastTime = endTime
        except Exception as e:
            print(e)
            print("Something went wrong")
