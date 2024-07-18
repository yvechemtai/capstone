from flask import request, redirect, url_for, flash
from flask_login import login_required
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import settings


# Define SettingsForm
@settings.route('/system_settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    roles = Role.query.all()
    loan_types = System.query.with_entities(System.loan_types).first()
    loan_durations = System.query.with_entities(System.loan_durations).first()

    if request.method == 'POST':
        if 'update_roles' in request.form:
            handle_update_roles(request.form.getlist('selectRoleToUpdate'), request.form.getlist('updatedRoleName'))

        elif 'add_new_roles' in request.form:
            handle_add_new_roles(request.form.getlist('newRoleName'))

        elif 'delete_roles' in request.form:
            handle_delete_roles(request.form.getlist('selectRoleToDelete'))

        elif 'update_loan_type' in request.form:
            handle_update_loan_types(request.form.getlist('selectLoanTypeToUpdate'), request.form.getlist('updatedLoanTypeName'))

        elif 'add_loan_type' in request.form:
            handle_add_loan_types(request.form.getlist('newLoanTypeName'))

        elif 'delete_loan_type' in request.form:
            handle_delete_loan_types(request.form.getlist('selectLoanTypeToDelete'))

        elif 'update_loan_duration' in request.form:
            handle_update_loan_durations(request.form.getlist('selectLoanDurationToUpdate'), request.form.getlist('updatedLoanDurationName'))

        elif 'add_loan_durition' in request.form:
            handle_add_loan_durations(request.form.getlist('newLoanDurationName'))

        elif 'dalete_loan_durition' in request.form:
            handle_delete_loan_durations(request.form.getlist('selectLoanDurationToDelete'))
    else:
        flash('The changes were not updated.', 'danger')

    return redirect(url_for('home.dashboard', roles=roles, loan_types=loan_types, loan_durations=loan_durations))
