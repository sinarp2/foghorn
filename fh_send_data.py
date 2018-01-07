#!/usr/bin/python
import time
import csv
import requests

'''
pip install requests
'''


class Datafile:
    # __POST_ENDPOINT = 'http://charger.tetrapacific.com/api/api-collector.php'
    __POST_URL = 'http://localhost:8080/post-to-me'

    def __init__(self, filename):
        self.__file = open(filename, 'r')
        self.__reader = csv.reader(self.__file, delimiter=',', quotechar='|')
        self.__reader.next()

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
        #print row
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
        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }
        try:
            res = requests.post(url=self.__POST_URL,
                                headers=headers, data=data, timeout=15 * 60)
            #print res.text
        except Exception as e:
            print e


def main():
    datafiles = []
    datafiles.append(Datafile('upload-foghorn-ac-10022001.csv'))
    datafiles.append(Datafile('upload-foghorn-dc-10011103.csv'))
    datafiles.append(Datafile('upload-foghorn-dc-10021101.csv'))

    while True:
        for datafile in datafiles:
            datafile.post_data()
        time.sleep(5)


if __name__ == '__main__':
    main()
