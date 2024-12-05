import datetime
from flask import Blueprint, render_template, redirect, session, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import OAuth, RecentChats, User
from . import db,oauth

auth = Blueprint('auth', __name__)

google = oauth.google

# Register the blueprint in your main application (e.g., app.py)
@auth.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_login', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            session['user_id'] = user.id
            return redirect(url_for('views.chat_page'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup'))

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.signup'))

        # Create a new user
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('views.chat_page'))

    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/login/google/authorized')
def google_login():

    try:
        print("Request Args:", request.args) 
        token = google.authorize_access_token()
        print("Token:",token)
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()
        if user_info:
            email = user_info.get("email")
            name = user_info.get("name")
            profile_picture = user_info.get("picture")
            provider_id = user_info.get("id")
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User.query.filter_by(provider="google", provider_id=provider_id).first()

            if not user:
                # If no user found, create a new user
                user = User(
                    email=email,
                    name=name,
                    profile_picture=profile_picture,
                    provider="google",
                    provider_id=provider_id
                )
                db.session.add(user)
                db.session.commit()  # Commit the new user to the database

            # Log the user in
            login_user(user)

            # Create or update the OAuth token association
            oauth = OAuth.query.filter_by(provider="google", provider_user_id=provider_id).first()
            if not oauth:
                oauth = OAuth(
                    provider="google",
                    provider_user_id=provider_id,
                    token= token,
                    user_id=user.id
                )
                db.session.add(oauth)
                db.session.commit()
            new_recent = RecentChats(user_id=user.id, recent_time=datetime.utcnow(), title="New Chat") 
            db.session.add(new_recent)
            db.session.commit()
            session['user_id'] = user.id

            flash("Logged in successfully!")
            return redirect(url_for('auth.handle_google_login',recent_id=new_recent.recent_id))
    except Exception as e: # Print detailed exception 
        print(f"An error occurred: {e}") 
        flash("An error occurred during Google login.","error")
        return redirect(url_for("auth.login"))

@auth.route('/handle_google_login')
def handle_google_login():
    recent_id=request.args.get('recent_id')
    return render_template('handle_google_login.html',recent_id=recent_id)
