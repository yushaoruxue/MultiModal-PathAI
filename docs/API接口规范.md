# AI赋能职教视频个性化教学系统 - API接口规范文档

## 文档信息
- **版本**: v1.0
- **编写日期**: 2025-01-25
- **编写人**: 周东吴（队长）
- **API版本**: v1
- **文档状态**: 初稿

---

## 1. 统一响应格式

### 1.1 成功响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 具体数据
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### 1.2 失败响应格式

```json
{
  "code": 400,
  "message": "错误描述",
  "error_code": "INVALID_PARAMETER",
  "error_detail": {
    "field": "username",
    "reason": "用户名不能为空"
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### 1.3 分页响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

---

## 2. 错误码规范

### 2.1 HTTP状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 请求格式正确但语义错误 |
| 429 | Too Many Requests | 请求频率过高 |
| 500 | Internal Server Error | 服务器内部错误 |

### 2.2 业务错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| SUCCESS | 200 | 成功 |
| INVALID_PARAMETER | 400 | 参数错误 |
| UNAUTHORIZED | 401 | 未认证 |
| FORBIDDEN | 403 | 无权限 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| RESOURCE_CONFLICT | 409 | 资源冲突 |
| VALIDATION_ERROR | 422 | 验证错误 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率过高 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| VIDEO_PARSING_FAILED | 500 | 视频解析失败 |
| AI_SERVICE_ERROR | 500 | AI服务错误 |

---

## 3. 认证授权方案

### 3.1 JWT Token认证

#### 3.1.1 获取Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "student001",
  "password": "password123"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "refresh_token_here"
  }
}
```

#### 3.1.2 使用Token
```http
Authorization: Bearer {access_token}
```

#### 3.1.3 刷新Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token_here"
}
```

---

## 4. OpenAPI 3.0 接口文档

### 4.1 基本信息

```yaml
openapi: 3.0.3
info:
  title: AI赋能职教视频个性化教学系统 API
  description: |
    本API提供视频管理、学习行为采集、难点识别、补偿资源推送、学习路径生成等功能。
  version: 1.0.0
  contact:
    name: API支持
    email: support@example.com

servers:
  - url: https://api.example.com/v1
    description: 生产环境
  - url: https://api-dev.example.com/v1
    description: 开发环境

tags:
  - name: 认证
    description: 用户认证相关接口
  - name: 视频管理
    description: 视频上传、查询、管理
  - name: 学习行为
    description: 观看事件采集、疑难点查询
  - name: 补偿资源
    description: 补偿资源查询、练习提交、反馈
  - name: 学习路径
    description: 学习路径生成、查询、更新
  - name: 教师端
    description: 教师端功能接口

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ErrorResponse:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
        error_code:
          type: string
        error_detail:
          type: object
        timestamp:
          type: string
          format: date-time

    SuccessResponse:
      type: object
      properties:
        code:
          type: integer
          example: 200
        message:
          type: string
          example: "success"
        data:
          type: object
        timestamp:
          type: string
          format: date-time

    Pagination:
      type: object
      properties:
        page:
          type: integer
          example: 1
        page_size:
          type: integer
          example: 20
        total:
          type: integer
          example: 100
        total_pages:
          type: integer
          example: 5
```

### 4.2 视频管理接口

#### 4.2.1 上传视频

```yaml
  /api/videos/upload:
    post:
      tags:
        - 视频管理
      summary: 上传视频
      description: 支持大文件分片上传，支持断点续传
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                title:
                  type: string
                  example: "Python基础教程"
                description:
                  type: string
                  example: "Python编程入门课程"
      responses:
        '201':
          description: 上传成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          video_id:
                            type: integer
                          upload_id:
                            type: string
                          status:
                            type: string
                            example: "uploading"
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
```

#### 4.2.2 获取视频列表

```yaml
  /api/videos:
    get:
      tags:
        - 视频管理
      summary: 获取视频列表
      description: 支持分页、筛选（按状态、上传者等）
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, parsing, completed, failed]
        - name: uploader_id
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          items:
                            type: array
                            items:
                              $ref: '#/components/schemas/Video'
                          pagination:
                            $ref: '#/components/schemas/Pagination'
```

#### 4.2.3 获取视频详情

```yaml
  /api/videos/{id}:
    get:
      tags:
        - 视频管理
      summary: 获取视频详情
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Video'
        '404':
          $ref: '#/components/responses/NotFound'
```

#### 4.2.4 获取视频知识点列表

```yaml
  /api/videos/{id}/knowledge-points:
    get:
      tags:
        - 视频管理
      summary: 获取视频的知识点列表
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          items:
                            type: array
                            items:
                              $ref: '#/components/schemas/KnowledgePoint'
```

#### 4.2.5 删除视频

```yaml
  /api/videos/{id}:
    delete:
      tags:
        - 视频管理
      summary: 删除视频
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 删除成功
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'
```

### 4.3 学习行为接口

#### 4.3.1 上报观看事件

```yaml
  /api/watch-events:
    post:
      tags:
        - 学习行为
      summary: 上报观看事件（批量）
      description: 支持批量上报多个观看事件
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                events:
                  type: array
                  items:
                    $ref: '#/components/schemas/WatchEvent'
      responses:
        '201':
          description: 上报成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          received_count:
                            type: integer
                          processed_count:
                            type: integer
