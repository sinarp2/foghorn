#!/usr/bin/env python

import os
import time
import csv
import requests
import logging
import threading

from foghorn_sdk.fhclient import FHClient
from foghorn_sdk.logger import Logger
from foghorn_sdk.topic_data_handler import TopicDataHandler

'''
pip install requests
'''

headers = {
    'Content-type': 'application/x-www-form-urlencoded'
}

def post_data(url, data):
    try:
        res = requests.post(url=url, headers=headers, data=data, timeout=15 * 60)
        Logger.get_logger().log_debug(res.text)
    except Exception as e:
        Logger.get_logger().log_debug('send data error:', e)

class TopicSubscriber(TopicDataHandler):

    __app_id = '100.200-100-FF'
    __app_name = 'com_acme_best_app_1'
    __app_author = 'acme'
    __app_version = '1.0'

    def __init__(self, post_url, topic_names):

        self.__post_url = post_url
        self.message_count_received = 0

        # create client
        self.client = FHClient(self)

        self.client.subscribe_system_events(self)

        # get list of topics.
        self.topics = []
        tmp = self.client.get_topics()
        for topic in tmp:
            for topic_name in topic_names:
                if topic.get_name() == topic_name:
                    self.topics.append(topic)
                    break

        # subscribe to topics
        self.client.add_topic_subscriber(self.topics, self)

    def get_id(self):
        return self.__app_id

    def get_name(self):
        return self.__app_name

    def get_author(self):
        return self.__app_author

    def get_version(self):
        return self.__app_version

    def shutdown(self):
        if self.client is not None:
            self.client.close()

    def get_health_data(self):
        return HealthStatus.running

    def on_topic_data(self, topic_data):
        """
        on_topic_data is implementation of the TopicDataHandler abstract class.
        SDK calls this method when there is a message (data) available for one
        of the topics the application has subscribed to.
        :param topic_data: New data available on a specific topic
        :return: nothing
        """
        name = topic_data.get_topic().get_name()
        if topic_data.get_data() is not None:
            post_data(self.__post_url, { name : str(topic_data.get_data())} )
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " data = " +
                                               str(topic_data.get_data()) + " recevied = " + str(self.message_count_received))
        else:
            post_data(self.__post_url, { name : str(topic_data.get_raw_data())} )
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " row data = " +
                                               str(topic_data.get_raw_data()) + " recevied = " + str(self.message_count_received))
        self.message_count_received += 1


class Datafile:

    def __init__(self, filename, post_url):
        self.__post_url = post_url
        self.__file = open(filename, 'r')
        self.__reader = csv.reader(self.__file, delimiter=',', quotechar='|')
        self.__reader.next()
        self.__logger = Logger.get_logger()
        self.__logger.log_debug(
            'Initialized Datafile Object [' + filename + ']')

    def __del__(self):
        if self.__file is None:
            self.__file.close()

    def __getline(self):
        try:
            row = self.__reader.next()
        except Exception as e:
            self.__file.seek(0)
            self.__reader.next()
            row = self.__reader.next()
        return row

    def post_data(self):
        row = self.__getline()
        # print row
        data = {
            'charger_id': row[0],
            'gun_a_status': row[1],
            'gun_b_status': row[2],
            'gun_a_power': row[3],
            'gun_b_power': row[4],
            'gun_a_qty': row[5],
            'gun_b_qty': row[6],
            'gun_a_soc': row[7],
            'gun_b_soc': row[8],
            'alarm_old': row[9],
            'phase_a_volt_under': row[10],
            'phase_b_volt_under': row[11],
            'phase_c_volt_under': row[12],
            'phase_a_volt_over': row[13],
            'phase_b_volt_over': row[14],
            'phase_c_volt_over': row[15],
            'phase_a_curr_over': row[16],
            'phase_b_curr_over': row[17],
            'phase_c_curr_over': row[18]
        }
        post_data(self.__post_url, data)

def main():
    Logger.path = os.getcwd() + "/sdk_log"
    Logger.log_level = logging.DEBUG

    # post_url = 'http://charger.tetrapacific.com/api/api-collector.php'
    post_url = 'http://localhost:9000/post-to-me'

    datafiles = []
    datafiles.append(Datafile('upload-foghorn-ac-10022001.csv', post_url))
    datafiles.append(Datafile('upload-foghorn-dc-10011103.csv', post_url))
    datafiles.append(Datafile('upload-foghorn-dc-10021101.csv', post_url))

    topics = ['/raw/mqtt/inlet_pressure',
              '/analytics/cavitation_data']

    subs = TopicSubscriber(post_url, topics)

    while True:
        for datafile in datafiles:
            datafile.post_data()
        time.sleep(5)


if __name__ == '__main__':
    main()
