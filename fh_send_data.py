#!/usr/bin/env python

import os
import time
import csv
import requests
import logging
import threading

from foghorn_sdk.health_status import HealthStatus
from foghorn_sdk.fhapplication import FHApplication
from foghorn_sdk.health_report import HealthReport
from foghorn_sdk.new_configuration_event import NewConfigurationEvent
from foghorn_sdk.system_event import SystemEvent
from foghorn_sdk.fhclient import FHClient
from foghorn_sdk.logger import Logger
from foghorn_sdk.new_topic_event import NewTopicEvent
from foghorn_sdk.schema_type import SchemaType
from foghorn_sdk.topic_data_handler import TopicDataHandler
from foghorn_sdk.system_event_handler import SystemEventHandler

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

class TopicSubscriber(FHApplication, SystemEventHandler, TopicDataHandler, HealthReport):

    __client_id = "com_acme_best_app_1"
    __app_id = '100.200-100-FF'
    __app_name = 'com_acme_best_app_1'
    __app_author = 'acme'
    __app_version = '1.0'
    __db_user = ''
    __db_passwd = ''
    __db_name = 'TestDb'

    def __init__(self, post_url, topic_names):
        self.__post_url = post_url
        self.message_count_received = 0
        self.topic = None

        # create client
        self.client = FHClient(self)

        self.create_topic()

        self.client.subscribe_system_events(self)

        # get list of topics.
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

    def on_system_event(self, event):
        """
        on_system_event is the the implementation of the SystemEventHandler abstract class.
        SDK calls this method when there is a new system event.
        :param event: is the system event.
        :return: nothing.
        """
        if isinstance(event, NewTopicEvent):
            name = event.get_topic().get_name()
            id_ = event.get_topic().get_id()
            self.client.get_logger().log_debug(
                "sample_app.on_system_event NewTopicEvent: " + name + "  " + id_)

            # Subscribe to receive data from the new sensor.
            sensors = [event.get_topic()]
            self.client.add_topic_subscriber(sensors, self)
        elif isinstance(event, NewConfigurationEvent):
            self.client.get_logger().log_debug(
                "sample_app.on_system_event NewConfigurationEvent")
        elif isinstance(event, SystemEvent):
            self.client.get_logger().log_debug("sample_app.on_system_event SystemEvent type = " + str(event.get_type()) +
                                               " id = " + str(event.get_id()))

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
            post_data(self.__post_url, str(topic_data.get_data()))
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " plain data = " +
                                               str(topic_data.get_data()) + " recevied = " + str(self.message_count_received))
        else:
            post_data(self.__post_url, str(topic_data.get_raw_data()))
            self.client.get_logger().log_debug("sample_app.on_topic_data name = " + name + " data = " +
                                               str(topic_data.get_raw_data()) + " recevied = " + str(self.message_count_received))

        self.message_count_received += 1

    def query_database(self):
        """
        query_database method is an example code on to connect to the local TSDB and
        query data. In this example, it is assumed that a database with "FoghornSampleApp" name exist.
        :return:
        """
        try:
            # get the database
            tsdb = self.client.get_database(self.__db_user, self.__db_passwd)

            # list the available databases.
            dblist = tsdb.get_list_database()

            if dblist is not None:
                self.client.get_logger().log_debug("db count = " + str(len(dblist)))

                # list series available in each database
                for db in dblist:
                    for key, dbname in db.iteritems():
                        self.client.get_logger().log_debug("database name = " + str(dbname))
                        if dbname == '_internal':
                            continue

                        measurements = tsdb.get_list_measurements(dbname)
                        for measure in measurements:
                            self.client.get_logger().log_debug("  measurement: " + str(measure))
                            fields = tsdb.get_list_fields(measure, dbname)
                            for field in fields:
                                self.client.get_logger().log_debug("  field: " + str(field))

                        series = tsdb.get_list_series(dbname)
                        for serie in series:
                            for key2, sname in serie.iteritems():
                                if sname == self.__db_name:
                                    result = tsdb.query(
                                        "SELECT * FROM " + sname)
                                    values = result.raw['series'][0]['values']
                                    for item in values:
                                        self.client.get_logger().log_debug("     " + str(item))
        except Exception as e:
            self.client.get_logger().log_debug("sample_app.query_database error: ", e)

    def show_database_schema(self):
        try:
            # get the database object
            tsdb = self.client.get_database(self.__db_user, self.__db_passwd)

            # list the available databases.
            dblist = tsdb.get_list_database()

            if dblist is not None:
                self.client.get_logger().log_debug("db count = " + str(len(dblist)))

                # list measurements and fields available in each database
                for db in dblist:
                    for key, dbname in db.iteritems():

                        self.client.get_logger().log_debug("database name = " + str(dbname))

                        tsdb.switch_database(str(dbname))

                        # measurements
                        measurements = tsdb.get_list_measurements(dbname)
                        for measure in measurements:
                            self.client.get_logger().log_debug("    measurement: " + str(measure))

                            # fields for each measurement
                            fields = tsdb.get_list_fields(measure)
                            for field in fields:
                                self.client.get_logger().log_debug("        field: " + str(field))
        except Exception as e:
            self.client.get_logger().log_error("create_database failed", e)

    def create_database(self):
        try:
            # get the database object
            tsdb = self.client.get_database(self.__db_user, self.__db_passwd)
            tsdb.create_database_with_rentention_policy(self.__db_name)
        except Exception as e:
            self.client.get_logger().log_error("create_database failed ", e)

    def delete_database(self):
        try:
            # get the database object
            tsdb = self.client.get_database(self.__db_user, self.__db_passwd)
            tsdb.drop_database(self.__db_name)
        except Exception as e:
            self.client.get_logger().log_error("delete_database failed ", e)

    def write_database(self):
        tsdb = self.client.get_database(self.__db_user, self.__db_passwd)
        json_body = [
            {
                "measurement": "MyTable",
                "tags": {
                    "Vel_Version": "2.0"
                },
                "time": "2009-11-10T23:00:00Z",
                "fields": {
                    "pressure": 0.64,
                    "temperature": 3.0,
                }
            }
        ]
        tsdb.write_points(json_body, database=self.__db_name)

    def test_database(self):
        self.create_database()
        self.write_database()
        self.query_database()
        self.show_database_schema()

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
              '/raw/mqtt/temperature/decoded']

    subs = TopicSubscriber(post_url, topics)

    while True:
        for datafile in datafiles:
            datafile.post_data()
        time.sleep(5)


if __name__ == '__main__':
    main()
