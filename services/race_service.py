from utils.db import query, execute_insert, execute

def get_all_races(season=None, city=None):
    """Multi-table join: grandprix + track """
    sql = """
        SELECT g.gp_id, g.gp_name, g.gp_date, g.gp_season, g.gp_laps,
               g.track_id, g.audit_user_id,
               t.track_name, t.track_city
        FROM grandprix g
        JOIN track t ON g.track_id = t.track_id
    """
    conditions = []
    params = []
    if season is not None:
        conditions.append("g.gp_season = %s")
        params.append(int(season))
    if city:
        conditions.append("t.track_city LIKE %s")
        params.append(f"%{city}%")
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY g.gp_date"
    return query(sql, tuple(params))


def get_track_cities():
    rows = query("SELECT DISTINCT track_city FROM track ORDER BY track_city")
    return [r['track_city'] for r in rows]

def get_race_by_id(gp_id):
    sql = """
        SELECT g.*, t.track_name, t.track_city, t.track_length,
               u.user_name AS auditor_name
        FROM grandprix g
        JOIN track t ON g.track_id = t.track_id
        JOIN user u ON g.audit_user_id = u.user_id
        WHERE g.gp_id = %s
    """
    return query(sql, (gp_id,), fetch_one=True)

def create_race(name, date, season, laps, track_id, audit_user_id):
    return execute_insert(
        "INSERT INTO grandprix (gp_name, gp_date, gp_season, gp_laps, track_id, audit_user_id) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        (name, date, season, laps, track_id, audit_user_id))

def update_race(gp_id, name, date, season, laps, track_id):
    return execute(
        "UPDATE grandprix SET gp_name=%s, gp_date=%s, gp_season=%s, gp_laps=%s, track_id=%s "
        "WHERE gp_id=%s",
        (name, date, season, laps, track_id, gp_id))

def get_all_tracks():
    return query("SELECT * FROM track ORDER BY track_name")

def create_track(name, city, length):
    return execute_insert(
        "INSERT INTO track (track_name, track_city, track_length) VALUES (%s,%s,%s)",
        (name, city, length))

def delete_track(track_id):
    """
    删除赛道。若该赛道已被大奖赛引用（grandprix.track_id 外键），
    则拒绝删除并抛出异常提示用户。
    """
    from utils.db import query, execute
    # 检查是否有大奖赛引用该赛道
    refs = query("SELECT COUNT(*) AS cnt FROM grandprix WHERE track_id = %s", (track_id,))
    if refs and refs[0]['cnt'] > 0:
        raise Exception(f"该赛道已关联 {refs[0]['cnt']} 场大奖赛，无法删除，请先删除相关赛事")
    execute("DELETE FROM track WHERE track_id = %s", (track_id,))
