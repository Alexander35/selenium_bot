from selenium_bot import SeleniumBot
import json
import random
from crontab import CronTab
import os


class BotManager():

    def __init__(self):

        try:
            with open('conf/conf.json') as file:
                self.conf = json.load(file)
        except Exception as exc:
            print('read conf error : {}'.format(exc))

        self.thread_numbers = self.calculate_threads_number()
        # print(self.thread_numbers)
        self.create_schedule()

    def calculate_threads_number(self):
        return 1 + self.conf['client_hosts'] // (86400 // self.conf['time_on_session']['to'])

    def create_schedule(self):
        day_time_start = []
        night_time_start = []

        day_time_start.append(random.randrange(12, 23))

        for i in range(int(self.conf['client_hosts'] * 0.8)-1):
            day_time_start.append(random.randrange(12, 23))

        for i in range(int(self.conf['client_hosts'] * 0.2)):
            night_time_start.append(random.randrange(0, 11))

        self.sheduled_time_to_start = {
            'day_time': day_time_start, 'night_time': night_time_start}

        # print(self.sheduled_time_to_start)

        self.write_schedule_to_cron()

    def write_schedule_to_cron(self):
        cron = CronTab(user=self.conf['username'])

        # del old jobs
        for job in cron:
            if job.comment == 'selenium_bot':
                cron.remove(job)

        cron.write()

        for dt in self.sheduled_time_to_start['day_time']:
            selenium_job = cron.new(command=os.path.join(os.getcwd(), self.conf['bot_name']), comment='selenium_bot')
            selenium_job.hour.also.on(dt)
            selenium_job.minute.also.on(random.randrange(60))
            cron.write()

        for nt in self.sheduled_time_to_start['night_time']:
            selenium_job = cron.new(command=os.path.join(os.getcwd(), self.conf['bot_name']), comment='selenium_bot')
            selenium_job.minute.also.on(random.randrange(60))
            selenium_job.hour.also.on(nt)
            cron.write()

        self.renew_used_proxy_file()

    def renew_used_proxy_file(self):
        with open('conf/used_proxy.json', 'w') as save_proxy_file:
            json.dump({}, save_proxy_file)


def main():

    BM = BotManager()

if __name__ == '__main__':
    main()
