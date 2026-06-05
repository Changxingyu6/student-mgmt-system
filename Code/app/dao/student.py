"""
学生数据访问层
使用 SQLAlchemy ORM 进行数据库操作
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from model.student import Student
from scheme.student import StudentCreate, StudentUpdate


def get_students(db: Session, page: int = 1, limit: int = 10) -> List[Student]:
    """获取学生列表"""
    offset = (page - 1) * limit
    return db.query(Student).filter(Student.is_deleted == False).offset(offset).limit(limit).all()


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """根据 ID 获取学生"""
    return db.query(Student).filter(Student.id == student_id, Student.is_deleted == False).first()


def get_student_by_no(db: Session, student_no: str) -> Optional[Student]:
    """根据学生编号获取学生"""
    return db.query(Student).filter(Student.student_no == student_no, Student.is_deleted == False).first()


def create_student(db: Session, student: StudentCreate) -> Student:
    """创建学生"""
    db_student = Student(
        student_no=student.student_no,
        student_name=student.student_name,
        student_class=student.student_class,
        gender=student.gender,
        age=student.age,
        major=student.major,
        hometown=student.hometown,
        graduate_school=student.graduate_school,
        enrollment_date=student.enrollment_date,
        graduation_date=student.graduation_date,
        education=student.education
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: int, student: StudentUpdate) -> Optional[Student]:
    """更新学生信息"""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return None
    
    update_data = student.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    """软删除学生"""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return False
    
    db_student.is_deleted = True
    db.commit()
    return True