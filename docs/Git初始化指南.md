# Git仓库初始化指南

## 📋 前置准备

在开始之前，确保你已经：
1. ✅ 安装了Git（如果没有，请访问 https://git-scm.com/ 下载安装）
2. ✅ 有GitHub账号（如果没有，请访问 https://github.com/ 注册）

---

## 🚀 步骤一：检查Git是否已安装

打开PowerShell或命令提示符，输入：

```bash
git --version
```

如果显示版本号（如 `git version 2.40.0`），说明Git已安装。如果没有，请先安装Git。

---

## 🔧 步骤二：配置Git用户信息（首次使用需要）

如果你第一次使用Git，需要配置你的用户名和邮箱：

```bash
# 设置用户名（使用你的GitHub用户名或真实姓名）
git config --global user.name "你的名字"

# 设置邮箱（使用你的GitHub邮箱）
git config --global user.email "your.email@example.com"
```

**示例**：
```bash
git config --global user.name "周东吴"
git config --global user.email "zhoudongwu@example.com"
```

**验证配置**：
```bash
git config --global --list
```

---

## 📦 步骤三：初始化本地Git仓库

在项目根目录（`E:\java\MultiModal-PathAI`）下执行：

```bash
# 1. 初始化Git仓库
git init

# 2. 查看当前状态
git status
```

**说明**：
- `git init` 会在当前目录创建一个`.git`隐藏文件夹，这是Git仓库的核心
- `git status` 会显示当前有哪些文件还没有被Git跟踪

---

## 📝 步骤四：添加文件到Git

```bash
# 添加所有文件到暂存区
git add .

# 或者只添加特定文件
git add README.md
git add .gitignore
git add docs/
```

**说明**：
- `git add .` 会添加当前目录下所有文件（除了`.gitignore`中忽略的文件）
- 文件被添加到"暂存区"（staging area），还没有真正提交

**查看暂存区状态**：
```bash
git status
```

---

## 💾 步骤五：创建第一次提交（Commit）

```bash
# 创建提交，并添加提交信息
git commit -m "docs: 初始化项目，添加架构设计和开发规范文档"
```

**说明**：
- `-m` 后面是提交信息，要遵循Conventional Commits规范
- 这是项目的第一次提交，通常称为"初始提交"（initial commit）

**提交信息格式**：
```
<type>(<scope>): <subject>

例如：
- feat(video): 添加视频上传功能
- docs(readme): 更新项目README
- fix(api): 修复登录接口错误
```

---

## 🌿 步骤六：创建分支（可选，但推荐）

根据开发规范，我们应该创建`main`和`develop`分支：

```bash
# 1. 将当前分支重命名为main（如果默认是master）
git branch -M main

# 2. 创建develop分支
git checkout -b develop

# 3. 查看所有分支
git branch
```

**说明**：
- `main` 是主分支，用于生产环境
- `develop` 是开发分支，用于日常开发
- 新功能应该在`develop`分支上开发

---

## ☁️ 步骤七：在GitHub上创建远程仓库

1. **登录GitHub**：访问 https://github.com/ 并登录

2. **创建新仓库**：
   - 点击右上角的 `+` 号
   - 选择 `New repository`
   - 填写仓库信息：
     - Repository name: `MultiModal-PathAI`（或你喜欢的名字）
     - Description: `AI赋能职教视频个性化教学系统`
     - Visibility: 选择 `Private`（私有）或 `Public`（公开）
     - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
   - 点击 `Create repository`

3. **复制仓库地址**：
   - 创建成功后，GitHub会显示仓库地址
   - 格式类似：`https://github.com/你的用户名/MultiModal-PathAI.git`
   - 或者SSH格式：`git@github.com:你的用户名/MultiModal-PathAI.git`

---

## 🔗 步骤八：连接本地仓库和远程仓库

```bash
# 添加远程仓库（origin是远程仓库的默认名称）
git remote add origin https://github.com/你的用户名/MultiModal-PathAI.git

# 查看远程仓库
git remote -v
```

**说明**：
- `origin` 是远程仓库的别名，可以自定义
- 如果使用SSH，地址格式是：`git@github.com:用户名/仓库名.git`

---

## 📤 步骤九：推送代码到GitHub

```bash
# 1. 确保你在main分支
git checkout main

# 2. 推送main分支到远程仓库
git push -u origin main

# 3. 推送develop分支到远程仓库
git checkout develop
git push -u origin develop
```

**说明**：
- `-u` 参数会设置上游分支，以后可以直接用 `git push` 和 `git pull`
- 第一次推送可能需要输入GitHub用户名和密码（或Personal Access Token）

**如果遇到认证问题**：
- GitHub已经不支持密码认证，需要使用Personal Access Token
- 生成Token：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- 权限选择：至少勾选 `repo` 权限
- 复制Token，在输入密码时使用Token代替密码

---

## ✅ 步骤十：验证

1. **刷新GitHub页面**，你应该能看到所有文件已经上传

2. **在本地验证**：
```bash
# 查看远程分支
git branch -r

# 查看提交历史
git log --oneline
```

---

## 📚 常用Git命令速查

### 日常开发流程

```bash
# 1. 查看状态
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "feat: 添加新功能"

# 4. 推送到远程
git push

# 5. 从远程拉取更新
git pull
```

### 分支操作

```bash
# 创建新分支
git checkout -b feature/新功能名称

# 切换分支
git checkout 分支名

# 查看所有分支
git branch

# 合并分支
git checkout develop
git merge feature/新功能名称
```

### 查看历史

```bash
# 查看提交历史
git log

# 查看简洁历史
git log --oneline

# 查看文件变更
git diff
```

---

## 🎯 下一步

现在Git仓库已经初始化完成，你可以：

1. **开始开发**：按照开发规范创建功能分支
2. **团队协作**：邀请团队成员加入仓库
3. **设置保护分支**：在GitHub上设置main和develop分支的保护规则

---

## ❓ 常见问题

### Q1: 如何撤销最后一次提交？
```bash
# 撤销提交但保留更改
git reset --soft HEAD~1

# 完全撤销提交和更改（谨慎使用）
git reset --hard HEAD~1
```

### Q2: 如何忽略已提交的文件？
```bash
# 1. 添加到.gitignore
echo "文件名" >> .gitignore

# 2. 从Git中移除（但保留本地文件）
git rm --cached 文件名

# 3. 提交
git commit -m "chore: 从Git中移除文件"
```

### Q3: 如何查看远程仓库地址？
```bash
git remote -v
```

### Q4: 如何修改远程仓库地址？
```bash
git remote set-url origin 新的仓库地址
```

---

**祝你使用愉快！** 🚀

如有问题，随时查阅Git文档或询问团队成员。
