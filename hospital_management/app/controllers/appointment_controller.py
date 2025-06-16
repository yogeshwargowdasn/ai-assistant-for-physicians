from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.appointment import Appointment
from app.models.user import User
from app import db
from datetime import datetime

appointment_bp = Blueprint('appointment', __name__)


@appointment_bp.route('/create_appointment', methods=['GET', 'POST'])
@login_required
def create_appointment():
    doctors = User.query.filter_by(role='doctor').all()
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        reason = request.form['reason']
        appointment_date_str = request.form['appointment_date']
        time_str = request.form['appointment_time']
        appointment_datetime = datetime.strptime(f"{appointment_date_str} {time_str}", '%Y-%m-%d %H:%M')
        # use appointment_datetime instead of just appointment_date


        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            reason=reason,
            date=appointment_datetime
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment created!", "success")
        return redirect(url_for('auth.dashboard'))
    return render_template('create_appointment.html', doctors=doctors)

@appointment_bp.route('/view_appointments')
@login_required
def view_appointments():
    if current_user.role == 'admin':
        appointments = Appointment.query.all()
    elif current_user.role == 'doctor':
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    elif current_user.role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    else:
        appointments = []

    return render_template('view_appointments.html', appointments=appointments)



@appointment_bp.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Only allow doctor or admin to edit
    if current_user.role not in ['admin', 'doctor']:
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        appointment.reason = request.form['reason']
        db.session.commit()
        flash("Appointment updated successfully!", "success")
        return redirect(url_for('appointment.view_appointments'))

    return render_template('edit_appointment.html', appointment=appointment)


@appointment_bp.route('/delete_appointment/<int:appointment_id>', methods=['GET'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    print("DELETE appointment POST received")


    # Only allow doctor or admin to delete
    if current_user.role not in ['admin', 'doctor']:
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.dashboard'))

    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted successfully!", "success")
    return redirect(url_for('appointment.view_appointments'))
