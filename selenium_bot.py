from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
import json
import time
import requests
import logging
import os
import os
import errno
import re
import sys


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


class SeleniumBot():

    def write_both_logs_info(self, message):
        self.user_logger.info(message)
        self.system_logger.info(message)

    def __init__(self, conf=None, screen_resolutions=None, user_agents=None, proxy_list=None):

        self.target_url = conf['target_url']
        self.clicks_per_user = conf['clicks_per_user']
        self.device_type = conf['device_type']
        self.time_on_session = conf['time_on_session']
        self.screen_resolutions = screen_resolutions
        self.user_agents = user_agents
        self.proxy_list = proxy_list
        self.conf = conf

        self.timer_string = time.strftime("%d%b%Y_%H_%M_%S")
        stripped_url = re.sub(r'\W+', '', conf['target_url'][0])
        log_folder_name = os.path.join(
            'log', '{}{}'.format(self.timer_string, stripped_url))
        if not os.path.exists(log_folder_name):
            os.makedirs(log_folder_name)

        self.user_logger = setup_logger('user_logger', os.path.join(
            log_folder_name, 'user_log.log'), level=logging.DEBUG)
        self.system_logger = setup_logger('system_logger',  os.path.join(
            log_folder_name, 'system_log.log'), level=logging.DEBUG)
        self.write_both_logs_info('Log started')

        try:
            options = Options()

            if conf['headless'] == "yes":
                options.add_argument("--headless")

            profile = webdriver.FirefoxProfile()

            device_type_index = random.randrange(len(self.device_type))
            self.current_user_agent = random.choice(
                self.user_agents[self.device_type[device_type_index]])

            self.write_both_logs_info(
                'Current UA : {}'.format(self.current_user_agent))

            target_url_index = random.randrange(len(self.conf['target_url']))
            self.current_target_url = self.conf['target_url'][target_url_index]

            self.write_both_logs_info(
                'Current Target URL : {}'.format(self.current_target_url))

            self.proxies_for_request = None

            profile.set_preference(
                "general.useragent.override", self.current_user_agent)

            if self.conf['proxy_type'] != 'no':
                if self.conf['proxy_type'] == 'conf_file':
                    current_proxy = random.choice(self.proxy_list['proxy_list'])
                    current_proxy_addr = list(current_proxy)[0]
                    current_proxy_port = current_proxy[current_proxy_addr]
                elif self.conf['proxy_type'] == 'api.getproxylist.com':
                    response = requests.get(
                        'https://api.getproxylist.com/proxy?protocol[]=socks5&country[]=US&lastTested=3600&anonymity[]=high%20anonymity&anonymity[]=anonymous&allowsUserAgentHeader=1&maxSecondsToFirstByte=1&allowsHttps=1&maxConnectTime=1&minUptime=75&apiKey={}'.format(
                            self.conf['getproxylist_api_key']))
                    response = json.loads(response.text)
                    current_proxy_addr = response['ip']
                    current_proxy_port = response['port']
                    current_proxy = '{} : {}'.format(response['ip'], response['port'])

                with open('conf/used_proxy.json', encoding='utf-8') as used_proxy_file:
                    used_proxy = json.load(used_proxy_file)
                    if current_proxy_addr in used_proxy:
                        self.write_both_logs_info(
                            'The proxy used before. Exit : {}'.format(current_proxy))
                        sys.exit()

                used_proxy[current_proxy_addr] = current_proxy_port
                with open('conf/used_proxy.json', 'w') as save_proxy_file:
                    json.dump(used_proxy, save_proxy_file)

                self.write_both_logs_info(
                    'Current Proxy : {}'.format(current_proxy))

                self.proxies_for_request = {
                    'http': 'socks5://{}:{}'.format(current_proxy_addr, current_proxy_port),
                    'https': 'socks5://{}:{}'.format(current_proxy_addr, current_proxy_port),
                }

                profile.set_preference("network.proxy.type", 1)
                profile.set_preference(
                    "network.proxy.share_proxy_settings", False)
                profile.set_preference("network.http.use-cache", False)
                profile.set_preference(
                    'network.proxy.socks', current_proxy_addr)
                profile.set_preference(
                    'network.proxy.socks_port', int(current_proxy_port))



            caps = DesiredCapabilities().FIREFOX
            # interactive
            caps["pageLoadStrategy"] = "eager"

            self.driver = webdriver.Firefox(
                capabilities=caps, firefox_profile=profile, firefox_options=options, log_path="log/geckodriver.log")
            self.driver.set_page_load_timeout(300)
            current_screen_resolution = random.choice(
                self.screen_resolutions[self.device_type[device_type_index]])

            self.write_both_logs_info(
                'Current Screen Resolution : {}'.format(current_screen_resolution))

            self.driver.set_window_size(
                current_screen_resolution['h'],
                current_screen_resolution['w'],
                self.driver.window_handles[0]
            )

        except Exception as exc:
            print('Can not init driver : {}'.format(exc))
            self.system_logger.critical('Can not init driver : {}'.format(exc))
            self.driver.quit()

        self.write_both_logs_info('Task Starts')
        self.timer = time.time()
        self.get_current_url_time()
        self.do()

        if self.how_many_time() < self.time_on_session['from']:
            time.sleep(self.time_on_session['from']-self.how_many_time())

        self.write_both_logs_info(
            'Spended Time : {}'.format(self.how_many_time()))
        self.write_both_logs_info(
            'Task Ends'.format(current_screen_resolution))

        self.driver.quit()

    def do(self):

        try:

            if self.conf['serch_in_the_web'] != "no":
                self.write_both_logs_info(
                    'Search Throught Search Engines Starts')
                self.search_in_the_web()
                self.write_both_logs_info(
                    'Search Throught Search Engines Ends')

            # self.timer = time.time()

            # self.get_current_url_time()
            self.get_url()
            if self.conf['random_clicks'] != "no":
                self.current_clicks = random.randrange(
                    self.clicks_per_user['from'], self.clicks_per_user['to'])
                self.write_both_logs_info(
                    'Current Estimating Clicks Per Session: {}'.format(self.current_clicks))
                self.clicker(1)

        except Exception as exc:
            print('Session Error : {}'.format(exc))
            self.system_logger.error('Session Error : {}'.format(exc))
            

    def get_current_url_time(self):
        self.current_session_time = random.randrange(
            self.time_on_session['from'],
            self.time_on_session['to']
        )
        self.write_both_logs_info(
            'Current Estimating Session Duration: {}'.format(self.current_session_time))

    def elapsed_time(self):
        return self.current_session_time - self.how_many_time()

    def how_many_time(self):
        return time.time() - self.timer

    def get_all_links(self):
        return self.driver.find_elements_by_tag_name('a')

    def clicker(self, n):

        all_links = self.get_all_links()

        try:
            link = all_links[random.randrange(len(all_links))]

            if self.conf['target_url'][0] in link.get_attribute('href'):
                self.write_both_logs_info(
                    'Try To Click To: {}'.format(link.get_attribute('href')))
                link.location_once_scrolled_into_view
                link.click()
            n += 1
        except Exception as exc:
            self.system_logger.warning('click filed : {}'.format(exc))
            print('click filed : {}'.format(exc))

        finally:
            if (self.elapsed_time() > 0) and (n < self.current_clicks):
                self.clicker(n)

    def get_url(self):
        # if self.conf['referer_url'] != "no":
        #   print(self.proxies_for_request)
        #   a =requests.get(
        #       self.current_target_url,
        #       headers={'Referer': self.conf['referer_url'], 'User-Agent': self.current_user_agent},
        #       proxies=self.proxies_for_request
        #   )
        #   print(a)
        self.write_both_logs_info(
            'Gets Current Target URL: {}'.format(self.current_target_url))
        self.driver.get(self.current_target_url)

    def search_in_the_web(self, page_parameter=0):
        # print('page_parameter {}'.format(page_parameter))
        # self.write_both_logs_info('Search With Params: {}'.format(self.current_target_url))
        if page_parameter > 3:
            return

        for search_engine in self.conf['search_engines']:
            for keyword in self.conf['search_keywords']:
                try:
                    self.write_both_logs_info('Search Engine: {}, Search Keyword: {}, Search For: {} '.format(
                        search_engine, keyword, self.conf['target_url'][0]))
                    if page_parameter == 0:
                        self.driver.get('{}{}'.format(search_engine, keyword))
                    else:
                        p_string = '&start={}&p={}'.format(
                            page_parameter*10, page_parameter+1)
                        self.driver.get('{}{}{}'.format(
                            search_engine, keyword, p_string))

                    elems = self.driver.find_elements_by_tag_name('a')
                    for e in elems:
                        if ((self.clean_domain_fix(self.conf['target_url'][0]) in e.get_attribute('href'))
                                and (search_engine not in e.get_attribute('href'))):
                            self.write_both_logs_info(
                                'Click To: {} '.format(e.get_attribute('href')))
                            e.click()

                    for searched_link_title in self.conf['searched_link_titles']:
                        elems1 = self.driver.find_elements_by_partial_link_text(
                            searched_link_title)
                        for e in elems1:
                            self.write_both_logs_info(
                                'Click To: {} '.format(e.get_attribute('href')))
                            e.click()

                except Exception as exc:
                    print('error when search keywords : {}'.format(exc))
                    self.system_logger.error(
                        'error when search keywords : {}'.format(exc))

        self.search_in_the_web(page_parameter=page_parameter+1)

    def clean_domain_fix(self, raw_domain):
        clean_domain = raw_domain\
            .replace('https://www.', '')\
            .replace('https://', '')\
            .replace('http://www.', '')\
            .replace('http://', '')\
            .replace('/', '')

        return clean_domain


def main():
    try:
        with open('conf/conf.json', encoding='utf-8') as file:
            conf = json.load(file)

        with open('conf/screen_resolutions.json') as file:
            screen_resolutions = json.load(file)

        with open('conf/user_agents.json') as file:
            user_agents = json.load(file)

        with open('conf/proxy_list.json') as file:
            proxy_list = json.load(file)

    except Exception as exc:
        print('Can not init confs : {}'.format(exc))

    SB = SeleniumBot(
        conf=conf,
        screen_resolutions=screen_resolutions,
        user_agents=user_agents,
        proxy_list=proxy_list
    )


if __name__ == '__main__':
    main()
