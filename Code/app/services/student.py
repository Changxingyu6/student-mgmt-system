"""
学生业务逻辑层
负责学生相关的业务逻辑处理（验证、规则、事务等）
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from dao import student as student_repo
from schema.student import StudentCreate, StudentUpdate, StudentResponse
from utils.logger import get_logger

# 获取日志记录器
logger = get_logger("student")


def get_all_students(db: Session, page: int = 1, limit: int = 10) -> List[StudentResponse]:
    """获取学生列表"""
    logger.debug(f"获取学生列表 - 页码: {page}, 每页数量: {limit}")
    students = student_repo.get_students(db, page=page, limit=limit)
    logger.info(f"获取学生列表成功 - 共 {len(students)} 条记录")
    return [StudentResponse.model_validate(student) for student in students]


def get_student(db: Session, student_id: int) -> StudentResponse:
    """获取单个学生（带错误处理）"""
    logger.debug(f"获取学生信息 - 学生ID: {student_id}")
    student = student_repo.get_student_by_id(db, student_id)
    if student is None:
        logger.warn(f"获取学生失败 - 学生不存在 - 学生ID: {student_id}")
        raise HTTPException(status_code=404, detail="学生不存在")
    logger.debug(f"获取学生成功 - 学生ID: {student_id}, 姓名: {student.student_name}")
    return StudentResponse.model_validate(student)


def create_new_student(db: Session, student: StudentCreate) -> StudentResponse:
    """创建新学生（带验证）"""
    logger.info(f"创建学生 - 学号: {student.student_no}, 姓名: {student.student_name}")
    
    # 验证学生编号是否已存在
    existing = student_repo.get_student_by_no(db, student.student_no)
    if existing:
        logger.warn(f"创建学生失败 - 学号已存在 - 学号: {student.student_no}")
        raise HTTPException(status_code=400, detail="学生编号已存在")
    
    # 创建学生
    db_student = student_repo.create_student(db, student)
    
    logger.info(f"创建学生成功 - 学生ID: {db_student.id}, 学号: {db_student.student_no}")
    
    # 返回创建的学生信息
    return StudentResponse.model_validate(db_student)


def update_existing_student(db: Session, student_id: int, student: StudentUpdate) -> StudentResponse:
    """更新学生信息（带验证）"""
    logger.info(f"更新学生信息 - 学生ID: {student_id}")
    
    # 检查学生是否存在
    existing = student_repo.get_student_by_id(db, student_id)
    if existing is None:
        logger.warn(f"更新学生失败 - 学生不存在 - 学生ID: {student_id}")
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 如果修改了学生编号，检查新编号是否已被使用
    if student.student_no and student.student_no != existing.student_no:
        conflict = student_repo.get_student_by_no(db, student.student_no)
        if conflict:
            logger.warn(f"更新学生失败 - 学号已存在 - 学号: {student.student_no}")
            raise HTTPException(status_code=400, detail="学生编号已存在")
    
    # 更新学生
    db_student = student_repo.update_student(db, student_id, student)
    
    logger.info(f"更新学生成功 - 学生ID: {student_id}, 姓名: {db_student.student_name}")
    
    # 返回更新后的学生信息
    return StudentResponse.model_validate(db_student)


def delete_existing_student(db: Session, student_id: int) -> dict:
    """删除学生（带验证）"""
    logger.info(f"删除学生 - 学生ID: {student_id}")
    
    # 检查学生是否存在
    existing = student_repo.get_student_by_id(db, student_id)
    if existing is None:
        logger.warn(f"删除学生失败 - 学生不存在 - 学生ID: {student_id}")
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 删除学生
    student_repo.delete_student(db, student_id)
    
    logger.info(f"删除学生成功 - 学生ID: {student_id}, 姓名: {existing.student_name}")
    
    return {"message": "学生删除成功"}