import selenium
from flask import Blueprint, render_template, request, flash
from . import hanimebot
import requests

views = Blueprint('views', __name__, template_folder='templates')


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        inpt = request.form.get("field")
        try:
            header, response = hanimebot.main(inpt)
        except requests.exceptions.RequestException:
            header, response = None, None
        if header is None and response is None:
            return render_template('home.html', warning=True)
        return render_template('home.html', response=response, header=header)
    return render_template('home.html')


@views.route('/about')
def about():
    return render_template('about.html')
