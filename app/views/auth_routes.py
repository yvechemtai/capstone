from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from app import db, bcrypt
from ..forms.forms import *
from ..database.models import *
from ..routes.routes import auth


# Auth Management Routes
@auth.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            if user.verification_status:
                login_user(user)
                flash('You have been logged in successfully.', 'info')
                return redirect(url_for('home.dashboard'))
            else:
                flash('Your account is not verified. Please wait for verification before logging in.', 'warning')
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form, hide_navbar=True)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Email address already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        try:
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            # Set the default role as "standard"
            default_role = Role.query.filter_by(name='standard').first()

            # Create a new user
            new_user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                mobile_number=form.mobile_number.data,
                id_number=form.id_number.data,
                education_level=form.education_level.data,
                occupation=form.occupation.data,
                dob=form.dob.data,
                password=hashed_password,
                role=default_role  # Assign the default role to the user
            )

            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Handle any exceptions that may occur during database operations
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    # If form validation fails, display error messages
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('auth/register.html', form=form, hide_navbar=True)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
