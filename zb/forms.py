from flask import Blueprint, render_template, abort

forms_bp = Blueprint('forms', __name__, template_folder='templates/pages/forms')

@forms_bp.route("/advanced")
def advanced():
    return render_template('advanced.html')       

@forms_bp.route("/editors")
def editors():
    return render_template('editors.html')      

@forms_bp.route("/general")
def general():
    return render_template('general.html')  