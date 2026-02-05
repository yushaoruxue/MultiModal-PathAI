# AI赋能职教视频个性化教学项目需求规格说明书（第十一稿-最终版）

## 【Final Release Notes - 最终版】

- **版本定位**：v11.0（Final Integrated Version），**可直接进入开发与架构设计阶段的最终完整版**。
- **整合范围**：本版本完整整合了v6.0-v10.0的所有需求、设计与约束，是项目的**最终完整需求规格说明书**。
- **文档状态**：**最终版（Final Version）**，不再进行功能增补，仅用于开发实施与评审归档。

---

## 文档版本信息
- **版本号**: v11.0（Final Integrated Version）
- **编写日期**: 2026年1月
- **编写团队**: 周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
- **技术顾问**: 蒋国伟
- **指导老师**: 王海霞
- **文档状态**: **最终版（Final Version）**
- **版本说明**: 完整整合v6.0-v10.0所有版本内容，包含边界异常逻辑补齐、系统健壮性增强、数据审计与教师主权等全部功能

---

## 版本演进说明

### v11.0（最终版）整合说明

本版本完整整合了v6.0-v10.0的所有内容，是项目的**最终完整需求规格说明书**。

### v10.0 主要更新内容

| 更新类别 | 更新内容 | 影响模块 | 标记 |
|---------|---------|---------|------|
| 冲突处理 | 专家标注模式写锁（Write Lock）+ 租约（Lease Timeout 30min）+ 原子化发布/交还AI托管 | 模块A/D | [v10.0 新增] |
| 硬件适配 | 硬件画像驱动三级降级（全量/精简/仅日志）+ 权重补偿（0.4→0.8） | 模块B | [v10.0 新增] |
| 冷启动自动化 | 跨课原型匹配（Prototype Matching）复用相似课程基准 | 模块A/B | [v10.0 新增] |
| 教师定制 | 教师策略编辑器：干预激进系数（0.1-2.0） | 模块D/C | [v10.0 新增] |
| 数据可信 | 数据审计引擎：异常/恶意反馈过滤 + 难度保护区 + 反馈-行为一致性校验（80%门槛） | 模块C/D | [v10.0 新增] |

### v9.0 主要更新内容

| 更新类别 | 更新内容 | 影响模块 | 标记 |
|---------|---------|---------|------|
| 体验优化 | 干预抗震荡机制（Hysteresis） | 模块C | [v9.0 新增] |
| 教师主权 | 一键禁用AI自动生成+专家标注模式 | 模块A/D | [v9.0 新增] |
| 数据对齐 | 多模态时间戳对齐协议（±3s窗口） | 模块A | [v9.0 新增] |
| 弱网适配 | 降级策略矩阵（弱网自动降级） | 模块B | [v9.0 新增] |
| 路径完善 | 螺旋路径跳出策略（反复失败→L3） | 模块C | [v9.0 优化] |

### v9.0 vs v10.0 核心差异

| 维度 | v9.0 | v10.0 |
|------|------|------|
| **人机协作** | 教师可禁用AI，但缺少并发冲突协议 | **写锁+租约（30min）+原子发布+交还托管** |
| **硬件适配** | 主要考虑弱网与信号误判 | **加入算力画像与三级降级矩阵+权重补偿** |
| **冷启动** | 教师专家基准为主 | **跨课原型匹配半自动冷启动** |
| **教师定制** | 侧重"禁用AI/专家标注" | **可统一调节干预敏感度（激进系数）** |
| **数据可信** | 反馈闭环/灰度复核 | **审计引擎+难度保护区+一致性校验（80%）** |

### v8.0 vs v9.0 核心差异

| 维度 | v8.0 | v9.0 |
|------|------|------|
| **干预触发** | 多触发器并行，可能频繁弹窗 | **抗震荡机制+5分钟冷静期** |
| **教师权限** | 仅审核，无法禁用AI | **一键锁定+专家标注模式** |
| **时间戳对齐** | 未定义对齐误差处理 | **±3秒软对齐窗口协议** |
| **网络环境** | 未考虑弱网场景 | **降级策略矩阵+本地缓存** |
| **螺旋路径** | 仅生成路径，无跳出机制 | **反复失败自动跳转L3** |
| **边界处理** | 极端场景部分覆盖 | **边界异常逻辑全面补齐** |

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

构建一个**以主动智能补偿为核心、认知+情境驱动、人机协作容错、极端场景全覆盖、边界异常逻辑完善、系统健壮性完备、数据审计可信**的教学视频个性化学习支持系统，通过多模态分析学习者的观看行为与认知状态，**精准识别知识薄弱点并分层主动推送高质量补偿资源**，实现真正意义上的"一人一策"个性化教学。

**[v9.0 优化]** 新增"边界异常逻辑完善"理念，解决干预震荡、时间戳对齐、弱网降级等边界场景问题。

**[v10.0 优化]** 新增"系统健壮性完备"与"数据审计可信"理念，解决人机冲突、硬件适配、冷启动自动化、教师统一调参、恶意反馈过滤等最终落地问题。

**[v11.0 最终版]** 完整整合v6.0-v10.0所有版本内容，形成可直接交付开发的最终完整需求规格说明书。

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
- **[v9.0 新增] 干预界面震荡**：多触发器并行导致频繁弹窗，影响学习体验
- **[v9.0 新增] 教师主权缺失**：教师无法禁用AI自动生成，缺乏教学主导权
- **[v9.0 新增] 时间戳对齐误差**：ASR/CV/行为日志时间戳不对齐，导致知识图谱错误
- **[v9.0 新增] 弱网环境误判**：网络波动导致信号丢失误判，强制暂停学习
- **[v10.0 新增] 人机并发冲突**：教师手改与AI后台更新同时进行，导致数据覆盖丢失
- **[v10.0 新增] 硬件算力不足**：老旧设备无法承载多模态识别，导致页面卡死
- **[v10.0 新增] 冷启动无人标注**：新课程缺乏历史数据，教师忙碌时无法及时标注
- **[v10.0 新增] 干预敏感度一刀切**：无法按班级统一调整干预策略，缺乏灵活性
- **[v10.0 新增] 恶意反馈污染**：异常/恶意差评导致优质资源被误下架

## 1.3 核心愿景

- **懂学生的AI**：打造"教育版淘宝"的千人千面推荐能力，实现学习内容与路径的个性化匹配
- **认知驱动**：从单纯的行为数据分析升级为认知状态+情境感知的智能判定
- **安全优先**：职教场景下的安全熔断机制，保障实操学习安全
- **动态干预**：让AI从单纯的视频播放器，升级为能实时捕捉学习障碍、分层提供"补偿教育"的智能导师
- **[v7.0 新增] 人机协作**：AI辅助判断，人类最终确认，避免过度依赖AI导致的误判
- **[v8.0 新增] 工程化完善**：覆盖极端场景，解决深层逻辑漏洞，确保系统鲁棒性
- **[v9.0 新增] 边界逻辑完善**：补齐干预震荡、时间对齐、弱网降级等边界异常场景

## 1.4 项目目标（优先级排序）

### 1.4.1 核心目标

1. **精准认知状态识别 + 容错机制 + 算法优化 + 抗震荡**（最高优先级）
   - 引入**信号不协和（Signal Dissonance）**检测
   - 区分"深度思考"、"困难卡顿"与"走神/离开"
   - **[v7.0 新增] 低置信度人工确认兜底**，避免误判
   - **[v8.0 优化] 认知步频难度系数加权**，避免"虚假繁荣"误报
   - **[v9.0 新增] 干预抗震荡机制**，防止频繁弹窗
   - 认知状态识别准确率目标：≥ 85%（v1.0）

2. **主动智能补偿 + 个性化适配 + 风格自适应 + 抗震荡**
   - 系统必须在学习者"卡住"时**主动干预**，而非等他求助
   - 响应时间：行为检测 → 补偿推送 ≤ 3-5分钟
   - 分层干预，避免干预疲劳
   - **[v7.0 新增] 基于个人认知步频的动态阈值**
   - **[v8.0 新增] 学习风格自适应过滤器**，根据反馈调整资源类型
   - **[v9.0 新增] 干预冷静期**，防止界面震荡

3. **溯源式根本原因诊断 + 数据驱动图谱 + 环路处理 + 跳出策略**
   - 若连续失败，回溯前置知识点而非重复当前知识点
   - 基于GNN知识依赖图计算最短回溯路径
   - **[v7.0 新增] 学习数据自动修正图谱依赖关系**
   - **[v8.0 新增] 逻辑环路检测与螺旋上升路径**
   - **[v9.0 新增] 螺旋路径反复失败自动跳转L3**

4. **职教安全保障 + 环境容错 + 监控信号处理 + 弱网降级**
   - 高危场景安全熔断机制
   - 动作规范性实时评分
   - **[v7.0 新增] 环境因素干扰时的人工确认**
   - **[v8.0 新增] 摄像头遮挡/丢失强制暂停机制**
   - **[v9.0 新增] 弱网环境降级策略**，避免误判

5. **自动生成高质量补偿资源 + 持续进化 + 风格匹配 + 教师主权**
   - 补偿资源时长控制在90秒以内
   - 必须"**短、狠、准**"，直击痛点
   - 负反馈闭环保证资源质量
   - **[v7.0 新增] 细化反馈维度 + 修正资源灰度复核**
   - **[v8.0 新增] 学习风格标签与资源类型匹配**
   - **[v9.0 新增] 教师一键禁用AI自动生成**，保护教学主权

6. **[v7.0 新增] 教师决策支持**
   - 从被动的数据看板到主动的趋势预测
   - 提供具体的教学策略推荐

7. **[v8.0 新增] 数据冷启动处理**
   - 教师预设基准线机制
   - 新课程专家标注支持
   - 冷启动保护策略

8. **[v9.0 新增] 多模态数据对齐**
   - 时间戳对齐协议（±3秒窗口）
   - 语义脱节检测与教师校验

## 1.5 项目边界（本期不做/暂缓）

- ❌ 不做泛娱乐平台视频理解与推荐
- ❌ 不做完整LMS/教务系统替代，仅做"视频学习辅助闭环"
- ❌ 不追求全学科通用，优先聚焦**汽修（Auto Repair）**课程跑通闭环
- ❌ 不以"最强模型"作为指标，优先可用、可验证、可迭代
- ❌ 不做完整的用户注册登录系统（初期可简化）
- ❌ 不做移动端APP（优先Web端，但保留WebSocket同步协议）
- ❌ [v7.0 补充] 不追求100%自动化，预留人工确认接口保证容错
- ❌ [v8.0 补充] 不追求完美预测，接受70%准确率作为底线
- ❌ [v9.0 补充] 不追求完美对齐，接受±3秒时间戳误差作为容错窗口

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
  - **[v9.0 新增] 在弱网环境下正常学习（降级模式）**

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
  - **[v9.0 新增] 一键禁用AI自动生成，进入专家标注模式**

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
  - **[v9.0 新增] 多模态对齐误差日志查看**

---

# 3. 核心功能模块详细设计

## 3.1 模块A：视频多模态语义解析与知识建模（基石 + v8.0优化 + v9.0对齐协议）

### 3.1.1 模块目标
把视频内容结构化到"知识点-时间段-关键词-资源-安全规范"层面，为后续的个性化推荐提供准确的内容语义基础，**[v7.0新增] 并通过学习数据持续优化知识依赖关系**，**[v8.0新增] 支持教师预设基准线，解决数据冷启动问题**，**[v9.0新增] 通过时间戳对齐协议处理多模态数据对齐误差**。

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
  - **[v9.0新增] 教师禁用AI标记**（专家标注模式）

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
  - **[v9.0新增] 时间戳精度标记**（用于对齐协议）

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
  - **[v9.0新增] 时间戳精度标记**（用于对齐协议）

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

#### A3.2 **[v9.0新增] 多模态时间戳对齐协议**

**问题背景**：ASR（语音）、CV（视觉）和行为日志的时间戳往往是不对齐的（网络延迟、硬件性能差异）。如果ASR显示教师在01:10讲完知识点，但CV在01:12才捕捉到板书变化，系统该以哪个为基准？

**解决方案**：定义"时间戳对齐窗口（Sync Window）"协议。

```python
class MultimodalTimestampAlignment:
    """
    [v9.0新增] 多模态时间戳对齐服务
    """
    
    SYNC_WINDOW = 3.0  # 软对齐窗口：±3秒
    SEMANTIC_DISCONNECT_THRESHOLD = 5.0  # 语义脱节阈值：5秒
    
    def align_timestamps(self, asr_events, cv_events, behavior_events):
        """
        [v9.0新增] 对齐多模态时间戳
        """
        aligned_events = []
        
        # 按时间排序所有事件
        all_events = []
        for event in asr_events:
            all_events.append({
                "source": "asr",
                "timestamp": event.timestamp,
                "content": event.text,
                "type": "speech"
            })
        
        for event in cv_events:
            all_events.append({
                "source": "cv",
                "timestamp": event.timestamp,
                "content": event.detected_content,
                "type": "visual"
            })
        
        for event in behavior_events:
            all_events.append({
                "source": "behavior",
                "timestamp": event.timestamp,
                "content": event.action,
                "type": "interaction"
            })
        
        all_events.sort(key=lambda x: x["timestamp"])
        
        # [v9.0核心逻辑] 在±3秒窗口内的事件视为同一语义块
        current_semantic_block = []
        block_start_time = None
        
        for event in all_events:
            if block_start_time is None:
                block_start_time = event["timestamp"]
                current_semantic_block = [event]
            else:
                time_gap = event["timestamp"] - block_start_time
                
                if time_gap <= self.SYNC_WINDOW:
                    # 在软对齐窗口内，加入当前语义块
                    current_semantic_block.append(event)
                else:
                    # 超出窗口，处理当前块并开始新块
                    aligned_block = self._merge_semantic_block(current_semantic_block)
                    aligned_events.append(aligned_block)
                    
                    block_start_time = event["timestamp"]
                    current_semantic_block = [event]
        
        # 处理最后一个块
        if current_semantic_block:
            aligned_block = self._merge_semantic_block(current_semantic_block)
            aligned_events.append(aligned_block)
        
        return aligned_events
    
    def _merge_semantic_block(self, events):
        """
        [v9.0新增] 合并同一语义块的事件
        """
        # 计算块的时间范围
        timestamps = [e["timestamp"] for e in events]
        block_start = min(timestamps)
        block_end = max(timestamps)
        block_duration = block_end - block_start
        
        # [v9.0核心逻辑] 检查是否语义脱节
        if block_duration > self.SEMANTIC_DISCONNECT_THRESHOLD:
            # 记录语义脱节日志
            self._log_semantic_disconnect(events, block_duration)
            
            return {
                "type": "semantic_disconnect",
                "start_time": block_start,
                "end_time": block_end,
                "duration": block_duration,
                "events": events,
                "requires_manual_review": True,
                "warning": f"检测到语义脱节（{block_duration:.1f}秒），建议教师手动校验"
            }
        
        # 正常合并
        merged_content = {
            "asr_text": [e["content"] for e in events if e["source"] == "asr"],
            "cv_content": [e["content"] for e in events if e["source"] == "cv"],
            "behavior_actions": [e["content"] for e in events if e["source"] == "behavior"]
        }
        
        # 使用中位数时间戳作为对齐后的时间
        aligned_timestamp = statistics.median(timestamps)
        
        return {
            "type": "aligned_semantic_block",
            "aligned_timestamp": aligned_timestamp,
            "time_range": (block_start, block_end),
            "content": merged_content,
            "source_count": {
                "asr": sum(1 for e in events if e["source"] == "asr"),
                "cv": sum(1 for e in events if e["source"] == "cv"),
                "behavior": sum(1 for e in events if e["source"] == "behavior")
            }
        }
    
    def _log_semantic_disconnect(self, events, duration):
        """
        [v9.0新增] 记录语义脱节日志
        """
        disconnect_log = SemanticDisconnectLog(
            video_id=events[0].get("video_id"),
            disconnect_start=min(e["timestamp"] for e in events),
            disconnect_end=max(e["timestamp"] for e in events),
            duration=duration,
            event_sources=[e["source"] for e in events],
            requires_manual_review=True,
            created_at=datetime.now()
        )
        db.save(disconnect_log)
        
        # 通知教师
        notification_service.notify_teacher(
            type="semantic_disconnect",
            message=f"检测到时间戳对齐误差（{duration:.1f}秒），建议手动校验知识点边界",
            video_id=events[0].get("video_id")
        )
```

**对齐规则**：
1. **软对齐窗口**：±3秒内的所有特征点视为同一语义块
2. **对齐时间戳**：使用中位数时间戳作为对齐后的时间
3. **语义脱节检测**：超过5秒未对齐 → 记录日志，提示教师手动校验
4. **教师校验**：教师可查看语义脱节日志，手动调整知识点边界

#### A3.3 知识点切分与标注

**输出格式**：知识点列表 K = {K1, K2, ..., Kn}

**每个知识点Ki包含**：
- **基本信息**：
  - 知识点ID（唯一标识）
  - 知识点名称（可自动生成+人工可编辑）
  - 所属视频ID
  - 起止时间段（start_time, end_time，精确到秒）
  - 动态时间戳（v6.0新增）：基于用户行为自动修正
  - **[v9.0新增] 对齐后时间戳**：经过多模态对齐协议处理的时间戳
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
  - **[v9.0新增] AI生成禁用标记**：教师是否禁用AI自动生成

#### A3.4 **[v9.0新增] 教师一键禁用AI自动生成机制** + **[v10.0升级] 写锁（Write Lock）与租约（Lease Timeout）**

**问题背景**：如果教师判定AI对某视频的知识点拆解完全错误，应能"锁定"该视频，禁止AI再次自动生成，并切换为"纯人工标注模式"。

**[v10.0新增] 人机并发冲突**：AI后台正在生成/更新某视频的知识图谱（例如5.0版），教师在前端同时编辑旧版本（例如4.0版），可能导致数据覆盖丢失。

**解决方案**：教师主权保护机制 + **[v10.0新增] 写锁（Write Lock）+ 租约（Lease Timeout）+ 原子化发布**。

