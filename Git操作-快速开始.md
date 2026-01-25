# Git操作 - 快速开始（5分钟搞定）

## 📍 Git仓库位置说明

### 本地Git仓库（已创建）
- **位置**：`E:\java\MultiModal-PathAI\.git\`（隐藏文件夹）
- **状态**：✅ 已初始化完成
- **作用**：记录你本地代码的所有变更历史

### 远程Git仓库（需要你创建）
- **位置**：GitHub网站（https://github.com）
- **状态**：⏳ 待创建
- **作用**：代码云端备份、团队协作

---

## 🚀 快速操作步骤（按顺序执行）

### 步骤1：配置Git用户信息（必须）

**在PowerShell中执行**（在项目目录下）：

```bash
# 设置你的名字（替换成你的真实姓名或GitHub用户名）
git config --global user.name "yushaoruxue"

# 设置你的邮箱（替换成你的GitHub邮箱）
git config --global user.email "18274242128@163.com"
```

**示例**：
```bash
git config --global user.name "周东吴"
git config --global user.email "zhoudongwu@example.com"
```

**验证**：
```bash
git config --global --list
```

---

### 步骤2：添加文件并提交

```bash
# 添加所有文件
git add .

# 创建第一次提交
git commit -m "docs: 初始化项目，添加架构设计和开发规范文档"
```

---

### 步骤3：创建分支

```bash
# 重命名主分支为main
git branch -M main

# 创建develop分支
git checkout -b develop
```

---

### 步骤4：在GitHub上创建仓库（重要！）

#### 4.1 登录GitHub
1. 打开浏览器，访问：**https://github.com/**
2. 登录你的账号（如果没有，先注册）

#### 4.2 创建新仓库
1. 点击右上角 **`+`** 号
2. 选择 **`New repository`**
3. 填写信息：
   - **Repository name**: `MultiModal-PathAI`
   - **Description**: `AI赋能职教视频个性化教学系统`
   - **Visibility**: 选择 `Private`（私有）或 `Public`（公开）
   - ⚠️ **重要**：**不要勾选**任何选项（README、.gitignore、license）
4. 点击 **`Create repository`**

#### 4.3 复制仓库地址
创建成功后，你会看到仓库地址，格式：
```
https://github.com/你的用户名/MultiModal-PathAI.git
```
**复制这个地址**（点击旁边的复制按钮）

---

### 步骤5：连接本地和远程仓库

**回到PowerShell**，执行（**替换成你复制的地址**）：

```bash
# 添加远程仓库
git remote add origin https://github.com/yushaoruxue/MultiModal-PathAI.git

# 查看是否添加成功
git remote -v
```

---

### 步骤6：推送代码到GitHub

```bash
# 推送main分支
git checkout main
git push -u origin main
```

**如果提示输入用户名和密码**：
- **Username**：输入你的GitHub用户名
- **Password**：**不是GitHub密码！** 需要使用Personal Access Token

#### 如何获取Token（如果提示需要密码）：
1. 访问：https://github.com/settings/tokens
2. 点击 `Generate new token` → `Generate new token (classic)`
3. Note填写：`MultiModal-PathAI`
4. 勾选 `repo` 权限
5. 点击 `Generate token`
6. **复制Token**（只显示一次！）
7. 在输入密码时，粘贴Token

```bash
# 推送develop分支
git checkout develop
git push -u origin develop
```

---

### 步骤7：验证

1. **刷新GitHub页面**，应该能看到所有文件
2. **在PowerShell中验证**：
```bash
git branch -r
```

---

## ✅ 完成检查清单

- [ ] Git用户信息已配置
- [ ] 文件已提交（`git commit`）
- [ ] 已创建main和develop分支
- [ ] 已在GitHub创建仓库
- [ ] 已连接远程仓库（`git remote add origin`）
- [ ] 已推送代码到GitHub（`git push`）
- [ ] 在GitHub上能看到所有文件

---

## 📚 详细说明

如果需要更详细的说明，请查看：
- `docs/Git详细操作步骤-从零开始.md` - 完整详细版
- `docs/Git初始化指南.md` - 理论说明版

---

**完成这些步骤后，你的Git仓库就完全设置好了！** 🎉