```

#### 4.3.2 获取用户观看事件

```yaml
  /api/users/{id}/watch-events:
    get:
      tags:
        - 学习行为
      summary: 获取用户的观看事件
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
        - name: knowledge_point_id
          in: query
          schema:
            type: integer
        - name: start_time
          in: query
          schema:
            type: string
            format: date-time
        - name: end_time
          in: query
          schema:
            type: string
            format: date-time
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          items:
                            type: array
                            items:
                              $ref: '#/components/schemas/WatchEvent'
                          pagination:
                            $ref: '#/components/schemas/Pagination'
```

#### 4.3.3 获取用户疑难点列表

```yaml
  /api/users/{id}/difficult-points:
    get:
      tags:
        - 学习行为
      summary: 获取用户的疑难点列表
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          items:
                            type: array
                            items:
                              $ref: '#/components/schemas/DifficultPoint'
```

### 4.4 补偿资源接口

#### 4.4.1 获取知识点补偿资源

```yaml
  /api/knowledge-points/{id}/resources:
    get:
      tags:
        - 补偿资源
      summary: 获取知识点的补偿资源
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
        - name: type
          in: query
          schema:
            type: string
            enum: [knowledge_card, exercise, micro_video]
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          items:
                            type: array
                            items:
                              $ref: '#/components/schemas/Resource'
```

#### 4.4.2 提交练习题答案

```yaml
  /api/exercises/{id}/submit:
    post:
      tags:
        - 补偿资源
      summary: 提交练习题答案
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                answer:
                  type: string
                  description: 学生答案
      responses:
        '200':
          description: 提交成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          is_correct:
                            type: boolean
                          score:
                            type: number
                          explanation:
                            type: string
```

#### 4.4.3 提交资源反馈

```yaml
  /api/resources/{id}/feedback:
    post:
      tags:
        - 补偿资源
      summary: 提交资源反馈
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                feedback:
                  type: string
                  enum: [mastered, still_difficult]
      responses:
        '200':
          description: 反馈成功
```

### 4.5 学习路径接口

#### 4.5.1 获取用户学习路径

```yaml
  /api/users/{id}/learning-path:
    get:
      tags:
        - 学习路径
      summary: 获取用户的学习路径
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/LearningPath'
```

#### 4.5.2 重新生成学习路径

```yaml
  /api/users/{id}/learning-path/regenerate:
    post:
      tags:
        - 学习路径
      summary: 重新生成学习路径
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 生成成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/LearningPath'
```

#### 4.5.3 更新知识点掌握状态

```yaml
  /api/users/{id}/mastery/{kp_id}:
    put:
      tags:
        - 学习路径
      summary: 更新知识点掌握状态
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
        - name: kp_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [not_learned, learning, difficult, mastered]
                mastery_score:
                  type: number
                  minimum: 0
                  maximum: 1
      responses:
        '200':
          description: 更新成功
```

### 4.6 教师端接口

#### 4.6.1 获取班级学情统计

```yaml
  /api/classes/{id}/statistics:
    get:
      tags:
        - 教师端
      summary: 获取班级学情统计
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          total_students:
                            type: integer
                          difficult_knowledge_points:
                            type: array
                            items:
                              $ref: '#/components/schemas/DifficultKnowledgePoint'
                          learning_heatmap:
                            type: object
```

#### 4.6.2 编辑知识点信息

```yaml
  /api/knowledge-points/{id}:
    put:
      tags:
        - 教师端
      summary: 编辑知识点信息
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                start_time:
                  type: number
                end_time:
                  type: number
                summary:
                  type: string
                keywords:
                  type: array
                  items:
                    type: string
                difficulty:
                  type: string
                  enum: [easy, medium, hard]
      responses:
        '200':
          description: 更新成功
```

#### 4.6.3 获取知识点困难度统计

```yaml
  /api/knowledge-points/{id}/difficulty-stats:
    get:
      tags:
        - 教师端
      summary: 获取知识点困难度统计
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          difficulty_ratio:
                            type: number
                          average_difficulty_score:
                            type: number
                          affected_students:
                            type: integer
                          recommendation:
                            type: string
```

---

## 5. 数据模型定义

### 5.1 Video（视频）

```yaml
  Video:
    type: object
    properties:
      id:
        type: integer
      uploader_id:
        type: integer
      title:
        type: string
      file_path:
        type: string
      duration:
        type: number
      status:
        type: string
        enum: [pending, parsing, completed, failed]
      description:
        type: string
      upload_time:
        type: string
        format: date-time
      created_at:
        type: string
        format: date-time
      updated_at:
        type: string
        format: date-time
```

### 5.2 KnowledgePoint（知识点）

```yaml
  KnowledgePoint:
    type: object
    properties:
      id:
        type: integer
      video_id:
        type: integer
      name:
        type: string
      start_time:
        type: number
      end_time:
        type: number
      summary:
        type: string
      keywords:
        type: array
        items:
          type: string
      difficulty:
        type: string
        enum: [easy, medium, hard]
      type:
        type: string
      created_at:
        type: string
        format: date-time
      updated_at:
        type: string
        format: date-time
