-- 沃林学生管理系统 - 数据库初始化脚本
-- 在MySQL中执行此脚本创建数据库和表

-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE student_db;

-- 1. 学生表
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '学生ID',
    student_no VARCHAR(20) UNIQUE NOT NULL COMMENT '学生编号',
    student_class VARCHAR(50) NOT NULL COMMENT '学生班级',
    student_name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    hometown VARCHAR(100) COMMENT '籍贯',
    graduate_school VARCHAR(100) COMMENT '毕业院校',
    major VARCHAR(50) COMMENT '专业',
    enrollment_date DATE COMMENT '入学时间',
    graduation_date DATE COMMENT '毕业时间',
    education VARCHAR(20) COMMENT '学历',
    age INT COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (student_name),
    INDEX idx_class (student_class)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';

-- 2. 成绩表
CREATE TABLE IF NOT EXISTS scores (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '成绩ID',
    student_id INT NOT NULL COMMENT '学生ID',
    exam_no INT NOT NULL COMMENT '考核序次（第几次考试）',
    score FLOAT NOT NULL COMMENT '成绩',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_student_exam (student_id, exam_no),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生考核成绩表';

-- 3. 就业信息表
CREATE TABLE IF NOT EXISTS employments (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '就业ID',
    student_id INT UNIQUE NOT NULL COMMENT '学生ID',
    employment_open_date DATE COMMENT '就业开放时间',
    offer_date DATE COMMENT 'offer下发时间',
    company_name VARCHAR(100) COMMENT '就业公司名称',
    salary DECIMAL(10, 2) COMMENT '就业薪资',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_company (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生就业信息表';

-- 4. 班级表
CREATE TABLE IF NOT EXISTS classes (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '班级ID',
    class_no VARCHAR(20) UNIQUE NOT NULL COMMENT '班级编号',
    class_name VARCHAR(50) NOT NULL COMMENT '班级名称',
    start_date DATE COMMENT '开课时间',
    head_teacher_id INT COMMENT '班主任ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_class_no (class_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级信息表';

-- 5. 老师表
CREATE TABLE IF NOT EXISTS teachers (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '老师ID',
    teacher_no VARCHAR(20) UNIQUE NOT NULL COMMENT '老师编号',
    teacher_name VARCHAR(50) NOT NULL COMMENT '老师姓名',
    phone VARCHAR(20) COMMENT '电话',
    email VARCHAR(100) COMMENT '邮箱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='老师信息表';

-- 添加班级表外键约束（老师表创建后）
ALTER TABLE classes 
ADD FOREIGN KEY (head_teacher_id) REFERENCES teachers(id) ON DELETE SET NULL;

-- 6. 班级课程关联表
CREATE TABLE IF NOT EXISTS class_courses (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    class_id INT NOT NULL COMMENT '班级ID',
    teacher_id INT NOT NULL COMMENT '老师ID',
    course_name VARCHAR(50) NOT NULL COMMENT '课程名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_class_course (class_id, course_name),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级课程关联表';

-- 7. 顾问表（预留）
CREATE TABLE IF NOT EXISTS advisors (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '顾问ID',
    advisor_no VARCHAR(20) UNIQUE NOT NULL COMMENT '顾问编号',
    advisor_name VARCHAR(50) NOT NULL COMMENT '顾问姓名',
    phone VARCHAR(20) COMMENT '电话',
    email VARCHAR(100) COMMENT '邮箱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='顾问信息表';

-- 插入测试数据
-- 老师数据
INSERT INTO teachers (teacher_no, teacher_name, phone, email) VALUES
('T001', '张老师', '13800138001', 'zhang@school.com'),
('T002', '李老师', '13800138002', 'li@school.com'),
('T003', '王老师', '13800138003', 'wang@school.com');

-- 班级数据
INSERT INTO classes (class_no, class_name, start_date, head_teacher_id) VALUES
('C001', 'Python一班', '2024-03-01', 1),
('C002', 'Python二班', '2024-03-01', 2),
('C003', 'Java一班', '2024-06-01', 3);

-- 班级课程关联数据
INSERT INTO class_courses (class_id, teacher_id, course_name) VALUES
(1, 1, 'Python基础'),
(1, 2, '数据库'),
(2, 1, 'Python基础'),
(2, 3, 'Web开发'),
(3, 2, 'Java基础'),
(3, 3, 'Spring框架');

-- 学生数据
INSERT INTO students (student_no, student_class, student_name, hometown, graduate_school, major, enrollment_date, education, age, gender) VALUES
('S001', 'C001', '张三', '北京', '北京大学', '计算机', '2024-03-01', '本科', 22, '男'),
('S002', 'C001', '李四', '上海', '复旦大学', '软件工程', '2024-03-01', '本科', 23, '女'),
('S003', 'C002', '王五', '广州', '中山大学', '计算机', '2024-03-01', '本科', 21, '男'),
('S004', 'C002', '赵六', '深圳', '深圳大学', '网络工程', '2024-03-01', '本科', 24, '女'),
('S005', 'C003', '孙七', '杭州', '浙江大学', '计算机', '2024-06-01', '硕士', 25, '男');

-- 成绩数据
INSERT INTO scores (student_id, exam_no, score) VALUES
(1, 1, 85), (1, 2, 88), (1, 3, 92),
(2, 1, 78), (2, 2, 82), (2, 3, 80),
(3, 1, 90), (3, 2, 85),
(4, 1, 65), (4, 2, 58), (4, 3, 70),
(5, 1, 88);

-- 就业数据
INSERT INTO employments (student_id, employment_open_date, offer_date, company_name, salary) VALUES
(1, '2024-09-01', '2024-09-15', '字节跳动', 15000.00),
(2, '2024-09-01', '2024-10-01', '腾讯', 18000.00),
(3, '2024-09-01', '2024-09-20', '阿里巴巴', 16000.00);
