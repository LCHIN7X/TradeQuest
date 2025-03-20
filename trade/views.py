from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db
from user.models import User, History


trade = Blueprint("trade", __name__, template_folder="templates", static_folder="static")




@trade.route("/buy", methods=["GET", "POST"])

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