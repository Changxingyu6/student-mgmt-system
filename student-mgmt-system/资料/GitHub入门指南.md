# GitHub 入门指南 - 6人团队协作版

> 专为学生管理系统团队准备的极简入门教程

---

## 目录
1. [注册账号](#1-注册账号)
2. [创建仓库](#2-创建仓库)
3. [安装 Git](#3-安装-git)
4. [配置 Git](#4-配置-git)
5. [克隆仓库](#5-克隆仓库)
6. [本地开发](#6-本地开发)
7. [提交代码](#7-提交代码)
8. [推送代码](#8-推送代码)
9. [拉取更新](#9-拉取更新)
10. [团队协作流程](#10-团队协作流程)
11. [常见问题](#11-常见问题)

---

## 1. 注册账号

### 访问网址
- **GitHub**: https://github.com/
- **Gitee（国内推荐）**: https://gitee.com/

### 注册步骤
1. 打开网址，点击「Sign up」或「注册」
2. 输入邮箱、用户名、密码
3. 验证邮箱（重要！）

---

## 2. 创建仓库（组长操作）

### 步骤
1. 登录后，点击右上角 `+` → `New repository`
2. 填写信息：
   - Repository name: `student-mgmt-system`
   - Description: 学生管理系统
   - 勾选 `Initialize this repository with a README`
   - 点击 `Create repository`

### 获取仓库地址
创建成功后，点击绿色按钮 `Code`，复制 **HTTPS** 地址，类似：
```
https://github.com/你的用户名/student-mgmt-system.git
```

---
## 3. 安装 Git

### Windows 安装
1. 下载地址：https://git-scm.com/download/win
2. 运行安装程序，一路点击「Next」即可
3. 安装完成后，打开命令提示符（CMD）或 PowerShell，输入：
```bash
git --version
```
显示版本号即安装成功。

---

## 4. 配置 Git（每个成员都要做）

### 设置用户名和邮箱
打开命令行，输入以下命令：
```bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
```

### 验证配置
```bash
git config --list
```

---

## 5. 克隆仓库（第一次获取代码）

### 在本地创建工作目录
```bash
cd C:\Users\Windows\Desktop\student_mgmt
mkdir team_project
cd team_project
```

### 克隆远程仓库
```bash
git clone https://github.com/你的用户名/student-mgmt-system.git
```

### 进入项目目录
```bash
cd student-mgmt-system
```

---

## 6. 本地开发

### 创建自己的分支（每人一个分支）
```bash
git checkout -b feature/你的名字_模块名
# 例如：git checkout -b feature/张三_学生管理
```

### 查看当前分支
```bash
git branch
```

### 创建/修改文件
在本地目录中编写代码，例如创建 `students.py`

---

## 7. 提交代码

### 查看修改状态
```bash
git status
```

### 添加修改到暂存区
```bash
git add .          # 添加所有修改
# 或
git add students.py  # 添加特定文件
```

### 提交到本地仓库
```bash
git commit -m "完成学生管理模块的新增功能"
```
> 注意：commit 信息要清晰描述做了什么

---

## 8. 推送代码到远程

### 推送到自己的分支
```bash
git push origin feature/你的名字_模块名
```

### 推送到主分支（谨慎使用）
```bash
git checkout main
git push origin main
```

---

## 9. 拉取更新（获取队友代码）

### 切换到主分支
```bash
git checkout main
```

### 拉取最新代码
```bash
git pull origin main
```

---

## 10. 团队协作流程

### 推荐工作流程
```
┌────────────────────────────────────────────────────────────┐
│ 1. 早上开工                                               │
│    git checkout main                                      │
│    git pull origin main    ← 获取最新代码                  │
│    git checkout -b feature/你的分支名   ← 创建/切换分支     │
│                                                           │
│ 2. 白天开发                                               │
│    编写代码...                                            │
│                                                           │
│ 3. 晚上提交                                               │
│    git add .                                             │
│    git commit -m "完成XX功能"                             │
│    git push origin feature/你的分支名   ← 推送到远程       │
│                                                           │
│ 4. 合并到主分支（组长操作）                                │
│    git checkout main                                      │
│    git merge feature/你的分支名                           │
│    git push origin main                                  │
└────────────────────────────────────────────────────────────┘
```

### 分工建议（6人小组）
| 成员 | 负责模块 | 分支名称示例 |
|------|---------|------------|
| 张三 | 学生管理 | feature/zhangsan_students |
| 李四 | 成绩管理 | feature/lisi_scores |
| 王五 | 就业管理 | feature/wangwu_employment |
| 赵六 | 班级管理 | feature/zhaoliu_classes |
| 钱七 | 统计分析 | feature/qianqi_statistics |
| 孙八 | 配置文档 | feature/sunba_config |

---

## 11. 常见问题

### Q1: 提示输入用户名密码？
**解决方案**：使用个人访问令牌（Personal Access Token）
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token，勾选 repo 权限
3. 复制 token，推送时代替密码输入

### Q2: 拉取代码冲突？
```bash
# 先保存自己的修改
git stash

# 拉取最新代码
git pull origin main

# 恢复自己的修改
git stash pop

# 手动解决冲突文件，然后重新提交
```

### Q3: 误删文件怎么恢复？
```bash
git checkout -- 文件名
```

### Q4: 查看历史记录？
```bash
git log
git log --oneline  # 简洁显示
```

---

## 命令速查表

| 命令 | 功能 |
|------|------|
| `git init` | 初始化仓库 |
| `git clone <url>` | 克隆仓库 |
| `git status` | 查看状态 |
| `git add .` | 添加所有修改 |
| `git commit -m "message"` | 提交代码 |
| `git push origin <branch>` | 推送代码 |
| `git pull origin <branch>` | 拉取代码 |
| `git branch` | 查看分支 |
| `git checkout <branch>` | 切换分支 |
| `git checkout -b <branch>` | 创建并切换分支 |
| `git merge <branch>` | 合并分支 |

---

## 学习资源
- 🎬 B站视频：https://www.bilibili.com/video/BV1FE411P7B3
- 📖 官方文档：https://docs.github.com/zh
- 🎮 互动学习：https://learngitbranching.js.org/

---

> 祝你们团队协作顺利！🚀