from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symbols.db'

db = SQLAlchemy(app)


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    shares = db.Column(db.Integer, nullable=False)


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
    days = 5
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


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        clear = request.form.get('clear')
        if clear == 'clear':
            print("clearing table")
            stocks = Stock.query.all()
            for stock in stocks:
                db.session.delete(stock)
                db.session.commit()
        else:
            new_symbol = request.form.get('symbol')
            new_symbol_shares = request.form.get('shares')
            exists = db.session.query(Stock.id).filter_by(name=new_symbol).scalar() is not None
            print(exists)
            if new_symbol and not exists:
                new_symbol_obj = Stock(name = new_symbol, shares = new_symbol_shares)
                db.session.add(new_symbol_obj)
                db.session.commit()

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}' \
          '&outputsize=compact&apikey=KIH6VFJ03Z89T5DI'
    stock_data = []
    stocks = Stock.query.all()
    total_value = 0
    high_charts_data = []

    for symbol in stocks:
        r = requests.get(url.format(symbol.name)).json()
        high_charts_data = to_high_charts(r)
        last_updated = r['Meta Data']['3. Last Refreshed']
        shares = symbol.shares
        last_price = float(r['Time Series (Daily)'][last_updated]['4. close'])

        stock = {
            'symbol' : symbol.name,
            'shares' : shares,
            'last_price' : last_price,
            'value' : "$" + "{:,.2f}".format(shares*last_price),
            'price_per_share' : "$" + "{:,.2f}".format(last_price),
            'high_charts' : high_charts_data,
        }
        total_value = total_value + stock['shares']*stock['last_price']
        stock_data.append(stock)

    total_value = "$" + "{:,.2f}".format(total_value)

    return render_template("weather.html", stock_data=stock_data, total_value=total_value, chart=high_charts_data)


@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)


@app.route('/post/<int:post_id>')
def post(post_id):
    return "<h2>Post id is %s</h2>" % post_id


if __name__ == "__main__":
    app.run(debug=True)