from flask import Blueprint, render_template, abort

layout_bp = Blueprint('layout', __name__, template_folder='templates/pages/layout')

@layout_bp.route("/boxed")
def boxed():
    return render_template('boxed.html')       

@layout_bp.route("/collapsed_sidebar")
def collapsed_sidebar():
    return render_template('collapsed-sidebar.html')      

@layout_bp.route("/fixed")
def fixed():
    return render_template('fixed.html')  

@layout_bp.route("/top_nav")
def top_nav():
    return render_template('top-nav.html')      