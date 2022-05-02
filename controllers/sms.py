from flask import Flask, request, jsonify
import requests
import json
url = "https://www.fast2sms.com/dev/bulk"

headers = {
'authorization': "Aeoh3MDGpWajkNVBxmSysJgOKzIf7LPTc2YUw6tiR9lZEbv10Q8EX5xvCAYP31kMTDQmStB9s46l7nJq",
'Content-Type': "application/x-www-form-urlencoded",
'Cache-Control': "no-cache",
}
def send_sms(phone,msg):
    payload = "sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+phone
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def sms():
    data = request.data
    data = json.loads(data)
    send_sms(data['phone'],data['msg'])
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7500)
