from utils.db import query, execute_insert, execute
from utils.auth import md5

def get_all_users():
    return query("SELECT user_id, user_name, user_role FROM user ORDER BY user_id")

def create_user(username, password, role, team_id=None):
    return execute_insert(
        "INSERT INTO user (user_name, password, user_role, team_id) VALUES (%s,%s,%s,%s)",
        (username, md5(password), role, team_id))

def verify_login(username, password):
    return query(
        "SELECT user_id, user_name, user_role, team_id FROM user WHERE user_name=%s AND password=%s",
        (username, md5(password)), fetch_one=True)

def delete_user(user_id):
    return execute("DELETE FROM user WHERE user_id=%s", (user_id,))
