from flask import Blueprint, render_template, request, redirect, url_for, session
from services.team_service import get_all_teams, get_team_standings, get_team_by_id
from services.driver_service import (get_all_drivers, get_driver_by_id,
                                     get_champion_driver_ids)
from services.race_service import get_all_races, get_race_by_id, get_track_cities
from services.result_service import (get_results_by_race, get_driver_standings,
                                     get_driver_results, query_driver_standings_view)

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    standings = get_driver_standings(2024)
    return render_template('index.html', standings=standings)

# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
@public_bp.route('/teams')
def teams():
    season = request.args.get('season', 2024, type=int)
    leader = request.args.get('leader', '').strip()

    teams_list = get_all_teams()
    team_points = {t['team_name']: t['total_points']
                   for t in get_team_standings(season)}

    all_drivers = get_all_drivers()
    team_drivers = {}
    for d in all_drivers:
        team_drivers.setdefault(d['team_id'], []).append(d)

    # 通过领队姓名查询队伍
    if leader:
        teams_list = [t for t in teams_list if leader.lower() in t['team_leader'].lower()]

    return render_template('teams.html',
                           teams=teams_list, team_drivers=team_drivers,
                           team_points=team_points, season=season,
                           leader=leader)


@public_bp.route('/teams/<int:team_id>')
def team_detail(team_id):
    team = get_team_by_id(team_id)
    drivers = [d for d in get_all_drivers() if d['team_id'] == team_id]
    return render_template('team_detail.html', team=team, drivers=drivers)

# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------
@public_bp.route('/drivers')
def drivers():
    nation = request.args.get('nation', '').strip()
    champion_only = request.args.get('champion', '0')

    all_drivers = get_all_drivers()
    champion_ids = get_champion_driver_ids()
    matched_ids = set()

    # 单表查询
    if nation:
        filtered = [d for d in all_drivers
                    if d['driver_nation'].lower() == nation.lower()]
        matched_ids = {d['driver_id'] for d in filtered}
    else:
        matched_ids = {d['driver_id'] for d in all_drivers}

    # EXISTS query
    if champion_only == '1':
        matched_ids = matched_ids & champion_ids

    display_drivers = [d for d in all_drivers if d['driver_id'] in matched_ids]

    # 构建下拉菜单的国家列表
    nations = sorted({d['driver_nation'] for d in all_drivers})

    return render_template('drivers.html',
                           drivers=display_drivers, all_drivers=all_drivers,
                           champion_ids=champion_ids,
                           nation=nation, nations=nations,
                           champion_only=champion_only)


@public_bp.route('/drivers/<int:driver_id>')
def driver_detail(driver_id):
    driver = get_driver_by_id(driver_id)
    results = get_driver_results(driver_id)
    return render_template('driver_detail.html', driver=driver, results=results)

# ---------------------------------------------------------------------------
# Races (JOIN grandprix + track)
# ---------------------------------------------------------------------------
@public_bp.route('/races')
def races():
    season = request.args.get('season', '', type=str)
    city = request.args.get('city', '').strip()

    season_int = int(season) if season else None
    races_list = get_all_races(season=season_int, city=city)
    cities = get_track_cities()

    return render_template('races.html',
                           races=races_list,
                           season=season,
                           city=city,
                           cities=cities,
                           races_count=len(races_list))


@public_bp.route('/races/<int:gp_id>')
def race_detail(gp_id):
    race = get_race_by_id(gp_id)
    results = get_results_by_race(gp_id)
    return render_template('race_detail.html', race=race, results=results)

# ---------------------------------------------------------------------------
# Standings — 基于视图 driver_standings_view 的查询
# ---------------------------------------------------------------------------
@public_bp.route('/standings')
def standings():
    season = request.args.get('season', 2024, type=int)
    # 查询视图 driver_standings_view，按赛季筛选（gp_season IS NULL 保留0场未参赛车手）
    driver_standings = query_driver_standings_view(season)
    team_standings = get_team_standings(season)

    return render_template('standings.html',
                           driver_standings=driver_standings,
                           team_standings=team_standings,
                           season=season)