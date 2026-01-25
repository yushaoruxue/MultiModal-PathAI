# Git详细操作步骤 - 从零开始（完整版）

## 📍 Git仓库的位置说明

### 本地Git仓库
- **位置**：`E:\java\MultiModal-PathAI\.git\`（隐藏文件夹）
- **说明**：这是你本地的Git仓库，已经初始化完成
- **查看方法**：在文件资源管理器中显示隐藏文件，或使用命令查看

### 远程Git仓库（GitHub）
- **位置**：GitHub网站上的在线仓库
- **说明**：这是代码的云端备份，需要你手动创建
- **作用**：代码备份、团队协作、版本管理

---

## 🎯 完整操作流程

### 第一步：确认Git仓库已初始化

**在PowerShell中执行**（在项目目录 `E:\java\MultiModal-PathAI` 下）：

```bash
# 查看Git状态
git status
```

**预期结果**：应该显示 "On branch master" 和未跟踪的文件列表

**如果显示错误**：说明Git仓库未初始化，执行：
```bash
git init
```

---

### 第二步：配置Git用户信息（首次使用必须）

**检查是否已配置**：
```bash
git config --global user.name
git config --global user.email
```

**如果显示为空，需要配置**：

```bash
# 设置用户名（使用你的GitHub用户名或真实姓名）
git config --global user.name "你的名字"

# 设置邮箱（使用你的GitHub邮箱，必须与GitHub账号邮箱一致）
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

应该能看到你刚才设置的用户名和邮箱。

---

### 第三步：添加文件到Git

```bash
# 查看当前有哪些文件
git status

# 添加所有文件到Git（.gitignore会自动忽略不需要的文件）
git add .

# 再次查看状态，文件应该变成绿色（已添加到暂存区）
git status
```

**说明**：
- `git add .` 会添加当前目录下所有文件
- `.gitignore` 文件会告诉Git哪些文件不需要跟踪（如`.env`、`node_modules/`等）

---

### 第四步：创建第一次提交

```bash
# 创建提交
git commit -m "docs: 初始化项目，添加架构设计和开发规范文档"
```

**提交信息说明**：
- `docs:` 表示这是文档相关的提交
- 后面的描述要清晰说明这次提交做了什么

**查看提交历史**：
```bash
git log --oneline
```

应该能看到你刚才创建的提交。

---

### 第五步：创建分支

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
- 你现在应该在 `develop` 分支上（前面有*号）

---

### 第六步：在GitHub上创建远程仓库（重要！）

这是最关键的一步，需要你在GitHub网站上操作：

#### 6.1 登录GitHub

1. 打开浏览器，访问：https://github.com/
2. 如果没有账号，点击右上角 `Sign up` 注册
3. 如果已有账号，点击右上角 `Sign in` 登录

#### 6.2 创建新仓库

1. **点击右上角的 `+` 号**（在头像旁边）
2. **选择 `New repository`**（新建仓库）

3. **填写仓库信息**：
   - **Repository name**: `MultiModal-PathAI`（或你喜欢的名字）
   - **Description**: `AI赋能职教视频个性化教学系统`（可选）
   - **Visibility**: 
     - 选择 `Private`（私有）- 只有你能看到
     - 或选择 `Public`（公开）- 所有人都能看到
   - **重要**：**不要勾选**以下选项：
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   
   （因为我们本地已经有了这些文件）

4. **点击绿色的 `Create repository` 按钮**

#### 6.3 复制仓库地址

创建成功后，GitHub会显示一个页面，上面有仓库地址，格式类似：

**HTTPS格式**（推荐新手使用）：
```
https://github.com/你的用户名/MultiModal-PathAI.git
```

**SSH格式**（需要配置SSH密钥）：
```
git@github.com:你的用户名/MultiModal-PathAI.git
```

**复制HTTPS地址**（点击地址旁边的复制按钮）

---

### 第七步：连接本地仓库和远程仓库

**回到PowerShell**，执行以下命令（**替换成你刚才复制的地址**）：

```bash
# 添加远程仓库（origin是远程仓库的默认名称）
git remote add origin https://github.com/你的用户名/MultiModal-PathAI.git

# 查看远程仓库配置
git remote -v
```

**预期结果**：
```
origin  https://github.com/你的用户名/MultiModal-PathAI.git (fetch)
origin  https://github.com/你的用户名/MultiModal-PathAI.git (push)
```

**如果显示错误**：
- 如果提示 "remote origin already exists"，说明已经添加过了
- 如果想重新添加，先删除：`git remote remove origin`，然后重新添加

---

### 第八步：推送代码到GitHub

#### 8.1 推送main分支

```bash
# 切换到main分支
git checkout main

# 推送main分支到GitHub（第一次推送）
git push -u origin main
```

**说明**：
- `-u` 参数会设置上游分支，以后可以直接用 `git push`
- 第一次推送可能需要输入GitHub用户名和密码

#### 8.2 处理认证问题

**如果提示输入用户名和密码**：

⚠️ **重要**：GitHub已经不支持密码认证，需要使用Personal Access Token（个人访问令牌）

