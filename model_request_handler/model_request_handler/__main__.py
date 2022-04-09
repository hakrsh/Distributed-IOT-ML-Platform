from model_request_handler.app import start, get_running_models
import threading

if __name__ == "__main__":
    threading.Thread(target=get_running_models, args=()).start()
    start()
