# Import necessary modules and classes

# app/setup.py
from datetime import datetime
from app import db
from ..database.models import *

admin_user_and_roles_data = {
    'first_name': 'system',
    'last_name': 'admin',
    'email': 'admin@mail.com',
    'mobile_number': '0000000000',
    'id_number': 'unique_id',
    'education_level': 'admin',
    'occupation': 'administrator',
    'dob': datetime.strptime('2023-11-01', '%Y-%m-%d'),
    'membership': True,
    'verification_status': True,
    'password': '$2b$12$4ZCociSjbcQPxJ26nbn6tu3yYZydKntC9wz4JEZIJWIzCYbHMO2W.',  # Apogen@2023
    'role': 'system',
    'role_names': ['system', 'admin', 'member', 'standard'],
    'loan_types': ['personal loan', 'mortgage loan', 'business loan'],
    'loan_durations': ['30', '60', '90', '180', '365']
}


def add_admin_role():
    roles = Role.query.filter(Role.name.in_(admin_user_and_roles_data['role_names'])).all()
    if not roles:
        for role_name in admin_user_and_roles_data['role_names']:
            add_roles = Role(name=role_name)
            db.session.add(add_roles)
        db.session.commit()

def add_admin_user():
    check_admin_user = User.query.filter_by(email=admin_user_and_roles_data['email']).first()
    if not check_admin_user:
        admin_role = Role.query.filter_by(name=admin_user_and_roles_data['role']).first()
        if admin_role:
            admin_user = User(
                first_name=admin_user_and_roles_data['first_name'],
                last_name=admin_user_and_roles_data['last_name'],
                email=admin_user_and_roles_data['email'],
                mobile_number=admin_user_and_roles_data['mobile_number'],
                id_number=admin_user_and_roles_data['id_number'],
                education_level=admin_user_and_roles_data['education_level'],
                occupation=admin_user_and_roles_data['occupation'],
                dob=admin_user_and_roles_data['dob'],
                membership=admin_user_and_roles_data['membership'],
                verification_status=admin_user_and_roles_data['verification_status'],
                password=admin_user_and_roles_data['password'],
                role=admin_role
            )

            db.session.add(admin_user)
            db.session.commit()

def verify_admin_user():
    check_admin_user = User.query.filter_by(email=admin_user_and_roles_data['email']).first()
    if check_admin_user:
        admin_role = Role.query.filter_by(name=admin_user_and_roles_data['role']).first()
        if admin_role:
            verified = Verification.query.filter_by(user_id=check_admin_user.id, role_id=admin_role.id).first()
            if not verified:
                verify = Verification(user_id=check_admin_user.id, role_id=admin_role.id, verified=True)
                db.session.add(verify)
                db.session.commit()

def add_loan_types():
    check_not_null_loan_types = System.query.filter(System.loan_types != '').all()
    if not check_not_null_loan_types:
        for loan_type in admin_user_and_roles_data['loan_types']:
            add_loan_type = System(loan_types=loan_type)
            db.session.add(add_loan_type)
        db.session.commit()

def add_loan_durations():
    check_not_null_loan_durations = System.query.filter(System.loan_durations != '').all()
    if not check_not_null_loan_durations:
        for loan_duration in admin_user_and_roles_data['loan_durations']:
            add_loan_duration = System(loan_durations=loan_duration)
            db.session.add(add_loan_duration)
        db.session.commit()
