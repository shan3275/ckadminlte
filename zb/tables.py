from flask import Blueprint, render_template, abort

tables_bp = Blueprint('tables', __name__, template_folder='templates/pages/tables')

@tables_bp.route("/data")
def data():
    return render_template('data.html')       

@tables_bp.route("/simple")
def simple():
    return render_template('simple.html')      

