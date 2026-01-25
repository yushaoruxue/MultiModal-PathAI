# MCP 和 Skill 工具资源指南

## 📚 什么是 MCP 和 Skill？

### MCP (Model Context Protocol)
- **定义**：模型上下文协议，用于扩展 AI 模型的能力
- **作用**：允许 AI 访问外部工具、API、数据库等资源
- **优势**：可以集成自定义工具，扩展 AI 功能

### Skill
- **定义**：预定义的 AI 能力模块或工具集
- **作用**：提供特定领域的 AI 辅助功能
- **类型**：代码生成、文档编写、架构设计等

---

## 🔍 可用的工具和资源

### 1. **Cursor IDE**（推荐⭐⭐⭐⭐⭐）

**简介**：AI-native 代码编辑器（桌面应用程序），内置强大的 AI 能力

**功能**：
- ✅ 代码自动生成和补全
- ✅ 代码审查和优化
- ✅ 文档自动生成
- ✅ 架构设计辅助
- ✅ 支持 MCP 服务器扩展
- ✅ 完整的代码编辑环境（类似 VS Code）

**获取方式**：
- 官网：https://cursor.sh/
- 下载桌面应用程序
- 支持 Windows/Mac/Linux
- 免费版和付费版

**适用场景**：
- 系统架构设计
- 代码开发（主要用途）
- 文档编写
- 代码审查
- 本地项目开发

**特点**：
- 🖥️ **桌面应用**：需要下载安装
- 📁 **本地开发**：直接在本地编辑代码
- 🔧 **完整 IDE**：包含代码编辑、调试、Git 等功能

---

### 1.1. **Cursor Agent**（网页版）

**简介**：Cursor 的网页版 AI Agent 平台，用于项目级别的 AI 辅助

**功能**：
- ✅ 连接 GitHub 仓库
- ✅ 项目级别的 AI 辅助
- ✅ 运行安全审计
- ✅ 改进文档
- ✅ 解决 TODO 任务
- ✅ 批量处理项目任务

**获取方式**：
- 网页版：https://cursor.com/cn/agents
- 无需下载，直接在浏览器使用
- 需要登录账号

**适用场景**：
- 项目级别的任务（如安全审计、文档改进）
- 批量处理代码问题
- 探索和分析代码库
- 不适合日常代码编辑

**特点**：
- 🌐 **网页版**：无需安装，浏览器访问
- 🔗 **连接 GitHub**：可以连接远程仓库
- 🤖 **Agent 模式**：更像是一个 AI 助手，而不是编辑器
- 📊 **Dashboard**：项目管理界面

---

## ⚖️ Cursor IDE vs Cursor Agent 对比

| 特性 | Cursor IDE | Cursor Agent |
|------|-----------|--------------|
| **类型** | 桌面应用程序 | 网页版平台 |
| **主要用途** | 代码编辑和开发 | 项目级 AI 辅助 |
| **使用方式** | 下载安装 | 浏览器访问 |
| **代码编辑** | ✅ 完整 IDE 功能 | ❌ 不支持直接编辑 |
| **本地项目** | ✅ 支持 | ⚠️ 需连接 GitHub |
| **AI 对话** | ✅ 支持（Ctrl+K） | ✅ 支持 |
| **项目分析** | ✅ 支持 | ✅✅ 更强（专门为此设计） |
| **批量任务** | ⚠️ 有限 | ✅✅ 专门设计 |
| **适用场景** | 日常开发 | 项目维护、审计、文档 |

---

## 🎯 如何选择？

### 使用 Cursor IDE 当你需要：
- ✅ **编写代码**：日常开发工作
- ✅ **编辑文件**：修改代码、编写文档
- ✅ **本地开发**：在本地项目上工作
- ✅ **调试代码**：使用 IDE 的调试功能
- ✅ **Git 操作**：版本控制

