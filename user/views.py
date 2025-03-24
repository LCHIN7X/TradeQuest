from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from models import db
from .forms import Register
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import os

views = Blueprint("views", __name__, template_folder="templates", static_folder="static")

def file_is_valid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}

@views.route("/register", methods=["GET", "POST"])
def register():
    form = Register()
    if request.method == "POST":
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data

        normalized_email = None
        try:
            email_info = validate_email(email,check_deliverability=True)
            normalized_email = email_info.normalized 

            if len(username) < 2:
                flash("Username must be at least 2 characters long.",category="error")
        
            elif len(password) < 8:
                flash("Password must be at least 8 characters long.",category="error")
            
            elif password != password2:
                flash("Passwords do not match.",category="error")
        
            else:            
                user_in_db = User.query.filter(or_(User.email == normalized_email, User.username == username)).first()

                if user_in_db:
                    flash("Account already exists",category="error")

                else: 
                # if user record is not in database, try to create new account
                    try:
                        new_user_account = User(email=normalized_email,username=username,password=generate_password_hash(password,method="scrypt"), cash=2000.0)
                        db.session.add(new_user_account)
                        db.session.commit()
                        flash("Account successfully created!",category="success")
                        return redirect(url_for("views.login"))

                
                    except IntegrityError:
                        db.session.rollback()
                        flash("Username already taken, please enter a new username.",category="error")

        except EmailNotValidError as e:
            flash("Invalid email address.",category="error")


    # if method is GET, render page
    return render_template('register.html',current_page="create_account",current_user=current_user)
    

@views.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password') 

        #  check if credentials entered exist in User table
        user_in_db = User.query.filter_by(email=email).first()
        
        if user_in_db:
            # if user account exists, first check if password is correct
            if check_password_hash(user_in_db.password, password):
                flash(f"Hello {user_in_db.username}, You Are Now Logged In!",category='success')
                login_user(user_in_db, remember=True)

                
                return render_template('home.html') #change after got home.html
            
            # if password is incorrect, flash error message
            else:
                flash("Incorrect password, please try again.",category='error')

        else:
            flash("User account does not exist, please create an account.",category="error")

    # if method is GET, render page
    return render_template('login.html',current_page="login",current_user=current_user)

@views.route("/logout",methods=["GET"])
@login_required
def logout():
    logout_user()

    flash("Logged Out Successfully.",category="success")
    return redirect(url_for('views.login',logout=True))



# define route for changing password
@views.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if old_password == new_password:
            flash("Old Password and New Password Are The Same.", category='error')

        elif new_password != confirm_new_password:
            flash("New Passwords Don't Match.",category="error")

        elif check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password,method='scrypt')
            db.session.commit()
            flash('Password successfully changed.',category='success')

        else:
            db.session.rollback()
            flash("Incorrect old password.",category='error')


    return render_template('change_password.html',current_page='change_password')

@views.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic.filename != "":
                if not file_is_valid(profile_pic.filename):
                    flash("Invalid File Type: Only .jpg, .jpeg, and .png files are allowed.", category="error")
                else:
                    cwd = os.getcwd()
                    upload_folder = os.path.join(cwd, "static/assets/images/user_uploads")
                    os.makedirs(upload_folder, exist_ok=True)

                    previous_profile_pic = current_user.profile_pic
                    if previous_profile_pic and previous_profile_pic != "default_pfp.png":
                        old_pic_path = os.path.join(upload_folder, previous_profile_pic)
                        if os.path.exists(old_pic_path):
                            os.remove(old_pic_path)

                    filename = secure_filename(profile_pic.filename)
                    img_path = os.path.join(upload_folder, filename)

                    img_size = (100, 100)
                    img = Image.open(profile_pic)
                    img.thumbnail(img_size)
                    img.save(img_path)

                    current_user.profile_pic = filename
                    db.session.commit()
                    flash("Profile picture successfully updated!", category='success')

        # Handle bio update
        new_bio = request.form.get('bio')
        if new_bio is not None and new_bio.strip() != current_user.bio:
            current_user.bio = new_bio.strip() if new_bio.strip() else None
            db.session.commit()
            flash("Bio successfully updated!", category='success')

        # Handle username change
        new_username = request.form.get("username").strip()
        if new_username and new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash("Oops! Username already taken. Please enter a different username.", category="error")
            else:
                current_user.username = new_username
                db.session.commit()
                flash("Username successfully changed!", category='success')

        # Handle VIP status toggle
        if "toggle_vip" in request.form:
            current_user.is_vip = not current_user.is_vip
            db.session.commit()
            flash("VIP status updated!", category='success')

    return render_template('profile.html',
                           current_page="profile",
                           current_profile_pic=current_user.profile_pic,
                           current_bio=current_user.bio,
                           current_username=current_user.username,
                           is_vip=current_user.is_vip)

