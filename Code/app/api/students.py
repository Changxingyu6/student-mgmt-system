"""
学生管理 API 路由
只负责接收请求和返回响应，不包含业务逻辑
"""
from fastapi import APIRouter, Depends
from deps import get_current_user
from services import student as student_service
from schema.student import StudentCreate, StudentUpdate
from utils import format_response

# 创建路由时添加依赖注入，所有接口自动需要认证
router = APIRouter(
    prefix="/students",
    tags=["学生管理"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/")
def get_students(
    data = Depends(student_service.get_all_students)
):
    """获取学生列表"""
    return format_response(data=data)


@router.get("/{student_id}")
def get_student(
    student_id: int,
    data = Depends(student_service.get_student)
):
    """根据 ID 获取学生信息"""
    return format_response(data=data)


@router.post("/")
def create_student(
    student: StudentCreate,
    data = Depends(student_service.create_new_student)
):
    """创建新学生"""
    return format_response(data=data, message="创建成功")


@router.put("/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate,
    data = Depends(student_service.update_existing_student)
):
    """更新学生信息"""
    return format_response(data=data, message="更新成功")


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    data = Depends(student_service.delete_existing_student)
):
    """删除学生"""
    return format_response(data=None, message="删除成功")