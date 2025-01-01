-- 数学练习生成器 PostgreSQL 数据库设置脚本

-- 切换到默认数据库
\c emsdb

-- 删除已存在的用户和数据库（如果需要）
DROP DATABASE IF EXISTS mathworksheetdb;
DROP USER IF EXISTS mathuser;

-- 创建数据库用户
CREATE USER mathuser WITH PASSWORD 'mathpassword';

-- 创建数据库
CREATE DATABASE mathworksheetdb
    WITH 
    OWNER = mathuser
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- 切换到新创建的数据库
\c mathworksheetdb

-- 授予用户对数据库的所有权限
GRANT ALL PRIVILEGES ON DATABASE mathworksheetdb TO mathuser;

-- 创建表结构
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- 练习记录表
CREATE TABLE worksheets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_problems INTEGER,
    correct_problems INTEGER,
    total_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 练习问题表
CREATE TABLE worksheet_problems (
    id SERIAL PRIMARY KEY,
    worksheet_id INTEGER NOT NULL REFERENCES worksheets(id),
    problem VARCHAR(100) NOT NULL,
    user_answer VARCHAR(50),
    correct_answer VARCHAR(50) NOT NULL,
    is_correct BOOLEAN NOT NULL
);

-- 为表添加索引以提高查询性能
CREATE INDEX idx_worksheets_user_id ON worksheets(user_id);
CREATE INDEX idx_worksheets_created_at ON worksheets(created_at);
CREATE INDEX idx_worksheet_problems_worksheet_id ON worksheet_problems(worksheet_id);

-- 授予用户对新创建表的权限
GRANT ALL PRIVILEGES ON TABLE users TO mathuser;
GRANT ALL PRIVILEGES ON TABLE worksheets TO mathuser;
GRANT ALL PRIVILEGES ON TABLE worksheet_problems TO mathuser;
GRANT ALL PRIVILEGES ON SEQUENCE users_id_seq TO mathuser;
GRANT ALL PRIVILEGES ON SEQUENCE worksheets_id_seq TO mathuser;
GRANT ALL PRIVILEGES ON SEQUENCE worksheet_problems_id_seq TO mathuser;

-- 完成
\echo 'PostgreSQL 数据库和表创建完成'
