from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.auth import login_required, role_required
from services.team_service import (create_team, update_team,
                                    get_team_by_id, delete_team_with_drivers)
from services.result_service import (call_update_race_result, get_results_by_race,
                                     create_result, update_result, delete_result)
from services.race_service import (get_all_tracks, create_track, delete_track, get_all_races,
                                   get_race_by_id, create_race, update_race)
from services.driver_service import get_all_drivers
from services.user_service import get_all_users, delete_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_bp.route('/')
@login_required
@role_required('Admin')
def dashboard():
    return render_template('admin/dashboard.html')

# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------
@admin_bp.route('/users')
@login_required
@role_required('Admin')
def users():
    return render_template('admin/users.html', users=get_all_users())

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_user_route(user_id):
    delete_user(user_id)
    flash('用户已删除', 'info')
    return redirect(url_for('admin.users'))

# ---------------------------------------------------------------------------
# Team CRUD
# ---------------------------------------------------------------------------
@admin_bp.route('/teams')
@login_required
@role_required('Admin')
def teams():
    from services.team_service import get_all_teams
    return render_template('admin/teams.html', teams=get_all_teams())

@admin_bp.route('/teams/add', methods=['POST'])
@login_required
@role_required('Admin')
def add_team():
    steward_user = request.form.get('steward_user', '').strip()
    steward_pass = request.form.get('steward_pass', '').strip()
    try:
        create_team(request.form['name'], request.form['address'], request.form['leader'],
                    steward_user=steward_user or None, steward_pass=steward_pass or None)
        if steward_user:
            flash(f'车队添加成功，领队账号 {steward_user} 已创建', 'success')
        else:
            flash('车队添加成功 (未创建领队账号)', 'success')
    except Exception as e:
        flash(f'添加失败: {str(e)}', 'danger')
    return redirect(url_for('admin.teams'))

@admin_bp.route('/teams/edit/<int:team_id>', methods=['POST'])
@login_required
@role_required('Admin')
def edit_team(team_id):
    update_team(team_id, request.form['name'], request.form['address'], request.form['leader'])
    flash('车队修改成功', 'success')
    return redirect(url_for('admin.teams'))

@admin_bp.route('/teams/delete/<int:team_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_team_transaction_route(team_id):
    """
    事务删除: 删除车队+旗下全部车手+成绩+子表(跨5张表)
    任何一步失败自动回滚 — 作业第1项(13分)
    """
    try:
        delete_team_with_drivers(team_id)
        flash('事务删除成功: 车队及其全部车手/成绩已清除, 事务已提交', 'success')
    except Exception as e:
        flash(f'事务删除失败, 已自动回滚: {str(e)}', 'danger')
    return redirect(url_for('admin.teams'))

# ---------------------------------------------------------------------------
# Stored Procedure interface
# ---------------------------------------------------------------------------
@admin_bp.route('/procedure/update-result', methods=['POST'])
@login_required
@role_required('Admin', 'Steward')
def procedure_update_result():
    """调用存储过程 update_race_result 更新成绩 + 联动积分"""
    try:
        result = call_update_race_result(
            request.form.get('result_id', type=int),
            request.form.get('rank', type=int),
            request.form.get('points', type=int),
            request.form.get('fastest_lap') or None,
            request.form.get('finish_time') or None,
            request.form.get('penalty') or None
        )
        flash(f'存储过程执行: {result["status"]}', 'success')
    except Exception as e:
        flash(f'存储过程执行失败: {str(e)}', 'danger')
    return redirect(url_for('admin.teams'))

# ---------------------------------------------------------------------------
# Tracks
# ---------------------------------------------------------------------------
@admin_bp.route('/tracks')
@login_required
@role_required('Admin')
def tracks():
    return render_template('admin/tracks.html', tracks=get_all_tracks())

@admin_bp.route('/tracks/add', methods=['POST'])
@login_required
@role_required('Admin')
def add_track():
    create_track(request.form['name'], request.form['city'], request.form['length'])
    flash('赛道添加成功', 'success')
    return redirect(url_for('admin.tracks'))

@admin_bp.route('/tracks/delete/<int:track_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_track_route(track_id):
    try:
        delete_track(track_id)
        flash('赛道删除成功', 'success')
    except Exception as e:
        flash(f'删除失败：{str(e)}', 'danger')
    return redirect(url_for('admin.tracks'))

# ---------------------------------------------------------------------------
# Grand Prix  赛事管理
# ---------------------------------------------------------------------------
@admin_bp.route('/races')
@login_required
@role_required('Admin')
def races():
    season = request.args.get('season', type=int)
    return render_template('admin/races.html',
                           races=get_all_races(season),
                           tracks=get_all_tracks(),
                           season=season)

@admin_bp.route('/races/add', methods=['POST'])
@login_required
@role_required('Admin')
def add_race():
    create_race(request.form['name'], request.form['date'], request.form['season'],
                request.form['laps'], request.form['track_id'], 1)
    flash('大奖赛添加成功', 'success')
    return redirect(url_for('admin.races'))

@admin_bp.route('/races/edit/<int:gp_id>', methods=['POST'])
@login_required
@role_required('Admin')
def edit_race(gp_id):
    update_race(gp_id, request.form['name'], request.form['date'],
                request.form['season'], request.form['laps'], request.form['track_id'])
    flash('大奖赛修改成功', 'success')
    return redirect(url_for('admin.races'))

# ---------------------------------------------------------------------------
# Result (比赛成绩) CRUD
# ---------------------------------------------------------------------------
@admin_bp.route('/results/<int:gp_id>')
@login_required
@role_required('Admin')
def results(gp_id):
    race = get_race_by_id(gp_id)
    results = get_results_by_race(gp_id)
    drivers = get_all_drivers()
    return render_template('admin/results.html',
                           race=race, results=results, drivers=drivers)

@admin_bp.route('/results/<int:gp_id>/add', methods=['POST'])
@login_required
@role_required('Admin')
def add_result(gp_id):
    try:
        create_result(request.form['rank'], request.form['points'],
                      request.form.get('fastest_lap') or None,
                      request.form.get('finish_time') or None,
                      request.form.get('penalty') or None,
                      request.form['driver_id'], gp_id)
        flash('成绩录入成功', 'success')
    except Exception as e:
        flash(f'数据库校验拒绝: {e}', 'danger')
    return redirect(url_for('admin.results', gp_id=gp_id))

@admin_bp.route('/results/edit/<int:result_id>', methods=['POST'])
@login_required
@role_required('Admin')
def edit_result(result_id):
    gp_id = request.form['gp_id']
    try:
        update_result(result_id, request.form['rank'], request.form['points'],
                      request.form.get('fastest_lap') or None,
                      request.form.get('finish_time') or None,
                      request.form.get('penalty') or None)
        flash('成绩修改成功', 'success')
    except Exception as e:
        flash(f'数据库校验拒绝: {e}', 'danger')
    return redirect(url_for('admin.results', gp_id=gp_id))

@admin_bp.route('/results/delete/<int:result_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_result_route(result_id):
    gp_id = request.form['gp_id']
    delete_result(result_id)
    flash('成绩记录已删除', 'info')
    return redirect(url_for('admin.results', gp_id=gp_id))