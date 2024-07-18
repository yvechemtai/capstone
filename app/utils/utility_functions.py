import calendar
from flask import request, flash, current_app
from flask_login import current_user
from wtforms.validators import  ValidationError
from datetime import datetime, timedelta
from operator import attrgetter
from app.forms.forms import *
from app.database.models import *
from app import db, login_manager
from app.routes.routes import routes


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@routes.context_processor
def inject_now():
    return {'now': datetime.utcnow() + timedelta(hours=3)}


# Functions
def validate_password(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long.')

def get_customer_names():
    if current_user.membership:
        customers = User.query.filter(User.id != '1', User.verification_status.is_(True)).all()
    elif current_user.verification_status:
        customers = [current_user]
    else:
        customers = []
    all_names = [f"{customer.first_name} {customer.last_name}" for customer in customers]
    names = sorted(all_names)  # Alphabetically sort names
    return names

def get_guarantor_names():
    guarantors = User.query.filter(User.id != '1', User.membership.is_(True)).all()
    all_names = [f"{guarantor.first_name} {guarantor.last_name}" for guarantor in guarantors]
    names = sorted(all_names)  # Alphabetically sort names
    return names

def get_loan_types():
    all_loan_types = System.query.filter(System.loan_types.isnot(None)).all()

    loan_types = sorted(all_loan_types, key=attrgetter('loan_types'))

    names = [loan_type.loan_types for loan_type in loan_types]
    return names

def get_loan_durations():
    loan_durations = System.query.filter(System.loan_durations.isnot(None)).all()
    all_durations = [loan_duration.loan_durations for loan_duration in loan_durations]
    durations = sorted(all_durations, key=lambda x: int(x))  # Sort durations as integers
    return durations

def get_system_id_by_loan_type(loan_type):
    system = System.query.filter_by(loan_types=loan_type).first()
    return system.id if system else None

def create_new_loan(
        customer_name,
        guarantor,
        loan_type,
        loan_duration,
        principal,
        service_cost,
        system_id):
    new_loan = Loan(
        customer_name=customer_name,
        guarantor_name=guarantor.first_name + " " + guarantor.last_name,
        loan_type=loan_type,
        loan_duration=loan_duration,
        principal=principal,
        service_cost=service_cost,
        system_id=system_id,
        guarantor_id=guarantor.id,
        timestamp=datetime.utcnow() + timedelta(hours=3),
        payment_timestamp=datetime.utcnow() + timedelta(days=int(loan_duration))
    )

    # Calculate outstanding balance
    new_loan.repayment = calculate_repayment(
        principal=principal,
        interest_rate=new_loan.interest_rate,
        fines=new_loan.fines if new_loan.fines else 0
    )

    # Calculate and update profit
    new_loan.profit = calculate_profit(
        repayment=new_loan.repayment,
        principal=principal
    )

    db.session.add(new_loan)
    db.session.commit()

def calculate_repayment(principal, interest_rate, fines):
    if interest_rate is not None:
        interest_amount = principal * (interest_rate / 100)
    else:
        interest_amount = 0

    repayment = principal + interest_amount + fines
    return repayment

def calculate_profit(repayment, principal):
    profit = repayment - principal
    return profit

def get_or_create_contribution_form():
    contribution_form = ContributionForm(request.form)
    contribution_form.members_name.choices = [(name, name) for name in get_guarantor_names()]
    return contribution_form

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def allowed_docs_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_DOCS_EXTENSIONS']

def handle_update_roles(role_ids, updated_roles):
    for role_id, updated_role in zip(role_ids, updated_roles):
        role = Role.query.get(role_id)
        if role:
            role.name = updated_role
    db.session.commit()
    flash('Roles updated successfully.', 'success')

def handle_add_new_roles(new_roles):
    for new_role in new_roles:
        if new_role:
            role = Role(name=new_role)
            db.session.add(role)
    db.session.commit()
    flash('New roles added successfully.', 'success')

def handle_delete_roles(roles_to_delete):
    for role_id in roles_to_delete:
        role = Role.query.get(role_id)
        if role:
            db.session.delete(role)
    db.session.commit()
    flash('Roles deleted successfully.', 'success')

def handle_update_loan_types(loan_type_ids, updated_loan_types):
    system = System.query.get(1)
    if system:
        # Update the loan types based on the IDs
        for loan_type_id, updated_loan_type in zip(loan_type_ids, updated_loan_types):
            loan_type = System.query.filter_by(id=int(loan_type_id)).first()
            if loan_type:
                loan_type.loan_types = updated_loan_type
        db.session.commit()
        flash('Loan types updated successfully.', 'success')

def handle_add_loan_types(new_loan_types):
    for new_loan_type in new_loan_types:
        if new_loan_type:
            loan_types = System(loan_types=new_loan_type)
            db.session.add(loan_types)
    db.session.commit()
    flash('New loan types added successfully.', 'success')

def handle_delete_loan_types(loan_types_to_delete):
    for loan_type in loan_types_to_delete:
        loan_types = System.query.get(loan_type)
        if loan_types:
            db.session.delete(loan_types)
    db.session.commit()
    flash('Loan types deleted successfully.', 'success')

def handle_update_loan_durations(loan_duration_ids, updated_loan_durations):
    system = System.query.get(1)
    if system:
        # Update the loan durations based on the IDs
        for loan_duration_id, updated_loan_duration in zip(loan_duration_ids, updated_loan_durations):
            loan_duration = System.query.filter_by(id=int(loan_duration_id)).first()
            if loan_duration:
                loan_duration.loan_durations = int(updated_loan_duration)
        db.session.commit()
        flash('Loan durations updated successfully.', 'success')

def handle_add_loan_durations(new_loan_durations):
    for new_loan_duration in new_loan_durations:
        if new_loan_duration:
            loan_durations = System(loan_durations=new_loan_duration)
            db.session.add(loan_durations)
    db.session.commit()
    flash('New loan durations added successfully.', 'success')

def handle_delete_loan_durations(loan_durations_to_delete):
    for loan_duration in loan_durations_to_delete:
        loan_durations = System.query.get(loan_duration)
        if loan_durations:
            db.session.delete(loan_durations)
    db.session.commit()
    flash('Loan durations deleted successfully.', 'success')

def calculate_users_acquisition_per_month(db, extract, func, User, calendar):
    users_acquisition_per_month = (
        db.session.query(
            extract('year', User.timestamp).label('year'),
            extract('month', User.timestamp).label('month'),
            func.count(User.id).label('count')
        )
        .filter(User.id != 1)
        .group_by('year', 'month')
        .order_by('year', 'month')
        .all()
    )

    customer_acquisition_data = {
        'labels': [f"{calendar.month_name[entry.month]} {entry.year}" for entry in users_acquisition_per_month],
        'data': [entry.count for entry in users_acquisition_per_month]
    }

    return customer_acquisition_data

def calculate_loans_processed_per_month(db, extract, func, Loan):
    loans_processed_per_month = (
        db.session.query(
            extract('year', Loan.timestamp).label('year'),
            extract('month', Loan.timestamp).label('month'),
            func.sum(Loan.principal).label('total_principal')
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
        .all()
    )

    loans_processed_data = {
        'labels': [f"{calendar.month_name[entry.month]} {entry.year}" for entry in loans_processed_per_month],
        'data': [entry.total_principal or 0 for entry in loans_processed_per_month]
    }

    return loans_processed_data

def retrieve_loan_status_data(Loan, func):
    loan_status_data = {
        'labels': ['Pending', 'Approved', 'Fully Issued', 'Partially Issued', 'Partially Paid', 'Fully Paid'],
        'data': [
            Loan.query.filter_by(loan_status='pending').with_entities(func.sum(Loan.principal)).scalar() or 0,
            Loan.query.filter_by(loan_status='approved').with_entities(func.sum(Loan.principal)).scalar() or 0,
            Loan.query.filter_by(loan_status='fully_issued').with_entities(func.sum(Loan.principal)).scalar() or 0,
            Loan.query.filter_by(loan_status='partially_issued').with_entities(func.sum(Loan.principal)).scalar() or 0,
            Loan.query.filter_by(loan_status='partially_paid').with_entities(func.sum(Loan.principal)).scalar() or 0,
            Loan.query.filter_by(loan_status='fully_paid').with_entities(func.sum(Loan.principal)).scalar() or 0,
        ],
        'backgroundColor': ['#FFC107', '#4CAF50', '#FF9800', '#2196F3', '#FF5722', '#8BC34A'],
    }

    return loan_status_data

def retrieve_contributions_per_user(db, func, User):
    contributions_per_user = (
        db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            func.sum(Contribution.amount).label('total_contribution')
        )
        .join(Contribution)
        .group_by(User.id, User.first_name, User.last_name)
        .all()
    )

    contributions_data = {
        'labels': [f"{entry.first_name} {entry.last_name}" for entry in contributions_per_user],
        'data': [entry.total_contribution or 0 for entry in contributions_per_user]
    }

    return contributions_data
