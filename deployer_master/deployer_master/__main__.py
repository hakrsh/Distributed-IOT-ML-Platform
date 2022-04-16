import logging
from deployer_master.master import start, model_deployment_thread
import threading
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting model deployment thread")    
    threading.Thread(target=model_deployment_thread).start()
    logging.info("Starting master")
    start()


