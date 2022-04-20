from platform_manager.app import start, worker_status_update
import threading

if __name__ == "__main__":
    threading.Thread(target=worker_status_update).start()
    start()
