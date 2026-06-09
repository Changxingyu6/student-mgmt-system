"""公共类型定义"""
from typing import Annotated, TypeAlias
from pydantic import StringConstraints


# ========== 自定义类型定义 ==========
# ID类型：支持多种ID格式
# 1. UUID（36位带连字符）：a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890
# 2. UUID（32位无连字符）：a1b2c3d4e5f67890a1b2c3d4e5f67890
# 3. 雪花ID（19位）：1843672850827264000
# 4. 普通数字ID（10-20位）：1234567890

# 定义ID类型别名：支持多种ID格式，长度不超过50
IDStr: TypeAlias = Annotated[
    str,
    StringConstraints(max_length=50)
]

# 保持向后兼容的别名
UUIDStr: TypeAlias = IDStr
