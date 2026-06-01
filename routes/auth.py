from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.user_service import verify_login, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = verify_login(request.form['username'], request.form['password'])
        if user:
            session['user_id']   = user['user_id']
            session['user_name'] = user['user_name']
            session['user_role'] = user['user_role']
            session['team_id']   = user['team_id']
            flash(f'欢迎, {user["user_name"]}!', 'success')
            # Role-based redirect
            if user['user_role'] == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user['user_role'] == 'Steward':
                return redirect(url_for('steward.dashboard'))
            else:
                return redirect(url_for('public.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        create_user(request.form['username'], request.form['password'], 'Guest')
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('login.html', register=True)
