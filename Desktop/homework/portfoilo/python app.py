from flask import Flask, render_template, redirect, url_for, request, session
from flask_oauthlib.client import OAuth

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# OAuth setup
oauth = OAuth(app)

# Google OAuth configuration
google = oauth.remote_app(
    'google',
    consumer_key='your_google_client_id',
    consumer_secret='your_google_client_secret',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# VK OAuth configuration
vk = oauth.remote_app(
    'vk',
    consumer_key='your_vk_client_id',
    consumer_secret='your_vk_client_secret',
    base_url='https://api.vk.com/method/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize',
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('authorized_google', _external=True))

@app.route('/login/google/authorized')
def authorized_google():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args.get('error_reason'),
            request.args.get('error_description')
        )
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    return f"Logged in as: {user_info.data['email']}"

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/login/vk')
def login_vk():
    return vk.authorize(callback=url_for('authorized_vk', _external=True))

@app.route('/login/vk/authorized')
def authorized_vk():
    response = vk.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied'
    session['vk_token'] = (response['access_token'], '')
    user_info = vk.get('users.get', data={'fields': 'email'})
    return f"Logged in as: {user_info.data['response'][0]['first_name']} {user_info.data['response'][0]['last_name']}"

@vk.tokengetter
def get_vk_oauth_token():
    return session.get('vk_token')

if __name__ == '__main__':
    app.run(debug=True)
