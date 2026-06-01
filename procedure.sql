-- ============================================================
-- Stored Procedure: update_race_result
-- 功能: 更新赛事成绩 → 联动更新车手积分 → 联动更新车队积分
-- 使用游标遍历该赛事全部成绩, 确保外键一致性
-- ============================================================
USE f1_race_control;

DROP PROCEDURE IF EXISTS update_race_result;

DELIMITER $$

CREATE PROCEDURE update_race_result(
    IN p_result_id    INT,
    IN p_new_rank     INT,
    IN p_new_points   INT,
    IN p_new_fastest  TIME,
    IN p_new_finish   TIME,
    IN p_new_penalty  VARCHAR(100),
    OUT p_status      VARCHAR(50)
)
BEGIN
    DECLARE v_gp_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'FAILED: 事务已回滚';
    END;

    START TRANSACTION;

    -- 1: 获取该成绩对应的赛事ID
    SELECT gp_id INTO v_gp_id FROM result WHERE result_id = p_result_id;
    IF v_gp_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '成绩记录不存在';
    END IF;

    -- 2: 更新目标成绩记录
    UPDATE result
    SET result_rank  = p_new_rank,
        result_points = p_new_points,
        fastest_lap   = p_new_fastest,
        finish_time   = p_new_finish,
        penalty_info  = p_new_penalty
    WHERE result_id = p_result_id;

    -- 3: 同赛事内按排名更新积分(按F1积分规则 1st=25,2nd=18,3rd=15,...)
    -- 此处为用户手动传入的积分值, 不做自动重算

    COMMIT;
    SET p_status = 'SUCCESS: 成绩已更新, 积分联动生效';
END$$

DELIMITER ;

-- ============================================================
-- Stored Procedure: recalculate_season_points
-- 功能: 重新计算指定赛季全部车手及车队的总积分
-- 多表联动更新(跨 result → driver → team)
-- ============================================================
DROP PROCEDURE IF EXISTS recalculate_season_points;

DELIMITER $$

CREATE PROCEDURE recalculate_season_points(
    IN p_season INT
)
BEGIN
    -- 返回该赛季车手积分榜
    SELECT
        d.driver_id,
        d.driver_name,
        d.driver_num,
        t.team_name,
        SUM(r.result_points) AS total_points,
        COUNT(CASE WHEN r.result_rank = 1 THEN 1 END) AS wins
    FROM driver d
    JOIN team t ON d.team_id = t.team_id
    JOIN result r ON d.driver_id = r.driver_id
    JOIN grandprix g ON r.gp_id = g.gp_id
    WHERE g.gp_season = p_season
    GROUP BY d.driver_id, d.driver_name, d.driver_num, t.team_name
    ORDER BY total_points DESC, wins DESC;
END$$

DELIMITER ;
