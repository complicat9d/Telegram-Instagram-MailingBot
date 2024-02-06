from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from App.Config import inst_sessions_dirPath
from App.Logger import ApplicationLogger

from App.Parser.Xpath import *
from App.Parser.Parser import Parser
from App.Parser.ProxyExtension import ProxyExtension

import ssl
import pickle 
import time
import os
import asyncio
import functools

from dotenv import load_dotenv
load_dotenv()
logger = ApplicationLogger()

ssl._create_default_https_context = ssl._create_unverified_context

class InstagramParserExceptions():
    def __init__(self):
        self.IncorrectPasswordOrLogin = Exception("You have entered invalid password or login")
        self.PageNotFound = Exception("The channel name you have entered is invalid")
        self.SuspendedAccount = Exception("This instagram account has been suspended")


class InstagramParser(Parser):
    def __init__(
            self, 
            login: str,
            password: str
        ):
        super().__init__()
        self.login = login
        self.password = password

        ip, port, login, password = os.getenv("PROXY_ADDRESS").split(":")
        proxy_extension = ProxyExtension(ip, int(port), login, password)
        options = uc.ChromeOptions()
        options.add_argument(f"--load-extension={proxy_extension.directory}")
        self.driver = uc.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        logger.log_info(f"InstagramParser initialization on {self.login}'s account")

    async def async_logging_in(self):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.logging_in)
        return result

    def logging_in(self):
        instagramExceptions = InstagramParserExceptions()
        try:
            self.driver.get(url="https://instagram.com/")
            wait = WebDriverWait(self.driver, 15)
            cookies = wait.until(EC.element_to_be_clickable((By.XPATH, COOKIES_AGREEMENT_XPATH)))
            cookies.click()
            time.sleep(5)
            wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_INPUT_XPATH))).send_keys(self.login) 
            wait.until(EC.presence_of_element_located((By.XPATH, PASSWORD_INPUT_XPATH))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH))).click()
            time.sleep(10)
            current_url = self.driver.current_url
            if ("suspended" in current_url):
                logger.log_error(f"Account {self.login} has been banned")
                raise instagramExceptions.SuspendedAccount
            
            try:
                wait.until(EC.visibility_of_element_located((By.XPATH, PROBLEM_WITH_LOGGING_IN_XPATH)))
            except Exception as e:
                time.sleep(15)
                self.dump_cookies()
                logger.log_info(f"{self.login} account's cookies have been dumped successfully")
                return None
            else:
                logger.log_error("Invalid login or password have been entered by the user for logging in")
                raise instagramExceptions.IncorrectPasswordOrLogin
            
        except Exception as e:
            logger.log_error(f"An error occured while logging in user's instagram account: {e}")
            return e
        finally:
            self.close_parser()

    
    async def async_parse_follower(self, channel):
        loop = asyncio.get_event_loop()
        partial_parse_followers = functools.partial(self.parse_followers, channel)
        result = await loop.run_in_executor(None, partial_parse_followers)
        return result
        
    def parse_followers(self, channel: str):
        try:
            wait = WebDriverWait(self.driver, 15)

            self.driver.get(url="https://instagram.com/")
            wait.until(EC.element_to_be_clickable((By.XPATH, COOKIES_AGREEMENT_XPATH))).click()
            
            self.load_cookies()

            self.driver.get(url=f"https://instagram.com/{channel}/")

            try:
                self.driver.find_element(By.XPATH, PAGE_NOT_FOUND_XPATH)
            except Exception as e:
                pass
            else:
                logger.log_error(f"User with channel name {channel} has not been found, such page does not exist")
                raise InstagramParserExceptions.PageNotFound
            
            followers_count = int(wait.until(EC.presence_of_element_located((By.XPATH, FOLLOWER_COUNT_XPATH))).text.replace(',', ''))

            wait.until(EC.element_to_be_clickable((By.XPATH, FOLLOWERS_BUTTON_XPATH))).click()
            time.sleep(5)

            dialogue = wait.until(EC.presence_of_element_located((By.CLASS_NAME, FOLLOWER_DIALOGUE_CLASS_NAME)))
            self.scroll_followers_dialogue(
                followers_count=followers_count,
                dialogue=dialogue
            )
            followers = dialogue.find_elements(By.CLASS_NAME, FOLLOWER_USERNAME_CLASS_NAME)
            usernames = list(set([follower.text for follower in followers]))
    
            return usernames
        except Exception as e:
            logger.log_error(f"An error occured while parsing {channel}'s followers")
            return e
        finally:
            self.close_parser()
    

    def scroll_followers_dialogue(self, dialogue, followers_count, step=12):
        curr_followers_count = 12
        while curr_followers_count + step <= followers_count:
            self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", dialogue)
            time.sleep(2)  
            curr_followers_count += step


    def dump_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            pickle.dump(cookies, open(f"{inst_sessions_dirPath}/{self.login}.cookies", "wb"))
        except Exception as e:
            return e 
        
    def load_cookies(self):
        try:
            print(self.login)
            cookies = pickle.load(open(f"{inst_sessions_dirPath}/{self.login}.cookies", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            return e
    
# selenium.common.exceptions.ElementClickInterceptedException

# i.logging_in()

# print(
#     i.parse_followers(
#         channel="mashapetrova_1"
#     )
# )

async def main():
    i = InstagramParser(
        login="",
        password=""
    )
    result = await i.async_logging_in()
    result = await i.async_parse_follower(
        channel="dlgkdlkhjldkhkdl"
    )
    print(result)
    instagramParserExceptions = InstagramParserExceptions()
    print(instagramParserExceptions.IncorrectPasswordOrLogin)

if __name__ == "__main__":
    asyncio.run(main())