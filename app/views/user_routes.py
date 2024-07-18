# app/routes/user_routes.py
import os
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from app import db, bcrypt
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import allowed_file
from ..routes.routes import users

@users.context_processor
def inject_now():
    return {'now': datetime.utcnow() + timedelta(hours=3)}


# User Management Routes
@users.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    roles = Role.query.all()
    form.role.choices = [(role.id, role.name) for role in roles]

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.mobile_number = form.mobile_number.data
        user.id_number = form.id_number.data
        user.education_level = form.education_level.data
        user.occupation = form.occupation.data
        user.dob = form.dob.data
        user.membership = form.membership.data
        user.verification_status = form.verification_status.data
        selected_role_id = form.role.data
        selected_role = Role.query.get(selected_role_id)
        user.role = selected_role

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                rename_filename = f"user_{user_id}.{file.filename.rsplit('.', 1)[1].lower()}"
                renamed_filename = secure_filename(rename_filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], renamed_filename)
                file.save(filepath)
                user.profile_picture = renamed_filename

        # Handle password change
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if current_password and new_password and confirm_new_password and new_password != None:
            if bcrypt.check_password_hash(user.password, current_password):
                if new_password == confirm_new_password:
                    # Hash the new password using bcrypt
                    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    user.password = hashed_new_password

                    db.session.commit()
                    flash('Password changed successfully!', 'success')
                    return redirect(url_for('home.dashboard'))
                else:
                    flash('New password and confirm new password do not match. Password not changed.', 'danger')
                    return redirect(url_for('home.dashboard'))
            else:
                flash('Current password is incorrect. Password not changed.', 'danger')
                return redirect(url_for('home.dashboard'))

        db.session.commit()
        flash('Your changes have been saved!', 'success')
        return redirect(url_for('home.dashboard'))

    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.mobile_number.data = user.mobile_number
        form.id_number.data = user.id_number
        form.education_level.data = user.education_level
        form.occupation.data = user.occupation
        form.dob.data = user.dob
        form.membership.data = user.membership
        form.verification_status.data = user.verification_status
        form.role.data = user.role.id if user.role else None

    return render_template('common/edit_user.html', title='Edit User', form=form, user=user)

@users.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            Verification.query.filter_by(user_id=user_id).delete()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User deleted successfully', 'success')
            return redirect(url_for('home.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting user: {str(e)}', 'danger')

    return render_template('common/edit_user.html', user=user_to_delete)