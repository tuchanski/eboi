from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def getHomeScreen():
    return render_template('home/home.html')

app.run('localhost', 8080, None)
