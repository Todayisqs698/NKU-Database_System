-- ============================================================
-- Sample data for testing
-- ============================================================
USE f1_race_control;

-- Users (passwords ： '123456')
INSERT INTO user (user_name, password, user_role, team_id) VALUES
('admin',    'e10adc3949ba59abbe56e057f20f883e', 'Admin',   NULL),
('rb_horner', 'e10adc3949ba59abbe56e057f20f883e', 'Steward', 1),
('merc_wolff', 'e10adc3949ba59abbe56e057f20f883e', 'Steward', 2),
('ferrari_vasseur', 'e10adc3949ba59abbe56e057f20f883e', 'Steward', 3),
('mclaren_stella', 'e10adc3949ba59abbe56e057f20f883e', 'Steward', 4),
('am_krack', 'e10adc3949ba59abbe56e057f20f883e', 'Steward', 5),
('guest1',   'e10adc3949ba59abbe56e057f20f883e', 'Guest',   NULL);

-- Teams
INSERT INTO team (team_name, team_address, team_leader) VALUES
('Red Bull Racing', 'Milton Keynes, UK',         'Christian Horner'),
('Mercedes',        'Brackley, UK',               'Toto Wolff'),
('Ferrari',         'Maranello, Italy',           'Fred Vasseur'),
('McLaren',         'Woking, UK',                 'Andrea Stella'),
('Aston Martin',    'Silverstone, UK',            'Mike Krack');

-- Tracks
INSERT INTO track (track_name, track_city, track_length) VALUES
('Bahrain International Circuit', 'Sakhir',    5.412),
('Jeddah Corniche Circuit',       'Jeddah',    6.174),
('Shanghai International Circuit','Shanghai',  5.451),
('Circuit de Monaco',             'Monte Carlo',3.337),
('Silverstone Circuit',           'Silverstone',5.891);

-- Drivers (with age for trigger validation)
INSERT INTO driver (driver_name, driver_num, driver_nation, driver_age, team_id) VALUES
('Max Verstappen',   1,  'Dutch',        26, 1),
('Sergio Perez',     11, 'Mexican',      34, 1),
('Lewis Hamilton',   44, 'British',      39, 2),
('George Russell',   63, 'British',      26, 2),
('Charles Leclerc',  16, 'Monégasque',   26, 3),
('Carlos Sainz',     55, 'Spanish',      29, 3),
('Lando Norris',     4,  'British',      24, 4),
('Oscar Piastri',    81, 'Australian',   23, 4);

-- Fulltime drivers
INSERT INTO fulltime_driver (driver_id, driver_salary) VALUES
(1, 5500.00),
(2, 1000.00),
(3, 3500.00),
(4, 800.00),
(5, 2500.00),
(6, 1200.00),
(7, 1500.00),
(8, 600.00);

-- Reserve drivers
INSERT INTO driver (driver_name, driver_num, driver_nation, driver_age, team_id) VALUES
('Liam Lawson',    40, 'New Zealander', 22, 1),
('Mick Schumacher', 47, 'German',       25, 2);

INSERT INTO reserve_driver (driver_id, test_hours) VALUES
(9,  120.5),
(10, 85.0);

-- Grand Prix events (2024 season)
INSERT INTO grandprix (gp_name, gp_date, gp_season, gp_laps, track_id, audit_user_id) VALUES
('Bahrain Grand Prix',       '2024-03-02', 2024, 57, 1, 1),
('Saudi Arabian Grand Prix', '2024-03-09', 2024, 50, 2, 1),
('Chinese Grand Prix',       '2024-04-21', 2024, 56, 3, 1),
('Monaco Grand Prix',        '2024-05-26', 2024, 78, 4, 1);

-- Race results (Bahrain GP)
INSERT INTO result (result_rank, result_points, fastest_lap, finish_time, penalty_info, driver_id, gp_id) VALUES
(1, 25, '01:32.608', '01:31:44.742', NULL, 1, 1),
(2, 18, '01:33.102', '01:32:06.913', NULL, 3, 1),
(3, 15, '01:33.453', '01:32:11.256', NULL, 5, 1),
(4, 12, '01:33.891', '01:32:20.104', NULL, 7, 1),
(5, 10, '01:34.102', '01:32:35.721', 'Track limits violation', 2, 1);
