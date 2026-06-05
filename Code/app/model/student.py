"""
学生模型
映射数据库 students 表
"""
from sqlalchemy import Column, Integer, String, Date, Boolean
from model import BaseModel


class Student(BaseModel):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_no = Column(String(20), unique=True, nullable=False, index=True, comment="学号")
    student_class = Column(String(50), nullable=False, index=True, comment="班级")
    student_name = Column(String(50), nullable=False, index=True, comment="姓名")
    hometown = Column(String(100), comment="籍贯")
    graduate_school = Column(String(100), comment="毕业学校")
    major = Column(String(50), comment="专业")
    enrollment_date = Column(Date, comment="入学日期")
    graduation_date = Column(Date, comment="毕业日期")
    education = Column(String(20), comment="学历")
    age = Column(Integer, comment="年龄")
    gender = Column(String(10), comment="性别")
    is_deleted = Column(Boolean, default=False, comment="是否删除")