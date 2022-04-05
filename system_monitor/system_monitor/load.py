import psutil
from flask import Flask

app = Flask(__name__)

@app.route('/get_sys_usage')
def get_usage():
    cpu_usage = psutil.cpu_percent(1)
    memory_usage = psutil.virtual_memory()[2]
    print(str(cpu_usage) + " " +  str(memory_usage))
    return str(cpu_usage) + " " +  str(memory_usage)

if(__name__ == "__main__"):
    app.run(host = "0.0.0.0", port=6969)

