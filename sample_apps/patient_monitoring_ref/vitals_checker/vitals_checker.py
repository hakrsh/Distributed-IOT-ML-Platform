import pickle
import importlib.resources as pkg_resources
def predict_condition(data):
    spo2 = int(data['spo2'])
    temperature = int(data['temperature'])
    pulse = int(data['pulse'])
    model = pickle.load(pkg_resources.open_binary('patient_monitoring.vitals_checker', 'vitals_checker.pkl'))
    pred = model.predict([[spo2, temperature, pulse]])
    if pred[0] == 0:
        return 'Safe'
    else:
        return 'Critical'
