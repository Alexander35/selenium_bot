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
			current_user_agent = random.choice(self.user_agents[self.device_type[device_type_index]])

			target_url_index = random.randrange(len(self.conf['target_url']))
			self.current_target_url = self.conf['target_url'][target_url_index]
			
			if self.conf['proxy_type'] != 'no':
				current_proxy = random.choice(self.proxy_list['proxy_list'])

				print(current_proxy)

				current_proxy_addr = list(current_proxy)[0]
				current_proxy_port = current_proxy[current_proxy_addr]			

				profile.set_preference("general.useragent.override", current_user_agent)

				# profile.set_preference("network.proxy.type", 1)
				profile.set_preference("network.proxy.share_proxy_settings", True)
				profile.set_preference("network.http.use-cache", False)
				# profile.set_preference("network.proxy.http", current_proxy_addr)
				# profile.set_preference("network.proxy.http_port", int(current_proxy_port))
				# profile.set_preference('network.proxy.ssl_port', int(current_proxy_port))
				# profile.set_preference('network.proxy.ssl', current_proxy_addr)
				profile.set_preference('network.proxy.socks', current_proxy_addr)
				profile.set_preference('network.proxy.socks_port', int(current_proxy_port))		
			
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

		# self.driver.implicitly_wait(10)
		requests.get(self.current_target_url, headers={'referer': self.conf['referer_url']})
		# print('ref : {}'.format(a))
		print('get_current_target_url : {}'.format(self.current_target_url))
		self.driver.get(self.current_target_url)

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