```python
class TeacherSovereigntyService:
    """
    [v9.0新增] 教师主权保护服务
    """
    
    def disable_ai_generation(self, video_id, teacher_id, reason):
        """
        [v9.0新增] 一键禁用AI自动生成
        """
        video = db.query(Video).get(video_id)
        
        # 创建禁用记录
        ai_lock = AIGenerationLock(
            video_id=video_id,
            teacher_id=teacher_id,
            lock_type="full_disable",  # 完全禁用
            reason=reason,
            locked_at=datetime.now(),
            status="active"
        )
        db.save(ai_lock)
        
        # 更新视频状态
        video.ai_generation_enabled = False
        video.annotation_mode = "expert_only"  # [v9.0新增] 专家标注模式
        video.locked_by = teacher_id
        video.locked_at = datetime.now()
        db.save(video)
        
        # 删除已生成的AI知识点（可选）
        if reason == "complete_rejection":
            ai_kps = db.query(KnowledgePoint).filter(
                video_id=video_id,
                ai_generated=True
            ).all()
            for kp in ai_kps:
                kp.status = "deleted_by_teacher"
                db.save(kp)
        
        # 通知系统
        notification_service.broadcast(
            type="ai_generation_disabled",
            message=f"视频{video.title}已切换为专家标注模式",
            video_id=video_id
        )
        
        return {
            "status": "locked",
            "annotation_mode": "expert_only",
            "message": "AI自动生成已禁用，请使用专家标注模式"
        }
    
    def enable_expert_annotation_mode(self, video_id, teacher_id):
        """
        [v9.0新增] 启用专家标注模式
        """
        video = db.query(Video).get(video_id)
        
        # 创建专家标注工作区
        annotation_workspace = ExpertAnnotationWorkspace(
            video_id=video_id,
            teacher_id=teacher_id,
            mode="manual_only",
            created_at=datetime.now()
        )
        db.save(annotation_workspace)
        
        return {
            "workspace_id": annotation_workspace.id,
            "mode": "expert_annotation",
            "features": [
                "手动切分知识点",
                "手动标注时间戳",
                "手动设置依赖关系",
                "完全控制知识点边界"
            ]
        }
    
    def check_ai_generation_allowed(self, video_id):
        """
        [v9.0新增] 检查是否允许AI自动生成
        """
        video = db.query(Video).get(video_id)
        
        if not video.ai_generation_enabled:
            return False, "AI自动生成已被教师禁用"
        
        # 检查是否有活跃的锁定
        active_lock = db.query(AIGenerationLock).filter(
            video_id=video_id,
            status="active"
        ).first()
        
        if active_lock:
            return False, f"AI自动生成已被锁定（原因：{active_lock.reason}）"
        
        return True, "允许AI自动生成"
```

#### A3.4.1 **[v10.0新增] 写锁（Write Lock）与租约（Lease Timeout）机制**

**问题背景**：教师在"专家标注模式"编辑到一半，突然关掉浏览器/停电，可能造成视频长期被锁，AI更新永久暂停（死锁）。

**解决方案**：写锁采用**租约机制（Lease）**，默认有效期 **30分钟**。

**规则**：
- **默认租约**：30分钟
- **续租条件**：教师有"有效编辑行为"（保存草稿/移动分段/修改依赖/新增知识点等）即刷新 `last_heartbeat_at`
- **超时释放**：若 `now - last_heartbeat_at > 30min`，系统自动释放写锁
- **状态对齐**：释放写锁后触发一次"状态对齐（State Reconcile）"
  - 将未发布的草稿标记为 `stale_draft`（可回收/可恢复）
  - **回滚到最近稳定版本**：将线上生效版本指向最近一次 `published` 的 `knowledge_graph_version`
  - 恢复该 `video_id` 的AI托管任务为 `running`
  - 生成一条审计记录：谁持锁、何时超时、释放原因、对齐结果

**原子化发布**：教师点击"发布并交还AI托管"时，必须一次性完成：
- 校验：版本号、编辑快照、差异变更集合法性
- 提交：写入新图谱版本（不可部分成功）
- 解锁：释放写锁
- 托管：恢复AI更新任务，并以最新版本为基线

```python
class KnowledgeGraphWriteLockServiceV10:
    """
    [v10.0新增] 知识图谱写锁服务（含Lease与超时释放）
    """
    
    DEFAULT_LEASE_SECONDS = 30 * 60  # 30分钟
    
    def acquire_write_lock(self, video_id, teacher_id, ttl_seconds=DEFAULT_LEASE_SECONDS):
        # 成功返回 lock_token；失败返回占用者信息
        pass
    
    def heartbeat(self, video_id, lock_token):
        # 教师有编辑行为则续租（刷新last_heartbeat_at / ttl）
        pass
    
    def release_write_lock(self, video_id, lock_token, reason="manual_release"):
        pass
    
    def force_release_if_timeout(self, video_id):
        # 定时任务扫描：now-last_heartbeat_at > DEFAULT_LEASE_SECONDS → force_release
        # 释放后触发 reconcile，并回滚线上图谱到最近published版本
        pass
```

#### A3.4.2 **[v10.0新增] 跨课原型匹配（Prototype Matching）冷启动**

**问题背景**：当新课程上传且教师未提供专家基准时，系统不能"空转等待标注"，必须具备半自动冷启动能力。

**解决方案**：从新课程视频中提取**核心术语频率向量**（ASR文本 + OCR关键词），与课程库中已成熟课程原型计算语义相似度：
- 若 `sim(new, prototype) > 0.8`：复用其**难度基准**与**步频阈值**作为初始值
- 若 `0.6 < sim ≤ 0.8`：复用但标记为"低置信度冷启动"，同时提示教师轻量确认
- 若 `sim ≤ 0.6`：退化为默认行业基准（或等待数据积累/教师标注）

**复用内容范围**：
- `knowledge_point_difficulty` 初始化（全网平均时长缺失时）
- `cognitive_pace` 初始阈值（personal_threshold的初始倍率）
- `intervention` 默认触发敏感度（可被教师激进系数再调）

**教师标注界面**：
```
┌─────────────────────────────────────────┐
│  【视频管理】汽修-发动机拆装            │
├─────────────────────────────────────────┤
│  AI自动生成：☑ 启用  ☐ 禁用            │
│                                          │
│  [一键禁用AI] [进入专家标注模式]        │
│                                          │
│  禁用原因：                              │
│  ☐ AI拆解完全错误                       │
│  ☐ 知识点边界不准确                     │
│  ☐ 依赖关系错误                         │
│  ☐ 其他：[_____________]                │
│                                          │
│  [确认禁用] [取消]                      │
└─────────────────────────────────────────┘
```

#### A3.5 知识图谱构建（GNN升级 + v7.0数据驱动 + v8.0环路处理 + v9.0对齐优化）

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

**验证流程**：
1. 每周批量分析全班学习数据
2. 识别显著的依赖关系（通过率差异≥20%）
3. 自动增强GNN图谱中的依赖权重
4. 教师端展示修正建议，可人工审核

**效果**：
- 修正初始图谱的偏见
- 发现隐性依赖关系
- 持续优化溯源诊断准确率

**[v8.0新增] 逻辑环路检测与螺旋上升路径**：
```python
class CircularDependencyDetector:
    """
    [v8.0新增] 知识点环路检测服务
    """
    
    def detect_cycle(self, knowledge_graph, start_kp_id):
        """
        检测从某知识点出发是否存在环路
        """
        visited = set()
        path = []
        
        def dfs(kp_id):
            if kp_id in path:
                # 找到环路
                cycle_start_idx = path.index(kp_id)
                return path[cycle_start_idx:] + [kp_id]
            
            if kp_id in visited:
                return None
            
            visited.add(kp_id)
            path.append(kp_id)
            
            for next_kp in knowledge_graph.get_next_kps(kp_id):
                cycle = dfs(next_kp)
                if cycle:
                    return cycle
            
            path.pop()
            return None
        
        return dfs(start_kp_id)
    
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

**[v9.0新增] 基于对齐时间戳的知识图谱构建**：

```python
def build_knowledge_graph_v9(video_id):
    """
    [v9.0优化] 构建知识图谱（使用对齐后的时间戳）
    """
    # 获取对齐后的语义块
    alignment_service = MultimodalTimestampAlignment()
    aligned_blocks = alignment_service.get_aligned_blocks(video_id)
    
    # 使用对齐时间戳构建知识点
    knowledge_points = []
    for block in aligned_blocks:
        if block["type"] == "semantic_disconnect":
            # 语义脱节：标记为待校验
            kp = KnowledgePoint(
                video_id=video_id,
                start_time=block["start_time"],
                end_time=block["end_time"],
                status="pending_review",  # [v9.0新增] 待教师校验
                requires_manual_review=True,
                review_reason="时间戳对齐误差"
            )
        else:
            # 正常对齐块
            kp = KnowledgePoint(
                video_id=video_id,
                start_time=block["aligned_timestamp"] - 2,  # 对齐时间戳±2秒
                end_time=block["aligned_timestamp"] + 2,
                aligned_timestamp=block["aligned_timestamp"],  # [v9.0新增]
                content=block["content"]
            )
        
        knowledge_points.append(kp)
    
    # 构建依赖关系（使用对齐时间戳）
    dependency_graph = build_dependency_graph(knowledge_points)
    
    return {
        "knowledge_points": knowledge_points,
        "dependency_graph": dependency_graph,
        "alignment_quality": calculate_alignment_quality(aligned_blocks)
    }
```

#### A3.6 **[v8.0新增] 教师预设基准线机制**
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

#### A3.7 时间戳动态修正（v6.0新增 + v9.0对齐优化）

**问题背景**：职教视频中常存在"操作与讲解异步"问题，静态时间戳往往不准确。

**修正逻辑**：
1. 记录多数学生在点击某知识点后实际倒退/快进到的具体时间点
2. 统计分析行为数据，计算实际有效时间范围
3. 自动修正该知识点在图谱中的起始和结束坐标
4. 修正阈值：当超过30%的学生行为偏离原时间戳时触发修正
5. **[v9.0新增] 考虑多模态对齐后的时间戳**，而非原始时间戳

#### A3.8 职教专属功能
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
- **[v9.0新增] 多模态对齐质量报告**
- **[v9.0新增] 语义脱节日志**

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
- ✅ **[v9.0新增] 多模态时间戳对齐协议正常工作，±3秒窗口有效**
- ✅ **[v9.0新增] 语义脱节检测准确，教师校验流程完整**
- ✅ **[v9.0新增] 教师一键禁用AI功能正常，专家标注模式可用**

---

## 3.2 模块B：学习行为采集与认知状态识别（v6.0重构 + v7.0容错 + v8.0算法优化 + v9.0弱网降级）

### 3.2.1 模块目标
从单纯的行为数据分析升级为**认知+情境驱动**的智能判定，精准区分"深度思考"、"困难卡顿"与"无效停留"，**[v7.0新增] 并在低置信度时引入人机协作兜底机制**，**[v8.0优化] 通过难度系数加权避免认知步频的虚假繁荣风险**，**[v9.0新增] 通过弱网降级策略避免网络波动导致的误判**。

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

#### B2.2 多模态认知状态信号（v6.0新增 + v8.0监控信号 + v9.0弱网降级）

| 信号类型 | 数据来源 | 采集内容 | **[v7.0新增] 置信度输出** | **[v8.0新增] 信号状态** | **[v9.0新增] 弱网降级** |
|---------|---------|---------|--------------------------|------------------------|------------------------|
| **视线追踪** | 摄像头（需授权） | 视线位置（屏幕区域）、视线偏移时长 | 0.0-1.0 | 正常/丢失/遮挡 | 弱网时关闭 |
| **微表情** | 摄像头（需授权） | 表情分类（专注/困惑/走神/皱眉） | 0.0-1.0 | 正常/丢失/遮挡 | 弱网时关闭 |
| **鼠标行为** | 前端采集 | 鼠标位置、悬停区域、点击频率 | 1.0（确定性） | 正常 | 始终可用 |
| **键盘行为** | 前端采集 | 打字速度（笔记区）、快捷键使用 | 1.0（确定性） | 正常 | 始终可用 |
| **环境音** | 麦克风（需授权） | 环境杂音判定（教学相关/非教学相关） | 0.0-1.0 | 正常/丢失 | 弱网时关闭 |
| **人体检测** | 摄像头（需授权） | 人体存在、大动作偏移 | 0.0-1.0 | 正常/丢失/遮挡 | 弱网时关闭 |
| **[v8.0新增] 摄像头状态** | 系统检测 | 画面黑屏/遮挡/正常 | - | 正常/黑屏/遮挡 | 弱网时降级检测 |
| **[v9.0新增] 网络状态** | 系统检测 | 带宽/延迟/丢包率 | - | 正常/弱网/离线 | 触发降级策略 |

#### B2.3 **[v9.0新增] 弱网环境降级策略矩阵**

**问题背景**：职教学生可能在宿舍、实训室等网络不稳的环境学习。如果在弱网下，微表情数据上传失败，但视频在播放，系统会判定为"信号丢失"并强制暂停吗？这会造成学习中断。

**解决方案**：降级策略矩阵 + 本地缓存。

```python
class NetworkDegradationStrategy:
    """
    [v9.0新增] 弱网环境降级策略服务
    """
    
    BANDWIDTH_THRESHOLD = 200  # 带宽阈值：200kbps
    LATENCY_THRESHOLD = 1000   # 延迟阈值：1000ms
    PACKET_LOSS_THRESHOLD = 0.1  # 丢包率阈值：10%
    
    def __init__(self):
        self.local_cache = IndexedDBCache()  # 前端本地缓存
        self.network_monitor = NetworkMonitor()
    
    def check_network_status(self):
        """
        [v9.0新增] 检测网络状态
        """
        bandwidth = self.network_monitor.get_bandwidth()
        latency = self.network_monitor.get_latency()
        packet_loss = self.network_monitor.get_packet_loss_rate()
        
        if bandwidth < self.BANDWIDTH_THRESHOLD or latency > self.LATENCY_THRESHOLD or packet_loss > self.PACKET_LOSS_THRESHOLD:
            return {
                "status": "weak_network",
                "bandwidth": bandwidth,
                "latency": latency,
                "packet_loss": packet_loss,
                "degradation_level": self._calculate_degradation_level(bandwidth, latency, packet_loss)
            }
        
        return {"status": "normal"}
    
    def _calculate_degradation_level(self, bandwidth, latency, packet_loss):
        """
        [v9.0新增] 计算降级等级
        """
        if bandwidth < 100 or latency > 2000:
            return "severe"  # 严重降级
        elif bandwidth < self.BANDWIDTH_THRESHOLD or latency > self.LATENCY_THRESHOLD:
            return "moderate"  # 中等降级
        else:
            return "light"  # 轻度降级
    
    def apply_degradation_strategy(self, network_status):
        """
        [v9.0新增] 应用降级策略
        """
        if network_status["status"] == "normal":
            return {
                "multimodal_enabled": True,
                "visual_monitoring": True,
                "audio_monitoring": True,
                "cache_mode": "realtime"
            }
        
        degradation_level = network_status["degradation_level"]
        
        if degradation_level == "severe":
            # [v9.0核心逻辑] 严重降级：关闭视觉监控，仅保留行为日志
            return {
                "multimodal_enabled": False,
                "visual_monitoring": False,
                "audio_monitoring": False,
                "behavior_logging_only": True,
                "cache_mode": "local_only",
                "message": "网络环境较差，已切换为行为日志模式，学习不受影响"
            }
        elif degradation_level == "moderate":
            # 中等降级：关闭微表情，保留基础视觉检测
            return {
                "multimodal_enabled": True,
                "visual_monitoring": True,
                "facial_expression": False,  # 关闭微表情
                "audio_monitoring": False,
                "cache_mode": "local_with_sync",
                "message": "网络环境一般，已关闭部分监控功能"
            }
        else:
            # 轻度降级：降低采样频率
            return {
                "multimodal_enabled": True,
                "visual_monitoring": True,
                "audio_monitoring": True,
                "sampling_rate": 0.5,  # 降低采样率
                "cache_mode": "local_with_sync"
            }
    
    def handle_offline_learning(self, user_id, video_id):
        """
        [v9.0新增] 处理离线学习
        """
        # 行为日志先在前端IndexDB缓存
        behavior_log = {
            "user_id": user_id,
            "video_id": video_id,
            "events": [],
            "cached_at": datetime.now()
        }
        
        # 存储到本地缓存
        self.local_cache.save("behavior_log", behavior_log)
        
        return {
            "mode": "offline",
            "cache_enabled": True,
            "sync_when_online": True,
            "message": "当前为离线模式，学习数据已本地缓存，网络恢复后自动同步"
        }
    
    def sync_cached_data(self, user_id):
        """
        [v9.0新增] 网络恢复后同步缓存数据
        """
        cached_logs = self.local_cache.get_all("behavior_log")
        
        for log in cached_logs:
            if log["user_id"] == user_id:
                # 异步上传到服务器
                api_service.upload_behavior_log(log)
                # 标记为已同步
                self.local_cache.mark_synced(log["id"])
        
        return {
            "synced_count": len(cached_logs),
            "message": "缓存数据已同步"
        }
```

**降级策略矩阵**：

| 网络状态 | 带宽 | 延迟 | 丢包率 | 降级策略 | 监控功能 |
|---------|------|------|--------|---------|---------|
| **正常** | ≥200kbps | <1000ms | <10% | 全功能模式 | 全部启用 |
| **轻度降级** | 100-200kbps | 1000-1500ms | 10-20% | 降低采样率 | 全部启用（采样率0.5x） |
| **中等降级** | 50-100kbps | 1500-2000ms | 20-30% | 关闭微表情/音频 | 仅基础视觉+行为日志 |
| **严重降级** | <50kbps | >2000ms | >30% | 仅行为日志模式 | 仅行为日志，关闭所有视觉/音频监控 |

**关键规则**：
1. **弱网不触发信号丢失**：网络波动导致的监控数据丢失，不触发"信号丢失强制暂停"
2. **本地缓存优先**：行为日志先在前端IndexDB缓存，网络恢复后异步同步
3. **降级不降体验**：降级模式下，学习功能正常，仅关闭部分监控功能

#### B2.3.1 **[v10.0新增] 硬件画像驱动三级降级矩阵**

**问题背景**：在设备老旧/无独显/CPU飙高时，系统必须**自动切换计算模式**，避免页面卡死，同时保持"可用的学习闭环"。

**设备画像采集（客户端）**：
- **采集指标**（前端周期性采样）：
  - CPU占用（或近似：页面帧率、长任务占比、JS主线程阻塞）
  - 内存占用（近似：资源加载失败、GC频率）
  - GPU可用性（WebGL/硬件加速能力探测）
  - 摄像头分辨率/帧率可达性

**三级降级矩阵**：

| 等级 | 触发条件（示例） | 监控能力 | 说明 |
|------|------------------|----------|------|
| **L0 全量** | CPU≤60% 且 FPS≥30 | 视线+微表情+姿态+人体+环境音+行为 | 高性能设备全开 |
| **L1 精简** | CPU 60-80% 或 FPS 20-30 | 关闭微表情/姿态，仅保留视线(低采样)+人体+行为+ASR | 控制开销 |
| **L2 仅日志** | CPU>80% 或 FPS<20 或无GPU | 仅ASR+行为日志（暂停/回看/拖拽/笔记） | 保证不卡死 |

**降级特征补偿（权重修正）**：
- **问题**：进入"仅日志模式"后失去微表情等视觉信号，模块B认知画像准确率可能断崖式下跌。
- **策略**：当 `device_mode == L2_only_log` 时，自动执行"降级算法权重修正"，用更稳定的行为信号补偿缺失模态。

**规则**：
- **鼠标轨迹/停留/悬停权重**：从 `0.4 → 0.8`
- **暂停/回看频次权重**：从 `0.4 → 0.8`
- **视觉/微表情权重**：降为 `0`（或极低），避免用无效信号污染判断

```python
def get_difficulty_weights(device_mode: str):
    """
    [v10.0补充] 根据硬件降级等级动态调整困难度/触发权重
    """
    # 默认（全量/精简）：保留多模态
    if device_mode in ("L0_full", "L1_lite"):
        return {
            "mouse_dwell": 0.4,
            "replay": 0.4,
            "facial": 0.3,
            "gaze": 0.3,
        }
    
    # 仅日志模式：提高行为权重补偿视觉缺失
    if device_mode == "L2_only_log":
        return {
            "mouse_dwell": 0.8,  # 0.4 → 0.8
            "replay": 0.8,       # 0.4 → 0.8（暂停/回看频次）
            "facial": 0.0,
            "gaze": 0.0,
        }
    
    return {"mouse_dwell": 0.4, "replay": 0.4, "facial": 0.0, "gaze": 0.0}
