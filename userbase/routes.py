import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from userbase import user_base, db, bcrypt
from userbase.forms import RegistrationForm, LoginForm, UpdateAccountForm
from userbase.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        'author': 'Bethanie Williams',
        'title': "Sandia National Lab",
        'content': 'First Week of Internship',
        'date_posted': 'June 1, 2021'
    },
    {
            'author': 'Savannah Fallis',
            'title': "Athletic Training",
            'content': 'Second Week of Internship',
            'date_posted': 'June 12, 2021'
        },
]


@user_base.route("/")
@user_base.route("/home")
def home():
    return render_template('home.html', posts=posts)


@user_base.route("/profile")  # this is how we create routes in flask
def user_profile():
    return render_template('user_profile.html')   # returns the html template of that page


@user_base.route("/register", methods=['GET', 'POST'])
def register_form():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, department=form.department.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login.', 'success')  # flashes a message and uses bootstrap success
        return redirect(url_for('login_form'))     # redirects to home page by redirecting to home function
    return render_template('register.html', title='Register', form=form)


@user_base.route("/login", methods=['GET', 'POST'])
def login_form():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): #comparing database password vs password written in form
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Attempt Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)


@user_base.route("/logout")  # this is how we create routes in flask
def logout_form():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext  # filename of picture
    picture_path = os.path.join(user_base.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    # form_picture.save(picture_path)
    return picture_fn


@user_base.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.department = form.department.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.department.data = current_user.department
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)