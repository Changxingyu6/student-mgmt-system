"""
学生业务逻辑层
负责学生相关的业务逻辑处理（验证、规则、事务等）
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from fastapi import HTTPException, Depends
from dao import student as student_repo
from scheme.student import StudentCreate, StudentUpdate, StudentResponse
from database import get_db


def get_all_students(
    page: int = 1, 
    limit: int = 10, 
    db: Session = Depends(get_db)
) -> List[StudentResponse]:
    """获取学生列表"""
    students = student_repo.get_students(db, page=page, limit=limit)
    return [StudentResponse.from_orm(student) for student in students]


def get_student(
    student_id: int, 
    db: Session = Depends(get_db)
) -> StudentResponse:
    """获取单个学生（带错误处理）"""
    student = student_repo.get_student_by_id(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    return StudentResponse.from_orm(student)


def create_new_student(
    student: StudentCreate, 
    db: Session = Depends(get_db)
) -> StudentResponse:
    """创建新学生（带验证）"""
    # 验证学生编号是否已存在
    existing = student_repo.get_student_by_no(db, student.student_no)
    if existing:
        raise HTTPException(status_code=400, detail="学生编号已存在")
    
    # 创建学生
    db_student = student_repo.create_student(db, student)
    
    # 返回创建的学生信息
    return StudentResponse.from_orm(db_student)


def update_existing_student(
    student_id: int, 
    student: StudentUpdate, 
    db: Session = Depends(get_db)
) -> StudentResponse:
    """更新学生信息（带验证）"""
    # 检查学生是否存在
    existing = student_repo.get_student_by_id(db, student_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 如果修改了学生编号，检查新编号是否已被使用
    if student.student_no and student.student_no != existing.student_no:
        conflict = student_repo.get_student_by_no(db, student.student_no)
        if conflict:
            raise HTTPException(status_code=400, detail="学生编号已存在")
    
    # 更新学生
    db_student = student_repo.update_student(db, student_id, student)
    
    # 返回更新后的学生信息
    return StudentResponse.from_orm(db_student)


def delete_existing_student(
    student_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """删除学生（带验证）"""
    # 检查学生是否存在
    existing = student_repo.get_student_by_id(db, student_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 删除学生
    student_repo.delete_student(db, student_id)
    
    return {"message": "学生删除成功"}