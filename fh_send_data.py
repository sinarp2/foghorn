#!/usr/bin/python
import time
import csv

class Datafile:
    __post_url = 'http://charger.tetrapacific.com/api/api-collector.php'

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
            print 'eof ------>'
            self.__file.seek(0)
            self.__reader.next()
            row = self.__reader.next()
        return row

    def post_data(self):
        row = self.__getline()
        print row


def main():
    datafiles = []
    datafiles.append(Datafile('upload-foghorn-ac-10022001.csv'))
    datafiles.append(Datafile('upload-foghorn-dc-10011103.csv'))
    datafiles.append(Datafile('upload-foghorn-dc-10021101.csv'))
    print datafiles
    while True:
        for datafile in datafiles:
            datafile.post_data()
        time.sleep(1)

if __name__ == '__main__':
    main()

