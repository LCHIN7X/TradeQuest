from flask import Blueprint, render_template
from flask_login import login_required

vip = Blueprint("vip", __name__, template_folder="templates", static_folder="static")

@vip.route("/layoutt")
@login_required
def lesson_page1():
    return render_template("layoutt.html")