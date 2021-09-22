# /usr/bin/python
# -*- coding: utf-8 -*-
"""
MongoDB logger module
"""
import datetime
import logging
import os
import json
import inspect
import random
from typing import Optional

from pymongo import MongoClient


class MongoLogger:
    """
    MongoDB logger class.\n
    """
    LEVELS = {'crit': 50, 'err': 40, 'warn': 30, 'info': 20, 'debug': 10}

    def __init__(self, collection_name='default_logger', pid='', config_file="monolog.json"):
        self._pid = pid
        if self._pid == '':
            self._generate_pid()

        self.config = self._get_merged_config(config_file)

        self._current_level = self.config["currentLevel"]
        self._collection = collection_name
        self._std_logger_duplicate = self.config.get("stdLoggerDuplicate", True)
        self._mongo_logger_duplicate = self.config.get("mongoLoggerDuplicate", True)

        if self._mongo_logger_duplicate:
            self._mongo_cli = MongoClient(self.config["connection"]["serv"],
                                          self.config["connection"]["port"],
                                          username=self.config["connection"]["username"],
                                          password=self.config["connection"]["password"],
                                          authSource=self.config["connection"]["authSource"],
                                          authMechanism=self.config["connection"]["authMechanism"])

            self._db = self._mongo_cli[self.config["connection"]["dataBase"]]
            self._node = self.config["node"]
        else:
            self._mongo_cli = None
            self._db = None
            self._node = None

        try:
            self._std_logger = self._build_std_logger()
        except Exception as ex_error:
            print(f"MongoLogger error. ex_error: {ex_error}.")
            self._std_logger = None
            self._std_logger_duplicate = False

    def _get_merged_config(self, config_file: str) -> dict:
        """
            Find and merge configs.\n
            config.local.json takes precedence over config.json
        """
        _local_config_file_name = f'{".".join(config_file.split(".")[:-1])}.local.{config_file.split(".")[-1]}'

        _config = {}
        if _config_path := self._find_config(config_file):
            _config = json.load(open(_config_path))
        if _local_config_path := self._find_config(_local_config_file_name):
            _config = self._merge_configs(_config, json.load(open(_local_config_path)))
        return _config

    def _merge_configs(self, first_dict: dict, second_dict: dict) -> dict:
        """
            Merge second_dict on first_dict.\n
        """
        out = {}
        for key in first_dict.keys():
            out[key] = first_dict[key]
            if key in second_dict:
                if isinstance(second_dict[key], dict):
                    out[key] = self._merge_configs(first_dict[key], second_dict[key])
                else:
                    out[key] = second_dict[key]
        for key in second_dict.keys():
            if key not in first_dict:
                out[key] = second_dict[key]
        return out

    @staticmethod
    def _find_config(config_file_name: str) -> Optional[str]:
        """
        Find config file.\n Will check current_dir, current_dir/config, ../current_dir/config.\n
        config.local.json takes precedence over config.json
        """

        if os.path.exists(config_file_name):
            return config_file_name

        _path_config = os.path.join("config", config_file_name)
        if os.path.exists(_path_config):
            return _path_config

        _upper_current_dir = os.path.split(os.getcwd())[0]
        _path_config = os.path.join(_upper_current_dir, "config", config_file_name)
        if os.path.exists(_path_config):
            return _path_config
        return None

    def _generate_pid(self):
        """
            Generate process id.\n
        """
        self._pid = f"{random.randrange(1000, 9999)}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    def set_pid(self, pid):
        """
            Set session(process) id.\n
        """
        self._pid = pid

    def get_pid(self):
        """
            Get current session(process) id.\n
        """
        return self._pid

    def _build_std_logger(self):
        """
            Make std logger.\n
        """
        logger = logging.getLogger(self._collection)
        _log_format = "[%(levelname)-8s][%(asctime)s][%(module)-10s]%(message)s"
        logger.setLevel(self.LEVELS[self._current_level])
        logger.addHandler(self._get_file_handler(_log_format))
        logger.addHandler(self._get_stream_handler(_log_format))
        return logger

    def _get_file_handler(self, _log_format):
        """
            Make file handler for std logger.\n
        """
        file_handler = logging.FileHandler(f"{self._collection}.log")
        file_handler.setFormatter(logging.Formatter(_log_format))
        return file_handler

    @staticmethod
    def _get_stream_handler(_log_format):
        """
            Make console handler for std logger.\n
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(_log_format))
        return stream_handler

    def _emit(self, level: str, msg: str, data: dict):
        """
        Emit log message
        :param level: message level
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        current_frame = inspect.currentframe()
        emit_func = current_frame.f_back.f_back.f_code.co_name

        if self._std_logger_duplicate:
            self._emit_std_logger(emit_func, level, msg, data)
        if self._mongo_logger_duplicate:
            self._emit_mongo(emit_func, level, msg, data)

    def _emit_std_logger(self, emit_func: str, level: str, msg: str, data: dict):
        """
            Emit msg to std logger.\n
        :param emit_func: emitter function
        :param level: message level
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        try:
            self._std_logger.log(self.LEVELS[level], "[%s][%s] %s %s.", emit_func, self._pid, msg, data)
        except UnicodeEncodeError:
            dump_data = json.dumps(data)
            self._std_logger.log(self.LEVELS[level], "[%s][%s][%s] %s %s.", level, emit_func, self._pid, msg,
                                 dump_data)

    def _emit_mongo(self, emit_func: str, level: str, msg: str, data: dict):
        """
            Emit msg to mongo.\n
        :param emit_func: emitter function
        :param level: message level
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        try:
            collection = self._db[datetime.datetime.now().strftime(self._collection)]
            data["function"] = emit_func
            var = {
                "created": datetime.datetime.now(),
                "node": self._node,
                "ssid": self._pid,
                "raddr": "",
                "level": level,
                "msg": msg,
                "dump": data
            }
            collection.insert_one(var)
        except Exception as ex_error:
            if self._std_logger:
                self._std_logger.critical("MongoLogger Critical error. %s dump: [%s][%s] %s %s.",
                                          ex_error, level, self._pid, msg, data)
            else:
                print("MongoLogger Critical error. %s dump: [%s][%s] %s %s.",
                      ex_error, level, self._pid, msg, data)

    def critical(self, msg: str, data=None) -> None:
        """
        Critical message.
        :param msg: critical message
        :param data: dump dict
        :return: None
        """
        if data is None:
            data = {}
        traceback = list(map(lambda x: {"function": x.function, "lineno": x.lineno}, inspect.stack()))
        data["traceback"] = traceback
        self._emit('crit', msg, data)

    def error(self, msg: str, data=None) -> None:
        """
        Error message.
        :param msg: error message
        :param data: dump dict
        :return: None
        """
        if data is None:
            data = {}
        self._emit('err', msg, data)

    def warning(self, msg: str, data=None) -> None:
        """
        Warning message.
        :param msg: warning message
        :param data: dump dict
        :return: None
        """
        if data is None:
            data = {}
        self._emit('warn', msg, data)

    def info(self, msg: str, data=None) -> None:
        """
        Info message.
        :param msg: info message
        :param data: dump dict
        :return: None
        """
        if data is None:
            data = {}
        self._emit('info', msg, data)

    def debug(self, msg: str, data=None) -> None:
        """
        Debug message.
        :param msg: debug message
        :param data: dump dict
        :return: None
        """
        if data is None:
            data = {}
        self._emit('debug', msg, data)
