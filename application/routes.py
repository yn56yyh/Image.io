from application import app, bcrypt, db
from flask import render_template, request, flash, redirect, url_for, jsonify
from application.models import User, Entry
from application.forms import PredictionForm
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps
import numpy as np
from datetime import datetime
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
    return render_template(
        "dashboard.html",
        entries=entries,
)

## Search Function for Dashboard PAge
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    # Perform search and get results
    entries = perform_search(search_term)
    print (entries)
#     return render_template(
#         "dashboard.html",
#         entries=entries,
# )

def perform_search(search_term):
    results = Entry.query.filter(
        db.or_(
            Entry.image_url.ilike(f'%{search_term}%'),
            Entry.model_selection.ilike(f'%{search_term}%'),
            Entry.pred.ilike(f'%{search_term}%'),
            Entry.pred_dt.ilike(f'%{search_term}%'),
            Entry.conf_pct.ilike(f'%{search_term}%'),
        )
    ).all()
    
    return results


## Logout Page ##
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index_page'))


## Predict Page ##
#Handles http://127.0.0.1:5000/predict
@app.route('/predict', methods=['GET', 'POST'])
def upload_page():
    form = PredictionForm()
    if form.validate_on_submit():
        file = form.file.data
        choice = form.Model_selection.data
        if int(choice) == 0:
            db_choice = 'NathanNet-v1'
        elif int(choice) == 1:
            db_choice = 'NathanNet-v2'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") + filename 
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename)
            output, index = predict(file_path, choice)
            index = index[0]
            conf_pct1 = max(index)
            # Add to Database 
            insert_db = Entry(
                image_url = filename,
                model_selection = db_choice,
                pred = output,
                conf_pct = conf_pct1,
                pred_dt = datetime.datetime.now()
            )
            result = add_entry(insert_db)
            print ('Added to Database', result)
            filename = 'upload/'+filename
            return redirect(url_for('results_page', mod_conf=round(conf_pct1*100,2), result=output, img=filename, choice = db_choice))
        else:
            flash('Error: Unsupported file type.')
    
    if current_user.is_authenticated == False:
        return redirect(url_for('index_page'))
    return render_template('Upload.html', index = True, pred = form)
   
def make_prediction(instances, url):
    data = json.dumps({"signature_name": "serving_default", "instances":
    instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions 


def predict(filename, choice):
    print ('enter predict')
    # Decoding and pre-processing image
    img = image.img_to_array(image.load_img(filename, target_size=(32, 32))) / 255.
    # reshape data to have 3 channels
    img = img.reshape(1, 32, 32, 3)
    if int(choice) == 0:
        predictions = make_prediction(img, 'https://ca2-model-1.onrender.com/v1/models/img_classifier:predict')
    elif int(choice) == 1:
        predictions = make_prediction(img, 'https://ca2-model-1.onrender.com/v1/models/img_classifier:predict')
    ret = ""
    class_labels = ['Airplane', 'Car', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']
    for i, pred in enumerate(predictions):
        index = np.argmax(pred)
        response = class_labels[index]
        ret = "{}".format(response)
    return ret, predictions

## Result Page ##
@app.route('/results')
def results_page():
    mod_conf = request.args.get('mod_conf')
    result = request.args.get('result')
    img = request.args.get('img')
    choice = request.args.get('choice')
    if not mod_conf or not result or not img or not choice:
        return redirect(url_for('upload_page'))
    return render_template('Results.html', mod_conf=mod_conf, result=result, img=img, choice = choice)




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


## Adding Entry ##
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id

    except Exception as error:
        db.session.rollback()
        flash (f'Error: {error}', 'danger')

## Removing Entry ##
def remove_entry(id):
    try:
        entry = db.get_or_404(Entry, id)
        db.session.delete(entry)
        db.session.commit()
    except Exception as error: 
        db.session.rollback()
        flash(f"Error: {error}", "danger")
        return error


@app.route('/remove/<id>', methods = ['POST'])
def remove(id):
    remove_entry(id)
    return redirect(url_for('dashboard_page'))



