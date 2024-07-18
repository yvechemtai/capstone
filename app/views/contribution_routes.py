from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, timedelta
from app import db
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import contribution

# Contribution Management Routes
@contribution.route('/submit_contribution', methods=['GET', 'POST'])
@login_required
def submit_contribution():
    contribution_form = get_or_create_contribution_form()

    if contribution_form.validate_on_submit():
        members_name = contribution_form.members_name.data
        amount = contribution_form.amount.data
        transaction_type = contribution_form.transaction_type.data == 'true'
        fine_amount = contribution_form.fine_amount.data or 0.0

        member_first_name, member_last_name = members_name.split(" ", 1)
        member = User.query.filter_by(first_name=member_first_name, last_name=member_last_name).first()

        if member:
            contributor_id = member.id

            new_contribution = Contribution(
                user_id=contributor_id,
                contributor=members_name,
                amount=amount,
                transaction_type=transaction_type,
                fine_amount=fine_amount,
                timestamp=datetime.utcnow() + timedelta(hours=3)
            )

            db.session.add(new_contribution)
            db.session.commit()

            flash('Transaction submitted successfully!', 'success')
        else:
            flash('Invalid Member ID. Please select a valid member.', 'danger')

        return redirect(url_for('home.dashboard'))

    return render_template('dashboard.html', form=contribution_form)

@contribution.route('/edit_contribution/<int:contribution_id>', methods=['GET', 'POST'])
@login_required
def edit_contribution(contribution_id):
    contribution = Contribution.query.get_or_404(contribution_id)
    form = EditContributionForm(request.form, obj=contribution)

    if request.method == 'POST' and form.validate():
        # Update contribution details
        contribution.amount = form.amount.data
        contribution.transaction_type = form.transaction_type.data == 'true'
        contribution.fine_amount = form.fine_amount.data or 0.0

        db.session.commit()

        flash('Transaction updated successfully!', 'success')

        return redirect(url_for('home.dashboard'))

    return render_template('common/edit_contribution.html', contribution=contribution, edit_contribution_form=form, contributor_name=contribution.contributor)
