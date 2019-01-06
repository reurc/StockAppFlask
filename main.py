from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

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

    for symbol in stocks:
        r = requests.get(url.format(symbol.name)).json()
        last_updated = r['Meta Data']['3. Last Refreshed']
        shares = symbol.shares
        last_price = float(r['Time Series (Daily)'][last_updated]['4. close'])

        stock = {
            'symbol' : symbol.name,
            'shares' : shares,
            'last_price' : last_price,
            'value' : shares*last_price,
        }

        stock_data.append(stock)

    print(weather)

    return render_template("weather.html", stock_data=stock_data)

@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)


@app.route('/post/<int:post_id>')
def post(post_id):
    return "<h2>Post id is %s</h2>" % post_id


if __name__ == "__main__":
    app.run(debug=True)