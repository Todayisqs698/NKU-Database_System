import pymysql
from config import Config

def get_db():
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def query(sql, params=None, fetch_one=False):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch_one:
                return cur.fetchone()
            return cur.fetchall()
    finally:
        conn.close()

def execute(sql, params=None):
    """执行插入 / 更新 / 删除操作，返回受影响的行数。"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            rows = cur.execute(sql, params or ())
            conn.commit()
            return rows
    finally:
        conn.close()

def execute_insert(sql, params=None):
    """INSERT and return the new id."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()

def get_transaction_db():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    return conn

def call_proc(proc_name, args=None):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.callproc(proc_name, args or ())
            results = []
            for row in cur.fetchall():
                results.append(row)
            while cur.nextset():
                try:
                    for row in cur.fetchall():
                        results.append(row)
                except Exception:
                    pass
            conn.commit()
            return results
    finally:
        conn.close()
