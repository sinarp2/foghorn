#!/bin/python

import csv

class Datafile:
    __post_url = 'http://charger.tetrapacific.com/api/api-collector.php'

    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.reader = csv.reader(self.file, delimiter=',', quotechar='|')

    def __del__(self):
        if self.file is None:
            self.file.close()

    def __getline():
        row = self.reader.next()
        return row
    def post_data():
        row = self.__getline()
        print row


def main():
    datafiles = []
    datafiles.append('upload-foghorn-ac-10022001.csv')
    datafiles.append('upload-foghorn-dc-10011103.csv')
    datafiles.append('upload-foghorn-dc-10021101.csv')
    while:
        for datafile in datafiles:
            datafile.post_data()
        sleep(5)

if __name__ == '__main__':
    main()

