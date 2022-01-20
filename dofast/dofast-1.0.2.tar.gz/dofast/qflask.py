import ast
import hashlib
import os
import time
from socket import timeout
import codefast as cf
import redis
import requests
from flask import Flask, flash, redirect, request, url_for
from hashids import Hashids
from waitress import serve
from werkzeug.utils import secure_filename
from authc import authc

from dofast.config import CHANNEL_MESSALERT
from dofast.flask.config import AUTH_KEY
from dofast.flask.model import lock_device, unlock_device
from dofast.flask.utils import authenticate_flask
from dofast.network import Twitter
from dofast.pipe import author
from dofast.security._hmac import certify_token
from dofast.toolkits.telegram import Channel

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'log', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1000 * 1000     # Maximum size 1GB
authenticate_flask(app)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    cf.error(error)
    return 'InternalError'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/device_control', methods=['GET', 'POST'])
def device_control():
    accs = authc()
    if request.headers.get('User-Agent') != accs['whitelist_agent']:
        return 'UNRECOGNIZED device'
    action = request.args.get('action', 'lock')
    task = unlock_device.delay() if action == 'unlock' else lock_device.delay()
    TIMEOUT = 10
    while TIMEOUT > 0:
        if task.status == 'SUCCESS':
            return 'SUCCESS'
        time.sleep(1)
        TIMEOUT -= 1
    return 'FAILED'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder = request.form.get('upload_folder')
            if folder:
                app.config['UPLOAD_FOLDER'] = folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
            return "SUCCESS"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    msg = request.get_json()
    text = cf.utils.decipher(AUTH_KEY, msg.get('text'))
    media = [f'/tmp/{e}' for e in msg.get('media')]
    cf.info(f'Input tweet: {text} / ' + ''.join(media))
    keys = ast.literal_eval(author.get('slp'))
    twitter_api = Twitter(keys['consumer_key'], keys['consumer_secret'],
                          keys['access_token'], keys['access_token_secret'])
    twitter_api.post([text] + media)
    return 'SUCCESS'


@app.route('/download', methods=['GET', 'POST'])
def download():
    js = request.get_json()
    filename = js['filename']
    return cf.io.reads(filename)


@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    js = request.get_json()
    Channel(CHANNEL_MESSALERT).post(js['text'])
    return 'SUCCESS'


@app.route('/nsq', methods=['GET', 'POST'])
def nsq():
    msg = request.get_json()
    topic = msg.get('topic')
    channel = msg.get('channel')
    data = msg.get('data')
    cf.net.post(f'http://127.0.0.1:4151/pub?topic={topic}&channel={channel}',
                json={'data': data})
    print(topic, channel, data)
    return 'SUCCESS'


@app.route('/hello')
def hello_world():
    return 'SUCCESS!'


r = redis.Redis(host='localhost', port='6379')


@app.route('/s', methods=['GET', 'POST'])
def shorten() -> str:
    data = request.get_json(force=True)
    if not data:
        return 'SUCCESS'
    url = data.get('url', '')
    md5 = hashlib.md5(url.encode()).hexdigest()
    hid = Hashids(salt=md5, min_length=6)
    uniq_id = hid.encode(42)
    r.hset('shorten', mapping={uniq_id: url})
    return request.host_url + 's/' + uniq_id


@app.route('/<path:path>')
def all_other(path):
    path_str = str(path)
    if not path_str.startswith('s/'):
        return ''
    cache = r.hgetall('shorten')
    _code = path_str.replace('s/', '').encode()
    cf.info(cache, _code)
    if _code in cache:
        url = cache[_code].decode()
        return redirect(url)
    else:
        return redirect('https://www.google.com')


@app.route('/hanlp', methods=['POST', 'GET'])
def hanlp_route():
    texts = request.json.get('texts', [])
    cf.info('hanlp input texts:', texts)
    resp = requests.post('http://localhost:55555/hanlp', json={'texts': texts})
    return resp.json()


def run():
    serve(app, host="0.0.0.0", port=6363)


if __name__ == '__main__':
    run()
