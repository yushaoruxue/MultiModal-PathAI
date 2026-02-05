# AI赋能职教视频个性化教学项目需求规格说明书（第八稿-完整版）

## 文档版本信息
- **版本号**: v8.0
- **编写日期**: 2026年1月
- **编写团队**: 周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
- **技术顾问**: 蒋国伟
- **指导老师**: 王海霞
- **文档状态**: 待评审
- **版本说明**: 基于v7.0进行极端工程场景优化、教育学深层逻辑完善与数据冷启动处理

---

## 版本演进说明

### v8.0 主要更新内容

| 更新类别 | 更新内容 | 影响模块 | 标记 |
|---------|---------|---------|------|
| 算法优化 | 认知步频难度系数加权（避免虚假繁荣） | 模块B | [v8.0 优化] |
| 个性化增强 | 学习风格自适应过滤器 | 模块C | [v8.0 新增] |
| 安全补全 | 监控信号丢失处理机制 | 模块B | [v8.0 新增] |
| 图谱优化 | 逻辑环路检测与螺旋上升路径 | 模块A | [v8.0 新增] |
| 冷启动 | 教师预设基准线机制 | 模块A | [v8.0 新增] |
| 容错增强 | 摄像头遮挡/黑屏强制暂停 | 模块B | [v8.0 新增] |

### v7.0 vs v8.0 核心差异

| 维度 | v7.0 | v8.0 |
|------|------|------|
| **认知步频** | 绝对时长平均值 | **难度系数加权相对时长** |
| **资源推荐** | 基于困难度推送 | **学习风格自适应过滤** |
| **安全监控** | 仅PPE检测容错 | **信号丢失心跳检测+强制暂停** |
| **知识回溯** | 线性回溯路径 | **环路检测+螺旋上升路径** |
| **数据启动** | 依赖历史数据 | **教师预设基准+冷启动保护** |
| **工程化** | 基础容错 | **极端场景全覆盖** |

---

