"""
Redis Pub for Tbot on Tradingboat
"""
import os
import sys
import json
from distutils.util import strtobool
from redis import Redis
from loguru import logger
from components.actions.base.action import Action

# Change the log levelfor loguru
logger.remove()
logger.add(sys.stderr, level=os.environ.get("TBOT_LOGLEVEL", "INFO"))


class RedisPubAction(Action):
    """Class for handling Redis connections for message delivery.

    This class sets up a Redis connection either as a stream or as a
    pub/sub channel, based on the value of the environment variable
    `TBOT_USES_REDIS_STREAM`.
    """
    REDIS_CHANNEL = "REDIS_CH_"
    REDIS_STREAM_KEY = "REDIS_SKEY_"
    REDIS_STREAM_TB_KEY = "tradingboat"

    def __init__(self):
        super().__init__()
        self.redis_connection = None
        self.client_id = os.getenv("TBOT_IBKR_CLIENTID", "1")
        self.is_redis_stream = strtobool(
            os.getenv("TBOT_USES_REDIS_STREAM", "1"))
        if self.is_redis_stream:
            # Use pre-defined stream key between TVWB and TBOT
            self.redis_stream_key = self.REDIS_STREAM_KEY + self.client_id
            self.redis_stream_tb_key = self.REDIS_STREAM_TB_KEY
        else:
            # Use pre-defined channelbetween TVWB and TBOT
            self.redis_channel = self.REDIS_CHANNEL + self.client_id
        self.connect_redis_host()

    def validate_broker_data(self):
        """Validate Message"""
        try:
            data = self.validate_data()
            return data
        except ValueError:
            return None

    def connect_redis_host(self):
        """Connect to Redis via either unix or tcp """
        password = os.getenv("TBOT_REDIS_PASSWORD", "")
        host = os.getenv("TBOT_REDIS_HOST", "127.0.0.1")
        unix = {
            'unix_socket_path': os.getenv("TBOT_REDIS_UNIXDOMAIN_SOCK", ""),
            'password': password,
            'decode_responses': True,
        }
        tcp = {
            'host': host,
            'port': int(os.getenv("TBOT_REDIS_PORT", "6379")),
            'password': password,
            'decode_responses': True,
            }
        try:
            if host:
                self.redis_connection = Redis(**tcp)
            else:
                self.redis_connection = Redis(**unix)
            if self.is_redis_stream:
                logger.success(f"Connected to Redis| {self.redis_stream_key}:"
                               "{self.redis_stream_tb_key}")
            else:
                logger.success(f"Connected to Redis| {self.redis_channel}")
        except ConnectionRefusedError as err:
            logger.error(err)

    def run_redis_stream(self):
        """Add data to the stream"""
        data_dict = self.validate_broker_data()
        if data_dict:
            # Create a bespoken dictionary for Redis Stream
            stream_dict = {self.redis_stream_tb_key: json.dumps(data_dict)}
            self.redis_connection.xadd(self.redis_stream_key, stream_dict)
            logger.success(
                f"->pushed| {self.redis_stream_key}:{self.redis_stream_tb_key}"
            )

    def run_redis_pubsub(self):
        """Publish message"""
        data_dict = self.validate_broker_data()
        # Publishing data
        if data_dict:
            json_string = json.dumps(data_dict)
            self.redis_connection.publish(self.redis_channel, json_string)
            logger.success(
                f"->pushed| {self.redis_channel}"
            )

    def run(self, *args, **kwargs):
        """
        Custom run method. Add your custom logic here.
        """
        super().run(*args, **kwargs)  # this is required
        if self.is_redis_stream:
            self.run_redis_stream()
        else:
            self.run_redis_pubsub()
