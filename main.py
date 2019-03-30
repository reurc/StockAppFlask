from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symbols.db'

db = SQLAlchemy(app)


class Tester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    release = db.Column(db.String, nullable=False)
    last_update = db.Column(db.Date, nullable=False)


@app.route('/')
@app.route('/<user>')
def index(user=None):
    #return 'Method used %s' % request.method
    return render_template("user.html", user=user)


@app.route('/bacon', methods=['GET', 'POST'])
def bacon():
    if request.method == 'POST':
        return "You are using POST"
    else:
        return "You are using GET"


#@app.route('/')
#def index():
#    return 'This is the home page'
def to_high_charts(response):
    high_charts = []
    days = 30
    i = iter(response["Time Series (Daily)"].values())
    a = iter(response["Time Series (Daily)"].keys())
    pattern = re.compile('(\d{4})-(\d{2})-(\d{2})')
    while days > 0:
        try:
            next_entry = next(a)
            next_price = float(next(i)["4. close"])
            m = pattern.match(next_entry)
        except StopIteration:
            print("we reached the end")
            break
        if m is not None:
            point = {
                'year': int(m.group(1)),
                'month': int(m.group(2))-1,
                'day': int(m.group(3)),
                'data': "{:.2f}".format(next_price),
            }
            high_charts.append(point)
            days -= 1
    print(high_charts)
    print(json.dumps(high_charts))
    return json.dumps(high_charts)


@app.route('/tuna')
def tuna():
    return '<h2>Tuna is good!</h2>'


@app.route('/shopping')
def shopping():
    food = ["Cheese", "Tuna", "Beef"]
    return render_template("shopping.html", food=food)


def get_efct_data():
    data = {
        'testerA' : {'status' : 'Running', 'temperature' : 70, 'release' : '1.0.0'},
        'testerB' : {'status' : 'Idle', 'temperature' : 65, 'release' : '1.2.3'},
        'testerC' : {'status' : 'Off', 'temperature' : 25, 'release' : '1.3.5'},
    }
    print(data)
    return json.dumps(data);


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    efct_data = get_efct_data()
    print(efct_data)
    data = json.loads(efct_data)
    print(data)
    tester_data = []
    for tester in data:
        print("tester is " + tester)
        value = data[tester]
        print("The key and value are ({}) = ({})".format(tester, value))
        element = {
            'id' : tester,
            'status' : data[tester]['status'],
            'temp' : data[tester]['temperature'],
            'release' : data[tester]['release'],
        }
        tester_data.append(element)

    print(tester_data)

    return render_template("weather.html", stock_data=tester_data)


@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)


@app.route('/post/<int:post_id>')
def post(post_id):
    return "<h2>Post id is %s</h2>" % post_id


if __name__ == "__main__":
    app.run(debug=True)