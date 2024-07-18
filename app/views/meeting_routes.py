import os
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from ..forms.forms import *
from ..database.models import *
from ..utils.utility_functions import *
from ..routes.routes import meetings

# Record/Meeting Management Routes
@meetings.route('/submit_record', methods=['POST'])
@login_required
def submit_record():
    records_form = RecordsForm(request.form)

    if records_form.validate_on_submit():

        # Create Records instance
        new_record = Records(
            title=records_form.title.data,
            category=records_form.category.data,
            tags=records_form.tags.data,
            description=records_form.description.data,
            invitees=records_form.invitees.data,
            meeting_date=records_form.meeting_date.data,
            location=records_form.location.data,
            location_address=records_form.location_address.data,
            user=current_user
        )

        # Save uploaded document if provided
        if 'document' in request.files:
            file = request.files['document']
            if file:
                if allowed_docs_file(file.filename):
                    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                    rename_filename = f"{current_time}.{file.filename.rsplit('.', 1)[1].lower()}"
                    renamed_filename = secure_filename(rename_filename)
                    filepath = os.path.join(current_app.config['DOCS_FOLDER'], renamed_filename)
                    file.save(filepath)
                    new_record.document_path = renamed_filename
                else:
                    flash('Invalid document format. Allowed formats: PDF, DOCX', 'danger')
                    return redirect(url_for('home.dashboard'))

        # Save the record to the database
        db.session.add(new_record)
        db.session.commit()

        # Flash formatted message based on the category
        category_flash_message = {
            'archives': 'Archival submitted successfully!',
            'meetings': 'Meeting scheduled successfully!'
        }
        flash(category_flash_message.get(new_record.category, 'Record submitted successfully!'), 'success')

        return redirect(url_for('home.dashboard'))

    # Provide more specific error messages
    flash_errors = "\n".join([f"{field.label.text}: {', '.join(errors)}" for field, errors in records_form.errors.items()])
    flash(f'Failed to submit meeting. Please check your input:\n{flash_errors}', 'danger')
    return render_template('errors/error.html', records_form=records_form)
