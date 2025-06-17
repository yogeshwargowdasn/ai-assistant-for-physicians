from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.report import MedicalReport
from docx import Document
from math import ceil

report_bp = Blueprint('report', __name__)  # ✅ Fix: __name__ instead of _name_

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

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

            # Optional: prevent overwriting existing file
            if os.path.exists(filepath):
                flash("A file with this name already exists.", "danger")
                return redirect(request.url)

            file.save(filepath)

            new_report = MedicalReport(user_id=current_user.id, filename=filename)
            db.session.add(new_report)
            db.session.commit()

            flash("Report uploaded successfully!", "success")
            return redirect(url_for('report.view_reports'))
        else:
            flash("Invalid file format", "danger")
            return redirect(request.url)

    return render_template('upload_report.html')


# ------------------------
# View Reports with Pagination + Search
# ------------------------
@report_bp.route('/view_reports')
@login_required
def view_reports():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 5

    if current_user.role == 'admin':
        query = MedicalReport.query
    else:
        query = MedicalReport.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(MedicalReport.filename.ilike(f"%{search_query}%"))

    total_reports = query.count()
    reports = query.order_by(MedicalReport.upload_date.desc()) \
                   .offset((page - 1) * per_page) \
                   .limit(per_page).all()

    class Pagination:
        def __init__(self, page, per_page, total):  # ✅ Fix: correct __init__
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = ceil(total / per_page)

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1

        @property
        def next_num(self):
            return self.page + 1

        def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (num >= self.page - left_current and num <= self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    pagination = Pagination(page, per_page, total_reports)

    return render_template('view_reports.html', reports=reports, search_query=search_query, pagination=pagination)


# ------------------------
# Delete Report
# ------------------------
@report_bp.route('/delete_report/<int:report_id>')
@login_required
def delete_report(report_id):
    report = MedicalReport.query.get_or_404(report_id)

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


# ------------------------
# View Report (inline or DOCX render)
# ------------------------
from flask import render_template_string

@report_bp.route('/view_report/<filename>')
@login_required
def view_report(filename):
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # Authorization check
    if current_user.role != 'admin':
        report = MedicalReport.query.filter_by(filename=filename, user_id=current_user.id).first()
        if not report:
            flash("You are not authorized to view this report.", "danger")
            return redirect(url_for('report.view_reports'))

    if not os.path.exists(file_path):
        flash("Report file not found.", "danger")
        return redirect(url_for('report.view_reports'))

    if file_ext == 'docx':
        try:
            doc = Document(file_path)
            html_content = ''.join(f'<p>{para.text}</p>' for para in doc.paragraphs if para.text.strip())
            return render_template_string("""
                <!DOCTYPE html>
                <html><body>{{ content|safe }}</body></html>
            """, content=html_content)
        except Exception as e:
            return f"<p class='text-danger'>Could not render DOCX: {str(e)}</p>"

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        mimetype='application/pdf' if file_ext == 'pdf' else None,
        as_attachment=False
    )
