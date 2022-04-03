from flask import Flask, render_template, request
# import requests

app = Flask(__name__)

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route('/showlog', methods = ['GET'])
def showlog():
    print("FUnction called")
    # file_name = request.form['topic']
    file_name = request.args.get('topic')+'.txt'
    
    with open(file_name,'r') as f:
        content = f.read()
    
    # print(content)
    return render_template('index.html',content=content)


if __name__ == "__main__":  
    app.run(debug=True, port = 8210)