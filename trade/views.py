from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db
from user.models import User, History
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
from .extra import lookup
from datetime import date
import requests
from werkzeug.exceptions import default_exceptions


api_key = 'a74c1d6a9bfc48a096826ab16608dd72'
if not api_key:
    raise RuntimeError("API_KEY not set")

trade = Blueprint("trade", __name__, template_folder="templates", static_folder="static")

@trade.route("/")
@login_required
def home():
    return render_template("home.html")

@trade.route("/stocktrade")
@login_required
def stocktrade():
    return render_template("stocktrade.html")



@trade.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        stock = lookup(symbol)

        if not symbol:
            flash("Please enter the correct symbol")
            return redirect(url_for("trade.buy"))

        if not stock:
            flash("Stock symbol does not exist")
            return redirect(url_for("trade.buy"))

        if not shares or not shares.isdigit() or int(shares) <= 0:
            flash("Please enter a valid number of shares")
            return redirect(url_for("trade.buy"))

        price = stock["price"]
        user = User.query.get(current_user.id)

        if not user:
            flash("User not found")
            return redirect(url_for("trade.buy"))

        user_cash = user.cash
        total_cost = float(price) * int(shares)

        if user_cash < total_cost:
            flash("Sorry! You don't have enough money")
            return redirect(url_for("trade.buy"))

        try:
            # update user cash
            user.cash -= total_cost
            db.session.commit()

            # insert transaction into history
            new_history = History(user_id=current_user.id, price=float(price), shares=int(shares), date=date.today(), symbol=symbol.upper())
            db.session.add(new_history)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f"Transaction failed: {e}")
            return redirect(url_for("trade.buy"))

        flash("Stock purchased successfully!")
        return redirect(url_for("trade.history"))
    else:
        return render_template("buy.html")





@trade.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        stock = lookup(symbol)

        if not symbol:
            flash("Symbol not entered")
            return redirect(url_for("trade.sell"))

        if not shares or not shares.isdigit() or int(shares) <= 0:
            flash("Invalid number of shares")
            return redirect(url_for("trade.sell"))

        try:
            historyy = db.session.query(History.symbol, db.func.sum(History.shares).label('shares')).filter_by(user_id=current_user.id, symbol=symbol).group_by(History.symbol).first()
        except SQLAlchemyError as e:
            flash(f"Can't connect to database: {e}")
            return redirect(url_for("trade.sell"))

        if not historyy or historyy.shares < int(shares):
            flash("You don't have enough shares to sell")
            return redirect(url_for("trade.sell"))

        try:
            user = User.query.get(current_user.id)
            user.cash += float(stock["price"]) * int(shares)
            db.session.commit()
        except SQLAlchemyError as e:
            flash(f"Can't connect to database: {e}")
            return redirect(url_for("trade.sell"))

        try:
            new_history = History(user_id=current_user.id,price=float(stock["price"]),shares=-int(shares),date=date.today(),symbol=symbol)
            db.session.add(new_history)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Can't connect to database: {e}")
            return redirect(url_for("trade.sell"))

        return redirect(url_for("trade.history"))
    else:
        try:
            stock = db.session.query(History.symbol).filter_by(user_id=current_user.id).group_by(History.symbol).having(db.func.sum(History.shares) > 0).all()
            return render_template("sell.html", stock=stock)
        except SQLAlchemyError as e:
            flash(f"Couldn't connect to database: {e}")
            return redirect(url_for("trade.sell"))


@trade.route("/history")
@login_required
def history():
    try:
        historyy = db.session.query(History.price, History.shares, History.date, History.symbol).filter_by(user_id=current_user.id).all()
    except SQLAlchemyError as e:
        flash(f"Can't connect to database: {e}")
        return redirect(url_for("trade.history"))

    return render_template("history.html", historyy=historyy)

@trade.route("/recommendations", methods=['GET'])
def recommendations():
    try:
        groq_api_key = "a74c1d6a9bfc48a096826ab16608dd72"

        # Create an instance of ChatGroq
        groq_instance = ChatGroq(groq_api_key=groq_api_key, model_name='llama3-8b-8192')

        # Fetch stock data
        symbols = ["AAPL", "MSFT", "GOOGL", "FB", "ORCL", "INTC"]
        stock_data = [lookup(symbol) for symbol in symbols if lookup(symbol)]  # Get valid stocks

        # Debugging output
        print(f"Fetched stock data: {stock_data}")

        if stock_data:
            names = [data['company'] for data in stock_data if 'company' in data]
            prices = [data['price'] for data in stock_data if 'price' in data]

            # Ensure valid stock data structure
            structured_stock_data = [
                {"company": data["company"], "price": data["price"]}
                for data in stock_data if "company" in data and "price" in data
            ]

            # Generate recommendations
            recommendations = groq_instance.get_recommendations(structured_stock_data)

            print(f"Recommendations: {recommendations}")
        else:
            names = ["No data available"]
            prices = ["No data available"]
            recommendations = {"No data available": "No data available"}

        return render_template("recommendations.html", names=names, prices=prices, recommendations=recommendations)

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("recommendations.html", names=["Error"], prices=["Error"], recommendations={"Error": "An error occurred while fetching data"})




@trade.route("/stocksHeld")
@login_required
def stocksHeld():
    try:
        user_id = current_user.id
        if not user_id:
            flash("You must be logged in to view this page.")
            return redirect(url_for("views.login"))

        
        user = User.query.get(user_id)
        if user is None:
            flash("User not found.")
            return redirect(url_for("views.login"))

        # fetch history data
        historyy = db.session.query(History.symbol, db.func.sum(History.shares).label('shares')).filter_by(user_id=user_id).group_by(History.symbol).all()

        # prepare portfolio and calculate total value
        portfolio = {}
        grandTotal = 0.0
        errors = []
        for stock in historyy:
            if stock.shares == 0:
                continue

            #  API request
            response = requests.get(f"https://api.twelvedata.com/quote?symbol={stock.symbol}&apikey={api_key}").json()
            
            # log the full response for debugging
            print(f"API response for {stock.symbol}: {response}")

            # 'price' if available, otherwise use 'close'
            price = None
            if "price" in response:
                price = float(response["price"])
            elif "close" in response:
                price = float(response["close"])
            
            if price is not None and "name" in response:
                grandTotal += stock.shares * price
                portfolio[stock.symbol.upper()] = [stock.shares, price, stock.shares * price, response["name"]]
            else:
                # handle missing fields and log the error
                missing_fields = []
                if price is None:
                    missing_fields.append("price or close")
                if "name" not in response:
                    missing_fields.append("name")
                errors.append(f"API error for {stock.symbol}: Missing fields {', '.join(missing_fields)}. Full response: {response}")

        # display any accumulated errors
        for error in errors:
            flash(error)
        
        return render_template("stocksHeld.html", cash=user.cash, portfolio=portfolio, grandTotal=grandTotal + user.cash)
    except SQLAlchemyError as e:
        flash(f"Database connection error: {e}")
        return redirect(url_for("trade.stocksHeld"))
    except Exception as e:
        flash(f"Unexpected error: {e}")
        return redirect(url_for("trade.stocksHeld"))



def errorhandler(e):
    flash(f"{e.name}: {e.code}")

for code in default_exceptions:
    trade.errorhandler(code)(errorhandler)
