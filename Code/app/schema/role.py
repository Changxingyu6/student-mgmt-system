"""
角色相关 Schema
定义角色的请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleCreateRequest(BaseModel):
    """角色创建请求"""
    role_name: str = Field(..., description="角色名称", max_length=50)
    description: Optional[str] = Field(None, description="角色描述", max_length=255)


class RoleUpdateRequest(BaseModel):
    """角色更新请求"""
    role_name: Optional[str] = Field(None, description="角色名称", max_length=50)
    description: Optional[str] = Field(None, description="角色描述", max_length=255)
    status: Optional[str] = Field(None, description="状态", pattern='^(active|inactive)$')


class RoleResponse(BaseModel):
    """角色响应"""
    id: str
    role_name: str
    description: Optional[str]
    status: str
    create_time: datetime
    update_time: datetime

    class Config:
        orm_mode = True


class RoleListResponse(BaseModel):
    """角色列表响应"""
    total: int
    items: List[RoleResponse]


class UserRoleUpdateRequest(BaseModel):
    """用户角色更新请求"""
    role_id: str = Field(..., description="角色ID")
