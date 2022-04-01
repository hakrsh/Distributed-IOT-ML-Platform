import requests
import time

while True:
    print('1. Upload model')
    print('2. Upload application')
    print('3. Fetch applications')
    print('4. Fetch application')
    print('5. Exit')
    choice = input('Enter your choice: ')
    if choice == '1':
        path = input('Enter path: ')
        data = {"path": path}
        url = 'http://localhost:5000/upload-model'
        response = requests.post(url, json=data).content
        print(response.decode('ascii'))
    elif choice == '2':
        ApplicationID = round(time.time())
        ApplicationName = input('Enter Application Name: ')
        FileLocation = input('Enter File Location: ')
        data = {"ApplicationID": ApplicationID,
                "ApplicationName": ApplicationName, "FileLocation": FileLocation}
        url = 'http://localhost:5000/upload-app'
        response = requests.post(url, json=data).content
        print(response.decode('ascii'))
    elif choice == '3':
        url = 'http://localhost:5000/api/get-applications'
        response = requests.get(url).content
        print(response.decode('ascii'))
    elif choice == '4':
        ApplicationID = input('Enter Application ID: ')
        url = 'http://localhost:5000/api/get-application/' + ApplicationID
        response = requests.get(url).content
        print(response.decode('ascii'))
    elif choice == '5':
        break
