# /usr/bin/python
# -*- coding: utf-8 -*-
"""
MongoDB logger module
"""
import datetime
import logging
import logging.config
import os
import json
from pymongo import MongoClient


class MongoLogger:
    """
    MongoDB logger class.\n
    """
    LEVELS = {'crit': 50, 'err': 40, 'warn': 30, 'info': 20, 'debug': 10}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MongoLogger, cls).__new__(cls)
        return cls.instance

    def __init__(self, config_file="monolog.json"):
        _current_dir = _path = os.getcwd()
        _local_config_file = os.path.join(_current_dir, "config", "monolog.local.json")
        if os.path.exists(_local_config_file):
            self.config = json.load(open(_local_config_file))
        else:
            _config_file = os.path.join(_current_dir, "config", config_file)
        self._mongo_cli = MongoClient(self.config["serv"],
                                      self.config["port"],
                                      username=self.config["username"],
                                      password=self.config["password"],
                                      authSource=self.config["authSource"],
                                      authMechanism=self.config["authMechanism"])
        self._db = self._mongo_cli[self.config["dataBase"]]
        self._node = self.config["node"]
        self._current_level = self.config["currentLevel"]
        self._collection = self.config["collectionName"]
        self._std_logger_duplicate = self.config["stdLoggerDuplicate"]
        try:
            logging.config.fileConfig(os.path.join(_current_dir, "config", "log_config"))
            self._std_logger = logging.getLogger('MainLog')
        except Exception as ex_error:
            print(f"MongoLogger error. ex_error: {ex_error}.")
            self._std_logger = None
            self._std_logger_duplicate = False

    def _emit(self, level: str, ssid: str, msg: str, data: dict):
        """
        Emit log message
        :param level: message level
        :param ssid: session id
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        if self._std_logger_duplicate:
            self._std_logger.log(self.LEVELS[level], "[%s][%s] %s %s.", level, ssid, msg, data)
        try:
            collection = self._db[datetime.datetime.now().strftime(self._collection)]
            var = {
                "created": datetime.datetime.now(),
                "node": self._node,
                "ssid": ssid,
                "raddr": "",
                "level": level,
                "msg": msg,
                "dump": data
            }
            collection.insert_one(var)
        except Exception as ex_error:
            if self._std_logger:
                self._std_logger.critical("MongoLogger Critical error. %s dump: [%s][%s] %s %s.",
                                          ex_error, level, ssid, msg, data)
            else:
                print("MongoLogger Critical error. %s dump: [%s][%s] %s %s.",
                      ex_error, level, ssid, msg, data)

    def critical(self, ssid: str, msg: str, data: dict) -> None:
        """
        Critical message.
        :param ssid: session ID
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        self._emit('crit', ssid, msg, data)

    def error(self, ssid: str, msg: str, data: dict) -> None:
        """
        Error message.
        :param ssid: session ID
        :param msg: error message
        :param data: dump dict
        :return: None
        """
        self._emit('err', ssid, msg, data)

    def warning(self, ssid: str, msg: str, data: dict) -> None:
        """
        Warning message.
        :param ssid: session ID
        :param msg: warning message
        :param data: dump dict
        :return: None
        """
        self._emit('warn', ssid, msg, data)

    def info(self, ssid: str, msg: str, data: dict) -> None:
        """
        Info message.
        :param ssid: session ID
        :param msg: info message
        :param data: dump dict
        :return: None
        """
        self._emit('info', ssid, msg, data)

    def debug(self, ssid: str, msg: str, data: dict) -> None:
        """
        Debug message.
        :param ssid: session ID
        :param msg: debug message
        :param data: dump dict
        :return: None
        """
        self._emit('debug', ssid, msg, data)
