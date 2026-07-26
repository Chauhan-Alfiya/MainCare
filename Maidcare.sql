SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS mindcare;
USE mindcare;

CREATE TABLE roles (
  role_id INT NOT NULL AUTO_INCREMENT,
  role VARCHAR(50) NOT NULL UNIQUE,
  PRIMARY KEY (role_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO roles (role) VALUES
('ADMIN'),
('STUDENT'),
('COUNSELLOR'),

-- USERS TABLE

CREATE TABLE users(

  user_id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL UNIQUE,
  email VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role_id INT NOT NULL,
  role VARCHAR(50) NOT NULL,
  stream VARCHAR(100) NOT NULL,
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
  PRIMARY KEY (user_id),
  FOREIGN KEY (role_id) REFERENCES roles(role_id)
);




CREATE TABLE assessments(

    

);



CREATE TABLE chat_support(
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    message TEXT NOT NULL,
    bot_reply TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

);



CREATE TABLE appointments(

   

);



CREATE TABLE wellness_resources(

   
);

CREATE TABLE wellness_tracker(

    

    
);