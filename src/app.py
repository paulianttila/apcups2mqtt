from dataclasses import asdict
from random import randint
import time
from mqtt_framework import Framework
from mqtt_framework import Config
from mqtt_framework.callbacks import Callbacks
from mqtt_framework.app import TriggerSource

from prometheus_client import Counter

from datetime import datetime

from cacheout import Cache
from apcups import ApcUps
from apcups_data import CommunicationError


class MyConfig(Config):
    def __init__(self):
        super().__init__(self.APP_NAME)

    APP_NAME = "apcups2mqtt"

    # App specific variables

    APC_HOST = None
    APC_PORT = 502
    CACHE_TIME = 300


class MyApp:
    def init(self, callbacks: Callbacks) -> None:
        self.logger = callbacks.get_logger()
        self.config = callbacks.get_config()
        self.metrics_registry = callbacks.get_metrics_registry()
        self.add_url_rule = callbacks.add_url_rule
        self.publish_value_to_mqtt_topic = callbacks.publish_value_to_mqtt_topic
        self.subscribe_to_mqtt_topic = callbacks.subscribe_to_mqtt_topic
        self.succesfull_fecth_metric = Counter(
            "succesfull_fecth", "", registry=self.metrics_registry
        )
        self.fecth_errors_metric = Counter(
            "fecth_errors", "", registry=self.metrics_registry
        )

        self.valueCache = Cache(maxsize=256, ttl=self.config["CACHE_TIME"])
        self.ups = ApcUps(
            self.config["APC_HOST"], self.config["APC_PORT"], logger=self.logger
        )
        self.inventory_data = None

    def get_version(self) -> str:
        return "1.0.2"

    def stop(self) -> None:
        self.logger.debug("Exit")

    def subscribe_to_mqtt_topics(self) -> None:
        pass

    def mqtt_message_received(self, topic: str, message: str) -> None:
        pass

    def do_healthy_check(self) -> bool:
        return True

    # Do work
    def do_update(self, trigger_source: TriggerSource) -> None:
        self.logger.debug(f"Update called, trigger_source={trigger_source}")
        if trigger_source == trigger_source.MANUAL:
            self.valueCache.clear()
            self.inventory_data = None

        try:
            self.fetch_data_with_retry(try_count=3)
        except Exception as e:
            self.fecth_errors_metric.inc()
            self.logger.error(f"Error occured: {e}")
            return

        self.succesfull_fecth_metric.inc()
        self.publish_value_to_mqtt_topic(
            "lastUpdateTime",
            str(datetime.now().replace(microsecond=0).isoformat()),
            True,
        )

    def fetch_data_with_retry(self, try_count: int = 1):
        for i in range(try_count):
            try:
                self.fetch_data()
                return
            except CommunicationError:
                rndtime = randint(100, 500) / 1000 # 0.1 - 0.5s #  nosec
                self.logger.debug(f"Communication error, retry {i+1} after {rndtime}s")
                time.sleep(rndtime)

    def fetch_data(self):
        if self.inventory_data is None:
            self.inventory_data = self.ups.fetch_inventory_data()
            self.inventory_data.serial_number

        status_data = self.ups.fetch_status_data()
        settings = self.ups.fetch_settings()
        dynamic_data = self.ups.fetch_dynamic_data()
        commands_data = self.ups.fetch_commands_data()
        self.ups.close_connection()
        self.publish_data(asdict(self.inventory_data))
        self.publish_data(asdict(status_data))
        self.publish_data(asdict(settings))
        self.publish_data(asdict(dynamic_data))
        self.publish_data(asdict(commands_data))

    def publish_data(self, data: dict):
        sn = self.inventory_data.serial_number
        for key, value in data.items():
            if value is not None:
                val = f"{value:.1f}" if type(value) == float else str(value)
                self.publish_value(f"{sn}/{key}", val)

    def publish_value(self, key: str, value: str) -> None:
        previousvalue = self.valueCache.get(key)
        publish = False
        if previousvalue is None:
            self.logger.debug(f"{key}: no cache value available")
            publish = True
        elif value == previousvalue:
            self.logger.debug(f"{key} = {value} : skip update because of same value")
        else:
            publish = True

        if publish:
            self.logger.info("%s = %s", key, value)
            self.publish_value_to_mqtt_topic(key, value, False)
            self.valueCache.set(key, value)


if __name__ == "__main__":
    Framework().run(MyApp(), MyConfig())