**生成Token的步骤**：

1. **访问Token设置页面**：
   - 在GitHub网站，点击右上角头像
   - 选择 `Settings`（设置）
   - 左侧菜单找到 `Developer settings`（开发者设置）
   - 点击 `Personal access tokens`（个人访问令牌）
   - 选择 `Tokens (classic)`（经典令牌）
   - 点击 `Generate new token` → `Generate new token (classic)`

2. **配置Token**：
   - **Note**（备注）：填写 `MultiModal-PathAI`（描述用途）
   - **Expiration**（过期时间）：选择 `90 days` 或 `No expiration`（不过期）
   - **Select scopes**（选择权限）：至少勾选以下权限：
     - ✅ `repo`（完整仓库访问权限）- **必须勾选**
     - ✅ `workflow`（如果需要CI/CD）
   - 滚动到底部，点击绿色的 `Generate token` 按钮

3. **复制Token**：
   - ⚠️ **重要**：Token只显示一次，一定要复制保存！
   - 建议保存到安全的地方（如密码管理器）

4. **使用Token**：
   - 当Git要求输入密码时：
     - **Username**（用户名）：输入你的GitHub用户名
     - **Password**（密码）：**粘贴刚才复制的Token**（不是GitHub密码！）

#### 8.3 推送develop分支

```bash
# 切换到develop分支
git checkout develop

# 推送develop分支到GitHub
git push -u origin develop
```

---

### 第九步：验证是否成功

#### 9.1 在GitHub网站验证

1. **刷新GitHub仓库页面**
2. **你应该能看到**：
   - 所有文件都在仓库中
   - 有 `main` 和 `develop` 两个分支
   - 能看到提交历史

#### 9.2 在本地验证

```bash
# 查看远程分支
git branch -r

# 查看所有分支（本地+远程）
git branch -a

# 查看提交历史
git log --oneline --graph --all
```

---

## 📚 日常使用Git的流程

### 开发新功能

```bash
# 1. 确保在develop分支
git checkout develop

# 2. 拉取最新代码
git pull

# 3. 创建功能分支
git checkout -b feature/功能名称

# 4. 开发代码...
# （编辑文件、添加功能等）

# 5. 查看变更
git status

# 6. 添加文件
git add .

# 7. 提交
git commit -m "feat(模块名): 功能描述"

# 8. 推送到远程
git push -u origin feature/功能名称

# 9. 在GitHub上创建Pull Request
# 10. 代码审查通过后，合并到develop分支
```

### 提交信息规范

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

## ❓ 常见问题解答

### Q1: Git仓库在哪里？

**本地仓库**：
- 位置：`E:\java\MultiModal-PathAI\.git\`（隐藏文件夹）
- 查看方法：
  - 文件资源管理器 → 查看 → 显示隐藏文件
  - 或在PowerShell中：`ls -Force` 或 `dir /a`

**远程仓库**：
- 位置：GitHub网站
- 地址：`https://github.com/你的用户名/MultiModal-PathAI`

### Q2: 如何查看远程仓库地址？

```bash
git remote -v
```

### Q3: 如何修改远程仓库地址？

```bash
# 删除旧的远程仓库
git remote remove origin

# 添加新的远程仓库
git remote add origin 新的仓库地址
```

### Q4: 如何撤销最后一次提交？

```bash
# 撤销提交但保留更改
git reset --soft HEAD~1

# 完全撤销提交和更改（谨慎使用）
git reset --hard HEAD~1
```

### Q5: 推送时提示 "remote: Support for password authentication was removed"

**原因**：GitHub已经不支持密码认证

**解决方法**：使用Personal Access Token（见第八步的说明）

### Q6: 如何查看提交历史？

```bash
# 简洁版
git log --oneline

# 图形版
git log --oneline --graph --all

# 详细信息
git log
```

### Q7: 如何切换分支？

```bash
# 切换到已有分支
git checkout 分支名

# 创建并切换到新分支
git checkout -b 新分支名
```

### Q8: 如何查看所有分支？

```bash
# 本地分支
git branch

# 远程分支
git branch -r

# 所有分支（本地+远程）
git branch -a
```

---

## 🎯 快速检查清单

完成以下步骤后，你的Git仓库就完全设置好了：

- [ ] Git用户信息已配置
- [ ] 文件已添加到Git（`git add .`）
- [ ] 已创建第一次提交（`git commit`）
- [ ] 已创建main和develop分支
- [ ] 已在GitHub上创建远程仓库
- [ ] 已连接本地和远程仓库（`git remote add origin`）
- [ ] 已推送main分支到GitHub（`git push -u origin main`）
- [ ] 已推送develop分支到GitHub（`git push -u origin develop`）
- [ ] 在GitHub上能看到所有文件

---

## 🎉 完成！

现在你的Git仓库已经完全设置好了！

**下一步**：
1. 按照《队长实施指南》开始开发核心模块
2. 使用功能分支进行开发
3. 定期提交代码并推送到GitHub

**需要帮助？** 随时查看本文档或询问团队成员。

---

**祝你开发顺利！** 🚀