### 使用 Cursor Agent 当你需要：
- ✅ **项目分析**：分析整个代码库
- ✅ **安全审计**：检查代码安全问题
- ✅ **文档改进**：批量改进项目文档
- ✅ **TODO 处理**：解决项目中的 TODO
- ✅ **代码探索**：理解大型代码库结构

---

## 💡 推荐使用方式

### 组合使用（最佳实践）

1. **日常开发** → 使用 **Cursor IDE**
   - 编写代码
   - 编辑文件
   - 调试程序

2. **项目级任务** → 使用 **Cursor Agent**
   - 安全审计
   - 文档生成
   - 代码分析

### 针对你的项目

**阶段1：需求分析和设计（第1-2周）**
- 使用 **Cursor Agent**：生成需求文档、分析项目结构
- 使用 **Cursor IDE**：编写设计文档、创建项目骨架

**阶段2：开发阶段（第3-8周）**
- 主要使用 **Cursor IDE**：编写代码、开发功能
- 偶尔使用 **Cursor Agent**：代码审查、安全审计

**阶段3：测试和优化（第9-12周）**
- 使用 **Cursor Agent**：运行安全审计、改进文档
- 使用 **Cursor IDE**：修复 bug、优化代码

---

### 2. **Kilo Code**（VS Code 扩展）

**简介**：开源 VS Code 扩展，专门用于 AI 驱动的代码生成

**核心功能**：
- 🚀 根据自然语言生成代码
- 📝 创建和更新文档
- 🔧 代码重构与调试
- 🤔 回答代码库相关问题
- 🔄 自动化重复性任务

**模式支持**：
- **Code模式** - 通用编码任务
- **Architect模式** - 规划和技术领导（**适合队长用**）
- **Ask模式** - 回答问题
- **Debug模式** - 问题诊断
- **自定义模式** - 创建专门角色

**MCP 支持**：
- ✅ 支持 MCP（模型上下文协议）
- ✅ 可添加自定义工具
- ✅ 集成外部 API
- ✅ 连接数据库

**获取方式**：
- 文档：https://kilocode.ai/docs/zh-CN/
- VS Code 扩展市场搜索 "Kilo Code"
- 支持本地模型离线使用

---

### 3. **GitHub Copilot**

**简介**：GitHub 官方 AI 编程助手

**功能**：
- 代码自动补全
- 代码生成
- 代码解释
- 测试生成

**获取方式**：
- 官网：https://github.com/features/copilot
- VS Code/IntelliJ 等 IDE 插件
- 学生可申请免费使用

---

### 4. **腾讯云 MCP 广场**

**简介**：腾讯云开发者社区提供的 MCP 工具集合平台

**功能**：
- 各类 AI 模型和工具集合
- 可能包含代码生成、文档生成等工具

**获取方式**：
- 访问：https://cloud.tencent.cn/developer/mcp
- 需要腾讯云账号

---

### 5. **Anthropic MCP Servers**

**简介**：Anthropic 官方提供的 MCP 服务器集合

**功能**：
- 文件系统操作
- 数据库连接
- Web 搜索
- 代码执行等

**获取方式**：
- GitHub：https://github.com/modelcontextprotocol/servers
- 文档：https://modelcontextprotocol.io/

---

## 🛠️ 针对你的项目的推荐方案

### 方案一：Cursor IDE（最推荐）

**为什么推荐**：
1. ✅ 功能最全面，适合项目开发全流程
2. ✅ 内置 AI 能力强大，无需额外配置
3. ✅ 支持 MCP 扩展，可自定义工具
4. ✅ 界面友好，学习成本低

**如何使用**：
1. 下载安装 Cursor IDE
2. 打开你的项目文件夹
3. 使用 `Ctrl+K`（Windows）或 `Cmd+K`（Mac）触发 AI 对话
4. 直接描述需求，AI 会生成代码或文档

**示例使用场景**：
```
// 在 Cursor 中，你可以直接说：
"帮我设计一个知识点切分算法的 Python 类，包括语义相似度计算和话题转换检测"
```

---

### 方案二：Kilo Code + VS Code

