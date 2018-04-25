from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import random
import json
import time

class SeleniumBot():
	
	def __init__(self, conf=None, screen_resolutions=None, user_agents=None, proxy_list=None):

		self.target_url = conf['target_url']
		self.clicks_per_user = conf['clicks_per_user']
		self.device_type = conf['device_type']
		self.time_on_url = conf['time_on_url']
		self.screen_resolutions = screen_resolutions
		self.user_agents = user_agents
		self.proxy_list = proxy_list

		try:				

			options = Options()
			profile = webdriver.FirefoxProfile()

			device_type_index = random.randrange(len(self.device_type))
			current_user_agent = random.choice(self.user_agents[self.device_type[device_type_index]])
			# proxy_index = random.randrange(len(self.proxy_list['proxy_list']))
			current_proxy = random.choice(self.proxy_list['proxy_list'])

			# print(self.current_proxy.keys())
			current_proxy_addr = list(current_proxy)[0]
			current_proxy_port = current_proxy[current_proxy_addr]
			
			print('Proxy {} {}'.format(current_proxy_addr, current_proxy_port))

			profile.set_preference("network.proxy.type", 1)
			profile.set_preference("network.proxy.socks", current_proxy_addr)
			profile.set_preference("network.proxy.socks_port", current_proxy_port);			

			profile.set_preference("general.useragent.override", current_user_agent)
			
			profile.update_preferences()
			self.driver = webdriver.Firefox(firefox_profile=profile, firefox_options=options)

			# print(self.driver)

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

		spended_time = self.time_on_url['to'] - self.how_many_time()
		if spended_time < self.time_on_url['from']:
			time.sleep(self.time_on_url['from']-spended_time)

		spended_time = self.time_on_url['to'] - self.how_many_time()
		print('spended_time : {}'.format(spended_time))	

	def do(self):

		try:
			self.timer = time.time()
			self.get_current_url_time()
			self.get_url()
			self.current_clicks = random.randrange(self.clicks_per_user['from'], self.clicks_per_user['to'])
			self.clicker(1)

		except Exception as exc:
			print('step Error : {}'.format(exc))	

		finally:
			self.driver.quit()

	def get_current_url_time(self):
		self.current_url_time =  random.randrange(
				self.time_on_url['from'], 
				self.time_on_url['to']
		)	

	def elapsed_time(self):
		return self.current_url_time - self.how_many_time()		

	def how_many_time(self):
		return time.time() - self.timer

	def clicker(self, n):
		all_links = self.driver.find_elements_by_tag_name('a')

		try:
			all_links[random.randrange(len(all_links))].click()
			n += 1
		except Exception as exc:
			print('click filed : {}'.format(exc)) 	

		finally:
			if (self.elapsed_time() > 0) and (n < self.current_clicks):
				self.clicker(n)

	def get_url(self):


		self.driver.get(self.target_url)

def main():
	try:
		with open('conf/conf.json') as file:
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