from model_request_handler.app import start, get_running_models, db, models
import threading

if __name__ == "__main__":
    if len(list(db.model_map.find())) != 0:
        models = db.model_map.find_one()
    threading.Thread(target=get_running_models, args=()).start()
    start()
