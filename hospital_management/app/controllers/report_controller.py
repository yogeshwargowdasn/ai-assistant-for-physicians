from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.report import MedicalReport  # Ensure this matches your model name

report_bp = Blueprint('report', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# Upload Report
# ------------------------

@report_bp.route('/upload_report', methods=['GET', 'POST'])
@login_required
def upload_report():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash("No file selected", "danger")
            return redirect(request.url)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_report = MedicalReport(user_id=current_user.id, filename=filename)
            db.session.add(new_report)
            db.session.commit()

            flash("Report uploaded successfully!", "success")
            return redirect(url_for('report.view_reports'))  # redirect to view reports
        else:
            flash("Invalid file format", "danger")
            return redirect(request.url)

    return render_template('upload_report.html')


# ------------------------
# View Reports
# ------------------------

@report_bp.route('/view_reports')
@login_required
def view_reports():
    if current_user.role == 'admin':
        reports = MedicalReport.query.all()
    else:
        reports = MedicalReport.query.filter_by(user_id=current_user.id).all()

    return render_template('view_reports.html', reports=reports)


# ------------------------
# Delete Report
# ------------------------

@report_bp.route('/delete_report/<int:report_id>')
@login_required
def delete_report(report_id):
    report = MedicalReport.query.get_or_404(report_id)

    # Only allow deleting your own reports, unless admin
    if report.user_id != current_user.id and current_user.role != 'admin':
        flash("You are not authorized to delete this report.", "danger")
        return redirect(url_for('report.view_reports'))

    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], report.filename))
    except Exception as e:
        flash(f"Error deleting file: {e}", "danger")

    db.session.delete(report)
    db.session.commit()
    flash("Report deleted successfully.", "success")
    return redirect(url_for('report.view_reports'))


# ------------------------
# Download Report
# ------------------------

@report_bp.route('/download_report/<filename>')
@login_required
def download_report(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
