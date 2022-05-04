from scheduler.app import start,get_running_apps
import threading

if __name__ == "__main__":
    threading.Thread(target=get_running_apps).start()
    start()
