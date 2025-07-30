from flask import render_template

from . import app
from .belt_history import load_history, get_current_champion, update_belt

@app.route('/belt')
def belt():
    update_belt()
    history = load_history()
    current = get_current_champion()
    return render_template('belt.html', history=history, current=current)
