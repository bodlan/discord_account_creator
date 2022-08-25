import random
import string
import time
import requests
import datetime

from libraries import logger
from libraries import CONFIG
from RPA.Browser.Selenium import Selenium
from twocaptcha import TwoCaptcha


class Discord:
    def __init__(self, email: str, username: str):
        self.email = email
        self.username = username
        self.password = self.generate_password()
        self.browser = Selenium()
        self.solver = TwoCaptcha(CONFIG.CAPTCHA_API_KEY)
        self.session = requests.session()
        self.start_date = datetime.datetime.strptime("1980-1-1", "%Y-%m-%d")
        self.end_date = datetime.datetime.strptime("2007-12-31", "%Y-%m-%d")
        self.random_day = self.random_date(self.start_date, self.end_date)

    @staticmethod
    def random_date(start, end):
        """
        This function will return a random datetime between two datetime
        objects.
        """
        delta = end - start
        int_delta = delta.days
        random_delta = random.randrange(int_delta)
        random_date = (start + datetime.timedelta(days=random_delta)).date()
        return random_date.strftime("%Y-%m-%d")

    def create_account(self):
        """
        Create discord account using requests
        :return: Token to discord account
        """
        submit_url = (
            f"http://2captcha.com/in.php?"
            f"key={CONFIG.CAPTCHA_API_KEY}"
            f"&method=hcaptcha"
            f"&sitekey={CONFIG.DISCORD_SITE_KEY}"
            f"&pageurl={CONFIG.DISCORD_SITE}"
        )
        r = requests.get(url=submit_url).text
        get_id = r.replace("OK|", "")
        print("ID:", get_id)
        self.session.headers["X-Fingerprint"] = self.session.get("https://discord.com/api/v9/experiments").json()[
            "fingerprint"
        ]
        fingerprint = self.session.headers["X-Fingerprint"]
        while True:
            print("Trying to get captcha key...")
            get_url = f"http://2captcha.com/res.php?key={CONFIG.CAPTCHA_API_KEY}&action=get&id={get_id}"
            captcha_key = requests.get(get_url).text
            if "OK" in captcha_key:
                captcha_key = captcha_key.replace("OK|", "")
                logger.info("Captcha key: %s" % captcha_key)
                headers = {"content-type": "application/json"}
                payload = {
                    "fingerprint": fingerprint,
                    "email": self.email,
                    "username": self.username,
                    "password": self.password,
                    "invite": "null",
                    "consent": "true",
                    "date_of_birth": self.random_day,
                    "gift_code_sku_id": "null",
                    "captcha_key": captcha_key,
                    "promotional_email_opt_in": "false",
                }
                token = requests.post(CONFIG.DISCORD_SITE_API, json=payload, headers=headers).text
                if "token" in token:
                    print(token)
                    return token
                else:
                    print("Failed request")
                    return None
            else:
                time.sleep(4)

    # Tried create_account using selenium, failed on Captcha.
    def register(self):
        try:
            self.browser.open_available_browser(CONFIG.DISCORD_SITE)
            self.browser.maximize_browser_window()
            self.browser.input_text_when_element_is_visible('//input[@name="email"]', self.email)
            self.browser.input_text_when_element_is_visible('//input[@name="username"]', self.username)
            self.password = self.generate_password()
            self.browser.input_text_when_element_is_visible('//input[@name="password"]', self.password)
            for i in range(1, 4):
                if i == 3:
                    self.browser.press_keys(f'//div[@tabindex="{i}"]//div[@class="css-1hwfws3"]', "2000+RETURN")
                else:
                    self.browser.press_keys(f'//div[@tabindex="{i}"]//div[@class="css-1hwfws3"]', "1+RETURN")
            self.browser.click_button('//button[@type="submit"]')
            self.browser.wait_until_page_contains_element(
                '//textarea[@name="h-captcha-response"]', timeout=datetime.timedelta(seconds=15)
            )
            url = self.browser.get_location()
            print("URL:", url)
            logger.info("Solving captcha")
            result = self.solver.hcaptcha(sitekey=CONFIG.DISCORD_SITE_KEY, url=url)
            print("result:", result)
            code = result["code"]
            self.browser.execute_javascript(f'document.getElementsByName("g-recaptcha-response")[0].innerHTML="{code}"')
            self.browser.execute_javascript(f'document.getElementsByName("h-captcha-response")[0].innerHTML="{code}"')
            print("After Js")
        except Exception as ex:
            logger.info("Exception in register function %s" % ex)

    @staticmethod
    def generate_password() -> str:
        password = "".join(random.choice(string.ascii_letters) for _ in range(random.randint(8, 12)))
        return password
