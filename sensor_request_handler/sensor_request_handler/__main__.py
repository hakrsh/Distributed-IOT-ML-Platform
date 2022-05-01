from sensor_request_handler.server import app,start_pending_threads,db_change_detector
import threading
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
	start_pending_threads()
	thread = threading.Thread(target=db_change_detector, args=())
	thread.start()
	app.run(port=7000,host='0.0.0.0')
	thread.join()
