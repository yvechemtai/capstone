# app/routes/dashboard_routes.py
import calendar
from flask import request, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from operator import attrgetter
from app import db
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import home

@home.context_processor
def inject_now():
    return {'now': datetime.utcnow() + timedelta(hours=3)}

@home.route('/dashboard')
@login_required
def dashboard():
    # Retrieve user-related data
    user_id = current_user.get_id()
    user = User.query.get_or_404(user_id)
    users = User.query.all()

    # Retrieve Loans data
    loans = Loan.query.all()
    loans_approved_count = Loan.query.filter_by(loan_status='approved').count()
    total_loans_as_customer = Loan.query.filter_by(customer_name=f"{current_user.first_name} {current_user.last_name}").count()

    # Retrieve Contributions data
    contribution_form = get_or_create_contribution_form()
    contributions = Contribution.query.all()

    # Retrieve Records data
    records_form = RecordsForm()
    reminder_form = ReminderForm()
    records = Records.query.all()
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.id.desc()).all()

    # Retrieve system settings data
    setting_form = SettingsForm()
    roles = Role.query.all()
    all_loan_types = System.query.filter(System.loan_types.isnot(None)).all()
    loan_types = sorted(all_loan_types, key=attrgetter('loan_types'))
    loan_durations = System.query.filter(System.loan_durations.isnot(None)).all()

    # Retrieve Charts data
    customer_acquisition_data = calculate_users_acquisition_per_month(db, extract, func, User, calendar)
    loans_processed_data = calculate_loans_processed_per_month(db, extract, func, Loan)
    loan_status_data = retrieve_loan_status_data(Loan, func)
    contributions_per_user_data = retrieve_contributions_per_user(db, func, User)

    # Prepare chart data
    chart_data = {
        'loan_status_data': loan_status_data,
        'customer_acquisition_data': customer_acquisition_data,
        'loans_processed_data': loans_processed_data,
        'contributions_per_user_data': contributions_per_user_data
    }

    # Handle JSON request
    if request.is_json:
        return jsonify(chart_data)

    # Render the template with organized data
    return render_template(
        'home/base.html',
        user=user,
        users=users,
        loans=loans,
        loans_approved_count=loans_approved_count,
        total_loans_as_customer=total_loans_as_customer,
        contributions=contributions,
        contributions_per_user_data=contributions_per_user_data,
        roles=roles,
        loan_types=loan_types,
        loan_durations=loan_durations,
        setting_form=setting_form,
        contribution_form=contribution_form,
        records=records,
        records_form=records_form,
        reminders=reminders,
        reminder_form=reminder_form
    )
