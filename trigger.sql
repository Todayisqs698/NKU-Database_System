-- ============================================================
-- Trigger: before_driver_insert
-- 功能: 插入车手时校验年龄≥18，不满足则禁止插入并报错
-- ============================================================
USE f1_race_control;

DROP TRIGGER IF EXISTS before_driver_insert;

DELIMITER $$

CREATE TRIGGER before_driver_insert
BEFORE INSERT ON driver
FOR EACH ROW
BEGIN
    IF NEW.driver_age IS NULL OR NEW.driver_age < 18 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 车手年龄必须≥18岁，插入操作已拒绝';
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- Trigger: before_driver_update
-- 功能: 更新车手信息时同样校验年龄
-- ============================================================
DROP TRIGGER IF EXISTS before_driver_update;

DELIMITER $$

CREATE TRIGGER before_driver_update
BEFORE UPDATE ON driver
FOR EACH ROW
BEGIN
    IF NEW.driver_age < 18 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 车手年龄必须≥18岁，更新操作已拒绝';
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- Trigger: before_result_insert
-- 功能: 插入成绩时校验积分 0~25、名次 ≥1
-- ============================================================
DROP TRIGGER IF EXISTS before_result_insert;

DELIMITER $$

CREATE TRIGGER before_result_insert
BEFORE INSERT ON result
FOR EACH ROW
BEGIN
    IF NEW.result_rank IS NULL OR NEW.result_rank < 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 名次必须≥1，插入操作已拒绝';
    END IF;
    IF NEW.result_points IS NULL OR NEW.result_points < 0 OR NEW.result_points > 25 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 积分必须在0~25之间，插入操作已拒绝';
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- Trigger: before_result_update
-- 功能: 更新成绩时校验积分 0~25、名次 ≥1
-- ============================================================
DROP TRIGGER IF EXISTS before_result_update;

DELIMITER $$

CREATE TRIGGER before_result_update
BEFORE UPDATE ON result
FOR EACH ROW
BEGIN
    IF NEW.result_rank IS NULL OR NEW.result_rank < 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 名次必须≥1，更新操作已拒绝';
    END IF;
    IF NEW.result_points IS NULL OR NEW.result_points < 0 OR NEW.result_points > 25 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '错误: 积分必须在0~25之间，更新操作已拒绝';
    END IF;
END$$

DELIMITER ;
