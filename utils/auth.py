import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash
from utils.db import query

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def login_required(f):
    """Decorator: must be logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """Decorator: must have one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            user = query("SELECT user_role FROM user WHERE user_id=%s",
                         (session['user_id'],), fetch_one=True)
            if user and user['user_role'] in roles:
                return f(*args, **kwargs)
            flash('权限不足', 'danger')
            return redirect(url_for('public.index'))
        return decorated
    return decorator
