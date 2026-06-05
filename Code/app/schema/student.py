from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class StudentCreate(BaseModel):
    student_no: str = Field(..., description="学生编号")
    student_class: str = Field(..., description="学生班级")
    student_name: str = Field(..., description="学生姓名")
    hometown: Optional[str] = Field(None, description="籍贯")
    graduate_school: Optional[str] = Field(None, description="毕业院校")
    major: Optional[str] = Field(None, description="专业")
    enrollment_date: Optional[date] = Field(None, description="入学日期")
    graduation_date: Optional[date] = Field(None, description="毕业日期")
    education: Optional[str] = Field(None, description="学历")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")

class StudentUpdate(BaseModel):
    student_no: Optional[str] = Field(None, description="学生编号")
    student_class: Optional[str] = Field(None, description="学生班级")
    student_name: Optional[str] = Field(None, description="学生姓名")
    hometown: Optional[str] = Field(None, description="籍贯")
    graduate_school: Optional[str] = Field(None, description="毕业院校")
    major: Optional[str] = Field(None, description="专业")
    enrollment_date: Optional[date] = Field(None, description="入学日期")
    graduation_date: Optional[date] = Field(None, description="毕业日期")
    education: Optional[str] = Field(None, description="学历")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")

class StudentResponse(BaseModel):
    id: int = Field(..., description="学生 ID")
    student_no: str = Field(..., description="学生编号")
    student_class: str = Field(..., description="学生班级")
    student_name: str = Field(..., description="学生姓名")
    hometown: Optional[str] = Field(None, description="籍贯")
    graduate_school: Optional[str] = Field(None, description="毕业院校")
    major: Optional[str] = Field(None, description="专业")
    enrollment_date: Optional[date] = Field(None, description="入学日期")
    graduation_date: Optional[date] = Field(None, description="毕业日期")
    education: Optional[str] = Field(None, description="学历")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    is_deleted: bool = Field(False, description="是否删除")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True
