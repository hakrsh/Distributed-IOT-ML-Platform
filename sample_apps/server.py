from flask import Flask, request
app = Flask(__name__)
@app.route('/')
def index():
    return '<h1>Patient Monitoring is running!</h1>'

@app.route('/diabetes-checker', methods=['GET', 'POST'])
def diabetes_checker():
    from patient_monitoring.diabetes_checker.diabetes_checker import predict_diabetes
    
    if request.method == 'POST':
        data = request.json
        return predict_diabetes(data)    
    

@app.route('/vitals-checker', methods=['GET', 'POST'])
def vitals_checker():
    from patient_monitoring.vitals_checker.vitals_checker import predict_condition
    
    if request.method == 'POST':
        data = request.json
        return predict_condition(data)    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)