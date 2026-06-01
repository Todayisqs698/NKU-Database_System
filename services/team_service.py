from utils.db import query, execute_insert, execute, get_transaction_db
from utils.auth import md5

def get_all_teams():
    return query("SELECT * FROM team ORDER BY team_name")

def get_team_by_id(team_id):
    return query("SELECT * FROM team WHERE team_id=%s", (team_id,), fetch_one=True)

def create_team(name, address, leader, steward_user=None, steward_pass=None):
    """Create a team and optionally a linked steward account in a transaction."""
    if not steward_user or not steward_pass:
        return execute_insert(
            "INSERT INTO team (team_name, team_address, team_leader) VALUES (%s,%s,%s)",
            (name, address, leader))

    conn = get_transaction_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO team (team_name, team_address, team_leader) VALUES (%s,%s,%s)",
                (name, address, leader))
            team_id = cur.lastrowid
            cur.execute(
                "INSERT INTO user (user_name, password, user_role, team_id) VALUES (%s,%s,%s,%s)",
                (steward_user, md5(steward_pass), 'Steward', team_id))
        conn.commit()
        return team_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_team(team_id, name, address, leader):
    return execute(
        "UPDATE team SET team_name=%s, team_address=%s, team_leader=%s WHERE team_id=%s",
        (name, address, leader, team_id))

def get_team_standings(season):
    """Aggregate query: total points per team for a given season.
       LEFT JOIN ensures all teams appear (even those with 0 points).
       COALESCE handles NULL for teams with no results.
       GROUP BY includes team_id for ONLY_FULL_GROUP_BY compliance."""
    sql = """
        SELECT t.team_id, t.team_name,
               COALESCE(SUM(s.pts), 0) AS total_points
        FROM team t
        LEFT JOIN driver d ON t.team_id = d.team_id
        LEFT JOIN (
            SELECT r.driver_id, r.result_points AS pts
            FROM result r
            JOIN grandprix g ON r.gp_id = g.gp_id
            WHERE g.gp_season = %s
        ) s ON d.driver_id = s.driver_id
        GROUP BY t.team_id, t.team_name
        ORDER BY total_points DESC
    """
    return query(sql, (season,))

def delete_team_with_drivers(team_id):
    """
    事务删除: 删除车队同时删除旗下全部车手.
    任意一步失败则自动回滚，保证数据一致性.
    """
    conn = get_transaction_db()
    try:
        with conn.cursor() as cur:
            # 1. 删除该车队所有车手的成绩记录
            cur.execute(
                "DELETE r FROM result r "
                "JOIN driver d ON r.driver_id = d.driver_id "
                "WHERE d.team_id = %s", (team_id,))
            # 2. 删除全职车手子表记录
            cur.execute(
                "DELETE f FROM fulltime_driver f "
                "JOIN driver d ON f.driver_id = d.driver_id "
                "WHERE d.team_id = %s", (team_id,))
            # 3. 删除储备车手子表记录
            cur.execute(
                "DELETE r2 FROM reserve_driver r2 "
                "JOIN driver d ON r2.driver_id = d.driver_id "
                "WHERE d.team_id = %s", (team_id,))
            # 4. 删除该车队所有车手(driver主表)
            cur.execute("DELETE FROM driver WHERE team_id = %s", (team_id,))
            # 5. 删除车队
            cur.execute("DELETE FROM team WHERE team_id = %s", (team_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
