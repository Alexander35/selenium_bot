from selenium_bot import SeleniumBot
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random


class YelpComClicker(SeleniumBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do(self):
        self.get_yelp()
        self.stay_on_page_time()
        self.click_find_by_keys()
        self.stay_on_page_time()
        self.find_page_with_target(1)

    def stay_on_page_time(self):
        curr_time = self.how_many_time()
        stay_time = random.randrange(self.conf['time_on_page_yelp_com']['from'],
                                     self.conf['time_on_page_yelp_com']['to'])
       
        if curr_time < self.conf['time_on_session']['to']:
            self.write_both_logs_info('stay on page for: {}sec, page : {}'.format(
                                      stay_time, curr_time))             
            time.sleep(stay_time)

    def get_yelp(self):
        self.driver.get("https://yelp.com")
        self.write_both_logs_info(
            'Get YELP.COM at {}'.format(self.how_many_time()))

    def click_find_by_keys(self):
        search_keys_index = random.randrange(len(self.conf["main_search_keys"]))
        current_search_keys = self.conf["main_search_keys"][search_keys_index]
        self.write_both_logs_info('current search keys are :{} . Time {}'.format(current_search_keys, self.how_many_time()))
        self.driver.find_element_by_id('find_desc').clear()
        self.driver.find_element_by_id('find_desc').send_keys(current_search_keys["find_desc"])
        self.driver.find_element_by_id('dropperText_Mast').clear()
        self.driver.find_element_by_id('dropperText_Mast').send_keys(current_search_keys["dropperText_Mast"])
        self.driver.find_element_by_id('header-search-submit').click()

        self.write_both_logs_info(
            'main search button at {}'.format(self.how_many_time()))

    def find_page_with_target(self, page):
        try:
            link = self.driver.find_element_by_partial_link_text(self.conf["search_for_company_yelp_com"])
            self.write_both_logs_info('We found a company link at {} company name : `{}`, page : {}'.format(
                self.how_many_time(), link.text, page))

            self.get_company_page(link)

        except NoSuchElementException as exc:
            self.write_both_logs_info('We have no found the searched company name: `{}`  into the current page : {}, get next page. time : {}'.format(
                                      self.conf['search_for_company_yelp_com'], page, self.how_many_time()))
            

            page_links = self.driver.find_elements_by_class_name(
                "pagination-label")

            for pl in page_links:
                if pl.text == "Next":
                    self.write_both_logs_info('Click!. time : {}'.format(
                                              self.how_many_time()))                    
                    try:
                        pl.click()
                        page = page + 1
                        self.stay_on_page_time()

                        if page > self.conf['page_trasholder_yelp_com']:
                            self.write_both_logs_info('Can`t find the company page link by walking on pages. Cantch page trasholder: {}. time : {}, EXIT!'.format(
                                                      self.conf['page_trasholder_yelp_com'], self.how_many_time()))
                            self.driver.quit()
                            break

                        self.write_both_logs_info('We found the `Next` button. Gonna get the next page: {}. time : {}'.format(
                                                  page, self.how_many_time()))                        
                    except StaleElementReferenceException:
                        self.find_page_with_target(page)
                    except ElementClickInterceptedException:
                        self.write_both_logs_info('Can`t click it. Sleep 3 secs. and try again time : {}'.format(
                                                  self.how_many_time()))                        
                        time.sleep(3)
                    finally:       
                        self.find_page_with_target(page)

    def get_company_page(self, company_page_link):
        company_page_link.click()
        self.write_both_logs_info('Get company page . Time : {}'.format(
                                  self.how_many_time()))

        self.write_both_logs_info('try to find the company link : {}, Time : {}'.format(
                                  self.current_target_url, self.how_many_time()))
        for i in range(10):
            try:
                company_site_link = self.driver.find_element_by_partial_link_text(self.current_target_url)
                company_site_link.click()
                self.write_both_logs_info('COMPANY SITE LINK CLICKED! Time : {}'.format(
                                          self.how_many_time()))
                self.stay_on_page_time() 
                break                                    
            except Exception as exc:
                self.write_both_logs_info('cant`t click to site link. try after 3 sec  Time : {}'.format(
                                          self.how_many_time()))
                time.sleep(3)

        self.write_both_logs_info('This is it, wait after session is closed! Time : {}'.format(
                                  self.how_many_time()))                                  

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

    SB = YelpComClicker(
        conf=conf,
        screen_resolutions=screen_resolutions,
        user_agents=user_agents,
        proxy_list=proxy_list
    )


if __name__ == '__main__':
    main()
