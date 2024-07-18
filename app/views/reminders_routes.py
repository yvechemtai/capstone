from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import reminder


# Reminder Management Routes
@reminder.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    form = ReminderForm()

    if form.validate_on_submit():
        # Add new reminder
        new_reminder = Reminder(text=form.text.data, user=current_user)
        db.session.add(new_reminder)
        flash('Reminder added successfully!', 'success')
        db.session.commit()
        return redirect(url_for('home.dashboard'))

    reminders_list = current_user.reminders
    return render_template('reminders.html', form=form, reminders_list=reminders_list)

@reminder.route('/reminders/delete/<int:reminder_id>', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    if reminder.user_id != current_user.id:
        flash('Permission Denied', 'danger')
        return redirect(url_for('reminders'))

    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!', 'success')
    return redirect(url_for('home.dashboard'))

@reminder.route('/reminders/toggle/<int:reminder_id>', methods=['POST'])
@login_required
def toggle_completed(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    if reminder.user_id != current_user.id:
        flash('Permission Denied', 'danger')
        return redirect(url_for('reminders'))

    reminder.completed = not reminder.completed
    db.session.commit()
    flash('Reminder updated successfully!', 'success')
    return redirect(url_for('home.dashboard'))
