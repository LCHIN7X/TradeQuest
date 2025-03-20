from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from user.models import User, History
from trade.extra import lookup
from models import db

rank = Blueprint("rank", __name__, template_folder="templates", static_folder="static")

@rank.route("/ranking")
@login_required
def ranking():
    try:
        users = User.query.all()
    except SQLAlchemyError as e:
        flash(f"Can't connect to database: {e}")
        return redirect(url_for("trade.stocktrade"))

    rankings = []

    for user in users:
        try:
            history = db.session.query(History.symbol, db.func.sum(History.shares).label('shares')).filter_by(user_id=user.id).group_by(History.symbol).all()
        except SQLAlchemyError as e:
            flash(f"Can't connect to database: {e}")
            return redirect(url_for("trade.stocktrade"))

        portfolio_value = 0.0
        for stock in history:
            if stock.shares == 0:
                continue
            stock_data = lookup(stock.symbol)
            if not stock_data or "price" not in stock_data:
                flash(f"API error for {stock.symbol}: Missing fields price. Please try again later.")
                continue
            try:
                current_price = float(stock_data["price"])
                portfolio_value += stock.shares * current_price
            except ValueError:
                flash(f"API returned invalid price for {stock.symbol}")
                continue

        total_value = user.cash + portfolio_value
        rankings.append({
            "username": user.username,
            "total_value": total_value
        })

    rankings = sorted(rankings, key=lambda x: x["total_value"], reverse=True)

    return render_template("ranking.html", rankings=rankings)