```

### 5.3 WatchEvent（观看事件）

```yaml
  WatchEvent:
    type: object
    required:
      - user_id
      - knowledge_point_id
      - event_type
      - timestamp
    properties:
      user_id:
        type: integer
      knowledge_point_id:
        type: integer
      event_type:
        type: string
        enum: [play, pause, seek, replay]
      timestamp:
        type: number
      duration:
        type: number
      metadata:
        type: object
```

### 5.4 Resource（补偿资源）

```yaml
  Resource:
    type: object
    properties:
      id:
        type: integer
      knowledge_point_id:
        type: integer
      type:
        type: string
        enum: [knowledge_card, exercise, micro_video]
      title:
        type: string
      content:
        type: string
      metadata:
        type: object
      quality_score:
        type: number
      created_at:
        type: string
        format: date-time
```

### 5.5 LearningPath（学习路径）

```yaml
  LearningPath:
    type: object
    properties:
      id:
        type: integer
      user_id:
        type: integer
      knowledge_point_sequence:
        type: array
        items:
          type: object
          properties:
            knowledge_point_id:
              type: integer
            order:
              type: integer
            reason:
              type: string
      current_position:
        type: integer
      created_at:
        type: string
        format: date-time
      updated_at:
        type: string
        format: date-time
```

---

## 6. 请求/响应示例

### 6.1 上传视频示例

**请求**：
```http
POST /api/videos/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [视频文件]
title: Python基础教程
description: Python编程入门课程
```

**响应**：
```json
{
  "code": 201,
  "message": "success",
  "data": {
    "video_id": 123,
    "upload_id": "upload_abc123",
    "status": "uploading"
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### 6.2 获取视频列表示例

**请求**：
```http
GET /api/videos?page=1&page_size=20&status=completed
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 123,
        "title": "Python基础教程",
        "duration": 3600,
        "status": "completed",
        "upload_time": "2025-01-20T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### 6.3 上报观看事件示例

**请求**：
```http
POST /api/watch-events
Authorization: Bearer {token}
Content-Type: application/json

{
  "events": [
    {
      "user_id": 1,
      "knowledge_point_id": 10,
      "event_type": "play",
      "timestamp": 120.5,
      "duration": 30.0
    },
    {
      "user_id": 1,
      "knowledge_point_id": 10,
      "event_type": "pause",
      "timestamp": 150.5,
      "duration": 5.0
    }
  ]
}
```

**响应**：
```json
{
  "code": 201,
  "message": "success",
  "data": {
    "received_count": 2,
    "processed_count": 2
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

---

## 7. 接口调用频率限制

### 7.1 限流策略

| 接口类型 | 限制 | 说明 |
|---------|------|------|
| 认证接口 | 10次/分钟 | 防止暴力破解 |
| 视频上传 | 5次/小时 | 防止滥用 |
| 观看事件上报 | 100次/分钟 | 正常使用足够 |
| 其他接口 | 100次/分钟 | 通用限制 |

### 7.2 限流响应

当超过频率限制时，返回：
```json
{
  "code": 429,
  "message": "请求频率过高",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_detail": {
    "limit": 100,
    "remaining": 0,
    "reset_at": "2025-01-25T10:31:00Z"
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

---

## 8. 文件上传说明

### 8.1 大文件分片上传

对于大于100MB的文件，使用分片上传：

1. **初始化上传**：
```http
POST /api/videos/upload/init
{
  "file_name": "video.mp4",
  "file_size": 500000000,
  "chunk_size": 10485760
}
```

2. **上传分片**：
```http
POST /api/videos/upload/chunk
{
  "upload_id": "upload_abc123",
  "chunk_number": 1,
  "chunk_data": "base64_encoded_data"
}
```

3. **完成上传**：
```http
POST /api/videos/upload/complete
{
  "upload_id": "upload_abc123",
  "chunks": [1, 2, 3, ...]
}
```

### 8.2 支持的文件格式

- **视频**：mp4, avi, mov, mkv
- **图片**：jpg, png, gif
- **文档**：pdf, doc, docx

---

## 9. WebSocket实时推送

### 9.1 连接

```javascript
const ws = new WebSocket('wss://api.example.com/ws?token={access_token}');
```

### 9.2 消息格式

**服务器推送**：
```json
{
  "type": "resource_push",
  "data": {
    "resource_id": 123,
    "knowledge_point_id": 10,
    "resource_type": "knowledge_card",
    "content": "..."
  }
}
```

**客户端确认**：
```json
{
  "type": "ack",
  "resource_id": 123
}
```

---

## 10. 下一步工作

1. ✅ API接口规范设计（本文档）
2. ⏳ 使用FastAPI实现接口
3. ⏳ 集成Swagger UI自动生成API文档
4. ⏳ 编写接口单元测试
5. ⏳ 接口性能测试

---

**文档版本**: v1.0  
**最后更新**: 2025-01-25  
**下次评审**: 待定