```

**弱网降级（v9.0）与硬件降级（v10.0）协同规则**：
- **取更严格者**：任何一个判定进入"仅日志"，最终即为"仅日志"。

#### B2.4 **[v8.0优化] 个人认知步频计算（难度系数加权）**

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

#### B2.5 **[v8.0新增] 监控信号丢失处理机制**

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
            self._mark_learning_time_invalid(user_id, video_id, reason="signal_loss")
        else:
            # 普通视频：仅提示告警，不强制暂停
            self._warn_user(user_id, "检测到监控信号丢失，请调整摄像头/环境光线")
            self._log_signal_loss(user_id, video_id, signal_loss)
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

### 3.2.3 认知状态判定模型（v6.0核心重构 + v7.0容错 + v8.0优化 + v9.0弱网适配）

#### B3.1 信号不协和检测（Signal Dissonance）+ **[v7.0新增] 置信度门控** + **[v8.0新增] 信号丢失检查** + **[v9.0新增] 弱网降级检查**

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

**[v8.0新增] 信号丢失检查**：

（已在B3.1小节中通过 `_check_signal_status()` 统一实现，并在判定结果中输出 `signal_lost` 状态；同时B2.5提供了高危/普通视频的差异化处置规则。）

**[v9.0新增] 弱网降级检查**：

```python
class CognitiveStateDetectorV9:
    """
    v9.0认知状态检测器（含弱网降级检查）
    """
    
    def detect_cognitive_state(self, multimodal_signals, network_status):
        """
        [v9.0优化] 检测认知状态（含弱网降级检查）
        """
        # [v9.0新增] 首先检查网络状态
        if network_status["status"] == "weak_network":
            # 弱网模式：仅使用行为数据
            return self._detect_with_behavior_only(multimodal_signals)
        
        # [v8.0新增] 检查监控信号状态
        signal_status = self._check_signal_status(multimodal_signals)
        if signal_status == "lost":
            # 区分信号丢失原因：网络问题 vs 真实遮挡
            if self._is_network_related_loss():
                # [v9.0核心逻辑] 网络导致的丢失，不强制暂停
                return self._handle_network_loss()
            else:
                # 真实遮挡，按v8.0逻辑处理
                return self._handle_real_signal_loss()
        
        # 正常模式：使用完整多模态检测
        return self._detect_with_full_multimodal(multimodal_signals)
    
    def _detect_with_behavior_only(self, multimodal_signals):
        """
        [v9.0新增] 仅使用行为数据检测（弱网模式）
        """
        # 仅依赖行为数据：暂停、回放、拖拽等
        pause_duration = multimodal_signals.get("pause_duration", 0)
        seek_count = multimodal_signals.get("seek_count", 0)
        replay_count = multimodal_signals.get("replay_count", 0)
        
        # 基于行为数据判定
        if pause_duration > 10 and (seek_count > 2 or replay_count > 1):
            return CognitiveStateResult(
                state="difficulty",
                confidence=0.6,  # 降级模式下置信度较低
                detection_mode="behavior_only",
                requires_confirmation=True  # 建议人工确认
            )
        
        return CognitiveStateResult(state="normal", detection_mode="behavior_only")
    
    def _is_network_related_loss(self):
        """
        [v9.0新增] 判断信号丢失是否由网络问题导致
        """
        network_status = self.network_monitor.get_status()
        return network_status["status"] == "weak_network"
```

#### B3.2-B3.5 其他检测逻辑

#### B3.2 多模态交叉验证（v6.0新增 + v8.0信号丢失检测）

**目的**：防止误判"走神"或临时离开为学习困难。

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

（困难度公式与权重配置详见本章B3.3相关代码段落与说明，v8.0在个人步频上引入难度系数加权，避免虚假繁荣误报。）

#### B3.4 公共难点识别
- 若某视频片段被多人（如≥5人）标记为"困难卡顿"，自动标记为"公共难点"
- 提升该知识点的优先级，供教师重点关注
- 自动加入"全班共同盲点图表"

#### B3.5 溯源式根本原因诊断（v6.0新增 + v8.0环路检测）

（溯源诊断流程详见本章B3.5相关说明；v8.0在图谱侧补充环路检测与螺旋路径，避免回溯死循环。）

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
- **[v9.0新增] 弱网模式**：网络环境差，降级为行为日志模式

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
- ✅ **[v9.0新增] 弱网降级策略有效，不因网络波动误判**
- ✅ **[v9.0新增] 本地缓存机制正常，数据同步完整**

---

## 3.3 模块C：个性化学习路径与智能补偿资源（v6.0升级 + v7.0反馈优化 + v8.0风格自适应 + v9.0抗震荡）

### 3.3.1 模块目标
基于学习者的认知状态与薄弱点，**主动、分层、精准**地推送补偿资源，实现真正的"智能补偿教育"，**[v7.0新增] 并通过细化反馈和灰度复核机制持续优化资源质量**，**[v8.0新增] 通过学习风格自适应过滤器实现资源类型精准匹配**，**[v9.0新增] 通过干预抗震荡机制防止频繁弹窗，提升学习体验**。

### 3.3.2 个性化学习路径生成

#### C2.1 路径生成触发条件
- **实时触发**：检测到"困难卡顿"认知状态（模块B输出）
- **测验触发**：知识点测验失败
- **溯源触发**：连续失败2次，启动溯源诊断
- **[v7.0新增] 停滞触发**：累计停留时长超过视频时长5倍
- **[v8.0新增] 环路触发**：检测到知识点环路，生成螺旋路径
- **[v9.0新增] 螺旋跳出触发**：螺旋路径反复失败，自动跳转L3

#### C2.2 路径生成策略

**策略1：单点补偿（L1/L2干预）**
- 针对单个知识点的困难
- 推送该知识点的补偿资源
- 快速、轻量、精准

**策略2：溯源回补（v6.0新增 + v8.0环路优化 + v9.0跳出策略）**
- 针对前置知识缺失
- 回溯GNN知识依赖图
- 找到根本薄弱点
- 生成从根本点到目标点的补偿路径
- **[v8.0新增] 检测到环路时，生成螺旋上升路径**
- **[v9.0新增] 螺旋路径反复失败时，自动跳转L3**

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

**策略6：[v9.0新增] 螺旋路径跳出策略**
- 学生在螺旋路径中反复失败（≥3次）
- 自动跳转L3级教师答疑
- 不再继续螺旋学习

### 3.3.3 智能补偿资源生成（短、狠、准 + v7.0反馈闭环 + v8.0风格自适应 + v9.0抗震荡）

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

#### C3.2 **[v9.0新增] 干预抗震荡机制（Hysteresis）**

**问题背景**：目前系统有多个触发器（步频、表情、安全、进度停滞）。在实际场景中，学生状态是波动的。如果学生刚在边缘线波动（一会儿困惑，一会儿专注），系统可能会频繁弹出/关闭干预窗口，造成**"界面震荡"**，极度影响体验。

**解决方案**：干预冷静期（Cooldown Period）机制。

```python
class InterventionHysteresisService:
    """
    [v9.0新增] 干预抗震荡服务
    """
    
    COOLDOWN_PERIOD_L1 = 300  # L1冷静期：5分钟（300秒）
    COOLDOWN_PERIOD_L2 = 600  # L2冷静期：10分钟（600秒）
    SAFETY_PRIORITY_OVERRIDE = True  # 安全熔断优先级最高，不受冷静期限制
    
    def should_trigger_intervention(self, user_id, kp_id, intervention_level, trigger_type):
        """
        [v9.0新增] 判断是否应触发干预（含冷静期检查）
        """
        # [v9.0核心逻辑] 安全熔断不受冷静期限制
        if trigger_type == "safety_circuit_breaker":
            return True, "安全熔断优先级最高"
        
        # 检查是否在冷静期内
        last_intervention = self._get_last_intervention(user_id, kp_id, intervention_level)
        
        if last_intervention:
            time_since_last = (datetime.now() - last_intervention.triggered_at).total_seconds()
            cooldown_period = self._get_cooldown_period(intervention_level)
            
            if time_since_last < cooldown_period:
                # [v9.0核心逻辑] 在冷静期内，禁止再次触发
                remaining_time = cooldown_period - time_since_last
                return False, f"干预冷静期内（剩余{remaining_time:.0f}秒），暂不触发"
        
        # 检查是否进入新知识点（新知识点重置冷静期）
        current_kp = self._get_current_kp(user_id)
        if last_intervention and last_intervention.kp_id != current_kp.id:
            # 进入新知识点，重置冷静期
            return True, "新知识点，重置冷静期"
        
        return True, "允许触发"
    
    def record_intervention_triggered(self, user_id, kp_id, intervention_level, dismissed_by_user=False):
        """
        [v9.0新增] 记录干预触发（含用户关闭标记）
        """
        intervention = Intervention(
            user_id=user_id,
            kp_id=kp_id,
            level=intervention_level,
            triggered_at=datetime.now(),
            dismissed_by_user=dismissed_by_user,  # [v9.0新增] 是否被用户关闭
            cooldown_until=self._calculate_cooldown_until(intervention_level)  # [v9.0新增] 冷静期结束时间
        )
        db.save(intervention)
        
        return intervention
    
    def _get_cooldown_period(self, intervention_level):
        """
        [v9.0新增] 获取冷静期时长
        """
        cooldown_map = {
            "L1": self.COOLDOWN_PERIOD_L1,
            "L2": self.COOLDOWN_PERIOD_L2,
            "L3": 0  # L3不受冷静期限制（人类介入）
        }
        return cooldown_map.get(intervention_level, self.COOLDOWN_PERIOD_L1)
    
    def _calculate_cooldown_until(self, intervention_level):
        """
        [v9.0新增] 计算冷静期结束时间
        """
        cooldown_period = self._get_cooldown_period(intervention_level)
        return datetime.now() + timedelta(seconds=cooldown_period)
```

**抗震荡规则**：
1. **L1干预冷静期**：5分钟（或直至进入下一个知识点）
2. **L2干预冷静期**：10分钟（或直至进入下一个知识点）
3. **安全熔断不受限制**：最高优先级，不受冷静期限制
4. **新知识点重置**：进入新知识点时，自动重置冷静期
5. **用户关闭标记**：如果学生主动关闭干预窗口，记录标记，在冷静期内不再弹出

#### C3.3 **[v9.0优化] 螺旋路径跳出策略**

**问题背景**：学生在螺旋路径中反复失败，系统应提供跳出机制。

**解决方案**：反复失败自动跳转L3。

```python
class SpiralPathEscapeService:
    """
    [v9.0新增] 螺旋路径跳出服务
    """
    
    MAX_SPIRAL_FAILURES = 3  # 最大失败次数：3次
    
    def check_spiral_escape(self, user_id, spiral_path_id):
        """
        [v9.0新增] 检查是否需要跳出螺旋路径
        """
        spiral_path = db.query(SpiralLearningPath).get(spiral_path_id)
        
        # 统计失败次数
        failures = db.query(Exercise).filter(
            user_id=user_id,
            spiral_path_id=spiral_path_id,
            is_correct=False
        ).count()
        
        if failures >= self.MAX_SPIRAL_FAILURES:
            # [v9.0核心逻辑] 反复失败 → 自动跳转L3
            return self._trigger_l3_escape(user_id, spiral_path_id, failures)
        
        return None
    
    def _trigger_l3_escape(self, user_id, spiral_path_id, failure_count):
        """
        [v9.0新增] 触发L3跳出
        """
        spiral_path = db.query(SpiralLearningPath).get(spiral_path_id)
        user = db.query(User).get(user_id)
        
        # 创建L3干预
        intervention = Intervention(
            user_id=user_id,
            kp_id=None,  # 螺旋路径涉及多个知识点
            level="L3",
            trigger_reason="spiral_path_escape",  # [v9.0新增] 螺旋路径跳出
            trigger_data={
                "spiral_path_id": spiral_path_id,
                "loop_kps": spiral_path.loop_kp_ids,
                "failure_count": failure_count,
                "description": f"在螺旋路径中失败{failure_count}次，建议教师直接答疑"
            },
            created_at=datetime.now(),
            status="pending"
        )
        db.save(intervention)
        
        # 更新螺旋路径状态
        spiral_path.status = "escaped_to_l3"
        spiral_path.escape_reason = "repeated_failures"
        db.save(spiral_path)
        
        # 发送预警至教师端
        alert = TeacherAlert(
            type="spiral_path_escape",
            priority="high",
            user_id=user_id,
            title=f"🔴 螺旋路径跳出：{user.name}需要直接答疑",
            message=f"""
            学生：{user.name}
            螺旋路径：知识点{spiral_path.loop_kp_ids}
            失败次数：{failure_count}次
            建议：直接进行1对1答疑，而非继续螺旋学习
            """,
            actions=[
                {"label": "1对1答疑", "action": "direct_tutoring"},
                {"label": "查看螺旋路径详情", "action": "view_spiral_path"}
            ]
        )
        alert_service.send(alert)
        
        return intervention
```

#### C3.4 **[v8.0新增] 学习风格自适应过滤器**
**目标**：基于学生对补偿资源的反馈与行为，推断学习风格画像，并在L2资源推荐时进行过滤与重排，提升匹配度，降低“风格冲突”导致的无效干预。

**学习风格画像（v8.0数据结构）**：
- `efficiency_preference`: fast / medium / slow
- `content_preference`: text / video / audio / visual / mixed
- `interaction_preference`: passive / active / social
- `confidence`: 0.0-1.0（风格推断置信度）
- `feedback_count`: 样本数

**更新触发**：
- 学生对资源提交反馈（尤其是负面原因：讲解啰嗦/内容太难/格式不喜欢/与知识点不符）
- 学生在资源上的停留/完成率/回放等行为信号（可作为弱特征）

**过滤/重排规则（示例）**：
- `efficiency_preference == fast`：
  - 优先：**参数速查表 / 思维导图 / 知识提示**
  - 降权：长视频、冗长讲解类卡片
- `content_preference == text`：
  - 优先：知识卡片/思维导图
  - 降权：纯音频/长微视频
- `interaction_preference == social`：
  - 优先：同伴经验（知识锦囊）、同伴互助入口

```python
class LearningStyleAdaptiveFilter:
    """
    [v8.0新增] 学习风格自适应过滤器（基于反馈画像重排资源）
    """
    def filter_resources_by_style(self, user_id, candidate_resources):
        style = db.query(LearningStyle).filter(user_id=user_id).first()
        if not style or style.confidence < 0.5:
            return candidate_resources  # 置信度不足，不强行过滤
        
        def score(res):
            s = 0.0
            tags = set(getattr(res, "style_tags", []) or [])
            # 效率偏好
            if style.efficiency_preference == "fast" and ("速查" in tags or "高效型" in tags):
                s += 2.0
            # 内容偏好
            if style.content_preference == "text" and ("文本型" in tags):
                s += 1.5
            if style.content_preference == "video" and ("视频型" in tags):
                s += 1.5
            # 社交偏好
            if style.interaction_preference == "social" and ("社交型" in tags):
                s += 1.0
            return s
        
        return sorted(candidate_resources, key=score, reverse=True)
```

#### C3.5 **[v7.0优化] 资源评价细化机制**
```python
class ResourceFeedbackServiceV7:
    """
    v7.0补偿资源反馈服务（细化评价维度）
    """
    
    FEEDBACK_DIMENSIONS = {
        "too_hard": "内容太难",
        "too_verbose": "讲解啰嗦",
        "format_issue": "格式不喜欢",
        "content_mismatch": "与知识点不符"
    }
    
    def record_feedback_v7(self, resource_id, user_id, is_helpful, negative_reason=None):
        """
        [v7.0新增] 记录细化反馈
        """
        feedback = ResourceFeedback(
            resource_id=resource_id,
            user_id=user_id,
            is_helpful=is_helpful,
            negative_reason=negative_reason,  # [v7.0新增] 负面原因
            created_at=datetime.now()
        )
        db.save(feedback)
        
        # 检查是否需要自动下架
        self._check_auto_remove_v7(resource_id)
    
    def _check_auto_remove_v7(self, resource_id):
        """
        [v7.0优化] 检查自动下架（按原因聚类）
        """
        recent_feedbacks = db.query(ResourceFeedback).filter(
            resource_id=resource_id
        ).order_by(desc(created_at)).limit(5).all()
        
        # 统计负面反馈
        negative_feedbacks = [f for f in recent_feedbacks if not f.is_helpful]
        
        if len(negative_feedbacks) >= 3:
            # [v7.0新增] 分析负面原因分布
            reason_counts = {}
            for fb in negative_feedbacks:
                reason = fb.negative_reason or "unknown"
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            
            # 找到主要问题
            main_reason = max(reason_counts, key=reason_counts.get)
            
            # 自动下架
            self._remove_resource_v7(resource_id, main_reason)
            self._notify_teacher_v7(resource_id, main_reason, reason_counts)
    
    def _remove_resource_v7(self, resource_id, main_reason):
        """[v7.0优化] 下架资源（记录原因）"""
        resource = db.query(Resource).get(resource_id)
        resource.status = "removed_auto"
        resource.removed_at = datetime.now()
        resource.removed_reason = f"连续负反馈自动下架（主因：{self.FEEDBACK_DIMENSIONS[main_reason]}）"
        db.save(resource)
    
    def _notify_teacher_v7(self, resource_id, main_reason, reason_counts):
        """[v7.0优化] 通知教师（含问题分析）"""
        notification = TeacherNotification(
            type="resource_removed",
            resource_id=resource_id,
            message=f"资源因'{self.FEEDBACK_DIMENSIONS[main_reason]}'被下架",
            detail=f"反馈统计：{reason_counts}",
            action_required="请修正后重新上线"
        )
        notification_service.send(notification)
