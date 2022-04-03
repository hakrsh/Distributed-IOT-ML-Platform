from flask import Flask, render_template, request
# import requests
import os
app = Flask(__name__)

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route('/showlog')
def showlog():
    print("Log FUnction called")
    # file_name = request.form['topic']
    # file_name = request.args.get('topic')+'.txt'
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    log_files = [f for f in files if f.endswith("logs.txt")]
    content = []
    for f in log_files:
        with open(f,'r') as k:
            content.append(k.read())
    
    # print(content)
    return render_template('aggregatorUI.html',content=content)


@app.route('/showstatus')
def showstatus():
    print("Status FUnction called")
    # file_name = request.form['topic']
    # file_name = request.args.get('topic')+'.txt'
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    status_files = [f for f in files if f.endswith("status.txt")]
    content = []
    for f in status_files:
        with open(f,'r') as k:
            content.append(k.read())
    
    # print(content)
    return render_template('aggregatorUI.html',content=content)





if __name__ == "__main__":  
    app.run(debug=True, port = 8210)