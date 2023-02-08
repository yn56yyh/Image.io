from application import app, bcrypt, db
from flask import render_template, request, flash, redirect, url_for, jsonify
from application.models import User, Entry
from application.forms import UploadFileForm, PredictionForm
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename
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
import datetime 

# Validation Stuff #
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


## Dashboard Page ##
ROWS_PER_PAGE = 8
@app.route("/dashboard")
def dashboard_page():
    if current_user.is_authenticated == False:
        return redirect(url_for("index_page"))
    # Set the pagination config
    page = request.args.get("page", 1, type=int)
    entries = Entry.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    # Create a variable to generate the number of times the loop will run
    return render_template(
        "dashboard.html",
        entries=entries,
        Gender=Gender,
        Hypertension=Hypertension,
        Heart_Disease=Heart_Disease,
        Ever_Married=Ever_Married,
        Work_Type=Work_Type,
        Residence_Type=Residence_Type,
        Smoking_Status=Smoking_Status,
        Stroke=Stroke,
)


## Logout Page ##
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index_page'))


## Predict Page ##
#Handles http://127.0.0.1:5000/predict
@app.route('/predict', methods=['GET', 'POST'])
def upload_page():
    form = UploadFileForm()
    predict_form = PredictionForm()
    if form.validate_on_submit():
        print ('Submit Button Clicked!')
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") + filename
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename)
            print ('Image Uploaded!')
            output = predict(file_path, 'https://ca2-model-j26f.onrender.com/v1/models/img_classifier:predict') 
            # Run Prediction
            # if 'model1_predict' in request.form:
            #     output = predict(filename, 'https://ca2-model-j26f.onrender.com/v1/models/img_classifier')
            # elif 'model2_predict' in request.form:
            #     output = predict(filename, 'https://ca2-model2.onrender.com/v1/models/img_classifier')
            print (output)
            # Add to Database (Not Complete)
            # return render_template('results.html', output = output)
        else:
            flash('Error: Unsupported file type.')
    if current_user.is_authenticated == False:
        return redirect(url_for('index_page'))
    return render_template('Upload.html', index = True, form = form, pred = predict_form)


def make_prediction(instances, url):
    data = json.dumps({"signature_name": "serving_default", "instances":
    instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions 


def predict(filename, url):
    # Decoding and pre-processing image
    img = image.img_to_array(image.load_img(filename, target_size=(32, 32))) / 255.
    # reshape data to have 3 channels
    img = img.reshape(1, 32, 32, 3)
    predictions = make_prediction(img, url)
    ret = ""
    for i, pred in enumerate(predictions):
        confidence = "{}".format(np.argmax(pred))
        ret = "{}".format(np.argmax(pred), axis = -1)
        response = ret
    print (confidence)
    return response



## Error Handling Pages ##
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


