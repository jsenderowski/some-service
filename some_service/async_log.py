import json
import time
import threading
import asyncio
import logging
import datetime
import traceback

from logging.handlers import RotatingFileHandler, QueueHandler

from queue import Queue, Empty

import aiohttp

def configure_logger(
        logger: logging.Logger,
        level: str | int = "DEBUG",
        /,
        propagate=False,
        reset_handlers=False,
        *,
        queue: Queue = None,
        stream=True,
        file="some_service.log") -> logging.Logger:
    """set logging level of `logger` to `level` and add chosen handlers:
    
     - `queue=None` - adds handler that emits JSON serialized messages to 
        queue specified by this parameter
     - `stream=True` - adds handler that emits messages to stdout or stderr
     - `file="file/path.log"` - adds handler that emits messages to file and rotates
        them every 1MB (ignored if empty or False)

    if `reset_handlers` is set to `True` any existing handlers on the logger will
    be cleared out before setting new handlers

    `propagate` argument value is directly assigned to `logger.propagate` which
    will, well, propagate records to parent logger
     """

    logger.setLevel(level=level)
    logger.propagate = propagate
    if reset_handlers:
        logger.handlers.clear()

    if queue:
        # putting records to a defined queue
        publishing_handler = QueueHandler(queue)
        publishing_handler.setFormatter(
            JSONFormatter()
        )
        logger.addHandler(publishing_handler)

        # the resulting emitted records are not normal `LogRecord` instances
        # instead they are preformatted and put back into `record.msg` and `record.message`
        # thus resulting record will be a repr of instance instead of message one may expect

    if stream:
        # print log records to sys.stderr
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(levelname)s(%(name)s): %(message)s")
        )  # TODO: shell colors?
        logger.addHandler(stream_handler)

    if file:
        # append records to files that rotate every 1MB
        file_handler = RotatingFileHandler(
            file,
            maxBytes=1024*1024,
            backupCount=4
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s: %(levelname)s(%(name)s): %(message)s")
        )
        logger.addHandler(file_handler)

    return logger


class JSONFormatter(logging.Formatter):
    """formatter that serializes record to string of JSON Object"""
    def format(self, record: logging.LogRecord) -> str:
        message = record.msg
        if record.args:
            try:
                message = message % record.args
            except TypeError:
                message.format(record.args)

        record_json = {
            "time": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "message": message,
            "level": record.levelname,
            "file": record.pathname,
        }
        if record.exc_info:
            exc_type, exc_val, exc_tb = record.exc_info
            record_json["exception"] = {
                "exc_val": str(exc_val),
                "exc_type": exc_type.__name__,
                "exc_tb": traceback.format_tb(exc_tb)
            }
        return json.dumps(record_json)


# logscollector part:

logscollector_logger = logging.getLogger("logscollector.debug")
configure_logger(logscollector_logger)


async def task_id():
    return id(asyncio.current_task(asyncio.get_running_loop()))


class LogSenderThread(threading.Thread):
    """thread class that runs as long as event loop it was initialized with is running
    and executes task that sends data from queue it was initialized with to specified
    address"""
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            queue: Queue,
            address: str,
            *args,
            **kwargs):
        self._log_queue = queue
        self._loop = loop
        self._address = address
        threading.Thread.__init__(self, *args, **kwargs)

    async def publish(self, record):
        """send `data` with aiohttp to `self._address`"""
        try:
            async with aiohttp.ClientSession() as session:
                logscollector_logger.debug(f"Request to {self._address}.")
                async with session.post(
                        self._address,
                        data=record.msg) as resp:
                    logscollector_logger.debug(
                        f"Response from {self._address}: {(await resp.read()).decode()}")
        except:
            pass

    def run(self):
        while self._loop.is_running():
            try:
                if self._log_queue.qsize() != 0:
                    asyncio.run_coroutine_threadsafe(
                        self.publish(self._log_queue.get_nowait()),
                        loop=self._loop
                    )
            except Empty:
                pass
            finally:
                time.sleep(0.01)

async def init_logger(queue, address) -> Queue:
    """start a thread that will send data in `log_queue` to `address`"""
    try:
        logger_thread = LogSenderThread(
            loop=asyncio.get_running_loop(),
            queue=queue,
            address=address
        )
        logger_thread.start()
        logging.info(f"Current task ID: id={await task_id()}")
    except RuntimeError:
        print("Could not start LogscollectorSender thread.")

log_queue = Queue()

root_logger = logging.getLogger()
configure_logger(root_logger, queue=log_queue)
root_logger.setLevel("DEBUG")
