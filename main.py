import pickle
import time

from selenium import webdriver

from selenium.webdriver.support.wait import WebDriverWait


def login():
    # wait for 2 minutes for user to login
    WebDriverWait(driver, 120).until(lambda driver: driver.current_url == "https://www.duolingo.com/learn")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get('https://www.duolingo.com/')
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    except FileNotFoundError:
        login()
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    driver.refresh()
    time.sleep(10)
