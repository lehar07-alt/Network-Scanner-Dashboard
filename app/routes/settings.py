from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app.extensions import db
from app.models.user import User

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def settings_page():
    return render_template('settings.html')


@settings_bp.route('/update-email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form.get('email', '').strip().lower()

    if not new_email or '@' not in new_email:
        flash('Please provide a valid email address.', 'danger')
        return redirect(url_for('settings.settings_page'))

    existing = User.query.filter(User.email == new_email, User.id != current_user.id).first()
    if existing:
        flash('That email is already in use by another account.', 'danger')
        return redirect(url_for('settings.settings_page'))

    current_user.email = new_email
    db.session.commit()
    flash('Email updated successfully.', 'success')
    return redirect(url_for('settings.settings_page'))


@settings_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('settings.settings_page'))

    if len(new_password) < 8:
        flash('New password must be at least 8 characters.', 'danger')
        return redirect(url_for('settings.settings_page'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('settings.settings_page'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('settings.settings_page'))


@settings_bp.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    theme = request.form.get('theme', 'light')
    email_notifications = request.form.get('email_notifications') == 'on'

    current_user.theme_preference = theme
    current_user.email_notifications = email_notifications
    db.session.commit()

    flash('Preferences updated successfully.', 'success')
    return redirect(url_for('settings.settings_page'))


@settings_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    confirm_username = request.form.get('confirm_username', '').strip()

    if confirm_username != current_user.username:
        flash('Username confirmation did not match. Account not deleted.', 'danger')
        return redirect(url_for('settings.settings_page'))

    user_to_delete = current_user._get_current_object()
    logout_user()
    db.session.delete(user_to_delete)
    db.session.commit()

    flash('Your account and all associated data have been deleted.', 'info')
    return redirect(url_for('auth.login'))