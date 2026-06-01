from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required, role_required
from utils.db import query
from services.driver_service import (get_drivers_by_team, create_driver,
                                     delete_driver, get_all_drivers)

steward_bp = Blueprint('steward', __name__, url_prefix='/steward')

IS_ADMIN = False  # set per-request below


def _is_admin():
    return session.get('user_role') == 'Admin'


def _get_steward_team():
    """Return (team_id, team_name, team_leader) for the current user.
       Admin (team_id=NULL) can access all teams; Steward must have team_id."""
    if _is_admin():
        return None, '全部车队', '系统管理员'
    team_id = session.get('team_id')
    if not team_id:
        return None, None, None
    team = query("SELECT team_id, team_name, team_leader FROM team WHERE team_id=%s",
                 (team_id,), fetch_one=True)
    if not team:
        return None, None, None
    return team['team_id'], team['team_name'], team['team_leader']


# ---------------------------------------------------------------------------
# Dashboard — 赛事管理面板
# ---------------------------------------------------------------------------
@steward_bp.route('/')
@login_required
@role_required('Steward', 'Admin')
def dashboard():
    team_id, team_name, team_leader = _get_steward_team()
    if team_id is None and not _is_admin():
        flash('未关联到任何车队，请联系管理员', 'warning')
        return redirect(url_for('public.index'))

    if _is_admin():
        # Admin sees all teams with their drivers
        teams = query("SELECT team_id, team_name, team_leader FROM team ORDER BY team_id")
        all_teams_drivers = {}
        for t in teams:
            all_teams_drivers[t['team_id']] = {
                'team_name': t['team_name'],
                'team_leader': t['team_leader'],
                'drivers': get_drivers_by_team(t['team_id']),
            }
        return render_template('steward/admin_dashboard.html',
                               all_teams=all_teams_drivers,
                               teams_count=len(teams))
    else:
        drivers = get_drivers_by_team(team_id)
        return render_template('steward/dashboard.html',
                               team_name=team_name,
                               team_leader=team_leader,
                               drivers=drivers,
                               drivers_count=len(drivers))


# ---------------------------------------------------------------------------
# Add driver — 签约车手 (触发器 age≥18 校验)
# ---------------------------------------------------------------------------
@steward_bp.route('/drivers/add', methods=['POST'])
@login_required
@role_required('Steward', 'Admin')
def add_driver():
    if _is_admin():
        team_id = request.form.get('team_id', type=int)
        if not team_id:
            flash('请选择目标车队', 'danger')
            return redirect(url_for('steward.dashboard'))
        team = query("SELECT team_name FROM team WHERE team_id=%s", (team_id,), fetch_one=True)
        team_name = team['team_name'] if team else '未知车队'
    else:
        team_id, team_name, _ = _get_steward_team()
        if team_id is None:
            flash('未关联到任何车队', 'danger')
            return redirect(url_for('public.index'))

    name = request.form.get('name', '').strip()
    num = request.form.get('num', type=int)
    nation = request.form.get('nation', '').strip()
    age = request.form.get('age', type=int)
    driver_type = request.form.get('driver_type', 'fulltime')
    salary = request.form.get('salary', type=float) if driver_type == 'fulltime' else None
    test_hours = request.form.get('test_hours', type=float) if driver_type == 'reserve' else None

    if not name or not num or not nation or not age:
        flash('请填写所有必填字段 (姓名/车号/国籍/年龄)', 'danger')
        return redirect(url_for('steward.dashboard'))

    try:
        create_driver(name, num, nation, age, team_id, driver_type, salary, test_hours)
        flash(f'车手 {name} (#{num}) 签约成功，已加入 {team_name}', 'success')
    except Exception as e:
        msg = str(e)
        if '45000' in msg or '年龄' in msg:
            flash(f'签约失败 — 触发器拒绝: {msg}', 'danger')
        elif 'Duplicate' in msg:
            flash(f'签约失败 — 车号 #{num} 已被使用', 'danger')
        else:
            flash(f'签约失败: {msg}', 'danger')

    return redirect(url_for('steward.dashboard'))


# ---------------------------------------------------------------------------
# Delete driver — 解约车手
# ---------------------------------------------------------------------------
@steward_bp.route('/drivers/delete/<int:driver_id>', methods=['POST'])
@login_required
@role_required('Steward', 'Admin')
def delete_driver_route(driver_id):
    driver = query("SELECT driver_name, driver_num, team_id FROM driver WHERE driver_id=%s",
                   (driver_id,), fetch_one=True)
    if not driver:
        flash('车手不存在', 'danger')
        return redirect(url_for('steward.dashboard'))

    if not _is_admin():
        team_id, _, _ = _get_steward_team()
        if driver['team_id'] != team_id:
            flash('无权操作其他车队的车手', 'danger')
            return redirect(url_for('steward.dashboard'))

    try:
        delete_driver(driver_id)
        flash(f'车手 {driver["driver_name"]} (#{driver["driver_num"]}) 已解约，相关成绩已清除', 'info')
    except Exception as e:
        flash(f'解约失败: {str(e)}', 'danger')

    return redirect(url_for('steward.dashboard'))
