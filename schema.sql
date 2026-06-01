-- ============================================================
-- F1 Race Management System - Database Schema
-- DBMS: MySQL 5.0+  Engine: InnoDB  Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS f1_race_control
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE f1_race_control;

-- ----------------------------
-- 1. Team (车队)
-- ----------------------------
CREATE TABLE team (
    team_id      INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    team_name    CHAR(50)    NOT NULL COMMENT '车队名称',
    team_address VARCHAR(100) NOT NULL COMMENT '总部地址',
    team_leader  CHAR(20)    NOT NULL COMMENT '领队'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 2. Track (赛道)
-- ----------------------------
CREATE TABLE track (
    track_id     INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    track_name   CHAR(50)    NOT NULL COMMENT '赛道名称',
    track_city   CHAR(50)    NOT NULL COMMENT '所在城市',
    track_length DECIMAL(5,3) NOT NULL COMMENT '长度(km)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 3. User (用户)
-- ----------------------------
CREATE TABLE user (
    user_id   INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_name CHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    password  CHAR(32) NOT NULL COMMENT '密码(MD5)',
    user_role CHAR(10) NOT NULL COMMENT '角色: Admin/Steward/Guest',
    team_id   INT(11)  DEFAULT NULL COMMENT '外键-关联车队(Steward专属)',
    CONSTRAINT fk_user_team FOREIGN KEY (team_id)
        REFERENCES team(team_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 4. Driver (车手) — parent entity
-- ----------------------------
CREATE TABLE driver (
    driver_id     INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    driver_name   CHAR(20) NOT NULL COMMENT '姓名',
    driver_num    INT(3)   NOT NULL UNIQUE COMMENT '车号',
    driver_nation CHAR(20) NOT NULL COMMENT '国籍',
    driver_age    INT(3)   NOT NULL DEFAULT 18 COMMENT '年龄',
    team_id       INT(11)  NOT NULL COMMENT '外键-车队',
    CONSTRAINT fk_driver_team FOREIGN KEY (team_id)
        REFERENCES team(team_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 5. Fulltime Driver (全职车手) — subclass of Driver
-- ----------------------------
CREATE TABLE fulltime_driver (
    driver_id     INT(11) PRIMARY KEY COMMENT '主键+外键',
    driver_salary DECIMAL(10,2) NOT NULL COMMENT '薪资(万元/年)',
    CONSTRAINT fk_fulltime_driver FOREIGN KEY (driver_id)
        REFERENCES driver(driver_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 6. Reserve Driver (储备车手) — subclass of Driver
-- ----------------------------
CREATE TABLE reserve_driver (
    driver_id  INT(11) PRIMARY KEY COMMENT '主键+外键',
    test_hours DECIMAL(5,1) NOT NULL COMMENT '测试时长(小时)',
    CONSTRAINT fk_reserve_driver FOREIGN KEY (driver_id)
        REFERENCES driver(driver_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 7. Grand Prix (大奖赛)
-- ----------------------------
CREATE TABLE grandprix (
    gp_id         INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    gp_name       CHAR(50) NOT NULL COMMENT '比赛名称',
    gp_date       DATE     NOT NULL COMMENT '举办日期',
    gp_season     INT(4)   NOT NULL COMMENT '赛季年份',
    gp_laps       INT(3)   NOT NULL COMMENT '圈数',
    track_id      INT(11)  NOT NULL COMMENT '外键-赛道',
    audit_user_id INT(11)  NOT NULL COMMENT '外键-审核人',
    CONSTRAINT fk_gp_track FOREIGN KEY (track_id)
        REFERENCES track(track_id),
    CONSTRAINT fk_gp_audit FOREIGN KEY (audit_user_id)
        REFERENCES user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 8. Result (成绩)
-- ----------------------------
CREATE TABLE result (
    result_id    INT(11) AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    result_rank  INT(3)      NOT NULL COMMENT '名次',
    result_points INT(2)     NOT NULL COMMENT '积分',
    fastest_lap  TIME        DEFAULT NULL COMMENT '最快单圈',
    finish_time  TIME        DEFAULT NULL COMMENT '完赛时间',
    penalty_info VARCHAR(100) DEFAULT NULL COMMENT '处罚信息',
    driver_id    INT(11)     NOT NULL COMMENT '外键-车手',
    gp_id        INT(11)     NOT NULL COMMENT '外键-大奖赛',
    CONSTRAINT fk_result_driver FOREIGN KEY (driver_id)
        REFERENCES driver(driver_id) ON DELETE CASCADE,
    CONSTRAINT fk_result_gp FOREIGN KEY (gp_id)
        REFERENCES grandprix(gp_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- View: driver_standings_view (车手积分榜视图)
-- 多表关联: driver + team + result + grandprix
-- ============================================================
CREATE OR REPLACE VIEW driver_standings_view AS
SELECT
    d.driver_id,
    d.driver_name,
    d.driver_num,
    d.driver_nation,
    d.driver_age,
    t.team_name,
    COALESCE(SUM(r.result_points), 0) AS total_points,
    COUNT(r.result_id)                 AS races_count,
    COUNT(CASE WHEN r.result_rank = 1 THEN 1 END) AS wins
FROM driver d
JOIN team t ON d.team_id = t.team_id
LEFT JOIN result r ON d.driver_id = r.driver_id
LEFT JOIN grandprix g ON r.gp_id = g.gp_id AND g.gp_season = 2024
GROUP BY d.driver_id, d.driver_name, d.driver_num, d.driver_nation, d.driver_age, t.team_name
ORDER BY total_points DESC, wins DESC;
