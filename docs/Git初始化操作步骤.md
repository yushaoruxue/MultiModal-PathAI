# Git初始化操作步骤 - 实战指南

## ✅ 已完成：Git仓库已初始化

我已经帮你执行了 `git init`，Git仓库已经创建成功！

---

## 📋 接下来你需要做的步骤

### 步骤1：配置Git用户信息（如果还没配置）

**打开PowerShell**，执行以下命令：

```bash
# 设置你的用户名（使用你的GitHub用户名或真实姓名）
git config --global user.name "你的名字"

# 设置你的邮箱（使用你的GitHub邮箱）
git config --global user.email "your.email@example.com"
```

**示例**（请替换成你的真实信息）：
```bash
git config --global user.name "周东吴"
git config --global user.email "zhoudongwu@example.com"
```

**验证配置**：
```bash
git config --global --list
```

---

### 步骤2：查看当前文件状态

```bash
git status
```

你会看到很多文件显示为红色，表示这些文件还没有被Git跟踪。

---

### 步骤3：添加文件到Git

```bash
# 添加所有文件（.gitignore会自动忽略不需要的文件）
git add .
```

**说明**：
- `.gitignore` 文件会告诉Git哪些文件不需要跟踪（如`.env`、`node_modules/`等）
- `git add .` 会添加当前目录下所有文件

**再次查看状态**：
```bash
git status
```

现在文件应该显示为绿色，表示已经添加到暂存区。

---

### 步骤4：创建第一次提交

```bash
git commit -m "docs: 初始化项目，添加架构设计和开发规范文档"
```

**提交信息说明**：
- `docs:` 表示这是文档相关的提交
- 后面的描述要清晰说明这次提交做了什么

**查看提交历史**：
```bash
git log --oneline
```

---

### 步骤5：创建分支

```bash
# 将当前分支重命名为main（如果默认是master）
git branch -M main

# 创建develop分支
git checkout -b develop

# 查看所有分支
git branch
```

**说明**：
- `main` 是主分支（生产环境）
- `develop` 是开发分支（日常开发）
- 你现在应该在 `develop` 分支上

---

### 步骤6：在GitHub上创建远程仓库

1. **登录GitHub**：访问 https://github.com/ 并登录

2. **创建新仓库**：
   - 点击右上角的 `+` 号 → `New repository`
   - Repository name: `MultiModal-PathAI`
   - Description: `AI赋能职教视频个性化教学系统`
   - Visibility: 选择 `Private`（私有）或 `Public`（公开）
   - **重要**：不要勾选 "Initialize this repository with a README"
   - 点击 `Create repository`

3. **复制仓库地址**：
   - 创建成功后，你会看到仓库地址
   - HTTPS格式：`https://github.com/你的用户名/MultiModal-PathAI.git`
   - 或者SSH格式：`git@github.com:你的用户名/MultiModal-PathAI.git`

---

### 步骤7：连接本地和远程仓库

**在PowerShell中执行**（替换成你的仓库地址）：

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/MultiModal-PathAI.git

# 查看远程仓库
git remote -v
```

---

### 步骤8：推送代码到GitHub

```bash
# 1. 先推送main分支
git checkout main
git push -u origin main

# 2. 再推送develop分支
git checkout develop
git push -u origin develop
```

**如果遇到认证问题**：

GitHub已经不支持密码认证，需要使用Personal Access Token：

1. **生成Token**：
   - 访问：https://github.com/settings/tokens
   - 点击 `Generate new token` → `Generate new token (classic)`
   - Note: 填写 `MultiModal-PathAI`（描述用途）
   - Expiration: 选择过期时间（建议90天或更长）
   - Select scopes: 至少勾选 `repo` 权限
   - 点击 `Generate token`
   - **重要**：复制Token（只显示一次，要保存好）

2. **使用Token**：
   - 当Git要求输入密码时，使用Token代替密码
   - 用户名：你的GitHub用户名
   - 密码：粘贴刚才复制的Token

---

## 🎯 完成后的验证

1. **刷新GitHub页面**，你应该能看到所有文件

2. **在本地验证**：
```bash
# 查看远程分支
git branch -r

# 查看提交历史
git log --oneline --graph --all
```

---

## 📚 日常开发工作流

### 开发新功能

```bash
# 1. 确保在develop分支
git checkout develop

# 2. 拉取最新代码
git pull

# 3. 创建功能分支
git checkout -b feature/功能名称

# 4. 开发代码...

# 5. 添加文件
git add .

# 6. 提交
git commit -m "feat(模块名): 功能描述"

# 7. 推送到远程
git push -u origin feature/功能名称

# 8. 在GitHub上创建Pull Request
# 9. 代码审查通过后，合并到develop分支
```

### 提交代码的规范

根据开发规范，提交信息格式：

```
<type>(<scope>): <subject>

例如：
- feat(video): 添加视频上传功能
- fix(api): 修复登录接口错误
- docs(readme): 更新项目README
- refactor(algorithm): 优化知识点切分算法
```

**类型（type）**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

---

## ❓ 常见问题

### Q: 如何撤销最后一次提交？
```bash
# 撤销提交但保留更改
git reset --soft HEAD~1
```

### Q: 如何查看文件变更？
```bash
# 查看工作区变更
git diff

# 查看暂存区变更
git diff --staged
```

### Q: 如何切换分支？
```bash
git checkout 分支名
```

### Q: 如何查看所有分支？
```bash
# 本地分支
git branch

# 远程分支
git branch -r

# 所有分支
git branch -a
```

---

## 🎉 完成！

现在你的Git仓库已经初始化完成，可以开始开发了！

**下一步**：
1. 按照《队长实施指南》开始开发核心模块
2. 使用功能分支进行开发
3. 定期提交代码并推送到GitHub

---

**需要帮助？** 随时查看 `docs/Git初始化指南.md` 获取更详细的说明。