```

#### C3.6 **[v7.0新增] 修正资源灰度复核机制**
```python
class GrayscaleReviewService:
    """
    灰度复核服务
    """
    
    def republish_resource(self, resource_id, teacher_id):
        """
        教师修正后重新上线资源
        """
        resource = db.query(Resource).get(resource_id)
        
        # [v7.0新增] 标记为测试版
        resource.status = "testing"
        resource.testing_started_at = datetime.now()
        resource.revised_by = teacher_id
        resource.testing_target_count = 5  # 灰度验证样本数
        resource.testing_feedback_count = 0
        
        db.save(resource)
        
        return resource
    
    def record_testing_feedback(self, resource_id, user_id, is_helpful):
        """
        记录灰度测试反馈
        """
        feedback = TestingFeedback(
            resource_id=resource_id,
            user_id=user_id,
            is_helpful=is_helpful,
            created_at=datetime.now()
        )
        db.save(feedback)
        
        # 更新测试进度
        resource = db.query(Resource).get(resource_id)
        resource.testing_feedback_count += 1
        
        # [v7.0新增] 检查是否达到验证标准
        if resource.testing_feedback_count >= resource.testing_target_count:
            self._evaluate_testing_result(resource_id)
    
    def _evaluate_testing_result(self, resource_id):
        """
        评估灰度测试结果
        """
        feedbacks = db.query(TestingFeedback).filter(
            resource_id=resource_id
        ).all()
        
        helpful_count = sum(1 for f in feedbacks if f.is_helpful)
        helpful_rate = helpful_count / len(feedbacks)
        
        resource = db.query(Resource).get(resource_id)
        
        # [v7.0新增] 根据反馈决定是否转正
        if helpful_rate >= 0.6:  # 60%好评率
            resource.status = "active"
            resource.approved_at = datetime.now()
            self._notify_teacher(resource_id, "测试通过，资源已正式上线")
        else:
            resource.status = "testing_failed"
            self._notify_teacher(resource_id, f"测试未通过（好评率{helpful_rate:.0%}），建议继续修正")
        
        db.save(resource)
```

#### C3.7 **[v7.0新增] 智能剪辑上下文保留协议**
```python
class VideoClippingServiceV7:
    """
    v7.0智能视频剪辑服务（含上下文保留）
    """
    
    CONTEXT_BEFORE = 5  # 前置上下文：5秒
    CONTEXT_AFTER = 3   # 后置上下文：3秒
    MAX_DURATION = 90   # 最大时长：90秒
    
    def clip_knowledge_point(self, video_id, kp_id):
        """
        [v7.0优化] 剪辑知识点片段（含上下文）
        """
        kp = db.query(KnowledgePoint).get(kp_id)
        video = db.query(Video).get(video_id)
        
        # [v7.0新增] 计算剪辑范围（含上下文）
        clip_start = max(0, kp.start_time - self.CONTEXT_BEFORE)
        clip_end = min(video.duration, kp.end_time + self.CONTEXT_AFTER)
        clip_duration = clip_end - clip_start
        
        # 时长控制
        if clip_duration > self.MAX_DURATION:
            core_duration = kp.end_time - kp.start_time
            if core_duration > self.MAX_DURATION - (self.CONTEXT_BEFORE + self.CONTEXT_AFTER):
                clip_start = kp.start_time - 3  # 缩短前置上下文
                clip_end = min(kp.start_time + self.MAX_DURATION - 3, kp.end_time + 2)
        
        clipped_video = self.video_editor.clip(
            video_path=video.file_path,
            start_time=clip_start,
            end_time=clip_end
        )
        
        subtitle = self._generate_subtitle(kp, clip_start, clip_end)
        
        return ClippedVideo(
            original_video_id=video_id,
            kp_id=kp_id,
            clip_start=clip_start,
            clip_end=clip_end,
            duration=clip_end - clip_start,
            file_path=clipped_video.path,
            subtitle=subtitle,
            has_context=True,  # [v7.0新增] 标记已保留上下文
            context_info={
                "before": clip_start < kp.start_time,
                "after": clip_end > kp.end_time,
                "before_duration": kp.start_time - clip_start if clip_start < kp.start_time else 0,
                "after_duration": clip_end - kp.end_time if clip_end > kp.end_time else 0
            }
        )
```

### 3.3.4 分层干预策略（L1/L2/L3）（v6.0新增 + v7.0优化 + v8.0风格过滤 + v9.0抗震荡）

| 干预等级 | 触发条件 | 干预形式 | 资源优先级 | **[v7.0优化]** | **[v8.0新增]** | **[v9.0新增]** |
|---------|---------|---------|-----------|----------------|----------------|----------------|
| **L1：轻量提醒** | 首次T1异常停留 | 侧边栏浮窗（知识卡片） | 原创视频摘要 | 细化反馈 | **风格过滤** | **5分钟冷静期** |
| **L2：交互修复** | 二次停留或测验失败 | 3min精准微视频 + 针对性练习 | AI智能剪辑片段 | 上下文保留 | **风格自适应** | **10分钟冷静期** |
| **L3：人类介入** | **[v7.0新增] 进度停滞或**修复后持续低增益 **或[v9.0新增] 螺旋路径反复失败** | 触发"求助"按钮，推送至班级群或导师端 | 1对1连线/同伴互助 | **自动触发** | - | **无冷静期限制** |

**[v9.0新增] L1/L2干预抗震荡流程**：

```python
def trigger_intervention_v9(user_id, kp_id, intervention_level, trigger_data):
    """
    [v9.0优化] 触发干预（含抗震荡检查）
    """
    hysteresis_service = InterventionHysteresisService()
    
    # [v9.0核心逻辑] 检查是否应触发（含冷静期）
    should_trigger, reason = hysteresis_service.should_trigger_intervention(
        user_id, kp_id, intervention_level, trigger_data.get("trigger_type")
    )
    
    if not should_trigger:
        # 在冷静期内，不触发
        logger.info(f"干预被冷静期阻止：{reason}")
        return None
    
    # 正常触发干预
    intervention = intervention_service.create_intervention(
        user_id=user_id,
        kp_id=kp_id,
        level=intervention_level,
        trigger_data=trigger_data
    )
    
    # [v9.0新增] 记录触发（用于冷静期计算）
    hysteresis_service.record_intervention_triggered(
        user_id, kp_id, intervention_level
    )
    
    return intervention
```

### 3.3.5 社会学习模块（v6.0新增）
**知识锦囊功能**：
- 学生通过L2干预掌握知识后
- 系统邀请录制30s经验分享
- 分享给正卡在同一处的同学
- 激励机制：贡献者获得学习积分

### 3.3.6 输出
- 个性化学习路径JSON（知识点序列+补偿资源）
- 补偿资源推送记录
- 干预效果评估报告
- **[v7.0新增] 资源反馈分析报告**
- **[v7.0新增] 灰度测试结果报告**
- **[v8.0新增] 学习风格画像**
- **[v8.0新增] 风格匹配度报告**
- **[v9.0新增] 干预冷静期记录**
- **[v9.0新增] 螺旋路径跳出记录**

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
- ✅ **[v9.0新增] 干预冷静期机制有效，界面震荡减少≥80%**
- ✅ **[v9.0新增] 螺旋路径跳出策略正常，反复失败自动跳转L3**

---

## 3.4 模块D：教师端赋能工具（v6.0升级 + v7.0决策支持 + v9.0教师主权）

### 3.4.1 模块目标
从"被动审核员"转变为"主动教练"，**[v7.0新增] 从数据看板升级为趋势预测+策略推荐的决策支持系统**，**[v9.0新增] 强化教师主权，支持一键禁用AI自动生成**。

### 3.4.2 核心功能

#### D2.1 班级学情大屏

**全班共同盲点图表**（v6.0新增）：
- 显示全班50%以上学生触发补偿动作的片段
- 按困难率排序
- 支持点击查看详细数据

**学习热力图**：
- 视频时间轴上的停留热力分布
- 回放密集区域标记
- 公共难点可视化

#### D2.2 **[v7.0新增] 趋势预测与策略推荐**

```python
class TeachingStrategyAdvisorV7:
    """
    v7.0教学策略建议服务
    """
    
    def predict_future_difficulties(self, course_id, class_id):
        """
        [v7.0新增] 预测未来难点
        """
        current_progress = self._get_class_progress(class_id, course_id)
        
        all_kps = db.query(KnowledgePoint).filter(
            course_id=course_id
        ).all()
        
        predictions = []
        
        for kp in all_kps:
            if kp.id in current_progress.completed_kps:
                continue
            
            predicted_difficulty = self._predict_difficulty_rate(
                kp,
                current_progress,
                class_id
            )
            
            if predicted_difficulty >= 0.5:  # 预测困难率≥50%
                predictions.append({
                    "kp_id": kp.id,
                    "kp_name": kp.name,
                    "predicted_difficulty_rate": predicted_difficulty,
                    "current_progress": self._calculate_progress_rate(kp.id, class_id),
                    "current_difficulty_rate": self._get_current_difficulty_rate(kp.id, class_id),
                    "prediction_basis": self._explain_prediction(kp, current_progress)
                })
        
        predictions.sort(key=lambda x: x["predicted_difficulty_rate"], reverse=True)
        return predictions

#### D2.3 **[v9.0新增] 教师主权管理**

**一键禁用AI自动生成**：

详见第3.1.4节A3.4小节。

**专家标注模式**：

```python
class ExpertAnnotationMode:
    """
    [v9.0新增] 专家标注模式
    """
    
    def create_expert_annotation(self, video_id, teacher_id, annotations):
        """
        [v9.0新增] 创建专家标注
        """
        # 检查是否允许专家标注
        video = db.query(Video).get(video_id)
        if video.annotation_mode != "expert_only":
            raise PermissionError("该视频未启用专家标注模式")
        
        expert_annotations = []
        for annotation in annotations:
            kp = KnowledgePoint(
                video_id=video_id,
                name=annotation["name"],
                start_time=annotation["start_time"],
                end_time=annotation["end_time"],
                ai_generated=False,  # [v9.0新增] 标记为人工标注
                expert_annotated=True,
                expert_id=teacher_id,
                created_at=datetime.now()
            )
            db.save(kp)
            expert_annotations.append(kp)
        
        return {
            "annotation_count": len(expert_annotations),
            "mode": "expert_only",
            "message": "专家标注已保存"
        }
```

#### D2.4 Coach Mode（教练模式）（v6.0新增）

**实时监控面板**：
- 当前正在学习的学生列表
- 实时困难状态标记
- L3级预警弹窗

**快速响应工具**：
- 1对1视频连线
- 推荐同伴互助
- 快速推送自定义资源

#### D2.5 资源审核与编辑

**AI生成资源审核**：
- 查看系统自动生成的知识卡片、微视频
- 在线编辑或标记为"需修正"
- **[v7.0新增] 查看资源反馈统计与问题分类**

**手动上传补充资源**：
- 上传自制补偿视频、练习题
- 关联到特定知识点

#### D2.6 **[v10.0新增] 数据审计引擎与难度保护区**

**问题背景**：资源反馈体系可能被以下因素污染：
- 学生"情绪化差评"
- 同一账号批量点踩
- 同一IP/设备短时间刷票
- 与学习行为矛盾的反馈（比如未观看就评价）

**审计引擎规则**：
- **一致性校验**：必须满足"看过/触发过资源"才可反馈
- **速率限制**：同一用户对同一资源 24h 内最多 N 次
- **异常模式识别**（规则优先，模型可后续加入）：
  - 低停留时长 + 立刻差评（可疑）
  - 多资源连续差评且无学习行为变化（可疑）
  - 班级内极端离群（可疑）
- **处置**：
  - 标记为 `audit_suspected`
  - 不参与"连续3个差评自动下架"的统计
  - 教师端可查看审计原因并手动放行/驳回

**难度保护区（Difficulty Protection Zone）**：
- **问题**：班级可能因进度压力/畏难情绪对"高难但必要"的资源集体差评，导致AI误下架优质资源。
- **规则**：当满足以下条件时，启用"难度保护区"，提高自动下架阈值：
  - `expert_difficulty_coefficient > 1.8`（例如教师预设难度系数/停留系数）
  - 或知识点被标记为 `is_core_difficulty = true`
- **阈值调整**：
  - 普通资源：连续负反馈阈值 `3`
  - 难度保护区资源：连续负反馈阈值 `10`（或更高，且必须包含至少1条"内容不符"类证据才允许下架）

**下架仲裁：反馈-行为一致性强制校验（80%门槛）**：
- **问题**：即使提高阈值，仍可能被恶意刷票；同时"未看先评"会污染资源评价体系。
- **强制规则**：任何"差评/无帮助"在计入下架统计前，必须通过**反馈-行为一致性校验**：
  - **观看门槛**：该用户对该资源的有效观看进度 ≥ 80%
  - **或测验门槛**：该用户完成了该资源关联的诊断测试/练习（满足最低作答数）
  - 不满足则直接判定为 `invalid_feedback`，进入审计但**不计入**自动下架统计。

```python
def is_negative_feedback_countable(user_id: str, resource_id: str) -> bool:
    """
    [v10.0补充] 反馈-行为一致性强制校验：未看先评不计入下架统计
    """
    watch_ratio = get_resource_watch_ratio(user_id, resource_id)  # 0.0-1.0
    has_related_test = has_completed_related_test(user_id, resource_id)
    
    if watch_ratio >= 0.8 or has_related_test:
        return True
    return False

def get_auto_remove_threshold(expert_difficulty_coefficient: float, is_core_difficulty: bool):
    """
    [v10.0补充] 难度保护区：提高自动下架阈值，防止优质高难资源被误杀
    """
    if is_core_difficulty or (expert_difficulty_coefficient and expert_difficulty_coefficient > 1.8):
        return 10
    return 3
```

### 3.4.3 输出
- 班级学情大屏（Web界面）
- 学生个体学习报告（PDF导出）
- **[v7.0新增] 趋势预测报告（JSON/PDF）**
- **[v7.0新增] 教学策略建议（结构化数据）**
- 动作偏差分析报告
- **[v9.0新增] AI生成禁用记录**
- **[v9.0新增] 语义脱节日志**

### 3.4.4 验收标准
- ✅ 教师能查看全班共同盲点图表
- ✅ 支持L3级预警实时推送
- ✅ Coach Mode响应延迟 < 2秒
- ✅ 资源审核界面友好，支持在线编辑
- ✅ **[v7.0新增] 趋势预测准确率 ≥ 70%**
- ✅ **[v7.0新增] 策略建议具体可执行，教师满意度 ≥ 80%**
- ✅ **[v7.0新增] 动作偏差报告自动生成，包含具体改进建议**
- ✅ **[v9.0新增] 一键禁用AI功能正常，专家标注模式可用**
- ✅ **[v9.0新增] 语义脱节日志可查看，教师校验流程完整**

---

# 4. 逻辑漏洞修复方案（v6.0 + v7.0容错增强 + v8.0深度优化 + v9.0边界补齐）

本章节详细说明从v4.0到v9.0版本的逻辑漏洞修复方案。

## 4.1-4.3 基础修复方案

对应v8.0的三类基础修复（按“问题 → 修复落点”整理）：
- **4.1 行为归因的“排他性”逻辑修复**：详见第3.2.3节（认知判定与信号丢失/置信度门控的容错闭环）
- **4.2 补偿资源“生成-反馈”负反馈闭环修复**：详见第3.3.3节（资源反馈细化 + 灰度复核 + 上下文保留）
- **4.3 知识点时间戳的“动态修正”逻辑修复**：详见第3.1.4节（多模态时间窗对齐 + 教师校验）

## 4.4 **[v9.0新增] 干预触发的"抗震荡"机制修复**

### 4.4.1 问题描述
**v8.0漏洞**：系统有多个触发器（步频、表情、安全、进度停滞）。在实际场景中，学生状态是波动的。如果学生刚在边缘线波动（一会儿困惑，一会儿专注），系统可能会频繁弹出/关闭干预窗口，造成**"界面震荡"**，极度影响体验。

### 4.4.2 修复方案

**[v9.0新增] 干预冷静期（Hysteresis）机制**：

详见第3.3.3节C3.2小节。

**效果**：
- 防止频繁弹窗，界面震荡减少≥80%
- 提升学习体验，减少干扰
- 安全熔断不受限制，保证安全优先

## 4.5 **[v9.0新增] 多模态时间戳对齐误差修复**

### 4.5.1 问题描述
**v8.0漏洞**：ASR（语音）、CV（视觉）和行为日志的时间戳往往是不对齐的（网络延迟、硬件性能差异）。如果ASR显示教师在01:10讲完知识点，但CV在01:12才捕捉到板书变化，系统该以哪个为基准？

### 4.5.2 修复方案

**[v9.0新增] 时间戳对齐窗口协议**：

详见第3.1.3节A3.2小节。

**效果**：
- 定义±3秒软对齐窗口，处理时间戳误差
- 语义脱节检测（>5秒），提示教师手动校验
- 提高知识图谱构建准确性

## 4.6 **[v9.0新增] 弱网环境误判修复**

### 4.6.1 问题描述
**v8.0漏洞**：如果在弱网下，微表情数据上传失败，但视频在播放，系统会判定为"信号丢失"并强制暂停吗？这会造成学习中断。

### 4.6.2 修复方案

**[v9.0新增] 降级策略矩阵**：

详见第3.2.2节B2.3小节。

**效果**：
- 弱网环境下自动降级，不触发信号丢失强制暂停
- 本地缓存机制，网络恢复后自动同步
- 保证学习连续性，不因网络波动中断

## 4.7 **[v9.0新增] 教师主权缺失修复**

### 4.7.1 问题描述
**v8.0漏洞**：如果教师判定AI对某视频的知识点拆解完全错误，缺乏"否定权重"，无法禁用AI自动生成。

### 4.7.2 修复方案

**[v9.0新增] 一键禁用AI + 专家标注模式**：

详见第3.1.4节A3.4小节。

**效果**：
- 保护教师教学主权
- 支持纯人工标注模式
- 提高知识点拆解准确性

## 4.8 **[v9.0新增] 螺旋路径跳出策略修复**

### 4.8.1 问题描述
**v8.0漏洞**：学生在螺旋路径中反复失败时，缺乏跳出机制，可能陷入死循环。

### 4.8.2 修复方案

**[v9.0新增] 反复失败自动跳转L3**：

详见第3.3.3节C3.3小节。

**效果**：
- 反复失败≥3次自动跳转L3
- 避免螺旋路径死循环
- 及时引入人类介入

---

# 5. 职教特色增强设计（v6.0 + v7.0容错 + v8.0盲区处理 + v9.0弱网适配）

## 5.1 高危场景"安全熔断"机制（v6.0新增 + v7.0容错增强 + v8.0盲区处理 + v9.0弱网区分）

### 5.1.1 应用场景

- 焊接操作视频
- 电工操作视频
- 化工实验视频
- 汽修高危操作（如千斤顶使用）

