import requests
from flask import render_template, request, redirect
from app import app, db, celery
from .models import *
from .forms import MainForm
from datetime import datetime
from requests.exceptions import Timeout


@app.route('/')
def index():
    all_tasks = Tasks.query.all()
    return render_template('index.html', all_tasks=all_tasks)


@app.route('/results')
def get_results():
    results = Results.query.all()
    return render_template('results.html', results=results)


@app.route('/addsite', methods=['GET', 'POST'])
def add_site():
    form = MainForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            address = request.form.get('address')
            task = Tasks(address=address, task_status='NOT_STARTED', timestamp=datetime.now())
            db.session.add(task)
            db.session.commit()
            parser.delay(task.id)
            return redirect('/results')
        return render_template('add_site.html', form=form)


@celery.task
def parser(id):
    task = Tasks.query.get(id)
    task.task_status = 'PENDING'
    db.session.commit()
    address = task.address

    status_code = 404
    try:
        res_address = requests.get(address, timeout=10)
        status_code = res_address.status_code
    except Timeout:
        status_code = 504

    count = 0
    if status_code == 200:
        words = res_address.text.split()
        count = words.count("Python")

    result = Results(address=address, words_count=count, http_status_code=status_code)
    task = Tasks.query.get(id)
    task.task_status = 'FINISHED'
    db.session.add(result)
    db.session.commit()
