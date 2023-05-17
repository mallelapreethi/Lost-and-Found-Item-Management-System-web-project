from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import mydb  
#it has a bunch of urls defined in it
views = Blueprint('views', __name__)
@views.route('/')
def login():
    return redirect(url_for('auth.login'))

