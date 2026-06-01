from utils.db import query, execute_insert, execute, get_transaction_db

def get_all_drivers():
    sql = """
        SELECT d.*, t.team_name,
               CASE WHEN f.driver_id IS NOT NULL THEN '全职' ELSE '储备' END AS driver_type,
               f.driver_salary, r2.test_hours
        FROM driver d
        JOIN team t ON d.team_id = t.team_id
        LEFT JOIN fulltime_driver f ON d.driver_id = f.driver_id
        LEFT JOIN reserve_driver r2 ON d.driver_id = r2.driver_id
        ORDER BY d.driver_num
    """
    return query(sql)

def get_driver_by_id(driver_id):
    sql = """
        SELECT d.*, t.team_name,
               f.driver_salary, r.test_hours
        FROM driver d
        JOIN team t ON d.team_id = t.team_id
        LEFT JOIN fulltime_driver f ON d.driver_id = f.driver_id
        LEFT JOIN reserve_driver r ON d.driver_id = r.driver_id
        WHERE d.driver_id = %s
    """
    return query(sql, (driver_id,), fetch_one=True)



def create_driver(name, num, nation, age, team_id, driver_type, salary=None, test_hours=None):
    conn = get_transaction_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO driver (driver_name, driver_num, driver_nation, driver_age, team_id) "
                "VALUES (%s,%s,%s,%s,%s)",
                (name, num, nation, age, team_id))
            driver_id = cur.lastrowid

            if driver_type == 'fulltime':
                cur.execute(
                    "INSERT INTO fulltime_driver (driver_id, driver_salary) VALUES (%s,%s)",
                    (driver_id, salary))
            else:
                cur.execute(
                    "INSERT INTO reserve_driver (driver_id, test_hours) VALUES (%s,%s)",
                    (driver_id, test_hours))
        conn.commit()
        return driver_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_drivers_by_nation(nation):
    """单表查询"""
    sql = """
        SELECT driver_id, driver_name, driver_num, driver_nation
        FROM driver WHERE driver_nation = %s ORDER BY driver_num
    """
    return query(sql, (nation,))

def get_drivers_by_team_leader(leader):
    """嵌套子查询"""
    sql = """
        SELECT driver_name FROM driver
        WHERE team_id IN (SELECT team_id FROM team WHERE team_leader = %s)
    """
    return query(sql, (leader,))

def get_race_winners():
    """EXISTS 查询"""
    sql = """
        SELECT d.driver_name, d.driver_num
        FROM driver d WHERE EXISTS (
            SELECT 1 FROM result r
            WHERE r.driver_id = d.driver_id AND r.result_rank = 1
        )
    """
    return query(sql)

def get_champion_driver_ids():
    """返回至少赢一场比赛的车手"""
    rows = query(
        "SELECT DISTINCT driver_id FROM result WHERE result_rank = 1"
    )
    return {r['driver_id'] for r in rows}


def delete_driver(driver_id):
    """Delete a driver (fulltime/reserve)."""
    return execute("DELETE FROM driver WHERE driver_id = %s", (driver_id,))


def get_drivers_by_team(team_id):
    """all drivers for a specific team with their type info."""
    sql = """
        SELECT d.*, t.team_name,
               CASE WHEN f.driver_id IS NOT NULL THEN '全职' ELSE '储备' END AS driver_type,
               f.driver_salary, r.test_hours
        FROM driver d
        JOIN team t ON d.team_id = t.team_id
        LEFT JOIN fulltime_driver f ON d.driver_id = f.driver_id
        LEFT JOIN reserve_driver r ON d.driver_id = r.driver_id
        WHERE d.team_id = %s
        ORDER BY d.driver_num
    """
    return query(sql, (team_id,))
