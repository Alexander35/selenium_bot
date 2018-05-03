from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import random
import json
import time
import requests

class SeleniumBot():
	
	def __init__(self, conf=None, screen_resolutions=None, user_agents=None, proxy_list=None):

		self.target_url = conf['target_url']
		self.clicks_per_user = conf['clicks_per_user']
		self.device_type = conf['device_type']
		self.time_on_session = conf['time_on_session']
		self.screen_resolutions = screen_resolutions
		self.user_agents = user_agents
		self.proxy_list = proxy_list
		self.conf = conf

		try:				
			options = Options()
			profile = webdriver.FirefoxProfile()

			device_type_index = random.randrange(len(self.device_type))
			self.current_user_agent = random.choice(self.user_agents[self.device_type[device_type_index]])

			target_url_index = random.randrange(len(self.conf['target_url']))
			self.current_target_url = self.conf['target_url'][target_url_index]

			self.proxies_for_request = None
			
			
			if self.conf['proxy_type'] != 'no':
				current_proxy = random.choice(self.proxy_list['proxy_list'])

				print(current_proxy)

				current_proxy_addr = list(current_proxy)[0]
				current_proxy_port = current_proxy[current_proxy_addr]	

				self.proxies_for_request = {
					# http='socks5://{}:{}'.format(current_proxy_addr, current_proxy_port),
				
     #                https='socks5://{}:{}'.format(current_proxy_addr, current_proxy_port)
     				  'http':'socks5://{}:{}'.format(current_proxy_addr, current_proxy_port),
     				  'https':'socks5://{}:{}'.format(current_proxy_addr, current_proxy_port),
                }		

				profile.set_preference("general.useragent.override", self.current_user_agent)

				profile.set_preference("network.proxy.type", 1)
				profile.set_preference("network.proxy.share_proxy_settings", False)
				profile.set_preference("network.http.use-cache", False)
				# profile.set_preference("network.proxy.http", current_proxy_addr)
				# profile.set_preference("network.proxy.http_port", int(current_proxy_port))
				# profile.set_preference('network.proxy.ssl_port', int(current_proxy_port))
				# profile.set_preference('network.proxy.ssl', current_proxy_addr)
				profile.set_preference('network.proxy.socks', current_proxy_addr)
				profile.set_preference('network.proxy.socks_port', int(current_proxy_port))
				# self.driver.set_page_load_timeout(300)	
			
			# profile.update_preferences()
			self.driver = webdriver.Firefox(firefox_profile=profile, firefox_options=options)
			self.driver.set_page_load_timeout(30)
			current_screen_resolution = random.choice(self.screen_resolutions[self.device_type[device_type_index]])

			# print('current_screen_resolution : {}'.format(current_screen_resolution))
			# print('current_UA : {}'.format(current_user_agent))

			self.driver.set_window_size(
					current_screen_resolution['h'], 
					current_screen_resolution['w'], 
					self.driver.window_handles[0]
				)

		except Exception as exc:
			print('Can not init driver : {}'.format(exc))
			self.driver.quit()

		self.do()

		if self.how_many_time() < self.time_on_session['from']:
			time.sleep(self.time_on_session['from']-self.how_many_time())


		print('spended_time : {}'.format(self.how_many_time()))	

	def do(self):

		try:
			print('search_keywords : {}'.format(self.conf['search_keywords'])  )
			print('search_engines : {}'.format(self.conf['search_engines'])  )
			
			if self.conf['serch_in_the_web'] != "no":
				self.search_in_the_web()

			self.timer = time.time()
			self.get_current_url_time()
			self.get_url()
			self.current_clicks = random.randrange(self.clicks_per_user['from'], self.clicks_per_user['to'])
			print('current_clicks {} '.format(self.current_clicks))
			self.clicker(1)

		except Exception as exc:
			print('step Error : {}'.format(exc))	

		finally:
			self.driver.quit()

	def get_current_url_time(self):
		self.current_session_time =  random.randrange(
				self.time_on_session['from'], 
				self.time_on_session['to']
		)	
		print('current session time {}'.format(self.current_session_time))

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
				print('LINK : {}'.format(link.get_attribute('href')))
				link.click()
			n += 1
		except Exception as exc:
			print('click filed : {}'.format(exc)) 	

		finally:
			if (self.elapsed_time() > 0) and (n < self.current_clicks):
				self.clicker(n)

	def get_url(self):

		if self.conf['referer_url'] != "no":
			print(self.proxies_for_request)
			a =requests.get(
				self.current_target_url, 
				headers={'Referer': self.conf['referer_url'], 'User-Agent': self.current_user_agent}, 
				proxies=self.proxies_for_request
			)
			print(a)
			
		print('get_current_target_url : {}'.format(self.current_target_url))
		self.driver.get(self.current_target_url)

	def search_in_the_web(self, page_parameter=0):
		print('page_parameter {}'.format(page_parameter))
		if page_parameter > 3:
			return

		for search_engine in self.conf['search_engines']:
			for keyword in self.conf['search_keywords']:
				try:
					print(search_engine, keyword,self.conf['target_url'][0])
					if page_parameter==0:
						self.driver.get('{}{}'.format(search_engine,keyword))
					else:
						p_string = '&start={}&p={}'.format(page_parameter*10, page_parameter+1)
						self.driver.get('{}{}{}'.format(search_engine,keyword, p_string))	

					elems = self.driver.find_elements_by_tag_name('a')
					for e in elems:
						if ((self.clean_domain_fix(self.conf['target_url'][0]) in e.get_attribute('href')) 
							and (search_engine not in e.get_attribute('href')) ):
							print(e.get_attribute('href'))
							e.click()

					for searched_link_title in self.conf['searched_link_titles']:
						elems1 = self.driver.find_elements_by_partial_link_text(searched_link_title)
						for e in elems1:
							print(e.get_attribute('href'))
							e.click()

				except Exception as exc:
					print('error when search keywords : {}'.format(exc))	

		self.search_in_the_web(page_parameter=page_parameter+1)			
		# self.driver.quit()			

	def clean_domain_fix(self, raw_domain):
		clean_domain = raw_domain\
			.replace('https://www.', '')\
			.replace('https://', '')\
			.replace('http://www.', '')\
			.replace('http://', '')\
			.replace('/','')

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