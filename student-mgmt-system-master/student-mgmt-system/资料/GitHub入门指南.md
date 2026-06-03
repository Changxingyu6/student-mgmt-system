# GitHub 入门指南

> 学生管理系统团队版

---

## 📦 准备

- **项目地址**: https://github.com/Changxingyu6/student-mgmt-system
- **安装 Git**: https://git-scm.com/download/win

---

## 🚀 核心操作

### 1. 首次下载代码
```bash
cd C:\Users\Windows\Desktop\项目
git clone https://github.com/Changxingyu6/student-mgmt-system.git
cd student-mgmt-system
```

### 2. 每日工作流程
```bash
# 早上开工 - 获取最新代码
git checkout main
git pull origin main
git checkout -b feature/你的分支名

# 开发中 - 保存进度
git add .
git commit -m "完成XX功能"

# 下班推送
git push origin feature/你的分支名
```

### 3. 合并到主分支（组长）
```bash
git checkout main
git pull origin main
git merge feature/张三_学生管理
git push origin main
```

---

## 🔑 认证配置（首次推送需要）

### 创建 Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. 勾选 `repo` 权限，生成 token（复制保存！）

### 使用 Token
```bash
# 一次性配置，之后不用再输密码
git remote set-url origin https://<你的Token>@github.com/Changxingyu6/student-mgmt-system.git
```

---

## 🤝 团队协作

### 组长邀请成员
1. 仓库 → Settings → Collaborators → Add people
2. 输入组员 GitHub 用户名/邮箱

### 组员接受邀请
1. 查收邮件或 GitHub 通知
2. 点击 Accept invitation

---

## ❓ 常见问题

**Q1: 拉取代码冲突？**
```bash
git stash          # 暂存修改
git pull origin main
git stash pop      # 恢复并解决冲突
git add . && git commit -m "解决冲突"
```

**Q2: 本地项目初始上传？**
```bash
git init && git add . && git commit -m "Initial"
git remote add origin https://github.com/.../student-mgmt-system.git
git push -u origin main
```

---

## ⚡ 命令速查

| 命令 | 功能 |
|------|------|
| `git add .` | 添加所有修改 |
| `git commit -m "说明"` | 提交到本地 |
| `git push origin <分支>` | 推送到远程 |
| `git pull origin <分支>` | 拉取最新代码 |
| `git checkout -b <分支>` | 创建并切换分支 |