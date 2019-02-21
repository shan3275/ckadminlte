from flask import Blueprint, render_template, abort

examples_bp = Blueprint('examples', __name__, template_folder='templates/pages/examples')

@examples_bp.route("/c404")
def c404():
    return render_template('404.html')

@examples_bp.route("/c500")
def c500():
    return render_template('500.html')   

@examples_bp.route("/blank")
def blank():
    return render_template('blank.html')                      

@examples_bp.route("/invoice_print")
def invoice_print():
    return render_template('invoice-print.html')  

@examples_bp.route("/invoice")
def invoice():
    return render_template('invoice.html')   

@examples_bp.route("/lockscreen")
def lockscreen():
    return render_template('lockscreen.html')    

@examples_bp.route("/pace")
def pace():
    return render_template('pace.html')  

@examples_bp.route("/profile")
def profile():
    return render_template('profile.html')  

@examples_bp.route("/regisger")
def regisger():
    return render_template('register.html')   