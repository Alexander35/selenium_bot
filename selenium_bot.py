from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options
import random
import json
import time

class SeleniumBot():
	
	def __init__(self, target_url, device_type, client_hosts, time_on_url):

		self.target_url = target_url
		self.client_hosts = client_hosts
		self.device_type = device_type
		self.time_on_url = time_on_url

		try:
			# with open('conf/conf.json') as file:
			# 	self.conf = json.load(file)

			with open('conf/screen_resolutions.json') as file:
				self.screen_resolutions = json.load(file)

			with open('conf/user_agents.json') as file:
				self.user_agents = json.load(file)				

		except Exception as exc:
			print('Can not init confs : {}'.format(exc))	

		try:				

			options = Options()
			options.set_headless(headless=True)
			profile = webdriver.FirefoxProfile()

			self.current_user_agent = random.choice(self.user_agents[self.device_type])
			profile.set_preference("general.useragent.override", self.current_user_agent)
			
			self.driver = webdriver.Firefox(profile, firefox_options=options)

		except Exception as exc:
			print('Can not init driver : {}'.format(exc))

		try:

			for ch in range(client_hosts):
				self.url()
				sleep_time = random.randrange(
						time_on_url['from'], 
						time_on_url['to']
					)
				print('sleep_time : {}'.format(sleep_time))
				time.sleep(sleep_time)

			self.driver.quit()	

		except Exception as exc:
			print('step Error : {}'.format(exc))	

	def url(self):
		print('step begin')
		# print('screen_resolutions : {}'.format(self.screen_resolutions['phone']))
		current_screen_resolution = random.choice(self.screen_resolutions[self.device_type])
		
		#todo change webagent
		#todo change proxy

		print('current_screen_resolution : {}'.format(current_screen_resolution))
		print('current_UA : {}'.format(self.current_user_agent))

		self.driver.set_window_size(
				current_screen_resolution['h'], 
				current_screen_resolution['w'], 
				self.driver.window_handles[0]
			)

		self.driver.get(self.target_url)
		

		print('step end')

def main():

	with open('conf/conf.json') as file:
		conf = json.load(file)
	
	SB = SeleniumBot(
			conf['target_url'],
			conf['device_type'], 
			conf['client_hosts'], 
			conf['time_on_url']
		)
	# SB.step()

if __name__ == '__main__':
	main()	