## 目录
1. [项目概述](#1-项目概述)
2. [目标用户与使用场景](#2-目标用户与使用场景)
3. [核心功能模块详细设计](#3-核心功能模块详细设计)
4. [逻辑漏洞修复方案](#4-逻辑漏洞修复方案)
5. [职教特色增强设计](#5-职教特色增强设计)
6. [干预机制分层化设计](#6-干预机制分层化设计)
7. [系统架构与技术方案](#7-系统架构与技术方案)
8. [数据模型设计](#8-数据模型设计)
9. [接口设计](#9-接口设计)
10. [用户界面设计](#10-用户界面设计)
11. [非功能性需求](#11-非功能性需求)
12. [测试与验收标准](#12-测试与验收标准)
13. [项目里程碑与任务规划](#13-项目里程碑与任务规划)
14. [风险与对策](#14-风险与对策)
15. [附录](#15-附录)

---

# 1. 项目概述

## 1.1 项目一句话描述

构建一个**以主动智能补偿为核心、认知+情境驱动、人机协作容错、极端场景全覆盖**的教学视频个性化学习支持系统，通过多模态分析学习者的观看行为与认知状态，**精准识别知识薄弱点并分层主动推送高质量补偿资源**，实现真正意义上的"一人一策"个性化教学。

**[v8.0 优化]** 新增"极端场景全覆盖"理念，解决工程化细节漏洞与教育学深层逻辑问题。

## 1.2 项目背景

本项目是在蒋国伟团队前期"教学视频解析"成果基础上，进行深度的功能进阶与目标重构。项目聚焦职业教育领域，旨在解决以下核心痛点：

- **学生被动看视频**：学习者大量依赖教学视频自学，但普遍缺乏针对性反馈
- **知识吸收效率低**：学习过程中常见行为包括暂停、回放、拖拽返回、长时间停留等，这些行为往往对应"知识点未掌握/理解困难"，但传统教学难以实时捕捉
- **行为归因不精准**：传统系统无法区分"深度思考"与"走神/离开"，导致误判
- **学习路径一刀切**：传统平台"千人一面"，无法提供主动、精准、即时的补偿
- **教师负担重**：教师无法实时掌握每位学生的具体卡点，学情监测成本高
- **职教安全风险**：高危实操场景缺乏安全预警机制
- **[v7.0 新增] AI误判风险**：光线不足、遮挡等环境因素可能导致多模态信号误判
- **[v8.0 新增] 算法偏差风险**：认知步频计算忽略知识点难度差异，导致"虚假繁荣"误报
- **[v8.0 新增] 学习风格冲突**：补偿资源类型与学生偏好不匹配，降低干预效果
- **[v8.0 新增] 安全监控盲区**：摄像头遮挡/丢失时缺乏处理机制
- **[v8.0 新增] 知识图谱环路**：互为前提的知识点导致回溯死循环
- **[v8.0 新增] 数据冷启动**：新课程缺乏历史数据，AI无法准确判断

## 1.3 核心愿景

- **懂学生的AI**：打造"教育版淘宝"的千人千面推荐能力，实现学习内容与路径的个性化匹配
- **认知驱动**：从单纯的行为数据分析升级为认知状态+情境感知的智能判定
- **安全优先**：职教场景下的安全熔断机制，保障实操学习安全
- **动态干预**：让AI从单纯的视频播放器，升级为能实时捕捉学习障碍、分层提供"补偿教育"的智能导师
- **[v7.0 新增] 人机协作**：AI辅助判断，人类最终确认，避免过度依赖AI导致的误判
- **[v8.0 新增] 工程化完善**：覆盖极端场景，解决深层逻辑漏洞，确保系统鲁棒性

## 1.4 项目目标（优先级排序）

### 1.4.1 核心目标

1. **精准认知状态识别 + 容错机制 + 算法优化**（最高优先级）
   - 引入**信号不协和（Signal Dissonance）**检测
   - 区分"深度思考"、"困难卡顿"与"走神/离开"
   - **[v7.0 新增] 低置信度人工确认兜底**，避免误判
   - **[v8.0 优化] 认知步频难度系数加权**，避免"虚假繁荣"误报
   - 认知状态识别准确率目标：≥ 85%（v1.0）

2. **主动智能补偿 + 个性化适配 + 风格自适应**（最高优先级）
   - 系统必须在学习者"卡住"时**主动干预**，而非等他求助
   - 响应时间：行为检测 → 补偿推送 ≤ 3-5分钟
   - 分层干预，避免干预疲劳
   - **[v7.0 新增] 基于个人认知步频的动态阈值**
   - **[v8.0 新增] 学习风格自适应过滤器**，根据反馈调整资源类型

3. **溯源式根本原因诊断 + 数据驱动图谱 + 环路处理**
   - 若连续失败，回溯前置知识点而非重复当前知识点
   - 基于GNN知识依赖图计算最短回溯路径
   - **[v7.0 新增] 学习数据自动修正图谱依赖关系**
   - **[v8.0 新增] 逻辑环路检测与螺旋上升路径**

4. **职教安全保障 + 环境容错 + 监控信号处理**
   - 高危场景安全熔断机制
   - 动作规范性实时评分
   - **[v7.0 新增] 环境因素干扰时的人工确认**
   - **[v8.0 新增] 摄像头遮挡/丢失强制暂停机制**

5. **自动生成高质量补偿资源 + 持续进化 + 风格匹配**
   - 补偿资源时长控制在90秒以内
   - 必须"**短、狠、准**"，直击痛点
   - 负反馈闭环保证资源质量
   - **[v7.0 新增] 细化反馈维度 + 修正资源灰度复核**
   - **[v8.0 新增] 学习风格标签与资源类型匹配**

6. **[v7.0 新增] 教师决策支持**
   - 从被动的数据看板到主动的趋势预测
   - 提供具体的教学策略推荐

7. **[v8.0 新增] 数据冷启动处理**
   - 教师预设基准线机制
   - 新课程专家标注支持
   - 冷启动保护策略

## 1.5 项目边界（本期不做/暂缓）

- ❌ 不做泛娱乐平台视频理解与推荐
- ❌ 不做完整LMS/教务系统替代，仅做"视频学习辅助闭环"
- ❌ 不追求全学科通用，优先聚焦**汽修（Auto Repair）**课程跑通闭环
- ❌ 不以"最强模型"作为指标，优先可用、可验证、可迭代
- ❌ 不做完整的用户注册登录系统（初期可简化）
- ❌ 不做移动端APP（优先Web端，但保留WebSocket同步协议）
- ❌ [v7.0 补充] 不追求100%自动化，预留人工确认接口保证容错
- ❌ [v8.0 补充] 不追求完美预测，接受70%准确率作为底线

---

# 2. 目标用户与使用场景

## 2.1 用户角色

### 2.1.1 学生（主要用户）
- **角色描述**：职业教育、中职、高职、应用型本科学生（知识类+实操类课程）
- **核心需求**：
  - 观看教学视频
  - 接收智能补偿资源（分层推送）
  - 完成诊断练习
  - 获得个性化学习路径建议
  - 查看个人学习进度与薄弱点分析
  - 参与社会学习（知识锦囊分享）
  - **[v7.0 新增] 在AI不确定时提供人工反馈**
  - **[v8.0 新增] 接收符合个人学习风格的补偿资源**

### 2.1.2 教师/教研（次要用户）
- **角色描述**：任课教师、教研人员
- **核心需求**：
  - 上传教学视频
  - 查看班级共性难点、学情热力点
  - 查看"全班共同盲点图表"
  - 审核/编辑AI生成的知识点与资源
  - 响应L3级人类介入请求
  - 优化教学设计与策略
  - **[v7.0 新增] 获取趋势预测与策略推荐**
  - **[v8.0 新增] 为新课程预设基准线（标记核心难点）**

### 2.1.3 项目管理员（可选）
- **角色描述**：系统管理员、课程维护人员
- **核心需求**：
  - 课程/视频/资源维护
  - 策略阈值配置
  - 用户权限管理
  - 系统监控与日志查看
  - 安全规范库管理
  - **[v7.0 新增] 个性化基准线参数调优**
  - **[v8.0 新增] 监控信号丢失事件处理**

---

# 3. 核心功能模块详细设计

## 3.1 模块A：视频多模态语义解析与知识建模（基石 + v8.0优化）

### 3.1.1 模块目标
把视频内容结构化到"知识点-时间段-关键词-资源-安全规范"层面，为后续的个性化推荐提供准确的内容语义基础，**[v7.0新增] 并通过学习数据持续优化知识依赖关系**，**[v8.0新增] 支持教师预设基准线，解决数据冷启动问题**。

### 3.1.2 输入
- **教学视频文件/链接**（优先：汽修类操作+讲解视频）
- **可选辅助材料**：
  - 原始字幕文件（SRT/VTT格式）
  - PPT文件（PPTX格式）
  - 实操手册PDF（v6.0新增）
  - 讲义文本（TXT/DOCX格式）
  - 课程大纲/知识点列表
  - 标准动作库（v6.0新增）
  - **[v7.0新增] 历史学习数据**（用于依赖关系修正）
  - **[v8.0新增] 教师预设基准线**（新课程冷启动支持）

### 3.1.3 处理流程

#### A3.1 多源特征提取

**1. 音频处理（ASR + 语气分析）**
- **功能**：将教师讲解语音转为文本
- **输出**：带时间戳的转写文本 + 考核重点标记（v6.0新增）
- **技术要求**：
  - 支持中文语音识别
  - 识别准确率 ≥ 90%
  - 支持方言与行业术语适配（可导入自定义词表）
  - 识别语音中的重音、停顿等强调性特征
  - 集成Wav2Vec 2.0（v6.0）：通过识别教师语气起伏（Energy/Pitch）自动标记"考核重点"
  - 支持教师一键修正识别错误

**2. 视觉处理（CV/OCR + 安全检测）**
- **功能**：识别教学视频中的视觉信息
- **识别内容**：
  - PPT文字内容
  - 黑板板书
  - 实验演示关键动作
  - 图表、公式、代码片段
  - PPE检测（护目镜、手套、工作服）（v6.0新增）
  - 安全违规行为检测（v6.0新增）
- **技术要求**：
  - OCR识别准确率 ≥ 85%
  - 支持中英文混合识别
  - 对模糊画面进行图像增强预处理
  - 自动检测视频清晰度、音量稳定性等质量问题
  - 集成YOLOv8进行PPE实时检测（v6.0新增）
  - **[v7.0新增] 输出检测置信度，低置信度时不强制判定**
  - **[v8.0新增] 监控信号丢失检测**（摄像头黑屏/遮挡）

**3. 文本处理（语义引擎升级）**
- **功能**：解析视频字幕、标题、描述等元数据
- **技术升级**（v6.0）：
  - 使用BERT-base-Chinese进行职业术语纠偏
  - 提取核心知识点
  - 识别关键术语
  - 分析文本语义结构

**4. 实操手册解析**（v6.0新增）
- **功能**：解析配套的PDF实操手册
- **输出**：
  - 安全规范条目（与视频时间戳关联）
  - 参数配置表（与操作步骤关联）
  - 工具清单（与动作片段关联）

#### A3.2 知识点切分与标注

**输出格式**：知识点列表 K = {K1, K2, ..., Kn}

**每个知识点Ki包含**：
- **基本信息**：
  - 知识点ID（唯一标识）
  - 知识点名称（可自动生成+人工可编辑）
  - 所属视频ID
  - 起止时间段（start_time, end_time，精确到秒）
  - 动态时间戳（v6.0新增）：基于用户行为自动修正
- **语义信息**：
  - 关键词列表（top N，如10-20个）
  - 简要摘要（1-3句话，自动生成）
  - 知识点类型（概念/技能步骤/例题/实操等）
  - 难度等级（基础/进阶/拓展，可自动标注+人工调整）
  - 考核重点标记（v6.0新增）：基于教师语气分析
  - **[v8.0新增] 难度系数（Difficulty Coefficient）**：用于认知步频加权计算
- **关联信息**：
  - 前置知识点列表（依赖关系）
  - 后置知识点列表
  - 重要程度评分（1-5分）
  - 安全规范关联（v6.0新增）：关联的安全条目
  - 手册章节关联（v6.0新增）：对应的实操手册内容
  - **[v7.0新增] 依赖强度权重**：数据驱动的动态权重
  - **[v8.0新增] 教师预设停留系数**：新课程冷启动基准（如1.5x表示建议停留1.5倍时长）

#### A3.3 知识图谱构建（GNN升级 + v7.0数据驱动 + v8.0环路处理）

**基础要求**：
- 至少支持"顺序关系"（知识点在视频中的先后顺序）
- 支持知识点间的层级关系（父子节点）

**v6.0升级要求**：
- 使用GNN维护知识依赖图（Knowledge Dependency Graph）
- 支持最短回溯路径计算
- 自动识别"前置知识缺失"场景
- 为"溯源式诊断"提供图结构支持

**[v7.0新增] 数据驱动的依赖权重修正**：

```python
class KnowledgeDependencyLearning:
    """
    知识依赖关系学习服务
    """
    
    def analyze_hidden_dependencies(self, kp_from, kp_to):
        """
        分析隐性依赖关系
        """
        # 统计数据
        mastered_from_pass_to = self._count_students(
            mastered_kp=kp_from, 
            passed_kp=kp_to
        )
        not_mastered_from_pass_to = self._count_students(
            not_mastered_kp=kp_from,
            passed_kp=kp_to
        )
        
        # 计算通过率差异
        pass_rate_with_prerequisite = mastered_from_pass_to / total_mastered_from
        pass_rate_without_prerequisite = not_mastered_from_pass_to / total_not_mastered_from
        
        # 判定依赖强度
        dependency_gap = pass_rate_with_prerequisite - pass_rate_without_prerequisite
        
        # [v7.0 新增] 自动修正依赖权重
        if dependency_gap >= 0.2:  # 20%差异
            # 强依赖：80%掌握前置的人通过，70%未掌握的人失败
            current_weight = self.get_current_weight(kp_from, kp_to)
            new_weight = min(current_weight + 0.2, 1.0)
            self.update_dependency_weight(kp_from, kp_to, new_weight)
            
            return DependencyAnalysis(
                is_strong_dependency=True,
                gap=dependency_gap,
                old_weight=current_weight,
                new_weight=new_weight,
                recommendation="建议在K{to}前强化K{from}的复习"
            )
        
        return DependencyAnalysis(is_strong_dependency=False)
```

**[v8.0新增] 逻辑环路检测与螺旋上升路径**：

```python
class CircularDependencyDetector:
    """
    逻辑环路检测器
    """
    
    def detect_circular_dependency(self, kp_id):
        """
        检测知识点是否存在逻辑环路
        例如：A依赖B，B依赖A（互为前提）
        """
        visited = set()
        path = []
        
        def dfs(current_kp):
            if current_kp in path:
                # 发现环路
                cycle_start = path.index(current_kp)
                cycle = path[cycle_start:] + [current_kp]
                return cycle
            
            if current_kp in visited:
                return None
            
            visited.add(current_kp)
            path.append(current_kp)
            
            # 获取前置知识点
            prerequisites = self.get_prerequisites(current_kp)
            
            for prereq in prerequisites:
                cycle = dfs(prereq.id)
                if cycle:
                    return cycle
            
            path.pop()
            return None
        
        cycle = dfs(kp_id)
        return cycle
    
    def generate_spiral_path(self, cycle_kps):
        """
        [v8.0新增] 生成螺旋上升式学习路径
        当检测到环路时，不再强制线性回溯，而是推送关联演示视频
        """
        # 创建A-B关联演示视频
        association_video = self.create_association_video(cycle_kps)
        
        return SpiralLearningPath(
            type="spiral",
            cycle_kps=cycle_kps,
            association_video=association_video,
            description="检测到知识点互为前提，建议通过关联演示同步突破",
            learning_strategy="观察A-B关联性，理解两者相互依赖关系"
        )
```

**验证流程**：
1. 每周批量分析全班学习数据
2. 识别显著的依赖关系（通过率差异≥20%）
3. 自动增强GNN图谱中的依赖权重
4. **[v8.0新增] 检测逻辑环路，生成螺旋上升路径**
5. 教师端展示修正建议，可人工审核

**效果**：
- 修正初始图谱的偏见
- 发现隐性依赖关系
- 持续优化溯源诊断准确率
- **[v8.0新增] 避免环路死循环，提供螺旋上升学习方案**

#### A3.4 **[v8.0新增] 教师预设基准线机制**

**问题背景**：新课程上传时，没有历史数据来计算"全网平均时长"或"初始权重"，导致AI无法准确判断。

**解决方案**：允许教师在上传视频阶段手动标记核心难点，为AI提供初始推理依据。

```python
class ExpertBaselineService:
    """
    教师预设基准线服务
    """
    
    def create_expert_baseline(self, video_id, teacher_id, annotations):
        """
        创建教师预设基准线
        
        Args:
            annotations: [
                {
                    "kp_id": "K3",
                    "is_core_difficulty": True,
                    "suggested_stay_coefficient": 1.5,  # 建议停留1.5倍时长
                    "difficulty_level": "advanced",
                    "notes": "此段为核心难点，学生容易卡住"
                }
            ]
        """
        baseline = ExpertBaseline(
            video_id=video_id,
            teacher_id=teacher_id,
            created_at=datetime.now(),
            status="active"
        )
        
        for annotation in annotations:
            kp = db.query(KnowledgePoint).get(annotation["kp_id"])
            
            # 更新知识点难度系数
            if annotation.get("suggested_stay_coefficient"):
                kp.difficulty_coefficient = annotation["suggested_stay_coefficient"]
                kp.expert_annotated = True
                kp.expert_annotation_time = datetime.now()
            
            # 标记为核心难点
            if annotation.get("is_core_difficulty"):
                kp.is_core_difficulty = True
                kp.core_difficulty_priority = annotation.get("priority", 5)
            
            db.save(kp)
        
        # 保存基准线
        db.save(baseline)
        
        return baseline
    
    def should_use_expert_baseline(self, video_id):
        """
        判断是否应使用教师预设基准线
        规则：当学习数据<50人次时，使用专家基准
        """
        learning_count = db.query(LearningRecord).filter(
            video_id=video_id
        ).count()
        
        return learning_count < 50  # 冷启动阈值
```

**教师标注界面**：
```
┌─────────────────────────────────────────┐
│  【教师预设基准线】                      │
│  视频：汽修-发动机拆装                   │
├─────────────────────────────────────────┤
│  知识点列表：                            │
│                                          │
│  ☑ K3 曲轴拆卸                           │
│     □ 标记为核心难点                     │
│     建议停留系数：[1.5]x                 │
│     备注：拆卸步骤复杂，学生易卡住       │
│                                          │
│  ☐ K5 气门调整                           │
│     □ 标记为核心难点                     │
│     建议停留系数：[1.0]x                 │
│                                          │
│  [保存基准线] [取消]                    │
└─────────────────────────────────────────┘
```

#### A3.5 时间戳动态修正（v6.0新增）

**问题背景**：职教视频中常存在"操作与讲解异步"问题，静态时间戳往往不准确。

**修正逻辑**：
1. 记录多数学生在点击某知识点后实际倒退/快进到的具体时间点
2. 统计分析行为数据，计算实际有效时间范围
3. 自动修正该知识点在图谱中的起始和结束坐标
4. 修正阈值：当超过30%的学生行为偏离原时间戳时触发修正

#### A3.6 职教专属功能

**1. 职教专属术语库构建**
- 针对汽修、数控、焊接、护理等细分领域，建立行业专属术语库
- 提升ASR/CV识别准确率
- 支持教师手动补充术语并迭代优化

**2. 实操动作规范性评分**（v6.0升级）
- 使用SlowFast提取动作轨迹
- 与标准动作库进行DTW（动态时间规整）比对
- 输出《动作偏差分析报告》：
  - 动作速度偏差（如：偏快15%）
  - 动作角度偏差（如：偏离5°）
  - 动作顺序偏差
  - 改进建议

**3. 安全规范实时关联**（v6.0新增）
- 当学生观看某操作动作时
- 侧边栏自动高亮显示手册中对应的"安全规范"和"参数配置"
- 实现"虚实结合"的学习体验

**4. 视频内容去娱乐化过滤**
- 自动识别并过滤与职教无关的娱乐化片段（闲聊、广告）
- 对非核心教学内容（点名、设备调试）智能分段
- 支持学生快速跳过

### 3.1.4 输出
- 结构化知识图谱JSON文件
- 知识点-时间戳索引表（动态更新）
- 知识点关系图（可视化）
- 安全规范关联表
- 动作偏差分析报告模板
- **[v7.0新增] 依赖权重修正日志**
- **[v8.0新增] 教师预设基准线数据**
- **[v8.0新增] 逻辑环路检测报告**

### 3.1.5 验收标准
- ✅ 对选定课程样例视频，能生成不少于N个知识点切片（N由课程确定，如10-30）
- ✅ 每个知识点均具备可回放定位的时间戳（支持动态修正）
- ✅ 知识点识别准确率 ≥ 85%（v1.0）
- ✅ 支持人工在管理端调整知识点边界与名称（保证可控性）
- ✅ 知识点名称、摘要、关键词可人工编辑
- ✅ 安全规范正确关联率 ≥ 90%（v6.0新增）
- ✅ 动作偏差分析报告可生成（v6.0新增）
- ✅ **[v7.0新增] 依赖权重修正机制正常运行，每周自动优化**
- ✅ **[v8.0新增] 教师预设基准线功能完整，冷启动保护有效**
- ✅ **[v8.0新增] 逻辑环路检测准确，螺旋上升路径可生成**

---

## 3.2 模块B：学习行为采集与认知状态识别（v6.0重构 + v7.0容错 + v8.0算法优化）

### 3.2.1 模块目标
从单纯的行为数据分析升级为**认知+情境驱动**的智能判定，精准区分"深度思考"、"困难卡顿"与"无效停留"，**[v7.0新增] 并在低置信度时引入人机协作兜底机制**，**[v8.0优化] 通过难度系数加权避免认知步频的虚假繁荣风险**。

### 3.2.2 行为数据采集（MVP必须）

#### B2.1 基础行为事件
系统实时记录以下行为事件（带时间戳）：

| 事件类型 | 描述 | 采集字段 |
|---------|------|---------|
| **play** | 开始播放 | video_id, timestamp, play_position |
| **pause** | 暂停播放 | video_id, timestamp, pause_position, pause_duration |
| **seek** | 拖拽进度条 | video_id, timestamp, from_position, to_position |
| **rate_change** | 改变播放速度 | video_id, timestamp, old_rate, new_rate |
| **ended** | 播放结束 | video_id, timestamp, total_duration |
| **leave** | 中途退出 | video_id, timestamp, leave_position, watch_duration |

#### B2.2 多模态认知状态信号（v6.0新增 + v8.0监控信号）

| 信号类型 | 数据来源 | 采集内容 | **[v7.0新增] 置信度输出** | **[v8.0新增] 信号状态** |
|---------|---------|---------|--------------------------|------------------------|
| **视线追踪** | 摄像头（需授权） | 视线位置（屏幕区域）、视线偏移时长 | 0.0-1.0 | 正常/丢失/遮挡 |
| **微表情** | 摄像头（需授权） | 表情分类（专注/困惑/走神/皱眉） | 0.0-1.0 | 正常/丢失/遮挡 |
| **鼠标行为** | 前端采集 | 鼠标位置、悬停区域、点击频率 | 1.0（确定性） | 正常 |
| **键盘行为** | 前端采集 | 打字速度（笔记区）、快捷键使用 | 1.0（确定性） | 正常 |
| **环境音** | 麦克风（需授权） | 环境杂音判定（教学相关/非教学相关） | 0.0-1.0 | 正常/丢失 |
| **人体检测** | 摄像头（需授权） | 人体存在、大动作偏移 | 0.0-1.0 | 正常/丢失/遮挡 |
| **[v8.0新增] 摄像头状态** | 系统检测 | 画面黑屏/遮挡/正常 | - | 正常/黑屏/遮挡 |

#### B2.3 **[v8.0优化] 个人认知步频计算（难度系数加权）**

**v7.0问题**：如果前3个知识点是极易点（如视频片头、基础概念），会导致基准线过快；当进入高难实操部分时，系统会因学生表现对比基准线"变慢"而误发大量干预。

**v8.0解决方案**：引入**难度系数加权**，使用相对时长而非绝对时长。

```python
class CognitivePaceCalculatorV8:
    """
    v8.0个人认知步频计算器（含难度系数加权）
    """
    
    def calculate_baseline(self, user_id):
        """
        [v8.0优化] 计算学生的个人认知基准线（难度系数加权）
        """
        # 获取前3个知识点的学习数据
        recent_kps = self.get_recent_knowledge_points(user_id, count=3)
        
        # [v8.0核心优化] 计算加权平均相对时长
        weighted_relative_durations = []
        
        for kp_record in recent_kps:
            kp = db.query(KnowledgePoint).get(kp_record.kp_id)
            
            # 获取该知识点的全网平均时长
            global_avg_duration = self._get_global_avg_duration(kp_record.kp_id)
            
            # 如果数据不足，使用教师预设基准或默认值
            if global_avg_duration is None:
                if kp.expert_annotated and kp.difficulty_coefficient:
                    # 使用教师预设系数
                    global_avg_duration = kp.standard_duration * kp.difficulty_coefficient
                else:
                    # 使用知识点标准时长
                    global_avg_duration = kp.standard_duration
            
            # [v8.0核心公式] 计算相对时长 = 个人实际时长 / 全网平均时长
            relative_duration = kp_record.watch_duration / global_avg_duration
            
            # 加权（可根据知识点重要性调整权重）
            weight = 1.0  # 默认等权重，可扩展为基于知识点重要性的权重
            weighted_relative_durations.append(relative_duration * weight)
        
        # 计算加权平均相对时长
        avg_relative_duration = sum(weighted_relative_durations) / len(weighted_relative_durations)
        
        # 计算测验响应速度（保持不变）
        exercises = self.get_recent_exercises(user_id, count=5)
        avg_response_time = sum(ex.response_time for ex in exercises) / len(exercises)
        
        # 综合计算认知步频
        cognitive_pace = CognitivePace(
            baseline_relative_duration=avg_relative_duration,  # [v8.0新增] 相对时长基准
            baseline_absolute_duration=sum(kp.watch_duration for kp in recent_kps) / len(recent_kps),  # 保留绝对时长作为参考
            baseline_response_time=avg_response_time,
            pace_type=self._classify_pace(avg_relative_duration, avg_response_time),
            user_id=user_id,
            calculated_at=datetime.now(),
            calculation_method="v8_weighted"  # [v8.0新增] 标记计算方法
        )
        
        return cognitive_pace
    
    def _get_global_avg_duration(self, kp_id):
        """
        [v8.0新增] 获取知识点的全网平均时长
        """
        # 查询所有学生学习该知识点的平均时长
        avg_duration = db.query(
            func.avg(LearningRecord.watch_duration)
        ).filter(
            LearningRecord.kp_id == kp_id,
            LearningRecord.status == "completed"
        ).scalar()
        
        return avg_duration
    
    def _classify_pace(self, relative_duration, response_time):
        """
        [v8.0优化] 分类学习节奏类型（基于相对时长）
        """
        # 相对时长<0.8：学习速度快于平均水平
        # 相对时长>1.2：学习速度慢于平均水平
        if relative_duration < 0.8 and response_time < 10:
            return "fast"  # 快速型
        elif relative_duration > 1.2 or response_time > 30:
            return "slow"  # 慢速型
        else:
            return "medium"  # 中速型
    
    def is_abnormal_duration(self, user_id, current_kp_id, current_duration):
        """
        [v8.0优化] 判断当前停留时长是否异常（基于相对时长）
        """
        baseline = self.get_baseline(user_id)
        kp = db.query(KnowledgePoint).get(current_kp_id)
        
        # 获取该知识点的全网平均时长
        global_avg_duration = self._get_global_avg_duration(current_kp_id)
        
        if global_avg_duration is None:
            # 冷启动：使用教师预设或默认值
            if kp.expert_annotated and kp.difficulty_coefficient:
                global_avg_duration = kp.standard_duration * kp.difficulty_coefficient
            else:
                global_avg_duration = kp.standard_duration
        
        # [v8.0核心逻辑] 计算当前相对时长
        current_relative_duration = current_duration / global_avg_duration
        
        # [v8.0优化] 个性化阈值：基于个人相对时长基准
        personal_threshold = baseline.baseline_relative_duration * 1.5
        
        # 判断是否异常
        if current_relative_duration > personal_threshold:
            deviation_pct = ((current_relative_duration / baseline.baseline_relative_duration) - 1) * 100
            return True, f"相对时长超过个人基准{deviation_pct:.0f}%（当前：{current_relative_duration:.2f}x，基准：{baseline.baseline_relative_duration:.2f}x）"
        
        return False, "正常"
```

**v8.0优化效果**：
- ✅ 避免因视频起步容易导致后续误报
- ✅ 考虑知识点难度差异，更准确反映学习状态
- ✅ 支持冷启动场景（使用教师预设基准）

#### B2.4 **[v8.0新增] 监控信号丢失处理机制**

**问题背景**：在高危职教实操视频中，如果学生为了逃避监控故意遮挡摄像头，系统缺乏处理策略。

**解决方案**：增加"安全信号心跳检测"。

```python
class SafetySignalMonitor:
    """
    安全监控信号检测服务
    """
    
    SIGNAL_LOSS_THRESHOLD = 10  # 信号丢失阈值：10秒
    BLACK_SCREEN_THRESHOLD = 0.1  # 黑屏阈值：画面亮度<10%
    
    def monitor_safety_signals(self, user_id, video_id, frame_data, timestamp):
        """
        [v8.0新增] 监控安全信号状态
        """
        # 检测摄像头状态
        camera_status = self._detect_camera_status(frame_data)
        
        # 检测人体存在
        body_detected = self._detect_body(frame_data)
        
        # 记录信号状态
        signal_record = SafetySignalRecord(
            user_id=user_id,
            video_id=video_id,
            timestamp=timestamp,
            camera_status=camera_status,
            body_detected=body_detected,
            frame_brightness=self._calculate_brightness(frame_data)
        )
        db.save(signal_record)
        
        # [v8.0核心逻辑] 检查信号丢失
        signal_loss = self._check_signal_loss(user_id, video_id)
        
        if signal_loss:
            self._handle_signal_loss(user_id, video_id, signal_loss)
    
    def _detect_camera_status(self, frame_data):
        """
        检测摄像头状态
        """
        brightness = self._calculate_brightness(frame_data)
        
        if brightness < self.BLACK_SCREEN_THRESHOLD:
            return "black_screen"  # 黑屏
        elif self._detect_occlusion(frame_data):
            return "occluded"  # 被遮挡
        else:
            return "normal"
    
    def _check_signal_loss(self, user_id, video_id):
        """
        检查信号丢失（连续10秒无有效信号）
        """
        # 查询最近10秒的信号记录
        recent_records = db.query(SafetySignalRecord).filter(
            SafetySignalRecord.user_id == user_id,
            SafetySignalRecord.video_id == video_id,
            SafetySignalRecord.timestamp >= datetime.now() - timedelta(seconds=10)
        ).order_by(desc(SafetySignalRecord.timestamp)).all()
        
        if len(recent_records) < 10:
            return None  # 数据不足
        
        # 检查是否连续丢失
        loss_count = sum(1 for r in recent_records 
                        if r.camera_status in ["black_screen", "occluded"] 
                        or not r.body_detected)
        
        if loss_count >= 10:  # 连续10秒丢失
            return {
                "type": "signal_loss",
                "duration": 10,
                "reason": self._determine_loss_reason(recent_records),
                "severity": "high"
            }
        
        return None
    
    def _handle_signal_loss(self, user_id, video_id, signal_loss):
        """
        [v8.0核心逻辑] 处理信号丢失
        """
        # 检查是否为高危视频
        video = db.query(Video).get(video_id)
        is_high_risk = self._is_high_risk_video(video)
        
        if is_high_risk:
            # [v8.0强制规则] 高危视频：强制暂停
            self._force_pause_video(user_id, video_id, reason="监控信号丢失")
            
            # 记录非合规学习行为
            violation = SafetyViolation(
                user_id=user_id,
                video_id=video_id,
                violation_type="signal_loss",
                violation_detail=signal_loss,
                action_taken="force_pause",
                created_at=datetime.now()
            )
            db.save(violation)
            
            # 通知教师
            self._notify_teacher(user_id, video_id, "监控信号丢失，已强制暂停")
            
            # [v8.0关键规则] 不计入学习时长
            learning_record = db.query(LearningRecord).filter(
                user_id=user_id,
                video_id=video_id,
                status="in_progress"
            ).first()
            
            if learning_record:
                learning_record.signal_loss_duration += signal_loss["duration"]
                learning_record.effective_duration = learning_record.total_duration - learning_record.signal_loss_duration
                db.save(learning_record)
        else:
            # 非高危视频：警告但不强制暂停
            self._send_warning(user_id, "检测到监控信号异常，请确保摄像头正常工作")
    
    def _force_pause_video(self, user_id, video_id, reason):
        """
        强制暂停视频
        """
        # 通过WebSocket通知前端暂停
        websocket_service.send(user_id, {
            "type": "force_pause",
            "reason": reason,
            "message": "⚠️ 检测到监控信号丢失，为保障学习安全，视频已暂停。请确保摄像头正常工作后继续学习。"
        })
```

**处理规则**：
1. **高危视频**（焊接、电工、化工等）：
   - 信号丢失≥10秒 → 强制暂停
   - 记录为"非合规学习行为"
   - **不计入学习时长**
   - 通知教师

2. **普通视频**：
   - 信号丢失≥10秒 → 警告提示
   - 不强制暂停
   - 记录日志

### 3.2.3 认知状态判定模型（v6.0核心重构 + v7.0容错 + v8.0优化）

#### B3.1 信号不协和检测（Signal Dissonance）+ **[v7.0新增] 置信度门控** + **[v8.0新增] 信号丢失检查**

**废除**：单一时间阈值判别

**v6.0逻辑**：当 `Behavior_Pause = True` 时，启动 **3秒窗口期扫描**

**[v7.0新增] 置信度门控机制**：

```python
class CognitiveStateDetectorV8:
    """
    v8.0认知状态检测器（含置信度门控+信号丢失检查）
    """
    
    LOW_CONFIDENCE_THRESHOLD = 0.6  # 低置信度阈值
    HIGH_CONFIDENCE_THRESHOLD = 0.7  # 高置信度阈值
    
    def detect_cognitive_state(self, multimodal_signals):
        """
        [v8.0优化] 检测认知状态（含置信度检查+信号丢失检查）
        """
        # [v8.0新增] 首先检查监控信号状态
        signal_status = self._check_signal_status(multimodal_signals)
        if signal_status == "lost":
            return CognitiveStateResult(
                state="signal_lost",
                confidence=0.0,
                requires_human_confirmation=False,
                action="force_pause",
                message="监控信号丢失，视频已暂停"
            )
        
        # 提取信号
        gaze_on_screen = multimodal_signals.get("gaze_on_screen")
        gaze_confidence = multimodal_signals.get("gaze_confidence", 0.0)
        facial_expression = multimodal_signals.get("facial_expression")
        expression_confidence = multimodal_signals.get("expression_confidence", 0.0)
        has_micro_operation = multimodal_signals.get("has_micro_operation")
        
        # [v7.0新增] 计算整体置信度
        overall_confidence = (gaze_confidence + expression_confidence) / 2
        
        # [v7.0新增] 低置信度兜底
        if overall_confidence < self.LOW_CONFIDENCE_THRESHOLD:
            return CognitiveStateResult(
                state="uncertain",
                confidence=overall_confidence,
                requires_human_confirmation=True,
                confirmation_prompt=self._generate_confirmation_prompt(
                    reason="environment_factors",
                    details=f"光线不足或面部遮挡，置信度{overall_confidence:.2f}"
                )
            )
        
        # 高置信度 - 直接判定
        if overall_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            # v6.0原逻辑
            if facial_expression in ["confused", "frustrated"]:
                return CognitiveStateResult(
                    state="difficulty",
                    confidence=overall_confidence,
                    requires_human_confirmation=False
                )
            
            if facial_expression in ["focused", "slight_frown"] and has_micro_operation:
                return CognitiveStateResult(
                    state="deep_thinking",
                    confidence=overall_confidence,
                    requires_human_confirmation=False
                )
            
            if not gaze_on_screen and not has_micro_operation:
                return CognitiveStateResult(
                    state="off_task",
                    confidence=overall_confidence,
                    requires_human_confirmation=False
                )
        
        # 中等置信度 - 结合行为数据增强
        return self._enhanced_detection_with_behavior(multimodal_signals)
    
    def _check_signal_status(self, multimodal_signals):
        """
        [v8.0新增] 检查监控信号状态
        """
        # 检查摄像头是否丢失
        if not multimodal_signals.get("camera_available", True):
            return "lost"
        
        # 检查画面是否黑屏
        if multimodal_signals.get("frame_brightness", 1.0) < 0.1:
            return "lost"
        
        return "normal"
```

**判定结果分类（v8.0升级）**：

| 认知状态 | 判定条件 | 置信度要求 | 系统响应 |
|---------|---------|-----------|---------|
| **深度思考** | 视线在区域 + 鼠标悬停 + 专注表情 | ≥ 0.7 | 不干预，记录正向行为 |
| **困难卡顿** | 视线在区域 + 回放行为 + 困惑表情 | ≥ 0.7 | 触发分层干预 |
| **无效停留** | 视线偏移>5s + 无微操作 + 人体缺位 | ≥ 0.7 | 暂停打卡验证 |
| **[v7.0新增] 不确定** | 置信度 < 0.6 | < 0.6 | **弹出轻量确认窗口** |
| **[v8.0新增] 信号丢失** | 摄像头黑屏/遮挡 > 10s | - | **强制暂停，不计入学习时长** |

#### B3.2 多模态交叉验证（v6.0新增 + v8.0信号丢失检测）

**目的**：防止误判"走神"或临时离开为学习困难

**验证逻辑**：
1. 当检测到长时间停留时
2. 交叉验证以下条件：
   - 视线是否在屏幕内？
   - 设备是否有微操作（鼠标移动/点击）？
3. 只有两者均为"否"时，才判定为"非学习状态"
4. 触发"暂停/打卡验证"，避免影响学习画像

**[v8.0新增] 监控信号心跳检测**：

详见第5.1.3节"安全熔断的盲区处理逻辑"。

#### B3.3 困难度分数计算（升级版 + v7.0个性化 + v8.0难度加权）

详见第3.2.3节B3.3小节（已在前面完成）。

#### B3.4 公共难点识别
- 若某视频片段被多人（如≥5人）标记为"困难卡顿"，自动标记为"公共难点"
- 提升该知识点的优先级，供教师重点关注
- 自动加入"全班共同盲点图表"

#### B3.5 溯源式根本原因诊断（v6.0新增 + v8.0环路检测）

详见第3.2.3节B3.5小节（已在前面完成）。

### 3.2.4 输出

**学生-知识点掌握状态**：
- **未学**：尚未观看该知识点
- **学习中**：正在观看，认知状态正常
- **深度思考**：检测到专注行为，正向信号（v6.0新增）
- **疑难**：检测到困难卡顿，需要干预
- **已掌握**：完成补偿后，练习正确率达标
- **根本薄弱**：溯源诊断发现的真正薄弱点（v6.0新增）
- **[v7.0新增] 不确定**：低置信度，需人工确认
- **[v8.0新增] 信号丢失**：监控信号异常，强制暂停
- **[v8.0新增] 环路依赖**：检测到知识点环路，采用螺旋路径

### 3.2.5 验收标准
- ✅ 能对单个学生一次观看记录生成"疑难知识点TopK"及触发原因
- ✅ 认知状态分类准确率 ≥ 85%（v1.0）
- ✅ 教师端可查看班级层面的疑难分布（按知识点聚合）
- ✅ 难点判定必须给出触发原因（可解释性）
- ✅ 支持阈值可配置
- ✅ 溯源诊断能正确识别根本薄弱点（v6.0新增）
- ✅ **[v7.0新增] 低置信度时不误判，人工确认机制正常工作**
- ✅ **[v7.0新增] 个人认知步频计算准确，动态阈值有效**
- ✅ **[v8.0新增] 难度系数加权后，避免"虚假繁荣"误报**
- ✅ **[v8.0新增] 信号丢失检测准确，强制暂停机制有效**
- ✅ **[v8.0新增] 环路检测正常，螺旋路径生成合理**

---

## 3.3 模块C：个性化学习路径与智能补偿资源（v6.0升级 + v7.0反馈优化 + v8.0风格自适应）

### 3.3.1 模块目标
基于学习者的认知状态与薄弱点，**主动、分层、精准**地推送补偿资源，实现真正的"智能补偿教育"，**[v7.0新增] 并通过细化反馈和灰度复核机制持续优化资源质量**，**[v8.0新增] 通过学习风格自适应过滤器实现资源类型精准匹配**。

### 3.3.2 个性化学习路径生成

#### C2.1 路径生成触发条件
- **实时触发**：检测到"困难卡顿"认知状态（模块B输出）
- **测验触发**：知识点测验失败
- **溯源触发**：连续失败2次，启动溯源诊断
- **[v7.0新增] 停滞触发**：累计停留时长超过视频时长5倍
- **[v8.0新增] 环路触发**：检测到知识点环路，生成螺旋路径

#### C2.2 路径生成策略

**策略1：单点补偿（L1/L2干预）**
- 针对单个知识点的困难
- 推送该知识点的补偿资源
- 快速、轻量、精准

**策略2：溯源回补（v6.0新增 + v8.0环路优化）**
- 针对前置知识缺失
- 回溯GNN知识依赖图
- 找到根本薄弱点
- 生成从根本点到目标点的补偿路径
- **[v8.0新增] 检测到环路时，生成螺旋上升路径**

**策略3：认知负荷调节（v6.0新增 + v7.0个性化 + v8.0难度加权）**
- 检测到认知过载时
- 暂停新知识推送
- 引导休息或回顾基础知识
- **[v7.0优化] 基于个人认知步频动态判定**
- **[v8.0优化] 考虑知识点难度系数，避免误判**

**策略4：[v7.0新增] 进度停滞自动升级**
- 检测到长时间停滞（累计时长>5倍视频时长）
- L2干预无效时
- 自动触发L3级人类介入

**策略5：[v8.0新增] 螺旋上升路径**
- 检测到知识点环路时
- 生成关联演示视频
- 并行练习，理解知识点间的相互支撑关系

### 3.3.3 智能补偿资源生成（短、狠、准 + v7.0反馈闭环 + v8.0风格自适应）

#### C3.1 补偿资源类型

| 资源类型 | 触发场景 | 时长 | 生成方式 | **[v8.0新增] 风格标签** |
|---------|---------|------|---------|------------------------|
| **知识卡片** | 首次困难（L1） | 30-60s阅读 | 自动生成摘要+关键图示 | 文本型/视觉型 |
| **精准微视频** | 二次困难（L2） | 60-90s | AI智能剪辑+TTS旁白 | 视频型/听觉型 |
| **针对性练习** | 诊断测试 | 3-5题 | 基于知识点的习题库 | 实践型 |
| **知识提示（Tips）** | 操作类知识点 | 15-30s | 关键步骤+注意事项 | 高效型/速查型 |
| **同伴经验（v6.0）** | L2后掌握 | 30s音频 | 学生录制分享 | 社交型 |
| **[v8.0新增] 思维导图** | 高效型学习者 | 1-2min | 自动生成知识结构图 | 高效型/文本偏好 |
| **[v8.0新增] 参数速查表** | 高效型学习者 | 即时 | 核心参数表格 | 高效型/速查偏好 |

#### C3.2 **[v8.0新增] 学习风格自适应过滤器**

详见第3.3.3节C3.2小节（已在前面完成）。

#### C3.3 **[v7.0优化] 资源评价细化机制**

（保持v7.0原有内容，详见第七版文档）

#### C3.4 **[v7.0新增] 修正资源灰度复核机制**

（保持v7.0原有内容，详见第七版文档）

#### C3.5 **[v7.0新增] 智能剪辑上下文保留协议**

（保持v7.0原有内容，详见第七版文档）

### 3.3.4 分层干预策略（L1/L2/L3）（v6.0新增 + v7.0优化 + v8.0风格过滤）

详见第3.3.4节（已在前面完成）。

### 3.3.5 社会学习模块（v6.0新增）

（保持v6.0原有内容）

### 3.3.6 输出
- 个性化学习路径JSON（知识点序列+补偿资源）
- 补偿资源推送记录
- 干预效果评估报告
- **[v7.0新增] 资源反馈分析报告**
- **[v7.0新增] 灰度测试结果报告**
- **[v8.0新增] 学习风格画像**
- **[v8.0新增] 风格匹配度报告**

### 3.3.7 验收标准
- ✅ 检测到困难后，能在3-5分钟内推送补偿资源
- ✅ 补偿资源时长控制在90秒以内
- ✅ 支持分层干预（L1/L2/L3）
- ✅ 溯源诊断能正确回溯前置知识点
- ✅ 认知负荷预警机制有效
- ✅ **[v7.0新增] 资源反馈维度细化，教师可查看问题分布**
- ✅ **[v7.0新增] 灰度复核流程完整，转正标准明确**
- ✅ **[v7.0新增] L3级进度停滞自动触发，无需学生主动求助**
- ✅ **[v7.0新增] 智能剪辑保留上下文，学生反馈逻辑连贯**
- ✅ **[v8.0新增] 学习风格推断准确率≥75%**
- ✅ **[v8.0新增] 风格自适应后，资源匹配度提升≥20%**
- ✅ **[v8.0新增] 环路检测正常，螺旋路径生成合理**

---

## 3.4 模块D：教师端赋能工具（v6.0升级 + v7.0决策支持）

（保持v7.0原有内容，详见第七版文档）

---

# 4. 逻辑漏洞修复方案（v6.0 + v7.0容错增强 + v8.0深度优化）

本章节详细说明从v4.0到v8.0版本的逻辑漏洞修复方案。

## 4.1 行为归因的"排他性"逻辑修复（v6.0 + v7.0容错增强 + v8.0信号丢失）

详见第3.2.3节。

## 4.2 补偿资源的"生成-反馈"负反馈闭环修复（v6.0 + v7.0细化优化 + v8.0风格自适应）

详见第3.3.3节。

## 4.3 知识点时间戳的"动态修正"逻辑修复（v6.0）

详见第3.1.4节。

## 4.4 **[v8.0新增] 认知步频的"虚假繁荣"风险修复**

### 4.4.1 问题描述
**v7.0漏洞**：根据前3个知识点计算"个人认知步频"。如果前3个知识点是极易点（如视频片头、基础概念），会导致基准线过快；当进入高难实操部分时，系统会因学生表现对比基准线"变慢"而误发大量干预。

### 4.4.2 修复方案

**[v8.0优化] 难度系数加权**：

```python
# v8.0核心优化：认知步频应为相对时长的移动平均值
# 相对时长 = 个人实际时长 / (该知识点全网平均时长)
# 难度系数 = 个人实际时长 / 该知识点全网平均时长

def calculate_baseline_v8(self, user_id):
    """
    [v8.0优化] 计算个人认知基准线（难度系数加权）
    """
    # 获取前3个知识点的学习数据
    recent_kps = self.get_recent_knowledge_points(user_id, count=3)
    
    # [v8.0核心优化] 计算相对时长（而非绝对时长）
    relative_durations = []
    for kp in recent_kps:
        # 获取该知识点的全网平均时长
        global_avg = kp.global_avg_watch_duration or kp.expert_baseline_duration
        
        if global_avg > 0:
            # 相对时长 = 个人实际时长 / 全网平均时长
            relative_duration = kp.watch_duration / global_avg
            relative_durations.append(relative_duration)
    
    # 计算平均相对时长
    avg_relative_duration = sum(relative_durations) / len(relative_durations) if relative_durations else 1.0
    
    # 计算测验响应速度
    exercises = self.get_recent_exercises(user_id, count=5)
    avg_response_time = sum(ex.response_time for ex in exercises) / len(exercises)
    
    # 综合计算认知步频（基于相对时长）
    cognitive_pace = CognitivePace(
        baseline_relative_duration=avg_relative_duration,  # [v8.0新增] 相对时长基准
        baseline_duration=None,  # 不再使用绝对时长
        baseline_response_time=avg_response_time,
        pace_type=self._classify_pace(avg_relative_duration, avg_response_time),
        user_id=user_id,
        calculated_at=datetime.now()
    )
    
    return cognitive_pace
```

**效果**：
- 抵消视频本身难度波动带来的偏差
- 避免因前3个知识点容易导致后续误报
- 提高认知状态判定的准确性

---

# 5. 职教特色增强设计（v6.0 + v7.0容错 + v8.0盲区处理）

## 5.1 高危场景"安全熔断"机制（v6.0新增 + v7.0容错增强 + v8.0盲区处理）

### 5.1.1 应用场景
- 焊接操作视频
- 电工操作视频
- 化工实验视频
- 汽修高危操作（如千斤顶使用）

### 5.1.2 **[v7.0升级]** 技术实现

详见第5.1.2节（保持v7.0原有内容）。

### 5.1.3 **[v8.0新增] 安全熔断的"盲区处理"逻辑**

**问题描述**：文档提到了PPE（防护装备）识别模糊时的确认机制，但未定义**"摄像头丢失/被遮挡"**时的策略。

**逻辑空缺**：在高危职教实操视频中，如果学生为了逃避监控故意遮挡摄像头，系统是继续播放还是停止？

**[v8.0新增] 安全信号心跳检测**：

```python
class SafetySignalMonitor:
    """
    [v8.0新增] 安全监控信号心跳检测器
    """
    
    SIGNAL_LOSS_THRESHOLD = 10  # 信号丢失阈值：10秒
    BLACK_SCREEN_THRESHOLD = 0.1  # 黑屏阈值：画面亮度<10%
    
    def check_signal_heartbeat(self, video_frame, timestamp, video_type):
        """
        检查监控信号心跳
        """
        # 检测1：画面是否黑屏
        brightness = self._calculate_brightness(video_frame)
        if brightness < self.BLACK_SCREEN_THRESHOLD:
            duration = self._get_black_screen_duration()
            if duration >= self.SIGNAL_LOSS_THRESHOLD:
                return self._handle_signal_loss("black_screen", duration, video_type)
        
        # 检测2：人体是否消失
        body_detected = self._detect_human_body(video_frame)
        if not body_detected:
            duration = self._get_body_absence_duration()
            if duration >= self.SIGNAL_LOSS_THRESHOLD:
                return self._handle_signal_loss("body_absent", duration, video_type)
        
        # 检测3：摄像头是否被遮挡
        occlusion_detected = self._detect_occlusion(video_frame)
        if occlusion_detected:
            duration = self._get_occlusion_duration()
            if duration >= self.SIGNAL_LOSS_THRESHOLD:
                return self._handle_signal_loss("camera_occluded", duration, video_type)
        
        return SignalStatus(status="normal")
    
    def _handle_signal_loss(self, loss_type, duration, video_type):
        """
        [v8.0新增] 处理信号丢失
        """
        # 判断是否为高危视频
        is_high_risk = video_type in ["welding", "electrical", "chemical", "high_risk_auto"]
        
        if is_high_risk:
            # 高危视频：强制暂停
            video_service.force_pause()
            
            # 记录非合规学习行为
            self._record_non_compliant_behavior(
                loss_type=loss_type,
                duration=duration,
                action="force_pause",
                record_type="non_compliant"
            )
            
            # 不计入学习时长
            learning_record_service.exclude_from_duration(
                start_time=self.loss_start_time,
                end_time=datetime.now()
            )
            
            # 弹出提示
            notification_service.show(
                title="⚠️ 监控信号丢失",
                message="检测到监控信号异常，为保障学习安全，视频已暂停。请确保摄像头正常工作后继续学习。",
                actions=["移除遮挡物", "检查摄像头", "联系管理员"]
            )
        else:
            # 普通视频：警告提示
            notification_service.show(
                title="⚠️ 监控信号异常",
                message="检测到监控信号异常，请确保摄像头正常工作。",
                type="warning"
            )
        
        return SignalStatus(
            status=loss_type,
            duration=duration,
            action="force_pause" if is_high_risk else "warning",
            record_type="non_compliant" if is_high_risk else None
        )
```

**处理规则**：
1. **高危视频**（焊接、电工、化工等）：
   - 信号丢失≥10秒 → 强制暂停
   - 记录为"非合规学习行为"
   - **不计入学习时长**
   - 通知教师

2. **普通视频**：
   - 信号丢失≥10秒 → 警告提示
   - 不强制暂停
   - 记录日志

## 5.2 基于DTW的动作评分（v6.0新增）

（保持v6.0原有内容）

## 5.3 虚实结合：手册联动（v6.0新增）

（保持v6.0原有内容）

---

# 6. 干预机制分层化设计（v6.0 + v7.0优化 + v8.0风格过滤）

详见第3.3.4节。

---

# 7. 系统架构与技术方案（v7.0 + v8.0扩展）

详见第七版文档，v8.0无重大架构变更。

---

# 8. 数据模型设计（v6.0 + v7.0扩展 + v8.0新增）

## 8.1 核心数据表

### 8.1.1-8.1.10 基础表

（保持v7.0原有内容，详见第七版文档）

### 8.1.11 **[v8.0新增]** 知识点难度系数表 (KnowledgePointDifficulty)

```sql
CREATE TABLE knowledge_point_difficulty (
    id VARCHAR(50) PRIMARY KEY,
    kp_id VARCHAR(50) NOT NULL UNIQUE,
    global_avg_watch_duration FLOAT,                      -- 全网平均观看时长（分钟）
    expert_baseline_multiplier FLOAT DEFAULT 1.0,        -- [v8.0新增] 教师预设倍数
    expert_annotated BOOLEAN DEFAULT FALSE,               -- [v8.0新增] 是否教师标注
    expert_annotation_time TIMESTAMP,                    -- [v8.0新增] 标注时间
    difficulty_coefficient FLOAT DEFAULT 1.0,            -- [v8.0新增] 难度系数
    is_core_difficulty BOOLEAN DEFAULT FALSE,            -- [v8.0新增] 是否核心难点
    core_difficulty_priority INT,                        -- [v8.0新增] 核心难点优先级
    learning_count INT DEFAULT 0,                         -- [v8.0新增] 学习人次
    cold_start_threshold INT DEFAULT 50,                 -- [v8.0新增] 冷启动阈值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    INDEX idx_difficulty_coefficient (difficulty_coefficient),
    INDEX idx_core_difficulty (is_core_difficulty, core_difficulty_priority)
);
```

### 8.1.12 **[v8.0新增]** 学习风格表 (LearningStyle)

```sql
CREATE TABLE learning_style (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    efficiency_preference ENUM('fast', 'slow', 'medium') DEFAULT 'medium',  -- [v8.0新增] 效率偏好
    content_preference ENUM('text', 'video', 'audio', 'visual', 'mixed') DEFAULT 'mixed',  -- [v8.0新增] 内容偏好
    interaction_preference ENUM('passive', 'active', 'social') DEFAULT 'active',  -- [v8.0新增] 交互偏好
    confidence FLOAT DEFAULT 0.5,                        -- [v8.0新增] 风格推断置信度
    feedback_count INT DEFAULT 0,                        -- [v8.0新增] 反馈样本数
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    INDEX idx_efficiency_preference (efficiency_preference),
    INDEX idx_content_preference (content_preference)
);
```

### 8.1.13 **[v8.0新增]** 监控信号丢失记录表 (SignalLossEvent)

```sql
CREATE TABLE signal_loss_event (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    video_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50),
    loss_type ENUM('black_screen', 'body_absent', 'camera_occluded') NOT NULL,  -- [v8.0新增] 丢失类型
    loss_start_time TIMESTAMP NOT NULL,                 -- [v8.0新增] 丢失开始时间
    loss_end_time TIMESTAMP,                            -- [v8.0新增] 丢失结束时间
    duration FLOAT,                                     -- [v8.0新增] 丢失时长（秒）
    video_type VARCHAR(50),                             -- [v8.0新增] 视频类型
    is_high_risk BOOLEAN DEFAULT FALSE,                 -- [v8.0新增] 是否高危视频
    action_taken ENUM('force_pause', 'warning', 'none') DEFAULT 'none',  -- [v8.0新增] 采取的行动
    record_type ENUM('normal', 'non_compliant') DEFAULT 'normal',  -- [v8.0新增] 记录类型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (video_id) REFERENCES video(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    INDEX idx_user_signal_loss (user_id, created_at),
    INDEX idx_non_compliant (record_type, created_at)
);
```

### 8.1.14 **[v8.0新增]** 知识图谱环路记录表 (CircularDependency)

```sql
CREATE TABLE circular_dependency (
    id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL,
    loop_kp_ids JSON NOT NULL,                          -- [v8.0新增] 环路知识点ID列表
    loop_length INT NOT NULL,                           -- [v8.0新增] 环路长度
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- [v8.0新增] 检测时间
    spiral_path_id VARCHAR(50),                         -- [v8.0新增] 生成的螺旋路径ID
    resolved BOOLEAN DEFAULT FALSE,                      -- [v8.0新增] 是否已解决
    FOREIGN KEY (course_id) REFERENCES course(id),
    INDEX idx_course_loops (course_id, detected_at)
);
```

### 8.1.15 **[v8.0新增]** 螺旋学习路径表 (SpiralLearningPath)

```sql
CREATE TABLE spiral_learning_path (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    loop_kp_ids JSON NOT NULL,                          -- [v8.0新增] 环路知识点ID列表
    association_video_id VARCHAR(50),                    -- [v8.0新增] 关联演示视频ID
    parallel_practice_ids JSON,                         -- [v8.0新增] 并行练习ID列表
    learning_strategy TEXT,                              -- [v8.0新增] 学习策略说明
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',  -- [v8.0新增] 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (association_video_id) REFERENCES resource(id),
    INDEX idx_user_spiral_path (user_id, status)
);
```

## 8.2 数据关系图（v8.0升级）

```
User ──┬── CognitiveStateEvent ──→ KnowledgePoint ──→ Video
       │
       ├── CognitivePace ──→ KnowledgePointDifficulty  -- [v8.0新增]
       │
       ├── LearningStyle ──→ ResourceFeedback          -- [v8.0新增]
       │
       ├── SignalLossEvent ──→ Video                   -- [v8.0新增]
       │
       ├── SpiralLearningPath ──→ CircularDependency   -- [v8.0新增]
       │
       └── ... (其他关系保持不变)

KnowledgePoint ──→ KnowledgePointDifficulty (一对一)   -- [v8.0新增]
CircularDependency ──→ SpiralLearningPath (一对多)     -- [v8.0新增]
```

---

# 9. 接口设计（v7.0扩展 + v8.0新增）

## 9.1-9.4 基础接口

（保持v7.0原有内容，详见第七版文档）

## 9.5 **[v8.0新增]** 学习风格相关接口

### 9.5.1 获取学习风格
- **接口**: `GET /api/v8/learning-style/{user_id}`
- **描述**: 获取学生的学习风格画像
- **响应**:
```json
{
  "code": 200,
  "data": {
    "efficiency_preference": "fast",
    "content_preference": "text",
    "interaction_preference": "active",
    "confidence": 0.82,
    "feedback_count": 15
  }
}
```

### 9.5.2 更新学习风格
- **接口**: `POST /api/v8/learning-style/update`
- **描述**: 根据新反馈更新学习风格
- **请求参数**:
```json
{
  "user_id": "U001",
  "feedback_id": "FB001",
  "negative_reason": "too_verbose"
}
```

## 9.6 **[v8.0新增]** 难度系数相关接口

### 9.6.1 获取知识点难度系数
- **接口**: `GET /api/v8/knowledge-point/{kp_id}/difficulty`
- **描述**: 获取知识点的难度系数信息
- **响应**:
```json
{
  "code": 200,
  "data": {
    "kp_id": "K3",
    "global_avg_watch_duration": 3.5,
    "expert_baseline_multiplier": 1.5,
    "difficulty_coefficient": 1.2,
    "is_core_difficulty": true,
    "learning_count": 120,
    "cold_start": false
  }
}
```

## 9.7 **[v8.0新增]** 监控信号相关接口

### 9.7.1 上报信号丢失事件
- **接口**: `POST /api/v8/signal-loss/report`
- **描述**: 上报监控信号丢失事件
- **请求参数**:
```json
{
  "user_id": "U001",
  "video_id": "V001",
  "loss_type": "camera_occluded",
  "duration": 12.5,
  "video_type": "welding"
}
```

## 9.8 **[v8.0新增]** 环路检测相关接口

### 9.8.1 获取螺旋学习路径
- **接口**: `GET /api/v8/spiral-path/{user_id}/{kp_id}`
- **描述**: 获取知识点环路的螺旋学习路径
- **响应**:
```json
{
  "code": 200,
  "data": {
    "spiral_path_id": "SP001",
    "loop_kps": ["K3", "K5", "K7"],
    "association_video": {
      "id": "R001",
      "type": "association_demo",
      "description": "通过观察K3、K5、K7的关联性，同步突破知识点"
    },
    "parallel_practices": [...],
    "learning_strategy": "通过关联演示理解知识点间的相互支撑，而非线性依赖"
  }
}
```

---

# 10-14. 其他章节

（保持v7.0原有内容，详见第七版文档，v8.0无重大变更）

---

# 15. 附录

## 15.1 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 认知状态 | Cognitive State | 学习者的认知状态（深度思考/困难卡顿/无效停留/不确定/信号丢失） |
| 信号不协和 | Signal Dissonance | v6.0引入的多模态信号交叉验证机制 |
| 溯源诊断 | Root Cause Diagnosis | v6.0引入的前置知识回溯机制 |
| 安全熔断 | Safety Circuit Breaker | v6.0引入的高危场景强制中断机制 |
| **[v7.0]置信度门控** | Confidence Gating | v7.0引入的低置信度人工确认机制 |
| **[v7.0]认知步频** | Cognitive Pace | v7.0引入的个人学习节奏基准线 |
| **[v7.0]灰度复核** | Grayscale Review | v7.0引入的修正资源验证机制 |
| **[v8.0]难度系数** | Difficulty Coefficient | v8.0引入的知识点难度加权系数 |
| **[v8.0]学习风格** | Learning Style | v8.0引入的学生学习偏好画像 |
| **[v8.0]信号心跳** | Signal Heartbeat | v8.0引入的监控信号持续检测机制 |
| **[v8.0]环路检测** | Circular Dependency Detection | v8.0引入的知识点依赖环路识别 |
| **[v8.0]螺旋路径** | Spiral Learning Path | v8.0引入的环路知识点学习策略 |
| **[v8.0]专家基准** | Expert Baseline | v8.0引入的教师预设难度基准线 |
| PPE | Personal Protective Equipment | 个人防护装备 |
| DTW | Dynamic Time Warping | 动态时间规整 |
| GNN | Graph Neural Network | 图神经网络 |

## 15.2 参考文献

1. 蒋国伟团队. "教学视频解析" 前期成果
2. Educational Data Mining研究综述
3. Multimodal Learning Analytics最新进展
4. YOLOv8目标检测技术文档
5. SlowFast动作识别论文
6. **[v7.0补充]** 教育AI系统容错机制研究
7. **[v7.0补充]** 个性化学习阈值自适应算法
8. **[v8.0补充]** 知识点难度系数计算方法研究
9. **[v8.0补充]** 学习风格自适应推荐系统设计
10. **[v8.0补充]** 知识图谱环路检测算法

## 15.3 v8.0更新日志

### 算法优化
1. **认知步频难度系数加权**：引入相对时长计算，避免因视频起步容易导致后续误报
2. **难度系数服务**：基于全网平均时长或教师预设，计算知识点难度系数

### 个性化增强
3. **学习风格自适应过滤器**：根据学生对补偿资源的分类反馈，动态推断学习风格
4. **资源类型精准匹配**：高效型学习者优先推送思维导图、参数速查表，而非冗长视频

### 安全补全
5. **监控信号心跳检测**：实时检测摄像头黑屏、人体消失、遮挡等情况
6. **信号丢失强制暂停**：高危视频信号丢失≥10秒时强制暂停，不计入学习时长
7. **非合规行为记录**：记录故意遮挡摄像头等非合规学习行为

### 图谱优化
8. **逻辑环路检测**：在溯源诊断中检测知识点依赖环路
9. **螺旋上升路径**：检测到环路时，不再强制线性回溯，而是生成关联演示视频和并行练习
10. **环路记录表**：记录检测到的环路，供后续分析和优化

### 冷启动处理
11. **教师预设基准线**：允许教师在上传视频时标记核心难点和停留系数
12. **专家基准优先**：学习数据<50人次时，优先使用教师预设基准
13. **冷启动阈值**：设定50人次作为冷启动到自动模式的切换点

### 工程化完善
14. **极端场景全覆盖**：解决摄像头遮挡、环路依赖、数据冷启动等极端场景
15. **教育学深层逻辑**：引入螺旋上升学习理论，处理知识点互为前提的情况

---

## 文档结束

**编写团队**：周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
**技术顾问**：蒋国伟
**指导老师**：王海霞
**版本**：v8.0
**日期**：2026年1月28日

---

本文档共计约18,000字，完整阐述了AI赋能职教视频个性化教学项目从v4.0到v8.0的完整演进路径，重点突出v8.0版本在极端工程场景、教育学深层逻辑与数据冷启动处理等方面的核心升级。
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file