### 5.1.2 **[v7.0升级]** 技术实现

```python
class SafetyMonitorServiceV7:
    """
    v7.0安全监控服务（含置信度检查）
    """
    
    PPE_CONFIDENCE_THRESHOLD = 0.85  # PPE检测置信度阈值
    
    def check_safety_v7(self, video_frame, operation_type):
        """
        [v7.0优化] 安全检查（含置信度门控）
        """
        # PPE检测
        ppe_result = self.ppe_detector.detect(video_frame)
        
        # [v7.0新增] 检查检测置信度：低置信度→人工确认兜底
        if ppe_result.confidence < self.PPE_CONFIDENCE_THRESHOLD:
            required_ppe = self._get_required_ppe(operation_type)
            return SafetyCheckResult(
                is_safe="uncertain",
                confidence=ppe_result.confidence,
                requires_confirmation=True,
                confirmation_prompt={
                    "title": "⚠️ 安全装备确认",
                    "message": "环境光线不足，无法确认防护装备佩戴情况。",
                    "checklist": [f"□ {item}" for item in required_ppe],
                    "action": "请确认已佩戴全部必需防护装备"
                }
            )
        
        # 高置信度 - 正常判定
        required_ppe = self._get_required_ppe(operation_type)
        missing_ppe = [ppe for ppe in required_ppe if not ppe_result.has(ppe, confidence_threshold=self.PPE_CONFIDENCE_THRESHOLD)]
        if missing_ppe:
            return SafetyCheckResult(
                is_safe=False,
                confidence=ppe_result.confidence,
                violation_type="missing_ppe",
                missing_items=missing_ppe,
                action="suspend_video",
                message=f"检测到未佩戴：{', '.join(missing_ppe)}"
            )
        return SafetyCheckResult(is_safe=True, confidence=ppe_result.confidence)
```

**强制中断逻辑（v7.0）**：
- **触发条件**（仅高置信度违规）：PPE检测置信度 ≥ 0.85 且明确检测到未佩戴必需PPE（或明确违规动作）
- **中断响应**：立即挂起当前视频，强制弹出“安全规范确认”（或播放事故案例回顾），通过后方可继续

### 5.1.3 **[v8.0新增] 安全熔断的"盲区处理"逻辑**

**问题描述**：仅做PPE识别的置信度确认仍存在“摄像头丢失/被遮挡/黑屏”等监控盲区；在高危实操视频里必须补齐策略，防止“遮挡规避”。

**[v8.0新增] 安全监控信号心跳检测（核心思路）**：
- 黑屏检测（亮度阈值）
- 人体缺位检测
- 遮挡检测
- 满足“丢失≥10秒”才进入处置（降低误报）

**处理规则（v8.0）**：
1. **高危视频**（焊接/电工/化工等）：信号丢失≥10秒 → **强制暂停**；记录为“非合规学习行为”，**不计入学习时长**，通知教师
2. **普通视频**：信号丢失≥10秒 → 警告提示；不强制暂停；记录日志

### 5.1.4 **[v9.0新增] 弱网环境下的安全检测区分**

```python
class SafetyMonitorServiceV9:
    """
    v9.0安全监控服务（含弱网区分）
    """
    
    def check_safety_v9(self, video_frame, operation_type, network_status):
        """
        [v9.0优化] 安全检查（区分网络问题与真实遮挡）
        """
        # [v9.0新增] 首先检查网络状态
        if network_status["status"] == "weak_network":
            # 弱网环境：降低安全检测严格度，不强制暂停
            return self._check_safety_degraded_mode(video_frame, operation_type)
        
        # 正常网络：使用完整安全检测
        return self._check_safety_full_mode(video_frame, operation_type)
    
    def _check_safety_degraded_mode(self, video_frame, operation_type):
        """
        [v9.0新增] 降级模式下的安全检查
        """
        # 仅进行基础检测，不强制暂停
        ppe_result = self.ppe_detector.detect(video_frame)
        
        if ppe_result.confidence < 0.5:
            # 置信度太低，可能是网络问题
            return SafetyCheckResult(
                is_safe="uncertain",
                confidence=ppe_result.confidence,
                requires_confirmation=True,
                mode="degraded",
                message="网络环境较差，安全检测受限，请手动确认防护装备"
            )
                    return SafetyCheckResult(
                is_safe="uncertain",
                confidence=ppe_result.confidence,
                requires_confirmation=True,
                mode="degraded",
                message="网络环境较差，安全检测受限，请手动确认防护装备"
            )
        
        # 降级模式下，即使检测到问题也不强制暂停
        return SafetyCheckResult(
            is_safe=True,
            confidence=ppe_result.confidence,
            mode="degraded",
            message="降级模式：安全检测受限，请确保防护装备已佩戴"
        )
```

**降级策略矩阵**：

| 网络状态 | 带宽 | 延迟 | 丢包率 | 降级措施 | 安全检测 |
|---------|------|------|--------|---------|---------|
| **正常** | ≥200kbps | ≤1000ms | ≤10% | 全功能模式 | 完整检测 |
| **轻度降级** | 100-200kbps | 1000-2000ms | 10-20% | 关闭微表情 | 降低置信度阈值 |
| **中度降级** | 50-100kbps | 2000-3000ms | 20-30% | 关闭视觉监控 | 仅手动确认 |
| **严重降级** | <50kbps | >3000ms | >30% | 仅行为日志 | 不强制暂停 |

**本地缓存逻辑**：

```python
class LocalCacheService:
    """
    [v9.0新增] 本地缓存服务
    """
    
    def __init__(self):
        self.indexed_db = IndexedDB("learning_behavior_cache")
    
    def cache_behavior_log(self, behavior_event):
        """
        [v9.0新增] 缓存行为日志到本地
        """
        # 存储到IndexedDB
        self.indexed_db.put("behavior_logs", {
            "id": behavior_event.id,
            "user_id": behavior_event.user_id,
            "video_id": behavior_event.video_id,
            "event_type": behavior_event.type,
            "timestamp": behavior_event.timestamp,
            "data": behavior_event.data,
            "synced": False  # 标记为未同步
        })
    
    def sync_cached_logs(self):
        """
        [v9.0新增] 网络恢复后同步缓存的日志
        """
        cached_logs = self.indexed_db.getAll("behavior_logs", {"synced": False})
        
        for log in cached_logs:
            try:
                # 尝试同步到服务器
                api_service.upload_behavior_log(log)
                
                # 标记为已同步
                log["synced"] = True
                self.indexed_db.put("behavior_logs", log)
            except Exception as e:
                # 同步失败，保留在本地
                console.error(f"同步失败：{e}")
```

### 3.2.3 认知状态判定模型（v6.0核心重构 + v7.0容错 + v8.0优化 + v9.0弱网适配）

#### B3.1 信号不协和检测（Signal Dissonance）+ **[v7.0新增] 置信度门控** + **[v8.0新增] 信号丢失检查** + **[v9.0新增] 弱网区分**

**废除**：单一时间阈值判别

**v6.0逻辑**：当 `Behavior_Pause = True` 时，启动 **3秒窗口期扫描**

**[v7.0新增] 置信度门控机制**：

```python
class CognitiveStateDetectorV7:
    """
    v7.0认知状态检测器（含置信度门控）
    """
    
    LOW_CONFIDENCE_THRESHOLD = 0.6  # 低置信度阈值
    HIGH_CONFIDENCE_THRESHOLD = 0.7  # 高置信度阈值
    
    def detect_cognitive_state(self, multimodal_signals):
        """
        检测认知状态（含置信度检查）
        """
        gaze_confidence = multimodal_signals.get("gaze_confidence", 0.0)
        expression_confidence = multimodal_signals.get("expression_confidence", 0.0)
        facial_expression = multimodal_signals.get("facial_expression")
        gaze_on_screen = multimodal_signals.get("gaze_on_screen")
        has_micro_operation = multimodal_signals.get("has_micro_operation")
        
        # [v7.0新增] 计算整体置信度
        overall_confidence = (gaze_confidence + expression_confidence) / 2
        
        # [v7.0新增] 低置信度兜底：标记为不确定，弹出轻量确认
        if overall_confidence < self.LOW_CONFIDENCE_THRESHOLD:
            return CognitiveStateResult(
                state="uncertain",
                confidence=overall_confidence,
                requires_human_confirmation=True
            )
        
        # 高置信度 - 直接判定
        if overall_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            if facial_expression in ["confused", "frustrated"]:
                return CognitiveStateResult(state="difficulty", confidence=overall_confidence)
            if facial_expression in ["focused", "slight_frown"] and has_micro_operation:
                return CognitiveStateResult(state="deep_thinking", confidence=overall_confidence)
            if not gaze_on_screen and not has_micro_operation:
                return CognitiveStateResult(state="off_task", confidence=overall_confidence)
        
        # 中等置信度 - 结合行为数据增强
        return self._enhanced_detection_with_behavior(multimodal_signals)
```

**[v8.0新增] 信号丢失检查**：

```python
class CognitiveStateDetectorV8:
    """
    v8.0认知状态检测器（含置信度门控+信号丢失检查）
    """
    def detect_cognitive_state(self, multimodal_signals):
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
        return super().detect_cognitive_state(multimodal_signals)
```

**[v9.0新增] 弱网环境区分**：

```python
def detect_cognitive_state_v9(self, multimodal_signals, network_status):
    """
    [v9.0优化] 检测认知状态（含弱网区分）
    """
    # [v9.0新增] 弱网环境：降级检测逻辑
    if network_status["status"] == "weak_network":
        # 仅使用行为数据，不依赖多模态信号
        return self._detect_with_behavior_only(multimodal_signals)
    
    # 正常网络：使用完整多模态检测
    return self._detect_with_full_multimodal(multimodal_signals)
```

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
- **[v9.0新增] 弱网降级**：网络环境差，使用降级检测模式

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
- ✅ **[v9.0新增] 弱网降级策略有效，不因网络波动误判**
- ✅ **[v9.0新增] 本地缓存机制正常，网络恢复后成功同步**

---

# 6. 干预机制分层化设计（v6.0 + v7.0优化 + v8.0风格过滤 + v9.0抗震荡）

## 6.1 设计目标

- **统一抽象干预策略**：在第3.3节模块C中，已经给出了按知识点粒度的分层干预逻辑，本章节从"系统级策略"角度，对L1/L2/L3三个层级进行统一抽象，便于前后端实现与参数配置。
- **避免学习打断与界面震荡**：通过**干预冷静期（Hysteresis）机制**和**风格过滤**，在保证干预有效的前提下，最大限度降低对学习节奏的打扰。
- **保证安全优先与人类兜底**：在任何情况下，都必须保证**高危安全熔断不受冷静期限制**，并在多模态置信度不足或弱网场景下，引入人工确认或降级检测兜底。

## 6.2 干预等级与触发条件总览

> 详细算法与代码实现已在第3.2节（模块B）与第3.3节（模块C）给出，本节仅从"策略分层"视角做整体抽象。

- **L1 轻量提醒（Low-impact）**
  - 触发条件：首次出现T1级异常停留或单次疑难判定
  - 主要信号来源：暂停/回放/拖拽、轻微困惑表情等
  - 典型形式：侧边栏知识卡片 + 轻量提示，不打断播放
- **L2 交互修复（Interactive Repair）**
  - 触发条件：同一知识点二次疑难、测验失败或溯源诊断发现前置薄弱
  - 主要信号来源：多次回放、错误率升高、溯源路径中核心薄弱点
  - 典型形式：精准微视频 + 针对性练习 + 上下文保留剪辑
- **L3 人类介入（Human-in-the-loop）**
  - 触发条件：
    - **进度长期停滞**（累计停留>5倍视频时长，L2无效）
    - **螺旋路径反复失败**（≥3次，见第3.3.3节C3.3）
    - **安全高危事件**（PPE严重违规或非合规行为）
  - 典型形式：教师1对1答疑、同伴互助、线下辅导等

## 6.3 干预抗震荡与冷静期策略（与模块C对齐）

- **冷静期规则**（与第3.3.4节表格保持一致）：
  - L1：默认冷静期5分钟或直到进入下一个知识点
  - L2：默认冷静期10分钟或直到进入下一个知识点
  - L3：不受冷静期限制（人为主动干预）
- **安全优先规则**：
  - 任何由**安全熔断**触发的干预（如PPE高置信度违规），不受冷静期限制
  - 高危视频场景下，安全相关干预优先级最高，可覆盖其他干预
- **用户体验规则**：
  - 学生主动关闭L1/L2干预窗口后，在当前冷静期内不再重复弹出
  - 进入新知识点视为"重置场景"，允许重新评估是否需要干预

## 6.4 与学习风格、弱网和硬件降级的协同

- **与学习风格自适应的协同**：
  - L1/L2干预在选取资源时，必须调用**学习风格过滤器**（见第3.3.3节C3.4），优先推送与风格匹配度高的资源，避免"风格冲突"导致的干预失败。
- **与弱网降级的协同**：
  - 当网络状态为 `weak_network` 或 `offline` 时，认知状态检测自动退化为**行为信号优先**（见第3.2.2节B2.3），干预冷静期仍然生效，但不再依赖多模态信号。
  - 弱网场景下，前端优先保证学习流程顺畅，干预以**轻量提醒与离线缓存**为主。
- **与硬件降级的协同（v10.0）**：
  - 当设备进入 `L2 仅日志模式` 时，提高行为信号权重（见第3.2.2节B2.3.1），但不改变干预分层与冷静期规则。

## 6.5 验收要点

- 干预触发条件与L1/L2/L3定义必须与第3.3节实现保持一致，不出现冲突逻辑。
- 冷静期机制能够有效减少**5分钟内重复弹窗**现象（目标减少≥80%，见第12章）。
- 在弱网、硬件降级和安全高危场景下，干预逻辑均有明确的降级与兜底路径。

---

# 7. 系统架构与技术方案（v7.0 + v8.0扩展 + v9.0弱网适配 + v10.0健壮性增强）

> 本章节从**宏观架构视角**总结系统组成，具体算法与数据结构已在第3章各模块及第8章数据模型中详细展开。

## 7.1 整体架构分层

- **前端层（Web / 实训教室终端）**
  - 学生端：视频播放、行为采集、多模态信号采集（摄像头/麦克风授权）、补偿资源展示、弱网与降级提示
  - 教师端：学情大屏、趋势预测与策略推荐、专家标注工作台、资源审核与编辑、策略编辑器
  - 管理端：课程/资源管理、系统配置、审计与日志查看
- **后端服务层**
  - 教学视频解析与知识建模服务（对应模块A）
  - 行为日志与认知状态识别服务（对应模块B）
  - 学习路径与补偿资源服务（对应模块C）
  - 教师端决策与主权管理服务（对应模块D）
  - 安全熔断与监控服务（支撑模块，关联第5章）
  - 弱网与硬件降级策略服务（v9.0/v10.0新增）
  - 数据审计与难度保护区服务（v10.0新增）
- **数据与存储层**
  - 关系型数据库（核心业务表，见第8章）
  - 对象存储（视频、微视频片段、知识卡片资源）
  - 日志与审计存储（行为日志、多模态对齐日志、审计记录）
  - 本地缓存（IndexedDB 等，支撑弱网与离线场景）

## 7.2 关键技术选型与约束

- **多模态感知**：ASR（语音识别）、CV/OCR（图像与文本识别）、SlowFast/YOLO 等动作与安全检测模型
- **图结构与推荐**：GNN 用于知识依赖图维护与溯源路径计算，结合难度系数与学习风格画像进行个性化推荐
- **实时与异步并存**：
  - 实时通路：行为采集 → 认知状态判定 → L1/L2干预触发
  - 异步通路：视频解析、知识图谱构建、数据审计、周批次依赖权重修正
- **健壮性增强（v9.0/v10.0）**：
  - 多模态时间戳对齐协议、干预抗震荡机制
  - 写锁 + 租约 + 原子化发布的人机并发冲突处理
  - 硬件画像驱动的三级降级与权重补偿

## 7.3 部署与扩展性

- 支持**单体 + 模块化服务**演进：MVP阶段可采用单体服务，后续按模块A/B/C/D解耦为独立服务。
- 通过标准化接口（见第9章）实现前后端解耦，便于后续替换模型或接入新算法。
- 数据模型预留 JSON 字段与扩展表（见第8章8.1.x），支持新增指标（如新类型信号或审计规则）时的平滑扩容。

---

# 8. 数据模型设计（v6.0 + v7.0扩展 + v8.0新增 + v9.0/v10.0扩展）

> 由于本项目数据模型大量随功能模块演进，**第8章不再重复所有字段定义**，而是给出数据分层与关键表清单；具体字段与示例DDL，可参考各模块内嵌的SQL片段与本章小节说明。

## 8.1 数据分层视角

- **教学内容层数据**
  - 视频：`video`、多模态原始数据、清晰度与质量指标
  - 知识点：`knowledge_point` 及其依赖关系、难度系数、专家基准、环路记录等（见模块A相关代码片段）
- **学习过程层数据**
  - 行为日志：播放/暂停/拖拽/倍速/退出等事件（模块B）
  - 多模态信号：视线、微表情、环境音、PPE检测结果、摄像头状态等
  - 认知状态事件：深度思考/疑难/无效停留/信号丢失/弱网降级等判定结果
- **干预与补偿层数据**
  - 补偿资源：知识卡片、微视频、练习题、知识提示、思维导图、参数速查表等
  - 干预记录：L1/L2/L3干预事件、冷静期记录、螺旋路径跳出记录
  - 学习风格与资源反馈：`learning_style`、资源反馈与灰度复核相关表
- **安全与审计层数据（v8.0/v9.0/v10.0）**
  - 安全事件与信号丢失记录、非合规学习行为、弱网状态记录、本地缓存与同步日志
  - 数据审计引擎相关表：异常/恶意反馈、难度保护区信息、反馈-行为一致性校验结果

## 8.2 关键扩展表汇总

- **难度与风格相关**
  - 知识点难度系数与专家基准表（对应v8.0：难度系数加权与冷启动机制）
  - 学习风格表 `learning_style`：记录效率偏好、内容偏好、交互偏好与置信度
- **安全与信号丢失相关**
  - 安全信号/监控信号丢失记录表：记录黑屏、遮挡、人体缺位等事件
  - 高危场景安全熔断记录与非合规学习行为表
- **环路与螺旋路径相关**
  - 知识图谱环路记录表 `circular_dependency`
  - 螺旋学习路径表 `spiral_learning_path`
- **弱网与本地缓存相关（v9.0）**
  - 网络状态记录表 `network_status_log`
  - 本地缓存同步记录表 `local_cache_sync_log`
- **教师主权与审计相关（v9.0/v10.0）**
  - AI生成锁定表 `ai_generation_lock`
  - 干预冷静期记录表 `intervention_cooldown`
  - 资源反馈与数据审计相关表（异常/恶意反馈、难度保护区配置等）

## 8.3 设计原则

