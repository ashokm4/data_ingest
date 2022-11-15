#!/usr/bin/env python3
import sys
import subprocess
import random
import multiprocessing as mp
import io
import time
from datetime import datetime
import os
import socket
import argparse
import mysql.connector
import json
from collections import defaultdict
import logging
import logging.handlers
import concurrent.futures


class Uploader:
    MYSQL_CREDENTIAL_FILE = '/home/ashok.mahajan/work/etl.conf.json'
    LOGDIR = '/var/log/schema-migrator/'
    LANDING_ZONE_DIR = '/home/ashok.mahajan/work/landing_zone'
    CLOUD_PATH_DIR = '/home/ashok.mahajan/work/cloud_storage'
    PROCESSED_FILES_DIR = '/home/ashok.mahajan/work/processed_files'

    def __init__(self):
        self.concurrency = 1
        self.retries= 5
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.fileList = []
        self.dbcount = None
        self.connect_args = ''
        self.user = ''
        self.password = ''
        self.setup_mysql_connection('metadata')

    def setup_mysql_connection(self, db):
        with open(Uploader.MYSQL_CREDENTIAL_FILE) as f:
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
    def run(self):
        l.logger.info("\nUploader Running")
        try:
            while True:
                self.buildFileList()
                self.uploadToS3(self.fileList)
                time.sleep(10)
        except Exception as e:
            l.logger.error("Error in run module: {0}\n".format(str(e)))

    def buildFileList(self):
        try:
            dbCnx = mysql.connector.connect(**self.connect_args)
            dbCur = dbCnx.cursor()
            dbQuery = "select file_id, file_name ,vehicle, date_created from files_inprocess where processed = False;"
            dbCur.execute(dbQuery)
            if (dbCur.with_rows):
                self.fileList = dbCur.fetchall()
                l.logger.info(self.fileList)
            rows = dbCur.rowcount
            dbCur.close()
            dbCnx.close()
            l.logger.info("Number of files: {}".format(len(self.fileList)))
            l.logger.info(self.fileList)
            self.fileCount = len(self.fileList)
        except Exception as e:
            l.logger.error("Error in buildFileList module: {0}\n".format(str(e)))

    def uploadToS3(self, fileSubList):
        try:
            for fileVehicle in fileSubList:
                _file_id=fileVehicle[0]
                _file=fileVehicle[1]
                _vehicle=fileVehicle[2]
                _dateArrived=fileVehicle[3]
                _srcFilePath=os.path.join(Uploader.LANDING_ZONE_DIR, _vehicle, _file)
                _destFilePath=os.path.join(Uploader.CLOUD_PATH_DIR, _file)
                l.logger.info("file id {0}, Source file path '{1}'".format(_file_id, _srcFilePath))
                if os.path.isfile(_srcFilePath):
                    _retries=0
                    l.logger.info("upload {0}".format(_srcFilePath))
                    while _retries < self.retries:
                        l.logger.info("Copy {0}".format(_srcFilePath))
                        _cmd='cp ' + _srcFilePath + ' ' + Uploader.CLOUD_PATH_DIR
                        _retries=_retries + 1
                        l.logger.info(_cmd)
                        (exit_status, stdout, stderr) = g_OSCmd(_cmd)
                        if exit_status == 0:
                           _json_string =  "{{\"filePath\": \"{0}\", \"vehicle\": \"{1}\", \"date_created\": \"{2}\", \"date_uploaded\": \"{3}\"}}".format(_destFilePath, _vehicle, _dateArrived, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                           l.logger.info(_json_string)
                           _sql="insert into metadata values ({0}, '{1}')".format(_file_id, _json_string)
                           self.updateMetadata(_sql)
                           _sql="update files_inprocess set processed = True where file_id = {}".format(_file_id)
                           self.updateMetadata(_sql)
                           break
                        else:
                           l.logger.info("Retry: {0}: Upload to cloud storage failed".format(_retries))
                           l.logger.info("exit status: {0}".format(exit_status))
                           _sql="insert into upload_failure_log (file_id, exit_status, stdout, stderr) values ({0}, {1}, '{2}', '{3}' )".format(_file_id, exit_status, stdout, stderr)
                           self.updateMetadata(_sql)
                    if _retries == self.retries:
                        self.filesFailed(_file_id)
                    _cmd='mv ' + _srcFilePath + ' ' + Uploader.PROCESSED_FILES_DIR
                    (exit_status, stdout, stderr) = g_OSCmd(_cmd)
                    if exit_status != 0:
                        l.logger.info("Unable to move file '{0}': processed file dir".format(_srcFilePath))
                        l.logger.info("exit status: {0}".format(exit_status))
                else:
                    l.logger.error("error for file {0}".format(_srcFilePath))
                    self.filesFailed(_file_id)
        except Exception as e:
            l.logger.error("Error in uploadToS3  module: {0}\n".format(str(e)))

    def filesFailed(self, file_id):
        try:
            dbCnx = mysql.connector.connect(**self.connect_args)
            dbCnx.autocommit = False
            dbCur = dbCnx.cursor()
            _sql_insert="insert into files_failed select * from files_inprocess where file_id = {0}".format(file_id)
            dbCur.execute(_sql_insert)
            _sql_delete="delete from files_inprocess where file_id = {0}".format(file_id)
            dbCur.execute(_sql_delete)
            dbCnx.commit()

        except mysql.connector.Error as error:
            l.logger.error("Failed to update record to database rollback: {}".format(error))
            # reverting changes because of exception
            dbCnx.rollback()
        finally:
            # closing database connection.
            if dbCnx.is_connected():
                dbCur.close()
                dbCnx.close()
                l.logger.info("connection is closed")

    def updateMetadata(self, sql):
        try:
            l.logger.info(sql)
            dbCnx = mysql.connector.connect(**self.connect_args)
            dbCur = dbCnx.cursor()
            dbCur.execute(sql)
            dbCnx.commit()
            dbCur.close()
            dbCnx.close()
        except Exception as e:
            l.logger.error("Error in updateMetadata module: {0}\n".format(str(e)))
            l.logger.error("Sql in error: {0}\n".format(sql))

def g_OSCmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    return (proc.returncode, output.strip().decode('UTF-8').replace("'", ""), error.decode('UTF-8').replace("'", ""))

class Logging:
    LOG_FILE = '/home/ashok.mahajan/work/log/fileUploader.log'
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

l = Logging()
b=Uploader()
b.run()
