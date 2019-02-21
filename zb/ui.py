from flask import Blueprint, render_template, abort

ui_bp = Blueprint('ui', __name__, template_folder='templates/pages/ui')

@ui_bp.route("/buttons")
def buttons():
    return render_template('buttons.html')       

@ui_bp.route("/general")
def general():
    return render_template('general.html')      

@ui_bp.route("/icons")
def icons():
    return render_template('icons.html')  

@ui_bp.route("/modals")
def modals():
    return render_template('modals.html')           

@ui_bp.route("/sliders")
def sliders():
    return render_template('sliders.html')        

@ui_bp.route("/timeline")
def timeline():
    return render_template('timeline.html')    