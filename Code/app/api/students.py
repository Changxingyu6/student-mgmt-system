"""
学生管理 API 路由
只负责接收请求和返回响应，不包含业务逻辑
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from services import student as student_service
from schema.student import StudentCreate, StudentUpdate
from utils import format_response, require_roles
from database import get_db

# 创建路由
router = APIRouter(
    prefix="/students",
    tags=["学生管理"]
)


@router.get("")
@require_roles(["admin", "teacher"])
def get_students(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10
):
    """获取学生列表 - admin 和 teacher 可访问"""
    data = student_service.get_all_students(db, page, limit)
    return format_response(data=data)


@router.get("/{student_id}")
@require_roles(["admin", "teacher"])
def get_student(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db)
):
    """根据 ID 获取学生信息 - admin 和 teacher 可访问"""
    data = student_service.get_student(db, student_id)
    return format_response(data=data)


@router.post("/")
@require_roles(["admin"])
def create_student(
    request: Request,
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """创建新学生 - 仅 admin 可访问"""
    data = student_service.create_new_student(db, student)
    return format_response(data=data, message="创建成功")


@router.put("/{student_id}")
@require_roles(["admin"])
def update_student(
    request: Request,
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):
    """更新学生信息 - 仅 admin 可访问"""
    data = student_service.update_existing_student(db, student_id, student)
    return format_response(data=data, message="更新成功")


@router.delete("/{student_id}")
@require_roles(["admin"])
def delete_student(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db)
):
    """删除学生 - 仅 admin 可访问"""
    student_service.delete_existing_student(db, student_id)
    return format_response(data=None, message="删除成功")