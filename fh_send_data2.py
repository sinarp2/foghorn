import logging
import os
import signal
import sys
import threading
import time
import requests

from foghorn_sdk.health_status import HealthStatus
from foghorn_sdk.fhapplication import FHApplication
from foghorn_sdk.health_report import HealthReport
from foghorn_sdk.fhclient import FHClient
from foghorn_sdk.logger import Logger
from foghorn_sdk.topic_data_handler import TopicDataHandler

'''
pip install requests
'''

headers = {
    'Content-type': 'application/x-www-form-urlencoded'
}

url = 'http://localhost:9000/post-to-me'

topic_names = ['/raw/mqtt/inlet_pressure',
          '/analytics/cavitation_data']


def post_data(data):
    print data
    try:
        res = requests.post(url=url, headers=headers,
                            data=data, timeout=15 * 60)
        # print res.text
    except Exception as e:
        print e


class TopicSubscriber(FHApplication, TopicDataHandler, HealthReport, threading.Thread):

    __client_id = "com_acme_best_app_1"
    __app_id = '100.200-100-FF'
    __app_name = 'com_acme_best_app_1'
    __app_author = 'acme'
    __app_version = '1.0'
    __db_user = ''
    __db_passwd = ''
    __db_name = 'TestDb'

    def __init__(self):

        self.message_count_received = 0
        self.topic = None
        threading.Thread.__init__(self)

        # create client
        self.client = FHClient(self)

        self.create_topic()

        self.client.subscribe_system_events(self)

        # get list of topics.
        # self.topics = self.client.get_topics()
        self.topics = []
        tmp = self.client.get_topics()
        for topic in tmp:
            for topic_name in topic_names:
                if topic.get_name() == topic_name:
                    self.topics.append(topic)
                    break

        self.log_topics()

        # subscribe to topics
        self.client.add_topic_subscriber(self.topics, self)

        self.daemon = True
        self.start()

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
            post_data( { name : str(topic_data.get_data())} )
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " data = " +
                                               str(topic_data.get_data()) + " recevied = " + str(self.message_count_received))
        else:
            post_data( { name : str(topic_data.get_raw_data())} )
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " data = " +
                                               str(topic_data.get_raw_data()) + " recevied = " + str(self.message_count_received))

        self.message_count_received += 1

    def run(self):

        index = 0
        while True:
            try:
                self.client.publish_data(self.topic, "hello world " + str(index))
                index = index + 1
                time.sleep(10)
            except Exception as e:
                self.client.get_logger().log_error("sample_app.run error: ", e)
                break

    def create_topic(self):
        """
        Create a topic and publish some data.
        :return:
        """
        try:
            topic_id = "Foo-Python-100"
            self.topic = self.client.get_topic(topic_id)
            if self.topic is None:
                topic_schema = "{\"type\":\"number\"}"
                self.topic = self.client.create_topic(
                    topic_schema, SchemaType.JSON, topic_id)
        except Exception as e:
            self.client.get_logger().log_error("create_topic failed ", e)

    def log_topics(self):
        self.client.get_logger().log_debug("topic count = " + str(len(self.topics)))
        for index in range(len(self.topics)):
            topic = self.topics[index]
            self.client.get_logger().log_debug(
                "topic name = " + topic.get_name() + " id = " + str(topic.get_id()))


def exit_app(sig, frame):
    print "Exiting..."
    sys.exit(0)


def main():
    Logger.path = os.getcwd() + "/sdk_log"
    Logger.log_level = logging.DEBUG
    signal.signal(signal.SIGINT, exit_app)

    subs = TopicSubscriber()

    try:
        while True:
            time.sleep(10)
            print '.'

    except KeyboardInterrupt:
        print '%s' % sys.exc_type


if __name__ == '__main__':
    main()
