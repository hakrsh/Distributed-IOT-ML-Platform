from deployer.deployerService import start, pending_jobs
import threading

if __name__ == "__main__":
    threading.Thread(target=pending_jobs).start()
    start()
