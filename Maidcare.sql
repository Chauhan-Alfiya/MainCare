SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- ======================================
-- CREATE DATABASE
-- ======================================

CREATE DATABASE IF NOT EXISTS mindcare;
USE mindcare;

-- ======================================
-- ROLES TABLE
-- ======================================

CREATE TABLE roles (

    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL UNIQUE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO roles(role)
VALUES
('ADMIN'),
('STUDENT'),
('COUNSELLOR');

-- ======================================
-- USERS TABLE
-- ======================================

CREATE TABLE users (

    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    class ENUM('11th','12th') NOT NULL,
    stream ENUM(
        'Science',
        'Commerce',
        'Arts'
    ) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_date DATETIME DEFAULT NULL,
    last_password_change DATETIME DEFAULT NULL,
    deleted_at DATETIME DEFAULT NULL,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_expires DATETIME DEFAULT NULL,
    otp_code VARCHAR(10) DEFAULT NULL,
    otp_expires DATETIME DEFAULT NULL,
    FOREIGN KEY(role_id)
    REFERENCES roles(role_id)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================
-- DEFAULT ADMIN
-- ======================================

INSERT INTO users
(username,email,password,role_id)

VALUES
(
'Admin',
'admin@mindcare.com',
'admin123',
(SELECT role_id FROM roles WHERE role = 'ADMIN')

);

-- ======================================
-- ASSESSMENT TABLE
-- ======================================

CREATE TABLE assessments (

    assessment_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    assessment_type ENUM(
        'PHQ-9',
        'GAD-7'
    ) NOT NULL,

    score INT NOT NULL,

    risk_level VARCHAR(50),

    recommendation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================
-- AI CHAT SUPPORT
-- ======================================

CREATE TABLE chat_support (

    chat_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    message TEXT NOT NULL,

    bot_reply TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================
-- APPOINTMENTS
-- ======================================

CREATE TABLE appointments (

    appointment_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    counsellor_id INT NOT NULL,

    appointment_date DATE NOT NULL,

    appointment_time TIME NOT NULL,

    reason TEXT,

    status ENUM(
        'Pending',
        'Approved',
        'Completed',
        'Cancelled'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    FOREIGN KEY(counsellor_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================
-- WELLNESS RESOURCES
-- ======================================

CREATE TABLE wellness_resources (

    resource_id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    category VARCHAR(100),

    description TEXT,

    file_path VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ======================================
-- WELLNESS TRACKER
-- ======================================

CREATE TABLE wellness_tracker (

    tracker_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    mood ENUM(
        'Happy',
        'Calm',
        'Sad',
        'Stressed',
        'Anxious'
    ),

    note TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;