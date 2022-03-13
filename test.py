import random
from queue import Queue
from random import choice, randint
from threading import Thread, RLock
from time import sleep

import multithreading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MultiThread(multithreading.MultiThread):
    def __init__(self, task_list=None, threads=None):
        self._lock = RLock()
        self._loop = True
        self._queue_task_list = Queue()

        self._task_list = task_list or []
        self._task_list_total = 0
        self._task_list_scanned_total = 0
        self._task_list_success = []
        self._task_list_failed = []

        self._threads = threads or 16
        self.playlist_url = str(input("Link playlist cần stream: "))

    def start_threads(self):
        for _ in range(min(self._threads, self._queue_task_list.qsize()) or self._threads):
            Thread(target=self.thread, daemon=True).start()
            sleep(8)


class Demo(MultiThread):
    def task(self, task):
        playlist_url = self.playlist_url
        username = task.split(':')[0]
        password = task.split(':')[-1]
        try:
            options = Options()
            options.add_argument(f'--user-agent={Main.GetRandomUserAgent()}')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
            options.add_argument('--lang=en')
            # Removes navigator.webdriver flag
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            # For older ChromeDriver under version 79.0.3945.16
            options.add_experimental_option('useAutomationExtension', False)
            # options.add_argument("window-size=400,400")
            # For ChromeDriver version 79.0.3945.16 or over
            options.add_argument('--disable-blink-features=AutomationControlled')
            # Fake ip address by public proxy
            # options.add_argument('–proxy-server=183.91.0.120:3128')
            driver = webdriver.Chrome(options=options, executable_path='C:\chromedriver.exe')
            Main.GoForIt(driver, username, password, playlist_url)
            sleep(99999)
        except AssertionError:
            print("Lỗi bấm nút")
        except Exception as e:
            print("Có lỗi gì đó")
            print(str(e))


class Main:
    def __init__(self):
        self.threads_number = int(input("Số lượng streaming: "))

    @staticmethod
    def ReadFile(filename, method):
        with open(filename, method) as f:
            return [line.strip('\n') for line in f]

    @staticmethod
    def GetRandomUserAgent():
        user_agents = Main.ReadFile('user_agents.txt', 'r')
        return choice(user_agents)

    @staticmethod
    def Login(driver, email, password, playlist_url):
        driver.get(f"https://accounts.spotify.com/en/login?continue={playlist_url}")
        driver.minimize_window()
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "login-username"))).send_keys(email)
        sleep(randint(1, 3))
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "login-password"))).send_keys(password)
        sleep(randint(1, 3))
        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='login-button']"))).click()
        except Exception as e:
            try:
                WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='login-button']"))).click()
            except Exception as e:
                try:
                    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='login-button']"))).click()
                except Exception as e:
                    try:
                        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='login-button']"))).click()
                    except Exception as e:
                        print(f"{email} không nhấn được nút login")
                        driver.maximize_window()
        sleep(randint(1, 3))

    @staticmethod
    def Play(driver, username):
        try:
            driver.find_element(by=By.XPATH, value="//div[@data-testid='action-bar-row']//button[@data-testid='play-button']").click()
        except Exception:
            print("Không nhấn được nút play")
            driver.maximize_window()
        print(f"******* Streaming with user {username} *******")
        try:
            sleep(5)
            driver.find_element(by=By.CLASS_NAME, value="banner-close-button").click()
        except Exception:
            print("Không tắt được banner")
            driver.maximize_window()

    @staticmethod
    def GoForIt(driver, username, password, playlist_url):
        Main.Login(driver, username, password, playlist_url)
        sleep(randint(3, 8))
        Main.Play(driver, username)

    def Start(self):
        combos = self.ReadFile('accounts.txt', 'r')
        random.shuffle(combos)
        demo = Demo(combos, threads=self.threads_number)
        demo.start()


if __name__ == "__main__":
    main = Main()
    main.Start()