- **范式化 + JSON 扩展结合**：基础业务字段遵循三范式；对高度可变的属性（如多模态对齐详情、降级策略参数）使用 JSON 字段存储。
- **可追溯与可审计**：所有自动化决策（干预触发、资源下架、时间戳对齐修正等）都必须在数据层留下可回放的审计记录。
- **性能与分区**：对高频写入表（行为日志、多模态信号、网络状态等）采用时间分区与必要索引，保证查询与归档性能。

## 8.4 基础核心数据表定义（继承自v4.0，供实现与数据库设计参考）

> 说明：本小节继承自第四稿的**基础数据模型**，用于支撑最初的"感知-分析-干预-反馈"闭环。  
> v6.0–v10.0 在此基础上引入了难度系数、学习风格、弱网与审计等扩展表（已在第8.2节列出），**本节不重复这些扩展内容，只补全最核心的业务表结构**。

### 8.4.1 用户表 `user`

```sql
CREATE TABLE user (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    class_id VARCHAR(50),
    profile JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 8.4.2 视频表 `video`

```sql
CREATE TABLE video (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    course_id VARCHAR(50),
    duration INT,  -- 秒
    url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    metadata JSON,  -- 视频元数据（分辨率、帧率、编码信息等）
    status ENUM('processing', 'ready', 'failed') DEFAULT 'processing',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8.4.3 知识点表 `knowledge_point`

```sql
CREATE TABLE knowledge_point (
    id VARCHAR(50) PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    start_time INT NOT NULL,  -- 秒
    end_time INT NOT NULL,    -- 秒
    keywords TEXT,            -- 建议存JSON数组
    summary TEXT,
    kp_type ENUM('concept', 'skill', 'example', 'practice'),
    difficulty_level ENUM('basic', 'intermediate', 'advanced'),
    importance_score INT,     -- 1-5
    parent_kp_id VARCHAR(50), -- 父知识点（层级结构）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES video(id)
);
```

### 8.4.4 知识点关系表 `kp_relation`

```sql
CREATE TABLE kp_relation (
    id VARCHAR(50) PRIMARY KEY,
    from_kp_id VARCHAR(50) NOT NULL,
    to_kp_id VARCHAR(50) NOT NULL,
    relation_type ENUM('prerequisite', 'next', 'related'),
    weight FLOAT,  -- 关联度（可与v6.0+的依赖权重机制联动）
    FOREIGN KEY (from_kp_id) REFERENCES knowledge_point(id),
    FOREIGN KEY (to_kp_id) REFERENCES knowledge_point(id)
);
```

### 8.4.5 观看事件表 `watch_event`

```sql
CREATE TABLE watch_event (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    video_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type ENUM('play', 'pause', 'seek', 'rate_change', 'ended', 'leave'),
    payload JSON,  -- 存储事件详细信息，如停留位置、倍速变化等
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (video_id) REFERENCES video(id),
    INDEX idx_user_video (user_id, video_id),
    INDEX idx_timestamp (timestamp)
);
```

### 8.4.6 掌握状态表 `mastery`

```sql
CREATE TABLE mastery (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50) NOT NULL,
    status ENUM('unlearned', 'learning', 'difficult', 'mastered') DEFAULT 'unlearned',
    difficulty_score FLOAT,  -- 0-1，用于度量个体层面的困难度
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    UNIQUE KEY uk_user_kp (user_id, kp_id)
);
```

### 8.4.7 补偿资源表 `resource`

```sql
CREATE TABLE resource (
    id VARCHAR(50) PRIMARY KEY,
    kp_id VARCHAR(50) NOT NULL,
    resource_type ENUM('card', 'exercise', 'video', 'mindmap', 'other'),
    title VARCHAR(200),
    content TEXT,  -- JSON或富文本内容
    source ENUM('ai_generated', 'manual', 'external'),
    version INT DEFAULT 1,
    status ENUM('draft', 'approved', 'rejected') DEFAULT 'draft',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id)
);
```

> 说明：v7.0–v10.0 在此基础上增加了资源反馈、灰度复核、自动下架与审计相关字段/表，已在第3.3节与第8.2节中说明，此处不重复。

### 8.4.8 练习题表 `exercise` 与练习结果表 `exercise_result`

```sql
CREATE TABLE exercise (
    id VARCHAR(50) PRIMARY KEY,
    kp_id VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    questions JSON NOT NULL,     -- 题目列表
    answer_key JSON NOT NULL,    -- 答案与解析
    difficulty ENUM('easy', 'medium', 'hard'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id)
);

CREATE TABLE exercise_result (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    exercise_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50) NOT NULL,
    score FLOAT,          -- 0-1
    detail JSON,          -- 存储每道题的答案与判分详情
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (exercise_id) REFERENCES exercise(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    INDEX idx_user_kp (user_id, kp_id)
);
```

### 8.4.9 学习路径表 `learning_path`

```sql
CREATE TABLE learning_path (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    video_id VARCHAR(50) NOT NULL,
    path_data JSON NOT NULL,  -- 存储知识点序列与当前状态
    current_kp_id VARCHAR(50),
    completion_rate FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (video_id) REFERENCES video(id)
);
```

### 8.4.10 课程表 `course`

```sql
CREATE TABLE course (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),  -- 课程分类
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8.4.11 补偿推送记录表 `compensation_log`

```sql
CREATE TABLE compensation_log (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50) NOT NULL,
    resource_id VARCHAR(50),
    push_type ENUM('auto', 'manual'),
    push_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_feedback ENUM('helpful', 'not_helpful', 'no_feedback'),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    FOREIGN KEY (resource_id) REFERENCES resource(id)
);
```

### 8.4.12 基础数据关系图（v4.0 → v11.0 兼容）

```text
User ──┬── WatchEvent ──→ Video
       │
       ├── Mastery ──→ KnowledgePoint ──→ Video
       │
       ├── ExerciseResult ──→ Exercise ──→ KnowledgePoint
       │
       ├── LearningPath ──→ Video
       │
       └── CompensationLog ──→ KnowledgePoint ──→ Resource

KnowledgePoint ──→ kp_relation (自关联，支撑图谱与溯源诊断)
Resource ──→ KnowledgePoint
Exercise ──→ KnowledgePoint
Video ──→ Course
```

> 后续版本（v6.0–v10.0）在此基础之上，引入了难度系数表、学习风格表、环路/螺旋路径表、弱网与本地缓存表、AI生成锁定表、审计与难度保护区等扩展数据结构，已在第3章、第4章与第8.2节分别说明。

---

# 9. 接口设计（v7.0扩展 + v8.0新增 + v9.0/v10.0扩展）

v11.0完整整合所有版本接口设计，形成可直接用于开发实施的完整接口规范。

## 9.1 接口分层与命名规范

- **学生端接口（前缀示例：`/api/v11/student/...`）**
  - 行为上报：播放/暂停/拖拽等行为事件上报
  - 补偿资源获取：根据知识点与认知状态获取待推送资源列表
  - 螺旋路径与学习路径查询：获取当前个性化路径与螺旋学习进度
- **教师端接口（前缀示例：`/api/v11/teacher/...`）**
  - 教学效果仪表盘数据查询
  - 专家标注工作台相关接口（获取/保存/发布知识点标注）
  - 教师策略编辑器与干预激进系数配置接口
- **管理与审计接口（前缀示例：`/api/v11/admin/...`）**
  - 安全事件与信号丢失日志查询
  - 数据审计与异常反馈处理接口
  - 系统配置、降级策略与阈值管理接口

## 9.2 关键功能类接口汇总（与模块对齐）

- **视频解析与知识建模（模块A）**
  - 触发/查询视频解析进度的接口
  - 获取某视频知识点列表、依赖关系与专家基准的接口
  - 教师一键禁用AI自动生成、启用专家标注模式的接口
- **行为采集与认知判定（模块B）**
  - 行为事件与多模态信号上报接口
  - 网络状态与硬件画像上报接口（支撑弱网与硬件降级）
  - 认知状态查询接口（供前端可视化或教师端分析使用）
- **学习路径与补偿资源（模块C）**
  - 获取个性化学习路径与当前推荐下一步的接口
  - L1/L2干预触发与记录接口（含冷静期检查）
  - 螺旋路径生成与跳出相关接口
- **教师端赋能与主权管理（模块D）**
  - 班级学情大屏数据接口
  - 趋势预测与教学策略推荐查询接口
  - AI生成锁定、专家标注结果提交及审计相关接口

## 9.3 基础核心接口示例（继承自v4.0，完整可实施）

### 9.3.1 视频相关接口

#### 上传视频
- **接口**: `POST /api/v11/videos/upload`
- **描述**: 教师上传教学视频
- **请求参数**:
  ```json
  {
    "file": "视频文件",
    "title": "视频标题",
    "course_id": "课程ID",
    "subtitle_file": "字幕文件（可选）",
    "ppt_file": "PPT文件（可选）",
    "manual_file": "实操手册PDF（可选）"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "video_id": "V001",
      "status": "processing",
      "message": "视频上传成功，正在解析中"
    }
  }
  ```

#### 获取视频列表
- **接口**: `GET /api/v11/videos`
- **描述**: 获取视频列表
- **请求参数**: `?course_id=xxx&page=1&page_size=20`
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "total": 100,
      "videos": [
        {
          "id": "V001",
          "title": "数据库-SELECT查询",
          "duration": 3600,
          "thumbnail_url": "...",
          "status": "ready"
        }
      ]
    }
  }
  ```

#### 获取视频知识点
- **接口**: `GET /api/v11/videos/{video_id}/knowledge-points`
- **描述**: 获取视频的知识点列表（含对齐时间戳、难度系数、专家基准等v8.0/v9.0扩展字段）
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "video_id": "V001",
      "knowledge_points": [
        {
          "id": "K1",
          "title": "SELECT基础语法",
          "start_time": 0,
          "end_time": 300,
          "aligned_timestamp": 150,
          "keywords": ["SELECT", "FROM", "WHERE"],
          "summary": "介绍SELECT语句的基本语法结构",
          "difficulty_level": "basic",
          "difficulty_coefficient": 1.0,
          "expert_annotated": false
        }
      ]
    }
  }
  ```

### 9.3.2 学习行为接口

#### 上报观看事件
- **接口**: `POST /api/v11/watch-events`
- **描述**: 前端实时上报观看行为事件（支持弱网降级模式下的本地缓存批量上报）
- **请求参数**:
  ```json
  {
    "user_id": "U001",
    "video_id": "V001",
    "event_type": "pause",
    "timestamp": "2024-01-15T10:30:00Z",
    "payload": {
      "pause_position": 150,
      "pause_duration": 30
    },
    "network_status": "normal",
    "cache_key": "behavior_log_001"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "事件记录成功",
    "synced": true
  }
  ```

#### 获取难点诊断结果
- **接口**: `GET /api/v11/users/{user_id}/difficult-points`
- **描述**: 获取学生的疑难知识点列表（含置信度、触发原因、认知状态等v7.0/v8.0扩展信息）
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "difficult_points": [
        {
          "kp_id": "K3",
          "kp_name": "多表连接",
          "difficulty_score": 0.85,
          "cognitive_state": "difficulty",
          "confidence": 0.82,
          "triggers": [
            {"type": "replay", "count": 3, "threshold": 2},
            {"type": "stay_duration", "ratio": 3.5, "threshold": 3.0}
          ],
          "detected_at": "2024-01-15T10:30:00Z"
        }
      ]
    }
  }
  ```

### 9.3.3 补偿资源接口

#### 获取补偿资源
- **接口**: `GET /api/v11/knowledge-points/{kp_id}/resources`
- **描述**: 获取知识点的补偿资源（含学习风格过滤、干预冷静期检查等v8.0/v9.0扩展逻辑）
- **请求参数**: `?user_id=U001&intervention_level=L1`
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "kp_id": "K3",
      "resources": [
        {
          "id": "R001",
          "type": "card",
          "title": "多表连接知识卡片",
          "content": "...",
          "style_tags": ["text", "visual"],
          "matched_style": true
        },
        {
          "id": "R002",
          "type": "exercise",
          "title": "多表连接诊断练习",
          "question_count": 3
        },
        {
          "id": "R003",
          "type": "video",
          "title": "多表连接精讲",
          "duration": 300,
          "url": "..."
        }
      ],
      "cooldown_status": {
        "can_trigger": true,
        "remaining_time": 0
      }
    }
  }
  ```

#### 提交练习结果
- **接口**: `POST /api/v11/exercises/{exercise_id}/submit`
- **描述**: 学生提交练习答案
- **请求参数**:
  ```json
  {
    "user_id": "U001",
    "answers": [
      {"question_id": "Q1", "answer": "A"},
      {"question_id": "Q2", "answer": "B"}
    ]
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "score": 0.85,
      "detail": [
        {"question_id": "Q1", "correct": true, "explanation": "..."},
        {"question_id": "Q2", "correct": true, "explanation": "..."}
      ],
      "mastery_updated": true,
      "new_status": "mastered"
    }
  }
  ```

#### 反馈补偿资源
- **接口**: `POST /api/v11/resources/{resource_id}/feedback`
- **描述**: 学生对补偿资源进行反馈（含v7.0细化反馈维度、v10.0数据审计校验）
- **请求参数**:
  ```json
  {
    "user_id": "U001",
    "kp_id": "K3",
    "feedback": "not_helpful",
    "feedback_details": {
      "reason": "too_verbose",
      "watch_percentage": 0.95,
      "completed_exercise": true
    }
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "feedback_id": "FB001",
      "audit_status": "normal",
      "message": "反馈已记录"
    }
  }
  ```

### 9.3.4 学习路径接口

#### 获取个人学习路径
- **接口**: `GET /api/v11/users/{user_id}/learning-path?video_id=V001`
- **描述**: 获取学生的个性化学习路径（含螺旋路径、溯源诊断等v6.0/v8.0扩展能力）
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "current_progress": {
        "video_id": "V001",
        "current_kp": "K5",
        "completion_rate": 0.65
      },
      "difficult_points": [...],
      "spiral_paths": [
        {
          "spiral_path_id": "SP001",
          "loop_kps": ["K3", "K5", "K7"],
          "status": "in_progress",
          "failure_count": 1
        }
      ],
      "next_suggestion": {
        "action": "continue_watch",
        "target_kp": "K6",
        "reason": "前置知识点已掌握"
      },
      "learning_path": [...]
    }
  }
  ```

### 9.3.5 教师端接口

#### 获取班级学情
- **接口**: `GET /api/v11/teachers/{teacher_id}/class-statistics?course_id=C001`
- **描述**: 获取班级整体学情数据（含v7.0趋势预测、v9.0教师主权等扩展功能）
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "difficult_kp_ranking": [
        {
          "kp_id": "K3",
          "kp_name": "多表连接",
          "difficult_count": 15,
          "avg_replay": 4.2
        }
      ],
      "heatmap_data": {...},
      "compensation_stats": {
        "usage_count": 250,
        "effectiveness": 0.78
      },
      "trend_prediction": {
        "future_difficulties": [
          {
            "kp_id": "K8",
            "predicted_difficulty_rate": 0.75,
            "reason": "相似班级历史表现",
            "suggested_strategy": "提前补充示范视频"
          }
        ]
      }
    }
  }
  ```

#### 编辑知识点
- **接口**: `PUT /api/v11/knowledge-points/{kp_id}`
- **描述**: 教师编辑知识点信息（含v9.0写锁租约、v10.0原子化发布等扩展机制）
- **请求参数**:
  ```json
  {
    "title": "修改后的知识点名称",
    "start_time": 100,
    "end_time": 400,
    "keywords": ["新关键词"],
    "summary": "新摘要",
    "difficulty_level": "intermediate",
    "lock_token": "lock_abc123",
    "teacher_id": "T001"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "kp_id": "K3",
      "status": "updated",
      "published_at": "2024-01-15T10:35:00Z",
      "lock_released": true
    }
  }
  ```

## 9.4 v10.0 新增能力的接口约定补充

### 9.4.1 写锁与租约接口

#### 获取知识图谱写锁
- **接口**: `POST /api/v11/knowledge-graph/lock`
- **描述**: 教师编辑前获取写锁，30分钟租约
- **请求参数**:
  ```json
  {
    "video_id": "V001",
    "teacher_id": "T001",
    "lock_type": "expert_annotation"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "lock_token": "lock_abc123",
      "expires_at": "2024-01-15T11:05:00Z",
      "lease_duration": 1800
    }
  }
  ```

#### 续约写锁
- **接口**: `POST /api/v11/knowledge-graph/lock/renew`
- **描述**: 心跳续约，延长租约时间
- **请求参数**:
  ```json
  {
    "lock_token": "lock_abc123",
    "teacher_id": "T001"
  }
  ```

#### 释放写锁
- **接口**: `POST /api/v11/knowledge-graph/lock/release`
- **描述**: 主动释放写锁或超时自动释放
- **请求参数**:
  ```json
  {
    "lock_token": "lock_abc123",
    "action": "release",
    "rollback_to_stable": true
  }
  ```

### 9.4.2 硬件降级与权重补偿接口

#### 上报设备性能
- **接口**: `POST /api/v11/device/performance`
- **描述**: 前端定期上报设备性能与帧率
- **请求参数**:
  ```json
  {
    "user_id": "U001",
    "cpu_usage": 0.75,
    "fps": 25,
    "gpu_available": true,
    "memory_usage": 0.6
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "degradation_level": "light",
      "recommended_mode": "full",
      "weight_compensation": 0.6,
      "message": "设备性能正常，全量模式"
    }
  }
  ```

### 9.4.3 数据审计与难度保护区接口

#### 查询反馈审计结果
- **接口**: `GET /api/v11/admin/feedback-audit?resource_id=R001`
- **描述**: 查询资源反馈的审计结果与异常标记
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "resource_id": "R001",
      "total_feedback": 50,
      "normal_feedback": 45,
      "abnormal_feedback": 5,
      "audit_logs": [
        {
          "feedback_id": "FB001",
          "status": "abnormal",
          "reason": "watch_percentage_too_low",
          "action": "excluded_from_statistics"
        }
      ]
    }
  }
  ```

#### 配置难度保护区
- **接口**: `PUT /api/v11/admin/difficulty-protection-zone`
- **描述**: 配置高难资源下架阈值
- **请求参数**:
  ```json
  {
    "difficulty_level": "advanced",
    "auto_offline_threshold": 10,
    "require_content_mismatch_evidence": true
  }
  ```

---

# 10. 用户界面设计

## 10.1 学生端界面

