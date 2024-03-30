from flask import Flask, render_template, request, redirect, url_for
import os
from flask import send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = '/home/Levimukuha/Pyconsole/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return True

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('files[]')
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/clear_files', methods=['POST'])
def clear_files():
    filelist = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    for file in filelist:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
