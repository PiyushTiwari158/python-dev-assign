import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file

app = Flask(__name__)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension == '.xlsx':
        df = pd.read_excel(file_path)
    else:
        return None
    return df.to_html(classes='data', header="true")

def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET'])
def admin():
   
    files = os.listdir(app.config['UPLOAD_FOLDER'])
   
    file_details = {}
    for i, filename in enumerate(files):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_details[i+1] = {
            'name': filename,
            'path': file_path
        }
    return render_template('admin.html', files=file_details)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('admin'))


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/open/<filename>', methods=['GET'])
def open_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    table = read_file(file_path)
    if not table:
        return 'Unsupported file type'
    return render_template('table.html', table=table)

if __name__ == '__main__':
    app.run(debug=True)
