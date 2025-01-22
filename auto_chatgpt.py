from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#from webdriver_manager.chrome import ChromeDriverManager
#pip install webdriver_manager
import undetected_chromedriver as uc
import configparser
import json
import time


# Make a new class from uc.Chrome and redefine quit() function to suppress OSError
class Chrome(uc.Chrome):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def quit(self):
        try:
            super().quit()
        except OSError:
            pass


class AutoChatGPT:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            return super().__new__(cls)
        return cls._instance

    def __init__(self):
        if AutoChatGPT._instance is None:
            AutoChatGPT._instance = self
            self.load_config()
            self.initialize()

    def initialize(self):
        self.access_website()
        self.load_cookies()
        self.click_ok_lets_go_button()
        self.send_default_message()

    def reinitialize(self):
        self.driver.quit()
        self.initialize()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        self.userAgent = config['default']['userAgent']
        self.password = config['default']['password']
        self.headless = config.getboolean('default', 'headless', fallback=False)
        self.cookies_path = config['driver']['cookies_path']
        self.unexpected_wait_time = config.getint('context', 'unexpected_wait_time')
        self.wait_time = config.getint('context', 'wait_time')
        self.timeout = config.getint('context', 'timeout')
        self.prompt_message = config['context']['prompt_message']

    def access_website(self):
        self.chrome_options = webdriver.ChromeOptions()
        if self.headless:
            self.chrome_options.add_argument('--headless') # must options for Google Colab
        #self.chrome_options.add_argument("--remote-debugging-address=0.0.0.0")
        self.chrome_options.add_argument('--no-sandbox') # Vô hiệu hóa chế độ "sandbox" của Chrome
        self.chrome_options.add_argument('--disable-dev-shm-usage') # Sử dụng đĩa thay vì bộ nhớ chia sẻ /dev/shm (shared memory)
        self.chrome_options.add_argument("--disable-extensions") # Vô hiệu hóa tất cả các tiện ích mở rộng (extensions) đã cài đặt trong Chrome
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument('--window-size=1920x1080')
        self.chrome_options.add_argument(f"user-agent={self.userAgent}")

        #service = Service(ChromeDriverManager().install())
        #self.driver = Chrome(service=service, options=self.chrome_options)
        self.driver = Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver.get("https://chatgpt.com/")

    def load_cookies(self):
        with open(self.cookies_path, 'r') as file:
            cookies = json.load(file)
        # Add cookies into the browser
        for cookie in cookies:
            # If domain is left in, then in the browser domain gets transformed to f'.{domain}'
            cookie.pop('domain', None)
            self.driver.add_cookie(cookie)
        # Refresh the page to apply the cookies
        self.driver.refresh()

    # Click "Ok. Let's go!" button if it exists
    def click_ok_lets_go_button(self):
        try:
            btn: WebElement = WebDriverWait(self.driver, self.unexpected_wait_time).until(
                EC.presence_of_element_located((By.XPATH, '//button[@data-testid="getting-started-button"]'))
            )
            if btn:
                btn.click()
        except Exception as e:
            pass

    def send_default_message(self):
        if self.prompt_message:
            response = self.send_request(self.prompt_message, self.password)
            print(response)

    def send_request(self, request: str, password: str = "") -> str:
        if password != self.password:
            raise ValueError("Invalid password")

        # Find the text area
        text_area: WebElement = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//div[@id="prompt-textarea"]'
            ))
        )
        if not text_area:
            return None
        
        # Input the request line by line
        lines = request.split('\n')
        for line in lines:
            text_area.send_keys(line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)

        # Count the number of "thumbups" to determine whether the reponse is finished
        thumbups = len(self.driver.find_elements(By.XPATH, '//button[@aria-label="Good response"]'))

        # Click the "Send" button
        send_button = WebDriverWait(self.driver, self.unexpected_wait_time).until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//button[@aria-label="Send prompt" and @data-testid="send-button"]'
            ))
        )
        if send_button.is_enabled():
            send_button.click()
        else:
            print("Send button is disabled.")
            return ""

        # Wait for the response, re-generate at most 3 times
        max_try = 3
        while max_try > 0:
            try:
                # Wait the stop button to appear
                stop_button = WebDriverWait(self.driver, self.unexpected_wait_time).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//button[@aria-label="Stop streaming" and @data-testid="stop-button"]'
                    ))
                )

                # Wait the voice button to appear -> the response is finished
                try:
                    send_button = WebDriverWait(self.driver, self.timeout).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            '//button[@data-testid="composer-speech-button" and @aria-label="Start voice mode"]'
                        ))
                    )
                except TimeoutError as e:
                    # Wait too long, stop generating
                    print("TimeoutError...")
                    stop_button.click()

                # Wait for the thumbups to increase -> the response is finished
                for _ in range(self.unexpected_wait_time):
                    new_thumbups = len(self.driver.find_elements(By.XPATH, '//button[@aria-label="Good response"]'))
                    if new_thumbups != thumbups:
                        break
                    time.sleep(1)

                # Get the last response
                time.sleep(self.unexpected_wait_time)
                last_answer = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR,
                        'div[data-message-author-role="assistant"]'
                    ))
                )
                last_answer = last_answer[-1]

            # Click the "Regenerate" button if cannot get the last response
            except Exception as e:
                print(e)
                try:
                    regenerate_button = WebDriverWait(self.driver, self.unexpected_wait_time).until(
                        EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "btn relative btn-primary m-auto") and contains(., "Regenerate")]'))
                    )
                    regenerate_button.click()
                    print("Regenerate button clicked.")
                except:
                    print("Regenerate button not found.")
                max_try -= 1

            else:
                return last_answer.text
        return None

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    auto_chat_gpt = AutoChatGPT()
    while True:
        request = input("You: ")
        if request == "exit":
            break
        response = auto_chat_gpt.send_request(request, auto_chat_gpt.password)
        print("Bot:", response)