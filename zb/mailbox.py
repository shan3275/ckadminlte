from flask import Blueprint, render_template, abort

mailbox_bp = Blueprint('mailbox', __name__, template_folder='templates/pages/mailbox')

@mailbox_bp.route("/compose")
def compose():
    return render_template('compose.html')       

@mailbox_bp.route("/mailbox")
def mailbox():
    return render_template('mailbox.html')      

@mailbox_bp.route("/read_mail")
def read_mail():
    return render_template('read-mail.html')  
    