**为什么推荐**：
1. ✅ 如果你习惯用 VS Code
2. ✅ Architect 模式特别适合队长做架构设计
3. ✅ 支持 MCP，可扩展功能
4. ✅ 开源免费

**如何使用**：
1. 在 VS Code 中安装 Kilo Code 扩展
2. 选择 Architect 模式
3. 描述架构需求，AI 会生成设计文档和代码框架

---

### 方案三：GitHub Copilot + 当前 AI 对话

**为什么推荐**：
1. ✅ GitHub Copilot 用于代码生成
2. ✅ 当前 AI 对话（如 Cursor 的 AI）用于文档和设计
3. ✅ 组合使用，覆盖所有需求

**如何使用**：
- GitHub Copilot：写代码时自动补全和生成
- AI 对话：设计架构、编写文档、解决问题

---

## 📦 MCP 服务器推荐

### 1. **文件系统 MCP**
- 功能：读取、写入、搜索文件
- 用途：自动生成项目文档、代码文件
- 获取：https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

### 2. **数据库 MCP**
- 功能：连接数据库，执行查询
- 用途：数据库设计、数据迁移
- 获取：https://github.com/modelcontextprotocol/servers/tree/main/src/postgres

### 3. **Git MCP**
- 功能：Git 操作自动化
- 用途：代码提交、分支管理
- 获取：https://github.com/modelcontextprotocol/servers/tree/main/src/git

### 4. **Web 搜索 MCP**
- 功能：联网搜索信息
- 用途：技术调研、问题解决
- 获取：https://github.com/modelcontextprotocol/servers/tree/main/src/web-search

---

## 🚀 快速开始指南

### 步骤 1：选择工具

**推荐顺序**：
1. **首选**：Cursor IDE（功能最全）
2. **备选**：Kilo Code + VS Code（如果你习惯 VS Code）
3. **补充**：GitHub Copilot（代码补全）

### 步骤 2：安装配置

#### Cursor IDE
1. 访问 https://cursor.sh/
2. 下载对应系统版本
3. 安装并登录（可用 GitHub 账号）
4. 打开项目文件夹

#### Kilo Code
1. 打开 VS Code
2. 搜索扩展 "Kilo Code"
3. 安装并重启 VS Code
4. 配置 API Key（如需要）

### 步骤 3：开始使用

#### 在 Cursor 中创建需求文档
```
1. 打开 Cursor
2. 创建新文件：需求规格说明书.md
3. 按 Ctrl+K，输入：
   "根据我的项目需求，生成一份完整的需求规格说明书，包括：
   - 项目概述
   - 功能需求
   - 非功能需求
   - 数据模型设计
   - 接口设计"
4. AI 会自动生成文档框架
```

#### 在 Cursor 中生成代码
```
1. 创建新文件：knowledge_point_segmenter.py
2. 按 Ctrl+K，输入：
   "实现一个知识点切分算法类，使用 sentence-transformers 计算语义相似度"
3. AI 会生成完整代码
```

---

## 💡 实用技巧

### 1. 使用 MCP 扩展功能

**在 Cursor 中配置 MCP**：
```json
// 在 Cursor 设置中添加 MCP 服务器
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "your-connection-string"
      }
    }
  }
}
```

### 2. 创建自定义 Skill

**示例：需求文档生成 Skill**
```
在 Cursor 中，你可以创建一个自定义的 Prompt 模板：

"你是一个需求分析师，请根据以下信息生成需求文档：
1. 项目名称：[项目名]
2. 核心功能：[功能列表]
3. 目标用户：[用户描述]

请生成包含以下章节的完整需求文档：
- 项目概述
- 功能需求
- 非功能需求
- 数据模型
- 接口设计"
```

### 3. 批量生成代码

**使用 AI 生成项目骨架**：
```
在 Cursor 中，你可以说：
"帮我生成一个 FastAPI 项目的完整结构，包括：
- 项目目录结构
- 配置文件
- 数据库模型
- API 路由
- 依赖注入
- 错误处理"
```

