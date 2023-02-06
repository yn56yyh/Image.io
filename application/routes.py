from application import app, bcrypt, db
from flask import render_template, request, flash, redirect, url_for, jsonify
from application.models import User
from flask_login import login_user, current_user, logout_user
from flask_cors import CORS, cross_origin
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps
import numpy as np
import tensorflow.keras.models
import re
import base64
from io import BytesIO
# from tensorflow.keras.datasets.mnist import load_data
import json
import numpy as np
import requests
import pathlib, os
from application.forms import RegistrationForm, LoginForm

# Rendering Pages

## Index Page ##
@app.route('/')
@app.route('/index')
@app.route('/home')
def index_page():
    return render_template('index.html')

## Login Page ##
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index_page'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


## Register Page ##
#Handles http://127.0.0.1:5000/register
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


## Predict Page ##


def parseImage(imgData):
    # parse canvas bytes and save as output.png
    imgstr = re.search(b'base64,(.*)', imgData).group(1)
    with open('output.png','wb') as output:
        output.write(base64.decodebytes(imgstr))
    im = Image.open('output.png').convert('RGB')
    im_invert = ImageOps.invert(im)
    im_invert.save('output.png')

def make_prediction(instances):
    data = json.dumps({"signature_name": "serving_default", "instances":
    instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions

#Server URL – change xyz to Practical 7 deployed URL [TAKE NOTE]
url = 'https://xyz.onrender.com/v1/models/img_classifier:predict'


#Handles http://127.0.0.1:5000/predict
@app.route("/predict", methods=['GET','POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def predict():
    # get data from drawing canvas and save as image
    parseImage(request.get_data())
    # Decoding and pre-processing base64 image
    img = image.img_to_array(image.load_img("output.png", color_mode="grayscale",
    target_size=(28, 28))) / 255.
    # reshape data to have a single channel
    img = img.reshape(1,28,28,1)
    predictions = make_prediction(img)
    ret = ""
    for i, pred in enumerate(predictions):
        ret = "{}".format(np.argmax(pred))
        response = ret
    return response

