import numpy as np
import pandas as pd
import pickle
import importlib.resources as pkg_resources


def predict_diabetes(data):
    dataset = pd.read_csv(pkg_resources.open_binary('patient_monitoring.diabetes_checker', 'diabetes.csv'))
    dataset_X = dataset.iloc[:,[1, 2, 5, 7]].values
    from sklearn.preprocessing import MinMaxScaler
    sc = MinMaxScaler(feature_range = (0,1))
    sc.fit_transform(dataset_X)

    age = float(data['age'])
    bmi = float(data['bmi'])
    glucose = float(data['glucose'])
    insuline = float(data['insuline'])
    float_features = [glucose, insuline,bmi,age]
    final_features = [np.array(float_features)]
    model = pickle.load(pkg_resources.open_binary('patient_monitoring.diabetes_checker', 'diabetes_checker.pkl'))
    pred = model.predict(sc.transform(final_features))
    if pred[0] == 0:
            return 'false'
    else:
        return 'true'

