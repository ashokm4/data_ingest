#!/usr/bin/env python3
import time
import os
import pathlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mysql.connector
import json
import logging
import logging.handlers

class Watcher:

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        l.logger.info( "\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        l.logger.info("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.user = ''
        self.password = ''
        self.db = 'metadata'
        self.connect_args = {}
        self.mysql_credential_file = '/home/ashok.mahajan/work/etl.conf.json'
        self.setup_mysql_connection('metadata')

    def on_any_event(self, event):
        l.logger.info(type(event))
        l.logger.info(event) # Your code here
        path = pathlib.PurePath(event.src_path)
        if event.event_type == "created" and event.is_directory == True:
            l.logger.info(os.path.basename(event.src_path))
            vehicle=(os.path.basename(event.src_path))
            _sql = "insert into vehicle (vehicle) values ('{0}');".format(vehicle)
            self.updateMetadata(_sql)
        if event.event_type == "closed" and event.is_directory == False:
            l.logger.info("New file added")
            (vehicle, file_name) = (path.parent.name, path.name)
            l.logger.info(os.path.basename(event.src_path))
            _sql = "insert into files_inprocess (file_name, vehicle, processed) values ('{0}', '{1}', {2});".format(file_name, vehicle, False)
            self.updateMetadata(_sql)

    def updateMetadata(self, sql):
        try:
            l.logger.info(sql)
            dbCnx = mysql.connector.connect(**self.connect_args)
            dbCur = dbCnx.cursor()
            dbCur.execute(sql)
            dbCnx.commit()
        except Exception as e:
            l.logger.error("Error in updateMetadata module: {0}\n".format(str(e)))
            l.logger.error("Sql in error: {0}\n".format(sql))
        finally:
            # closing database connection.
            if dbCnx.is_connected():
                dbCur.close()
                dbCnx.close()
                l.logger.info("connection is closed")

    def setup_mysql_connection(self, db):
        with open(self.mysql_credential_file) as f:
            mysql_cred = json.load(f)

        self.user = mysql_cred['User']
        self.password = mysql_cred['Password']
        self.connect_args = {
            "host": '127.0.0.1',
            "port": 3306,
            "user": self.user,
            "password": self.password,
            "database": db
        }

class Logging:
    LOG_FILE = '/home/ashok.mahajan/work/log/fileWatcher.log'
    LOG_FILE_SIZE = '200K'
    LOG_FILE_BACKUP_COUNT = 5
    LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.logger=None
        self.__log_it()

    def __log_it(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter_file = logging.Formatter('time: "%(asctime)s", level: "%(levelname)s", %(message)s',self.LOG_TIMESTAMP_FORMAT)

        fh = logging.handlers.RotatingFileHandler(self.LOG_FILE, maxBytes=1024*1024, backupCount=self.LOG_FILE_BACKUP_COUNT)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter_file)
        self.logger.addHandler(fh)

        if __debug__:
            formatter_console = logging.Formatter('%(message)s')
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter_console)
            self.logger.addHandler(ch)

if __name__=="__main__":
    l = Logging()
    w = Watcher("/home/ashok.mahajan/work/landing_zone", MyHandler())
    w.run()

