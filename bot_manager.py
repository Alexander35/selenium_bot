from selenium_bot import SeleniumBot
import json
import random

class BotManager():

	def __init__(self):

		try:
			with open('conf/conf.json') as file:
				self.conf = json.load(file)
		except Exception as exc:
			print('read conf error : {}'.format(exc))	

		self.thread_numbers = self.calculate_threads_number()	
		self.create_schedule()	

	def calculate_threads_number(self):
		return 1 + self.conf['client_hosts'] // (86400 // self.conf['time_on_url']['to'])

	def create_schedule(self):
		day_time = []
		night_time = []

		for i in range(int(self.thread_numbers * 0.8)): 
			day_time.append(random.randrange(12, 23))
		
		for	i in range(int(self.thread_numbers * 0.2)):
			night_time.append(random.randrange(0, 11))

		a = {'day_time' : day_time, 'night_time' : night_time}	

		print(a)	

		# return ('day_time': day_time, 'night_time' : night_time)
	
	def spawn_thread(self):
		pass		


def main():

	
	# run with one UA sting for client_hosts times
	# SB = SeleniumBot(
	# 		conf['target_url'],
	# 		conf['device_type'], 
	# 		conf['client_hosts'], 
	# 		conf['time_on_url']
	# 	)

	BM = BotManager()


if __name__ == '__main__':
	main()