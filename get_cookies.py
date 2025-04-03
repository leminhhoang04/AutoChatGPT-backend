from selenium import webdriver
import undetected_chromedriver as uc
import configparser
import json
import os

config = configparser.ConfigParser()
config.read('config.ini')
userAgent = config['default']['userAgent']
chromeVersion = int(config['default']['chromeVersion'])

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--no-sandbox') # Vô hiệu hóa chế độ "sandbox" của Chrome
#chrome_options.add_argument('--disable-dev-shm-usage') # Sử dụng đĩa thay vì bộ nhớ chia sẻ /dev/shm (shared memory)
chrome_options.add_argument("--disable-extensions") # Vô hiệu hóa tất cả các tiện ích mở rộng (extensions) đã cài đặt trong Chrome
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--window-size=1920x1080')
chrome_options.add_argument(f"user-agent={userAgent}")

driver = uc.Chrome(options=chrome_options, version_main=chromeVersion)
driver.maximize_window()
driver.get("https://chatgpt.com/")

input("Please log in manually and press Enter to continue...")
cookies_list = driver.get_cookies()
with open("cookies.pkl", 'w') as file_path:
    json.dump(cookies_list, file_path, indent=2, sort_keys=True)

try:
    driver.close()
except Exception as e:
    print(e)