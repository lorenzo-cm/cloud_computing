import datetime
import importlib.util
import json
import os
import pathlib
import time
from typing import Any
import zipfile
import sys
import logging


import redis


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

class Context:
    def __init__(
        self,
        host: str,
        port: int,
        input_key: str,
        output_key: str,
        function_getmtime: float,
        last_execution: datetime.datetime | None,
        env: dict[str, Any],
    ) -> None:
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        self.function_getmtime = function_getmtime
        self.last_execution = last_execution
        self.env = env


class ContextManager:
    def __init__(self) -> None:
        # File management
        self.USER_MODULE_PATH = "/opt/usermodule.py"
        self.USER_MODULE_NAME = "usermodule"

        # ZIP integration
        self.ZIP_FILE_PATH = os.getenv("ZIP_FILE_PATH", "")
        self.ZIP_ENTRY_RELATIVE_FILE_PATH = os.getenv("ZIP_ENTRY_RELATIVE_FILE_PATH", "main.py")
        self.IS_ZIP = self.ZIP_FILE_PATH != "" and self.ZIP_ENTRY_RELATIVE_FILE_PATH != ""
        self.ZIP_TARGET_PATH = "/opt/zip"
        
        if self.IS_ZIP:
            self.setup_zip()

        # Runtime management
        self.function_getmtime = self.get_function_mtime()
        self.last_execution: datetime.datetime | None = None

        # Redis config
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.host = os.getenv("REDIS_HOST", "")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=True,
        )

        self.input_key = os.getenv("REDIS_INPUT_KEY", "metrics")
        self.output_key = os.getenv("REDIS_OUTPUT_KEY", "")
        self.REDIS_MONITOR_PERIOD = int(os.getenv("REDIS_MONITOR_PERIOD", "5"))

        # User handler
        self.user_handler_name = os.getenv("USER_HANDLER_NAME", "handler")

        # env
        self.env: dict[str, Any] = {}
        
        # metrics
        self.last_metrics: dict[str, Any] = {}

        self.check_all_working()

    def run(self) -> None:
        while True:
            metrics = self.get_metrics()
            if metrics != self.last_metrics:
                logging.info("Metrics changed, running handler")
                self.last_metrics = metrics
                self.execute_module_handler(metrics)
            time.sleep(self.REDIS_MONITOR_PERIOD)

    def get_metrics(self) -> dict[str, Any]:
        metrics: Any = self.redis_client.get(self.input_key)
        if metrics is None:
            return {}
        return json.loads(metrics)

    def get_function_mtime(self) -> float:
        return os.path.getmtime(self.USER_MODULE_PATH)

    def check_all_working(self) -> None:
        if not pathlib.Path(self.USER_MODULE_PATH).exists():
            raise FileNotFoundError(f"User module path not found: {self.USER_MODULE_PATH}")
        if not self.redis_client.ping():
            raise ConnectionError(f"Redis connection failed: {self.host}:{self.port}")
        if self.output_key == "":
            raise ValueError("Redis output key is not set")
        
    def setup_zip(self) -> None:
        pathlib.Path(self.ZIP_TARGET_PATH).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.ZIP_FILE_PATH, "r") as zip_ref:
            zip_ref.extractall(self.ZIP_TARGET_PATH)
        self.USER_MODULE_PATH = os.path.join(self.ZIP_TARGET_PATH, self.ZIP_ENTRY_RELATIVE_FILE_PATH)
        
        if self.ZIP_TARGET_PATH not in sys.path:
            sys.path.insert(0, self.ZIP_TARGET_PATH)

    def export_context(self) -> Context:
        # mypy
        assert self.host is not None
        assert self.output_key is not None

        return Context(
            host=self.host,
            port=self.port,
            input_key=self.input_key,
            output_key=self.output_key,
            function_getmtime=self.function_getmtime,
            last_execution=self.last_execution,
            env=self.env,
        )
        
    def is_json_encodable(self, value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False
    
    def execute_module_handler(self, metrics: dict[str, Any]) -> None:
        context = self.export_context()

        spec = importlib.util.spec_from_file_location(
            self.USER_MODULE_NAME, self.USER_MODULE_PATH
        )
        if spec is None:
            raise ImportError(f"Failed to import user file: {self.USER_MODULE_PATH}")
        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise ImportError(f"Failed to import user module: {self.USER_MODULE_PATH}")
        if spec.loader is None:
            raise ImportError(f"Failed to load user module: {self.USER_MODULE_PATH}")
        spec.loader.exec_module(module)
        handler = getattr(module, self.user_handler_name)
        returned_value = handler(metrics, context)

        self.last_execution = datetime.datetime.now()
        self.env = context.env

        if self.is_json_encodable(returned_value):
            self.redis_client.set(self.output_key, json.dumps(returned_value))
        else:
            raise TypeError(
                f"User handler must return a JSON-encodable value, got {type(returned_value)}"
            )
            
def main() -> None:
    logging.info("PROJ3 - Lorenzo Carneiro - Starting serverless application")
    context_manager = ContextManager()
    context_manager.run()
    
if __name__ == "__main__":
    main()