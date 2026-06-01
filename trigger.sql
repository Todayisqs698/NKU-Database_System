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
