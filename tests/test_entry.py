from flask import json
from datetime import datetime
from application.models import User, Entry
from application import bcrypt
import pytest


# Test for User

# Testing User Model #
@pytest.mark.parametrize(
    "userlist",
    [['nathan', '1234'], ['test', '12345678']],
)

def test_user(userlist, capsys):
    encrypted = bcrypt.generate_password_hash(userlist[1]).decode('utf-8')
    with capsys.disabled():
        user = User(username=userlist[0], password=encrypted)
    # Assert Statement
    assert user.username == userlist[0]
    assert user.password == encrypted

# Expected Failures #

# Invalid Inputs
@pytest.mark.xfail(reason="Invalid Username")
@pytest.mark.parametrize(
    "userlist",
    [
        ['ema', '1234'], # Out of Range
        ['sammmmmmmmmmmmmm', '12345678'], # Out of Range
        ['in paris', '12345678'], # Contains Spaces
        ['nathan', '123'], # Out of Range (Passwoerd)
        ['test', '123456789'], # Out of Range (Password)
    ], 
)

def test_userInvalidUsername(userlist, capsys):
    test_user(userlist, capsys)


# Unit Testing for User-Related APIs 

# Testing User (Adding Entry)
@pytest.mark.parametrize('entrylist', [
    ['uwuwuwuwu', '12345678'], 
    ['oohlala', '12345678'], 
])

def test_addUser(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/api/user", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['id']

# Testing User (Deleting Entry)
@pytest.mark.parametrize('entrylist', [
    ['ronaldo', '12345678'], 
    ['messiargentina', '12345678'], 
])

def test_deleteUser(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post('/api/user', data = json.dumps(data), content_type = 'application/json')
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['id']
        response = client.get(f'/api/deleteu/{response_body["id"]}')
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['result'] == 'ok'
    
# Testing User (Get Entry)
@pytest.mark.parametrize('entrylist', [
    [1, 'uwuwuwuwu', '12345678'], 
    [2, 'oohlala', '12345678'], 
    [3, 'ronaldo', '12345678'], 
    [4, 'messiargentina', '12345678'], 
])

def test_getUser(client, entrylist, capsys):
    with capsys.disabled():
        response = client.get(f'/api/getuser/{entrylist[0]}')
        ret = json.loads(response.get_data(as_text=True))
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['id'] == entrylist[0]
        assert response_body['username'] == entrylist[1]

# Login API
@pytest.mark.parametrize('entrylist', [
    ['ronaldo', '12345678'], 
    ['messiargentina', '12345678'], 
])	

def test_login(client, entrylist, capsys):
    with capsys.disabled():
        entrylist[1] = bcrypt.generate_password_hash(entrylist[1]).decode('utf-8')
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/login_api", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['message'] == 'Login Successful'

# Testing User Login (Invalid Username)
@pytest.mark.xfail(reason="Invalid Username")
@pytest.mark.parametrize('entrylist', [
    ['wth123', 'lololol'],
    ['wtp123', '12345678'],
])

def test_loginInvalid(client, entrylist, capsys):
    with capsys.disabled():
        entrylist[1] = bcrypt.generate_password_hash(entrylist[1]).decode('utf-8')
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/login_api", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['message'] == 'Login Successful'

# Testing User Login (Invalid Password)
@pytest.mark.xfail(reason="Invalid Password")
@pytest.mark.parametrize('entrylist', [
    ['ronaldo', '123456789'], 
    ['messiargentina', '123456789'],
])

def test_loginInvalid(client, entrylist, capsys):
    with capsys.disabled():
        entrylist[1] = bcrypt.generate_password_hash(entrylist[1]).decode('utf-8')
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/login_api", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['message'] == 'Login Successful'

# Testing User Login (Empty Fields)
@pytest.mark.xfail(reason="Empty Fields")
@pytest.mark.parametrize('entrylist', [
    ['messiargentina', ''],
    ['', '12345678'],
    ['', ''],
]) 

def test_loginInvalid(client, entrylist, capsys):
    with capsys.disabled():
        entrylist[1] = bcrypt.generate_password_hash(entrylist[1]).decode('utf-8')
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/login_api", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['message'] == 'Login Successful'

# Unexpected Failure (Invalid Data Type)
@pytest.mark.xfail(reason="Invalid")
@pytest.mark.parametrize('entrylist', [
    ['wth123', None],
    [None, '12345678'],
    [None, None],
])

def test_loginInvalid(client, entrylist, capsys):
    with capsys.disabled():
        entrylist[1] = bcrypt.generate_password_hash(entrylist[1]).decode('utf-8')
        data = {
            "username": entrylist[0],
            "password": entrylist[1],
        }
        response = client.post(
            "/login_api", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['message'] == 'Login Successful'


# Test for Predict

# Testing Adding Entry Model

@pytest.mark.parametrize('entrylist', [
    ['car-test-1.jpeg', 0], 
    ['cat-test-2.jpg', 1], 
    ['airplane-test-3.jpg', 0], 
    ['bird-test-4.jpg', 1]
])

def test_addEntry(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            'filename':entrylist[0],
            'model':entrylist[1],   
        }
        response = client.post(
            "/api/entry", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['id']

@pytest.mark.parametrize('entrylist', [
    [1, 'car-test-1.jpeg', 0, 'Automobile', 100.0], 
    [2, 'cat-test-2.jpg', 1, 'Cat', 97.0], 
    [3, 'airplane-test-3.jpg', 0, 'Airplane', 100.0], 
    [4, 'bird-test-4.jpg', 1, 'Bird', 88.0]
])

def test_Entry(entrylist, capsys):
    with capsys.disabled():
        print (entrylist)
        entry = Entry(
            id = entrylist[0],
            image_url = entrylist[1],
            model_selection = entrylist[2],
            pred = entrylist[3],
            conf_pct = entrylist[4],
            pred_dt = datetime.now()
        )

    # Assert that the entry is valid
    assert entry.id == entrylist[0]
    assert entry.image_url == entrylist[1]
    assert entry.model_selection == entrylist[2]
    assert entry.pred == entrylist[3]
    assert entry.conf_pct == entrylist[4]

@pytest.mark.parametrize('delete', [
    ['car-test-1.jpeg', 0], 
    ['cat-test-2.jpg', 1], 
    ['airplane-test-3.jpg', 0], 
    ['bird-test-4.jpg', 1]
])

def test_removeEntry(client, delete, capsys):
    with capsys.disabled():
        data = {
            'filename':delete[0],
            'model':delete[1],   
        }
        response = client.post('/api/entry', data = json.dumps(data), content_type = 'application/json')
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['id']
        response = client.get(f'/api/deleteentry/{response_body["id"]}')
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        response_body = json.loads(response.get_data(as_text=True))
        assert response_body['result'] == 'ok'



# Invalid Image Type
@pytest.mark.xfail(reason = 'Invalid Image File Type')
@pytest.mark.parametrize('entrylist', [
    ['invalid1.html', 0], 
    ['invalid2.txt', 1], 
    ['invalid3.ipynb', 0], 
    ['invalid4.py', 1]
])

def test_entry_data_types(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            'filename':entrylist[0],
            'model':entrylist[1],   
        }
        response = client.post('/api/entry', data = json.dumps(data), content_type = 'application/json')





