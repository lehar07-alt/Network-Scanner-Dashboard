from flask import Blueprint, render_template

# 'main' is this blueprint's internal name
# __name__ helps Flask locate resources relative to this file
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing/home route — just renders a simple page for now."""
    return render_template('index.html', project_name="Network Scanner Dashboard")

@main_bp.route('/about')
def about():
    return "<h1>About</h1><p>This project scans local networks and displays results on a dashboard.</p>"