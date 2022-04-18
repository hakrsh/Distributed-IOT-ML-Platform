import logging
from model_request_handler.app import start, get_running_models
import threading
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info('Starting db watcher')
    threading.Thread(target=get_running_models, args=()).start()
    logging.info('Starting server')
    start()
