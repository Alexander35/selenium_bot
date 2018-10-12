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
        print(self.thread_numbers)
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

        print(self.sheduled_time_to_start)

    def write_schedule_to_celery(self):
        pass


def main():

    BM = BotManager()


if __name__ == '__main__':
    main()
