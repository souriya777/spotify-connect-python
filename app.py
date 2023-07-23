from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import requests, json

# Create a Flask app instance
app = Flask(__name__)
# session
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"

# home
@app.route('/')
def home():
  return render_template('home.html')

# authorize
@app.route('/authorize')
def authorize():
  # user-library-read is the "scope authorization" to retrieve infos like ALBUMS
  # redirect_uri is encoded, but correspond to http://localhost:5000/tokens
  AUTHORIZE_URL = "https://accounts.spotify.com/authorize?response_type=code&client_id=" + CLIENT_ID + "&scope=user-library-read&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Ftokens%2F"
  return redirect(AUTHORIZE_URL)

# tokens
@app.route('/tokens/')
def tokens():
  authorizationCode = request.args.get('code')
  response = requests.post(
      url="https://accounts.spotify.com/api/token",
      data={
        'code': str(authorizationCode),
        'redirect_uri': "http://localhost:5000/tokens/",
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
      }
  )

  jsonResponse = json.loads(response.content)

  for key in jsonResponse:
    if (key == 'access_token') :
      session['access_token'] = jsonResponse[key]
    elif(key == 'refresh_token') :
      session['refresh_token'] = jsonResponse[key]

  return render_template('tokens.html', access_token=session['access_token'], refresh_token=session['refresh_token'])

# my-albums
@app.route('/albums')
def myAlbums():
  response = requests.get(
      url="https://api.spotify.com/v1/me/albums?limit=50",
      headers={
        'Authorization': 'Bearer ' + session['access_token']
      },
  )

  jsonResponse = json.loads(response.content)

  return render_template('albums.html', albums=jsonResponse)

# Run the app when the script is executed
if __name__ == '__main__':
  app.run()
