# app/routes/loan_routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, timedelta, timezone
from app import db
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import loans

# Loan Management Routes
@loans.route('/add_loan', methods=['GET', 'POST'])
@login_required
def add_loan():
    form = LoanForm()

    # Populate choices for dropdowns
    form.customer_name.choices = [(name, name) for name in get_customer_names()]
    form.guarantor_name.choices = [(name, name) for name in get_guarantor_names()]
    form.loan_type.choices = [(name, name) for name in get_loan_types()]
    form.loan_duration.choices = [(duration, duration) for duration in get_loan_durations()]

    if form.validate_on_submit():
        customer_name = form.customer_name.data
        guarantor_name = form.guarantor_name.data
        loan_type = form.loan_type.data
        loan_duration = form.loan_duration.data
        principal = form.principal.data
        service_cost = form.service_cost.data  or 0.0

        guarantor_first_name, guarantor_last_name = guarantor_name.split(" ", 1)
        guarantor = User.query.filter_by(first_name=guarantor_first_name, last_name=guarantor_last_name).first()

        if guarantor:
            system_id = get_system_id_by_loan_type(loan_type)

            try:
                create_new_loan(customer_name, guarantor, loan_type, loan_duration, principal, service_cost, system_id)
                flash('Loan added successfully.', 'success')
                return redirect(url_for('home.dashboard'))
            except Exception as e:
                flash(f'Error adding loan: {str(e)}', 'danger')
        else:
            flash('Guarantor not found.', 'warning')

    return render_template('common/add_loan.html', form=form)

@loans.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def edit_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    form = EditLoanForm(obj=loan)

    form.customer_name.choices = get_customer_names()
    form.guarantor_name.choices = get_guarantor_names()
    form.loan_type.choices = get_loan_types()
    form.loan_duration.choices = get_loan_durations()

    if form.validate_on_submit():
        form.populate_obj(loan)

        if form.payment_timestamp.data:
            loan.payment_timestamp = form.payment_timestamp.data
        else:
            loan.loan_duration = form.loan_duration.data
            loan.payment_timestamp = datetime.utcnow() + timedelta(days=int(form.loan_duration.data))

        if form.issuance_timestamp.data:
            loan.issuance_timestamp = form.issuance_timestamp.data
        else:
            loan.issuance_timestamp = datetime.utcnow()

        if form.approval_timestamp.data:
            loan.approval_timestamp = form.approval_timestamp.data
        else:
            loan.approval_timestamp = datetime.utcnow()

        db.session.commit()

        flash('Loan details have been updated!', 'success')
        return redirect(url_for('home.dashboard'))

    return render_template('common/edit_loan.html', title='Edit Loan', form=form, loan=loan)

@loans.route('/approve_loan/<int:loan_id>')
@login_required
def approve_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'approved'
        loan.approval_timestamp = datetime.now(timezone.utc) + timedelta(hours=3)
        db.session.commit()
        flash('Loan approved successfully.', 'success')
    return redirect(url_for('home.dashboard'))

@loans.route('/decline_loan/<int:loan_id>')
@login_required
def decline_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'declined'
        loan.approval_timestamp = datetime.now(timezone.utc) + timedelta(hours=3)
        db.session.commit()
        flash('Loan declined successfully.', 'danger')
    return redirect(url_for('home.dashboard'))

@loans.route('/issue_fully/<int:loan_id>')
@login_required
def issue_fully(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'fully_issued'
        loan.issuance_timestamp = datetime.now(timezone.utc) + timedelta(hours=3)
        db.session.commit()
        flash('Loan fully issued successfully.', 'success')
    return redirect(url_for('home.dashboard'))

@loans.route('/issue_partially/<int:loan_id>')
@login_required
def issue_partially(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'partially_issued'
        db.session.commit()
        flash('Loan partially issued successfully.', 'success')
    return redirect(url_for('home.dashboard'))

@loans.route('/paid_partially/<int:loan_id>')
@login_required
def paid_partially(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'partially_paid'
        db.session.commit()
        flash('Loan partially paid successfully.', 'success')
    return redirect(url_for('home.dashboard'))

@loans.route('/paid_fully/<int:loan_id>')
@login_required
def paid_fully(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.loan_status = 'fully_paid'
        loan.payment_timestamp = datetime.now(timezone.utc) + timedelta(hours=3)
        db.session.commit()
        flash('Loan fully paid successfully.', 'success')
    return redirect(url_for('home.dashboard'))

@loans.route('/delete_loan/<int:loan_id>')
@login_required
def delete_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        db.session.delete(loan)
        db.session.commit()
        flash('Loan deleted successfully.', 'danger')
    return redirect(url_for('home.dashboard'))
