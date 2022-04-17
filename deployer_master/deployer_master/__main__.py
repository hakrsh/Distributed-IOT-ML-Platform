import logging
from deployer_master.master import start, kafka_thread, execute_pending
import threading
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting model deployment thread")    
    threading.Thread(target=kafka_thread).start()
    threading.Thread(target=execute_pending).start()
    logging.info("Starting master")
    start()


