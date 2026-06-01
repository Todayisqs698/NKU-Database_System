from utils.db import query, execute_insert, execute, get_db, call_proc

def get_results_by_race(gp_id):
    sql = """
        SELECT r.*, d.driver_name, d.driver_num, t.team_name
        FROM result r
        JOIN driver d ON r.driver_id = d.driver_id
        JOIN team t ON d.team_id = t.team_id
        WHERE r.gp_id = %s
        ORDER BY r.result_rank
    """
    return query(sql, (gp_id,))

def get_driver_results(driver_id, season=None):
    sql = """
        SELECT r.*, g.gp_name, g.gp_date, g.gp_season
        FROM result r
        JOIN grandprix g ON r.gp_id = g.gp_id
        WHERE r.driver_id = %s
    """
    params = (driver_id,)
    if season:
        sql += " AND g.gp_season = %s"
        params = (driver_id, season)
    sql += " ORDER BY g.gp_date"
    return query(sql, params)

def create_result(rank, points, fastest_lap, finish_time, penalty, driver_id, gp_id):
    return execute_insert(
        "INSERT INTO result (result_rank, result_points, fastest_lap, finish_time, "
        "penalty_info, driver_id, gp_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (rank, points, fastest_lap, finish_time, penalty, driver_id, gp_id))

def update_result(result_id, rank, points, fastest_lap, finish_time, penalty):
    return execute(
        "UPDATE result SET result_rank=%s, result_points=%s, fastest_lap=%s, "
        "finish_time=%s, penalty_info=%s WHERE result_id=%s",
        (rank, points, fastest_lap, finish_time, penalty, result_id))

def delete_result(result_id):
    return execute("DELETE FROM result WHERE result_id=%s", (result_id,))

def get_driver_standings(season):
    """Driver standings for a season, ordered by points."""
    sql = """
        SELECT d.driver_name, d.driver_num, t.team_name,
               SUM(r.result_points) AS total_points,
               COUNT(CASE WHEN r.result_rank = 1 THEN 1 END) AS wins
        FROM driver d
        JOIN team t ON d.team_id = t.team_id
        JOIN result r ON d.driver_id = r.driver_id
        JOIN grandprix g ON r.gp_id = g.gp_id
        WHERE g.gp_season = %s
        GROUP BY d.driver_id, d.driver_name, d.driver_num, t.team_name
        ORDER BY total_points DESC, wins DESC
    """
    return query(sql, (season,))

def call_update_race_result(result_id, new_rank, new_points, fastest_lap, finish_time, penalty):
    """
    调用存储过程 update_race_result 更新成绩 + 联动积分。
    存储过程内含三项业务校验：名次>=1、积分0~25、成绩记录存在。
    p_status 不以 SUCCESS 开头时，Python 层主动抛出异常以触发 Flash 报错。
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SET @p_status = ''")
            cur.execute(
                "CALL update_race_result(%s,%s,%s,%s,%s,%s,@p_status)",
                (result_id, new_rank, new_points, fastest_lap, finish_time, penalty))
            conn.commit()
            cur.execute("SELECT @p_status AS status")
            row = cur.fetchone()
            status = row['status'] if row else 'UNKNOWN'
            if not status.startswith('SUCCESS'):
                raise Exception(status)
            return {'data': [], 'status': status}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def call_recalculate_points(season):
    """
    调用存储过程 recalculate_season_points 重算赛季积分。
    演示跨表联动更新(result → driver → team)
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.callproc('recalculate_season_points', (season,))
            results = []
            for row in cur.fetchall():
                results.append(row)
            conn.commit()
            return results
    finally:
        conn.close()

def query_driver_standings_view(season=None):
    """
    查询 driver_standings_view 视图，按赛季筛选。
    gp_season IS NULL 的行对应0场未参赛车手，一并保留以展示完整车手列表。
    """
    if season is not None:
        return query(
            """SELECT * FROM driver_standings_view
               WHERE gp_season = %s OR gp_season IS NULL
               ORDER BY total_points DESC, wins DESC""",
            (season,))
    return query("SELECT * FROM driver_standings_view")