### 10.1.1 视频播放页
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  导航栏: [首页] [我的学习] [个人中心]            │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────┐  ┌─────────────────┐ │
│  │                      │  │ 知识点目录      │ │
│  │                      │  │ ┌─────────────┐ │ │
│  │   视频播放器         │  │ │ K1: SELECT  │ │ │
│  │                      │  │ │ K2: WHERE   │ │ │
│  │                      │  │ │ K3: 多表连接│ │ │
│  │                      │  │ │   ⚠️ 疑难点 │ │ │
│  └──────────────────────┘  │ └─────────────┘ │ │
│                            │                  │ │
│                            │ 补偿资源提示     │ │
│                            │ ┌─────────────┐ │ │
│                            │ │ 💡 检测到疑 │ │ │
│                            │ │   难点，推  │ │ │
│                            │ │   荐补偿资源│ │ │
│                            │ │ [查看详情]  │ │ │
│                            │ └─────────────┘ │ │
│                            │                  │ │
│                            │ [v9.0新增] 弱网提示│ │
│                            │ ┌─────────────┐ │ │
│                            │ │ ⚠️ 网络环境 │ │ │
│                            │ │   较差，已  │ │ │
│                            │ │   切换降级模式│ │
│                            │ └─────────────┘ │ │
└─────────────────────────────────────────────────┘
```

**功能要点**:
- 视频播放器支持播放、暂停、拖拽、倍速
- 实时采集行为事件（不打断用户体验）
- 知识点目录可点击跳转
- 疑难点标记（⚠️图标）
- 补偿资源提示（侧边栏浮层，非强制弹出）
- **[v9.0新增] 弱网环境提示**：显示当前网络状态和降级模式
- **[v9.0新增] 干预冷静期提示**：显示距离下次可触发干预的剩余时间
- **[v8.0新增] 学习风格标签显示**：显示当前推荐资源的学习风格类型

### 10.1.2 补偿资源页
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  知识点: 多表连接                               │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ 📄 知识卡片                              │  │
│  │ ┌──────────────────────────────────────┐ │  │
│  │ │ 多表连接语法:                        │ │  │
│  │ │ SELECT ... FROM table1               │ │  │
│  │ │ JOIN table2 ON ...                   │ │  │
│  │ └──────────────────────────────────────┘ │  │
│  │ [v8.0新增] 风格标签: 文本型/高效型        │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ 📝 诊断练习 (3题)                       │  │
│  │ 1. 选择题: ...                          │  │
│  │ 2. 填空题: ...                          │  │
│  │ 3. 判断题: ...                          │  │
│  │ [提交答案]                              │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ 🎥 精讲微视频 (60-90s)                  │  │
│  │ [播放视频]                               │  │
│  │ [v7.0新增] 反馈: [有帮助] [无帮助] [其他]│  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  [标记已掌握] [仍不懂]                          │
└─────────────────────────────────────────────────┘
```

### 10.1.3 学习路径/进度页
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  我的学习路径                                    │
├─────────────────────────────────────────────────┤
│  当前进度: 65%                                   │
│  ┌──────────────────────────────────────────┐  │
│  │ ████████████████░░░░░░░░░░░░░░░░░░░░░░░  │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  学习路径:                                       │
│  ✅ K1: SELECT基础 (已掌握)                      │
│  ✅ K2: WHERE条件 (已掌握)                      │
│  ⚠️  K3: 多表连接 (疑难 - 补偿中)               │
│  ⏭️  K4: 子查询 (已跳过 - 前置知识已掌握)        │
│  🔄 K5: 聚合函数 (学习中)                        │
│  ⏸️  K6: HAVING子句 (未学)                      │
│  🔁 [v8.0新增] K7-K9: 螺旋路径 (环路知识点)      │
│                                                  │
│  下一步建议: 继续学习 K5: 聚合函数              │
│  [继续学习] [查看详情]                          │
└─────────────────────────────────────────────────┘
```

## 10.2 教师端界面

### 10.2.1 教学效果仪表盘
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  教学效果仪表盘 - 《数据库-SELECT查询》          │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────┐  ┌──────────────────┐     │
│  │ 班级疑难排行     │  │ 学情热力图       │     │
│  │ 1. K3 多表连接   │  │ [时间轴热力图]   │     │
│  │    15人 4.2次    │  │                  │     │
│  │ 2. K7 子查询     │  │                  │     │
│  │    12人 3.8次    │  │                  │     │
│  └──────────────────┘  └──────────────────┘     │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ 补偿资源效果                              │  │
│  │ 使用量: 知识卡片120次 | 练习题85次 | ...  │  │
│  │ 掌握率提升: 45% → 78%                    │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ [v7.0新增] 趋势预测                      │  │
│  │ 预计下周难点: K10, K12                   │  │
│  │ 建议策略: 提前推送预习资源               │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ [v8.0新增] 学习风格分布                  │  │
│  │ 高效型: 35% | 视觉型: 28% | 文本型: 37% │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ [v9.0新增] 语义脱节日志                  │  │
│  │ 待校验: 2条 | 已校验: 15条               │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  [导出报告] [优化教学] [v9.0新增] [禁用AI生成]   │
└─────────────────────────────────────────────────┘
```

### 10.2.2 教师标注工作台
**功能**: 可视化编辑知识点边界、名称、摘要等

**[v9.0新增] 专家标注模式界面**:
```
┌─────────────────────────────────────────────────┐
│  专家标注工作台 - 汽修-发动机拆装                │
├─────────────────────────────────────────────────┤
│  AI自动生成: ☐ 禁用  ☑ 启用                    │
│  [一键禁用AI] [进入专家标注模式]                │
│                                                  │
│  知识点列表:                                     │
│  ┌──────────────────────────────────────────┐  │
│  │ K3: 曲轴拆卸                              │  │
│  │ 时间戳: 01:10 - 01:45                    │  │
│  │ [编辑] [删除] [标记为核心难点]            │  │
│  │ [v8.0新增] 难度系数: [1.5]x              │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  [新增知识点] [保存] [发布并交还AI托管]          │
└─────────────────────────────────────────────────┘
```

**[v10.0新增] 写锁状态显示**:
```
┌─────────────────────────────────────────────────┐
│  ⚠️ 当前视频已被锁定                            │
│  锁定人: 张老师                                 │
│  锁定时间: 2026-01-28 10:00:00                 │
│  剩余时间: 25分钟                               │
│  [续租] [释放锁定]                              │
└─────────────────────────────────────────────────┘
```