---

## 📋 工具对比表

| 工具 | 代码生成 | 文档生成 | 架构设计 | MCP支持 | 价格 | 推荐度 |
|------|---------|---------|---------|---------|------|--------|
| **Cursor IDE** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 免费/付费 | ⭐⭐⭐⭐⭐ |
| **Kilo Code** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 免费 | ⭐⭐⭐⭐ |
| **GitHub Copilot** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | 付费 | ⭐⭐⭐⭐ |
| **当前AI对话** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 免费 | ⭐⭐⭐⭐ |

---

## 🎯 针对你的具体任务

### 任务1：系统架构设计

**推荐工具**：Cursor IDE 或 Kilo Code（Architect 模式）

**使用方法**：
```
在 Cursor 中：
"帮我设计一个AI赋能职教视频个性化教学系统的架构，包括前端、后端、AI引擎、数据存储四层，请生成架构图和详细说明"
```

### 任务2：数据库设计

**推荐工具**：Cursor IDE + 数据库 MCP

**使用方法**：
```
"根据我的需求文档，生成完整的数据库 ER 图和 SQL 建表语句，包括所有实体和关系"
```

### 任务3：API 接口设计

**推荐工具**：Cursor IDE

**使用方法**：
```
"帮我设计 RESTful API 接口，包括请求/响应格式、错误码、认证方式，生成 OpenAPI 3.0 格式文档"
```

### 任务4：算法实现

**推荐工具**：Cursor IDE 或 GitHub Copilot

**使用方法**：
```
"实现一个知识点切分算法，使用 Python，包括语义相似度计算、话题转换检测、知识点标注"
```

### 任务5：文档编写

**推荐工具**：Cursor IDE 或当前 AI 对话

**使用方法**：
```
"根据我的项目代码，自动生成 API 文档、技术文档、用户手册"
```

---

## 🔗 资源链接汇总

### 官方文档
- **Cursor IDE**：https://cursor.sh/
- **Kilo Code**：https://kilocode.ai/docs/zh-CN/
- **GitHub Copilot**：https://github.com/features/copilot
- **MCP 协议**：https://modelcontextprotocol.io/
- **MCP Servers**：https://github.com/modelcontextprotocol/servers

### 社区资源
- **腾讯云 MCP 广场**：https://cloud.tencent.cn/developer/mcp
- **MCP 社区**：GitHub Discussions

### 学习资源
- **Cursor 教程**：https://docs.cursor.sh/
- **MCP 开发指南**：https://modelcontextprotocol.io/docs

---

## ⚠️ 注意事项

1. **数据安全**：使用 AI 工具时，注意不要上传敏感信息（API密钥、密码等）
2. **代码审查**：AI 生成的代码需要人工审查和测试
3. **版权问题**：确保生成的代码符合项目要求
4. **成本控制**：部分工具按使用量收费，注意控制成本

---

## 🎓 学习路径建议

### 第1周：熟悉工具
1. 安装 Cursor IDE
2. 学习基本操作（Ctrl+K、Ctrl+L）
3. 尝试生成简单代码和文档

### 第2周：深入使用
1. 配置 MCP 服务器
2. 创建自定义 Prompt 模板
3. 批量生成项目代码

### 第3周：高级技巧
1. 使用 AI 进行代码审查
2. 使用 AI 进行性能优化
3. 使用 AI 生成测试用例

---

## 📝 总结

**最佳实践**：
1. ✅ **主要工具**：Cursor IDE（功能最全）
2. ✅ **辅助工具**：GitHub Copilot（代码补全）
3. ✅ **扩展能力**：配置 MCP 服务器
4. ✅ **组合使用**：不同工具用于不同场景

**立即行动**：
1. 下载安装 Cursor IDE
2. 打开你的项目文件夹
3. 开始使用 AI 辅助开发！

---

**祝你开发顺利！** 🚀

如有问题，随时询问！
