from flask import Blueprint, render_template, abort

charts_bp = Blueprint('charts', __name__, template_folder='templates/pages/charts')

@charts_bp.route('/chartjs')
def chartjs():
    return render_template('chartjs.html')

@charts_bp.route('/flot')
def flot():
    return render_template('flot.html')

@charts_bp.route('/inline')
def inline():
    return render_template('inline.html')

@charts_bp.route('/morris')
def morris():
    return render_template('morris.html')    