### 10.2.3 [v10.0新增] 教师策略编辑器
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  教师策略配置 - 《数据库-SELECT查询》            │
├─────────────────────────────────────────────────┤
│  作用范围: [课程] [班级] [视频] [知识点]        │
│                                                  │
│  干预激进系数: [1.5] (范围: 0.1-2.0)           │
│  说明: 系数越高，干预触发越频繁                  │
│                                                  │
│  当前配置:                                       │
│  - 课程级别: 1.2                                 │
│  - 班级级别: 1.5 (覆盖课程级别)                 │
│                                                  │
│  [保存配置] [重置为默认值]                       │
└─────────────────────────────────────────────────┘
```

### 10.2.4 [v10.0新增] 数据审计面板
**布局结构**:
```
┌─────────────────────────────────────────────────┐
│  资源反馈审计报告                                │
├─────────────────────────────────────────────────┤
│  资源: 多表连接-知识卡片                         │
│                                                  │
│  反馈统计:                                       │
│  - 正常反馈: 12条                                │
│  - 可疑反馈: 2条 (已标记)                        │
│  - 无效反馈: 1条 (未观看≥80%)                    │
│                                                  │
│  可疑反馈详情:                                   │
│  ┌──────────────────────────────────────────┐  │
│  │ 用户: U001 | 时间: 2026-01-28 10:05:00   │  │
│  │ 原因: 低停留时长+立刻差评                 │  │
│  │ [放行] [驳回] [查看详情]                  │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  [导出审计报告]                                  │
└─────────────────────────────────────────────────┘
```

---

# 11. 非功能性需求

## 11.1 性能要求

- **视频解析响应时间**: 上传后24小时内完成解析（可异步处理）
- **行为检测响应时间**: 实时采集，延迟 < 1秒
- **补偿推送响应时间**: 行为检测 → 补偿推送 ≤ 3-5分钟
- **接口响应时间**: API接口平均响应时间 < 500ms
- **视频播放流畅度**: 支持1080p流畅播放，缓冲时间 < 3秒
- **[v9.0新增] 弱网降级响应时间**: 网络状态检测 → 降级策略应用 ≤ 2秒
- **[v10.0新增] 写锁获取响应时间**: 获取写锁响应时间 < 100ms
- **[v10.0新增] 硬件降级检测周期**: 设备画像采集周期 ≤ 5秒

## 11.2 可用性要求

- **系统可用性**: ≥ 99%（7×24小时）
- **视频播放与事件采集**: 不应明显卡顿
- **界面响应**: 用户操作响应时间 < 200ms
- **[v9.0新增] 弱网环境可用性**: 弱网环境下学习功能正常，仅降级监控功能
- **[v10.0新增] 硬件降级可用性**: 低性能设备下系统不卡死，自动降级到仅日志模式

## 11.3 准确性要求

- **知识点识别准确率**: ≥ 85%（v1.0）
- **ASR识别准确率**: ≥ 90%
- **OCR识别准确率**: ≥ 85%
- **难点判定准确率**: ≥ 80%（减少误报/漏报）
- **[v7.0新增] 认知状态识别准确率**: ≥ 85%（含置信度门控）
- **[v8.0新增] 学习风格推断准确率**: ≥ 75%
- **[v9.0新增] 时间戳对齐准确率**: ±3秒窗口内对齐率 ≥ 95%
- **[v10.0新增] 反馈审计准确率**: 异常反馈识别准确率 ≥ 90%

## 11.4 可解释性要求

- **难点判定**: 必须给出触发原因（可解释性）
- **路径推荐**: 提供推荐理由
- **补偿资源**: 说明为什么推送该资源
- **[v8.0新增] 学习风格推断**: 提供推断依据（反馈样本数、置信度）
- **[v9.0新增] 干预冷静期**: 显示剩余冷静期时间，说明不触发原因
- **[v10.0新增] 审计结果**: 提供审计原因和依据

## 11.5 可控性要求

- **知识点切分**: 允许人工修订
- **资源内容**: 允许人工审核/编辑
- **阈值配置**: T1/T2/T3等阈值可配置
- **[v9.0新增] AI生成控制**: 教师可一键禁用AI自动生成，进入专家标注模式
- **[v10.0新增] 干预敏感度控制**: 教师可统一调节干预激进系数（0.1-2.0）
- **[v10.0新增] 写锁控制**: 教师可手动释放写锁，系统支持30分钟超时自动释放

## 11.6 安全性要求

- **隐私保护**: 
  - 仅采集学习相关行为数据
  - 不采集与课程无关信息
  - 数据脱敏展示
  - 学习行为数据本地化或强加密
- **权限控制**: 学生只能查看自己的数据，教师只能查看所教班级数据
- **数据安全**: 敏感数据加密存储，API接口需要身份认证
- **[v8.0新增] 监控信号安全**: 高危视频信号丢失时强制暂停，不计入学习时长
- **[v10.0新增] 数据审计安全**: 异常/恶意反馈过滤，防止资源被误下架

## 11.7 可扩展性要求

- **模块化设计**: 各功能模块相对独立，便于扩展
- **接口标准化**: 支持后续功能扩展
- **数据模型**: 支持新字段扩展（使用JSON字段存储灵活数据）
- **[v9.0新增] 降级策略可扩展**: 支持新增降级等级和策略
- **[v10.0新增] 审计规则可扩展**: 支持新增审计规则和模式识别

## 11.8 兼容性要求

- **浏览器兼容**: 支持Chrome、Firefox、Edge最新版本
- **视频格式**: 支持MP4、WebM等主流格式
- **移动端**: 响应式设计，支持移动端浏览器访问（优先Web端）
- **[v9.0新增] 弱网兼容**: 支持弱网环境下的降级模式，保证学习连续性
- **[v10.0新增] 硬件兼容**: 支持低性能设备，自动降级到仅日志模式

## 11.9 [v9.0新增] 弱网环境要求

- **降级策略**: 根据网络状态自动降级监控功能
- **本地缓存**: 行为日志本地缓存，网络恢复后自动同步
- **学习连续性**: 弱网环境下学习功能正常，不因网络波动中断
- **降级提示**: 明确告知用户当前降级状态和功能限制

## 11.10 [v10.0新增] 硬件适配要求

- **设备画像**: 周期性采集CPU/内存/GPU/FPS等性能指标
- **三级降级**: 根据设备性能自动切换全量/精简/仅日志模式
- **权重补偿**: 降级模式下自动调整算法权重，保证准确率
- **性能监控**: 实时监控设备性能，防止页面卡死

---

# 12. 测试与验收标准

## 12.1 功能测试

### 12.1.1 视频解析模块测试
- ✅ 上传视频后能成功解析出知识点
- ✅ 知识点数量符合要求（10-30个）
- ✅ 知识点时间戳准确
- ✅ 支持人工编辑知识点
- ✅ **[v8.0新增] 教师预设基准线功能正常**
- ✅ **[v8.0新增] 逻辑环路检测准确**
- ✅ **[v9.0新增] 多模态时间戳对齐协议正常工作**
- ✅ **[v9.0新增] 语义脱节检测准确，教师校验流程完整**
- ✅ **[v9.0新增] 教师一键禁用AI功能正常，专家标注模式可用**
- ✅ **[v10.0新增] 写锁租约机制正常，30分钟超时自动释放并回滚稳定版本**
- ✅ **[v10.0新增] 跨课原型匹配冷启动正常，相似度>0.8自动复用基准**

### 12.1.2 行为采集模块测试
- ✅ 能正确采集所有行为事件（play/pause/seek等）
- ✅ 事件时间戳准确
- ✅ 行为数据能正确存储
- ✅ **[v8.0新增] 监控信号丢失检测准确，强制暂停机制有效**
- ✅ **[v9.0新增] 弱网降级策略有效，不因网络波动误判**
- ✅ **[v9.0新增] 本地缓存机制正常，网络恢复后成功同步**
- ✅ **[v10.0新增] 硬件降级策略有效，CPU>80%自动降级到仅日志模式，权重补偿正常**

### 12.1.3 难点识别模块测试
- ✅ 能正确识别疑难点（基于规则）
- ✅ 触发原因可解释
- ✅ 公共难点识别准确
- ✅ 个体弱项诊断准确
- ✅ **[v7.0新增] 低置信度时不误判，人工确认机制正常工作**
- ✅ **[v7.0新增] 个人认知步频计算准确，动态阈值有效**
- ✅ **[v8.0新增] 难度系数加权后，避免"虚假繁荣"误报**
- ✅ **[v9.0新增] 干预冷静期机制有效，界面震荡减少≥80%**

### 12.1.4 补偿推送模块测试
- ✅ 检测到疑难点后能及时推送补偿资源
- ✅ 补偿资源类型正确（卡片/练习/视频）
- ✅ 学生完成练习后能正确更新状态
- ✅ 反馈闭环机制正常工作
- ✅ **[v7.0新增] 资源反馈维度细化，教师可查看问题分布**
- ✅ **[v7.0新增] 灰度复核流程完整，转正标准明确**
- ✅ **[v8.0新增] 学习风格推断准确率≥75%**
- ✅ **[v8.0新增] 风格自适应后，资源匹配度提升≥20%**
- ✅ **[v8.0新增] 环路检测正常，螺旋路径生成合理**
- ✅ **[v9.0新增] 螺旋路径跳出策略正常，反复失败自动跳转L3**
- ✅ **[v10.0新增] 数据审计引擎正常，异常反馈被标记且不计入自动下架**
- ✅ **[v10.0新增] 难度保护区有效，高难资源下架阈值提高到10**
- ✅ **[v10.0新增] 反馈-行为一致性校验正常，未观看≥80%的差评不计入统计**

### 12.1.5 学习路径模块测试
- ✅ 能生成个性化学习路径
- ✅ 路径能根据反馈动态调整
- ✅ 跳过已掌握知识点功能正常
- ✅ **[v8.0新增] 螺旋路径生成合理，关联演示视频可播放**
- ✅ **[v9.0新增] 螺旋路径反复失败自动跳转L3**

## 12.2 性能测试

- ✅ 视频解析在24小时内完成
- ✅ 补偿推送响应时间 ≤ 5分钟
- ✅ API接口响应时间 < 500ms
- ✅ 视频播放流畅，无明显卡顿
- ✅ **[v9.0新增] 弱网降级响应时间 ≤ 2秒**
- ✅ **[v10.0新增] 写锁获取响应时间 < 100ms**
- ✅ **[v10.0新增] 硬件降级检测周期 ≤ 5秒**

## 12.3 准确性测试

- ✅ 知识点识别准确率 ≥ 85%
- ✅ ASR识别准确率 ≥ 90%
- ✅ 难点判定准确率 ≥ 80%
- ✅ **[v7.0新增] 认知状态识别准确率 ≥ 85%**
- ✅ **[v8.0新增] 学习风格推断准确率 ≥ 75%**
- ✅ **[v9.0新增] 时间戳对齐准确率 ≥ 95%（±3秒窗口）**
- ✅ **[v10.0新增] 反馈审计准确率 ≥ 90%**

## 12.4 用户体验测试

- ✅ 界面操作流畅，无明显延迟
- ✅ 补偿推送不打断学习体验（侧边栏/浮层）
- ✅ 功能易用，无需培训即可使用
- ✅ **[v9.0新增] 干预冷静期机制有效，界面震荡减少≥80%**
- ✅ **[v9.0新增] 弱网环境下学习功能正常，不因网络波动中断**
- ✅ **[v10.0新增] 低性能设备下系统不卡死，自动降级到仅日志模式**

## 12.5 边界场景测试

- ✅ **[v8.0新增] 摄像头遮挡/丢失场景测试通过**
- ✅ **[v8.0新增] 知识点环路场景测试通过**
- ✅ **[v8.0新增] 数据冷启动场景测试通过**
- ✅ **[v9.0新增] 弱网环境场景测试通过**
- ✅ **[v9.0新增] 时间戳对齐误差场景测试通过**
- ✅ **[v9.0新增] 干预震荡场景测试通过**
- ✅ **[v10.0新增] 人机并发冲突场景测试通过**
- ✅ **[v10.0新增] 硬件算力不足场景测试通过**
- ✅ **[v10.0新增] 恶意反馈污染场景测试通过**

## 12.6 验收标准总结

**MVP版本必须满足**:
1. 能完成完整的"感知-分析-干预-反馈"闭环
2. 至少支持一个课程/一类视频形态
3. 补偿推送功能正常工作
4. 教师端能查看基本学情数据
5. 所有核心功能验收标准达标
6. **[v8.0新增] 极端场景测试通过（信号丢失、环路、冷启动）**
7. **[v9.0新增] 边界异常逻辑测试通过（弱网、对齐、震荡）**
8. **[v10.0新增] 系统健壮性测试通过（人机冲突、硬件适配、数据审计）**

---

# 13. 项目里程碑与任务规划

## 13.1 总体时间规划（建议20周，含v8.0-v11.0扩展功能）

### 阶段一：需求分析与设计（2周）
- **第1周**:
  - 选定具体课程/样例视频（1-3个）
  - 明确知识点粒度（预计10-30个）
  - 完成需求文档（本文件）
  - 输出系统流程图（感知→分析→干预→反馈）
  - 团队内部研讨、头脑风暴

- **第2周**:
  - 产出低保真原型（Figma/墨刀/手绘）
  - 定义疑难阈值T1/T2/T3与正确率阈值P1
  - 准备最小补偿资源样例（3个知识点，每个：卡片+3题）
  - 技术调研（多模态解析、路径生成算法）

### 阶段二：MVP原型开发（8周，含v8.0扩展）
- **第3-4周**: 视频多模态解析模块
  - 实现ASR语音转写
  - 实现OCR文字识别
  - 实现知识点切分
  - 实现知识点标注界面
  - **[v8.0新增] 实现教师预设基准线功能**

- **第5周**: 行为采集与难点识别模块
  - 实现前端行为事件采集
  - 实现后端事件存储
  - 实现难点判定规则引擎
  - **[v8.0新增] 实现监控信号丢失检测**
  - **[v8.0新增] 实现难度系数加权计算**

- **第6-7周**: 补偿推送与学习路径模块
  - 实现补偿资源管理
  - 实现推送机制
  - 实现学习路径生成
  - 实现练习提交与判分
  - **[v8.0新增] 实现学习风格自适应过滤器**
  - **[v8.0新增] 实现螺旋路径生成**

- **第8周**: 教师端与管理端
  - 实现教师标注工作台
  - 实现教学效果仪表盘
  - 实现用户管理
  - **[v8.0新增] 实现环路检测功能**

- **第9-10周**: [v9.0新增] 边界异常逻辑完善
  - 实现干预抗震荡机制
  - 实现多模态时间戳对齐协议
  - 实现弱网降级策略
  - 实现教师一键禁用AI功能
  - 实现螺旋路径跳出策略

- **第11-12周**: [v10.0新增] 系统健壮性增强
  - 实现写锁与租约机制
  - 实现硬件画像三级降级
  - 实现跨课原型匹配冷启动
  - 实现教师策略编辑器
  - 实现数据审计引擎

### 阶段三：测试与优化（4周）
- **第13-14周**: 功能测试与修复
  - 完成所有功能测试
  - 修复发现的bug
  - 优化性能
  - **[v9.0新增] 边界场景测试**
  - **[v10.0新增] 健壮性测试**

- **第15周**: 用户体验优化
  - 界面优化
  - 交互优化
  - 响应速度优化
  - **[v9.0新增] 弱网环境优化**
  - **[v10.0新增] 硬件适配优化**

- **第16周**: 集成测试与验收
  - 端到端测试
  - 验收测试
  - 准备演示

### 阶段四：迭代与扩展（4周，可选）
- **第17-20周**: 
  - 根据反馈迭代优化
  - 扩展新功能
  - 准备项目答辩

## 13.2 关键里程碑

| 里程碑 | 时间 | 交付物 |
|--------|------|--------|
| M1: 需求确认 | 第2周末 | 需求文档、原型图 |
| M2: 解析模块完成 | 第4周末 | 视频解析功能可用 |
| M3: 核心闭环完成 | 第7周末 | 完整的学习闭环可用 |
| M4: MVP版本完成 | 第8周末 | 所有核心功能完成 |
| M5: [v8.0新增] 极端场景处理完成 | 第8周末 | 信号丢失、环路、冷启动功能完成 |
| M6: [v9.0新增] 边界逻辑完善完成 | 第10周末 | 抗震荡、对齐、弱网降级功能完成 |
| M7: [v10.0新增] 健壮性增强完成 | 第12周末 | 写锁、硬件适配、数据审计功能完成 |
| M8: 测试完成 | 第16周末 | 测试报告、演示视频 |
| M9: 项目交付 | 第20周末 | 最终版本、项目报告 |

## 13.3 任务分工建议

- **前端开发**: 视频播放器、行为采集、学生端界面、弱网降级前端实现
- **后端开发**: API接口、数据存储、算法实现、弱网降级后端处理
- **算法开发**: 多模态解析、难点识别、路径生成、学习风格推断
- **测试**: 功能测试、性能测试、边界场景测试、健壮性测试
- **UI/UX**: 界面设计、交互优化、用户体验测试

---

# 14. 风险与对策

## 14.1 技术风险

### 风险1: 多模态解析效果不稳定
- **风险描述**: ASR/OCR识别准确率不达标，知识点切分不准确
- **影响程度**: 高
- **应对策略**:
  - 先用"ASR+字幕/PPT文本"为主，OCR/视觉作为增强
  - 提供人工编辑兜底机制
  - 建立术语库提升识别准确率
  - 支持教师一键修正识别错误
  - **[v9.0新增] 支持教师一键禁用AI自动生成，进入专家标注模式**

### 风险2: 难点判定误报/漏报
- **风险描述**: 规则策略可能产生误判，将"走神"误判为"疑难"
- **影响程度**: 高
- **应对策略**:
  - 初版用可解释规则+阈值可配置
  - 支持多指标组合判定，减少单一指标误判
  - **[v7.0新增] 低置信度时人工确认兜底**
  - **[v8.0新增] 难度系数加权，避免"虚假繁荣"误报**
  - **[v9.0新增] 干预冷静期机制，防止频繁弹窗**
  - 后续迭代引入ML模型提高准确率
  - 允许学生反馈"误判"，系统学习优化

### 风险3: 补偿资源质量参差
- **风险描述**: AI生成的补偿资源质量不稳定，可能不够精准
- **影响程度**: 高
- **应对策略**:
  - 初版允许人工审核/编辑
  - 优先做"短小可用"的资源
  - 建立资源质量评估机制
  - **[v7.0新增] 细化反馈维度，灰度复核机制**
  - **[v8.0新增] 学习风格自适应过滤，提升匹配度**
  - **[v10.0新增] 数据审计引擎，过滤异常/恶意反馈**
  - 收集学生反馈，持续优化生成策略

### 风险4: 补偿短视频生成技术难度大
- **风险描述**: 视频生成技术复杂，可能无法在MVP版本实现
- **影响程度**: 中
- **应对策略**:
  - MVP版本优先实现知识卡片和练习题
  - 视频生成作为可选功能，可先用原视频智能剪辑
  - 或对接第三方视频生成API（Runway、Luma等）

### 风险5: [v8.0新增] 监控信号丢失处理复杂
- **风险描述**: 摄像头遮挡/丢失场景处理逻辑复杂，可能影响学习体验
- **影响程度**: 中
- **应对策略**:
  - 区分高危视频和普通视频，高危视频强制暂停
  - 普通视频仅警告，不强制暂停
  - 明确告知用户信号丢失原因和处理方式

### 风险6: [v9.0新增] 弱网环境适配困难
- **风险描述**: 弱网环境下系统可能误判，导致学习中断
- **影响程度**: 中
- **应对策略**:
  - 实现降级策略矩阵，根据网络状态自动降级
  - 本地缓存行为日志，网络恢复后自动同步
  - 弱网环境下不触发信号丢失强制暂停
  - 明确告知用户当前降级状态

### 风险7: [v10.0新增] 人机并发冲突
- **风险描述**: 教师编辑与AI后台更新同时进行，可能导致数据覆盖
- **影响程度**: 高
- **应对策略**:
  - 实现写锁机制，教师编辑时暂停AI更新
  - 30分钟租约机制，防止死锁
  - 原子化发布，保证数据一致性
  - 超时自动释放并回滚稳定版本

## 14.2 业务风险

### 风险8: 范围过大，无法闭环
- **风险描述**: 功能过多，无法在有限时间内完成完整闭环
- **影响程度**: 高
- **应对策略**:
  - 固定课程、固定视频形态、固定资源类型
  - 先闭环再扩展
  - 明确MVP边界，非核心功能延后
  - **[v8.0-v11.0] 分阶段实现扩展功能，优先核心功能**

### 风险9: 用户接受度低
- **风险描述**: 学生/教师不习惯新系统，使用率低
- **影响程度**: 中
- **应对策略**:
  - 注重用户体验设计，界面简洁易用
  - 补偿推送采用非强制方式（侧边栏/浮层）
  - **[v9.0新增] 干预冷静期机制，减少干扰**
  - 提供使用培训/帮助文档
  - 收集用户反馈，快速迭代

## 14.3 数据风险

### 风险10: 数据量过大，性能瓶颈
- **风险描述**: 行为事件数据量大，可能影响系统性能
- **影响程度**: 中
- **应对策略**:
  - 使用消息队列异步处理
  - 定期归档历史数据
  - 使用缓存优化查询性能
  - 数据库索引优化
  - **[v9.0新增] 本地缓存机制，减少服务器压力**

### 风险11: 隐私安全问题
- **风险描述**: 学习行为数据涉及隐私，可能引发安全问题
- **影响程度**: 高
- **应对策略**:
  - 仅采集学习相关数据
  - 数据加密存储
  - 数据脱敏展示
  - 遵循数据保护法规
  - **[v8.0新增] 监控信号数据安全处理**
  - **[v9.0新增] 弱网环境下本地缓存数据加密**

### 风险12: [v10.0新增] 恶意反馈污染
- **风险描述**: 异常/恶意差评导致优质资源被误下架
- **影响程度**: 中
- **应对策略**:
  - 实现数据审计引擎，过滤异常反馈
  - 难度保护区机制，提高高难资源下架阈值
  - 反馈-行为一致性校验，未观看≥80%不计入统计
  - 教师可手动放行/驳回异常反馈

## 14.4 团队风险

### 风险13: 技术难度超出团队能力
- **风险描述**: 多模态解析、AI生成等技术难度高
- **影响程度**: 中
- **应对策略**:
  - 充分利用技术顾问（蒋国伟）的经验
  - 使用成熟的第三方API/工具
  - 分阶段实现，先做简单版本
  - 加强团队技术培训
  - **[v8.0-v11.0] 分阶段实现复杂功能，降低技术风险**

### 风险14: 时间进度延误
- **风险描述**: 开发进度可能无法按计划完成
- **影响程度**: 中
- **应对策略**:
  - 明确优先级，先做核心功能
  - 定期进度检查，及时调整计划
  - 预留缓冲时间
  - 必要时缩减功能范围
  - **[v8.0-v11.0] 扩展功能作为可选，不影响MVP交付**

## 14.5 [v10.0新增] 系统健壮性风险

### 风险15: 硬件算力不足
- **风险描述**: 老旧设备无法承载多模态识别，导致页面卡死
- **影响程度**: 中
- **应对策略**:
  - 实现硬件画像驱动三级降级
  - 自动切换全量/精简/仅日志模式
  - 权重补偿机制，保证准确率
  - 实时监控设备性能，防止卡死

### 风险16: 冷启动无人标注
- **风险描述**: 新课程缺乏历史数据，教师忙碌时无法及时标注
- **影响程度**: 中
- **应对策略**:
  - 实现跨课原型匹配冷启动
  - 相似度>0.8自动复用基准
  - 教师可轻量确认，无需完整标注
  - 提供默认行业基准作为兜底

---

# 15. 附录

## 15.1 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 认知状态 | Cognitive State | 学习者的认知状态（深度思考/困难卡顿/无效停留/不确定/信号丢失/弱网降级） |
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
| **[v9.0]干预冷静期** | Intervention Cooldown | v9.0引入的干预抗震荡机制 |
| **[v9.0]时间戳对齐** | Timestamp Alignment | v9.0引入的多模态时间戳对齐协议 |
| **[v9.0]弱网降级** | Network Degradation | v9.0引入的网络环境自适应降级策略 |
| **[v9.0]教师主权** | Teacher Sovereignty | v9.0引入的教师禁用AI机制 |
| **[v9.0]螺旋跳出** | Spiral Path Escape | v9.0引入的螺旋路径反复失败跳出机制 |
| **[v10.0]写锁租约** | Write Lock Lease | v10.0引入的知识图谱写锁租约机制（30分钟超时自动释放） |
| **[v10.0]硬件降级** | Hardware Degradation | v10.0引入的设备画像驱动三级降级（全量/精简/仅日志） |
| **[v10.0]原型匹配** | Prototype Matching | v10.0引入的跨课原型匹配冷启动机制 |
| **[v10.0]激进系数** | Aggression Coefficient | v10.0引入的教师干预敏感度统一调节（0.1-2.0） |
| **[v10.0]数据审计** | Data Audit Engine | v10.0引入的异常/恶意反馈过滤与审计回放机制 |
| **[v10.0]难度保护区** | Difficulty Protection Zone | v10.0引入的高难资源下架阈值保护机制 |
| **[v10.0]一致性校验** | Consistency Check | v10.0引入的反馈-行为一致性强制校验（80%门槛） |
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
11. **[v9.0补充]** 干预系统抗震荡机制（Hysteresis）研究
12. **[v9.0补充]** 多模态数据时间戳对齐算法
13. **[v9.0补充]** 弱网环境自适应降级策略设计
14. **[v9.0补充]** 教师主导权与AI辅助平衡研究

## 15.3 版本演进更新日志（v6.0-v11.0）

### v6.0 核心更新
1. **从"数据驱动"转向"认知+情境驱动"**：引入信号不协和检测，区分深度思考/困难卡顿/无效停留
2. **溯源式根本原因诊断**：基于GNN知识依赖图回溯前置知识点
3. **安全熔断机制**：高危场景PPE检测与强制中断
4. **DTW动作评分**：基于标准动作库的动态时间规整比对
5. **资源反馈闭环**：细化反馈维度，连续3个差评自动下架

### v7.0 核心更新
6. **低置信度人机协作兜底**：置信度<0.6时弹出确认窗口，避免误判
7. **个体认知步频**：基于前3个知识点计算个人学习节奏基准线
8. **灰度复核机制**：修正资源优先推送给5名学生验证，评分回升后转正
9. **L3级进度停滞自动触发**：累计停留时长>5倍视频时长时自动触发人类介入
10. **智能剪辑上下文保留**：AI剪辑时强制包含前5s背景引入和后3s总结
11. **教师趋势预测与策略推荐**：从数据看板升级为决策支持系统

### v8.0 核心更新
12. **认知步频难度系数加权**：使用相对时长（个人/全网平均）避免"虚假繁荣"误报
13. **学习风格自适应过滤器**：根据反馈推断学习风格，自动过滤资源类型
14. **监控信号心跳检测**：实时检测摄像头黑屏/遮挡，高危视频强制暂停
15. **逻辑环路检测与螺旋路径**：检测知识点环路，生成关联演示视频和并行练习
16. **教师预设基准线**：新课程冷启动时，教师可标记核心难点和停留系数

### v9.0 核心更新
17. **干预抗震荡机制（Hysteresis）**：引入5-10分钟冷静期，防止频繁弹窗，界面震荡减少≥80%
18. **多模态时间戳对齐协议**：定义±3秒软对齐窗口，处理ASR/CV/行为日志的时间戳误差
19. **弱网降级策略矩阵**：根据网络状态自动降级监控功能，本地缓存保证学习连续性
20. **教师一键禁用AI自动生成**：支持专家标注模式，完全控制知识点边界
21. **螺旋路径跳出策略**：反复失败≥3次时自动跳转L3级教师答疑

### v10.0 核心更新
22. **写锁（Write Lock）与租约（Lease Timeout）**：专家标注模式30分钟租约，超时自动释放并回滚稳定版本
23. **原子化发布**：教师发布时一次性完成校验、提交、解锁、托管，避免数据覆盖
24. **硬件画像驱动三级降级**：根据CPU/FPS/GPU自动切换全量/精简/仅日志模式，权重补偿（0.4→0.8）
25. **跨课原型匹配冷启动**：新课程自动匹配相似课程原型（相似度>0.8），复用难度基准和步频阈值
26. **教师策略编辑器**：干预激进系数（0.1-2.0）支持全班级统一调参
27. **数据审计引擎**：过滤异常/恶意反馈，难度保护区提高下架阈值（3→10）
28. **反馈-行为一致性校验**：未观看≥80%或未完成关联测试的差评不计入自动下架统计

### v11.0（最终版）整合说明
29. **完整整合v6.0-v10.0所有版本内容**，形成可直接交付开发的最终完整需求规格说明书
30. **文档状态**：最终版（Final Version），不再进行功能增补，仅用于开发实施与评审归档

---

## 15.4 v11.0（最终版）完整功能清单

### 核心业务流（覆盖90%正常教学场景）
- ✅ 多模态解析与知识建模（ASR/OCR/CV/语义引擎）
- ✅ 学习行为采集与认知状态识别（信号不协和/置信度门控/难度系数加权）
- ✅ 个性化学习路径生成（单点补偿/溯源回补/认知负荷调节）
- ✅ 分层干预策略（L1轻量提醒/L2交互修复/L3人类介入）
- ✅ 智能补偿资源生成（知识卡片/微视频/练习/知识提示/思维导图/参数速查表）

### 复杂情境适配（职教特有难题）
- ✅ 溯源式诊断（GNN知识依赖图回溯）
- ✅ 知识环路与螺旋路径（环路检测/关联演示/并行练习/跳出L3）
- ✅ 职教安全熔断（PPE检测/动作评分DTW/信号心跳检测）
- ✅ 冷启动处理（教师预设基准线+跨课原型匹配）

### 系统健壮性（核心落地能力）
- ✅ 干预抗震荡（Hysteresis冷静期5-10分钟）
- ✅ 多模态时间戳对齐（±3秒软对齐窗口/语义脱节检测）
- ✅ 弱网降级与本地缓存（IndexDB缓存/网络恢复同步）
- ✅ 硬件画像三级降级（全量/精简/仅日志+权重补偿0.4→0.8）
- ✅ 人机冲突处理（写锁+租约30min+心跳续租+超时释放回滚+原子发布）

### 数据安全与审计（长期稳定运行不跑偏）
- ✅ 数据审计引擎（异常/恶意反馈过滤/速率限制/异常模式识别）
- ✅ 难度保护区（高难资源下架阈值3→10/内容不符类证据要求）
- ✅ 反馈-行为一致性校验（观看≥80%或完成关联测试门槛）
- ✅ 教师主权（禁用AI/专家标注/统一调参激进系数0.1-2.0）

---

## 文档结束

**编写团队**：周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
**技术顾问**：蒋国伟
**指导老师**：王海霞
**版本**：v11.0（最终版 Final Version）
**日期**：2026年1月

---

**版本说明**：v11.0为最终完整整合版，完整整合了v6.0-v10.0所有版本内容，形成可直接交付开发的最终完整需求规格说明书。本文档共计约39,000字，完整阐述了AI赋能职教视频个性化教学项目从v4.0到v11.0的完整演进路径，涵盖核心业务流、复杂情境适配、系统健壮性、数据安全与审计等全部功能模块，确保系统在真实职教场景下的鲁棒性、可用性和长期稳定运行。

**文档状态**：**最终版（Final Version）**，不再进行功能增补，仅用于开发实施与评审归档。
    