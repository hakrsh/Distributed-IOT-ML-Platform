from flask import Flask, request
import requests
import json
import importlib.resources as pkg_resources

module_config = json.loads(pkg_resources.read_binary('load_balancer', 'config.json'))

CONFIG_FILE_PATH = "config.json"

app = Flask(__name__)

def get_sys_usage_endpoint(ip_addr):
    return "http://" + ip_addr + ":6969/get_sys_usage"

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods = ['POST', 'GET'])
def hello(path):
    if(request.method == 'POST'):
        req_dic = request.get_json()
        print(type(req_dic), req_dic)
        worker_ips = [worker['ip'] for worker in module_config['workers']]
        target_ip = ""
        minsum = 200
        for ip in worker_ips:
            url = get_sys_usage_endpoint(ip)
            resp = requests.get(url)
            usage = resp.text.split()
            sum = float(usage[0]) + float(usage[1])
            print(usage)
            if(sum < minsum):
                target_ip = ip
        resp = requests.post(f"http://{target_ip}:9898/{path}", json=request.get_json())
        return resp
    else:
        return ""
    
    

if(__name__ == "__main__"):
    app.run(host = "0.0.0.0", port = 9898, debug=True)
