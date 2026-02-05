# AI赋能职教视频个性化教学项目需求规格说明书（第七稿-完整版）

## 文档版本信息
- **版本号**: v7.0
- **编写日期**: 2026年1月
- **编写团队**: 周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
- **技术顾问**: 蒋国伟
- **指导老师**: 王海霞
- **文档状态**: 待评审
- **版本说明**: 基于v6.0进行容错增强、动态适配与决策支持升级

---

## 版本演进说明

### v7.0 主要更新内容

| 更新类别 | 更新内容 | 影响模块 | 标记 |
|---------|---------|---------|------|
| 容错增强 | 多模态低置信度人机协作兜底 | 模块B | [v7.0 新增] |
| 动态适配 | 认知负荷个性化基准线（认知步频） | 模块B | [v7.0 新增] |
| 反馈优化 | 资源评价细化 + 修正资源复核流 | 模块C | [v7.0 优化] |
| 图谱进化 | 知识依赖图数据验证流（隐性依赖发现） | 模块A | [v7.0 新增] |
| 干预补全 | L3级进度停滞自动触发机制 | 模块C | [v7.0 优化] |
| 剪辑优化 | 智能剪辑上下文保留协议 | 模块C | [v7.0 新增] |
| 决策支持 | 教师端趋势预测与策略推荐 | 模块D | [v7.0 新增] |

### v6.0 vs v7.0 核心差异

| 维度 | v6.0 | v7.0 |
|------|------|------|
| **容错能力** | 信号置信度阈值固定 | **低置信度人工确认兜底** |
| **个性化** | 统一T1/T2阈值 | **个人认知步频动态基准** |
| **资源质量** | 简单"有帮助/无帮助" | **4维度反馈 + 灰度复核** |
| **知识图谱** | 静态GNN初始图谱 | **数据驱动的依赖权重修正** |
| **干预触发** | 仅学生主动求助 | **自动检测进度停滞** |
| **视频剪辑** | 精确时间戳切片 | **强制保留前5s后3s上下文** |
| **教师赋能** | 数据看板 | **预测 + 策略推荐** |

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

构建一个**以主动智能补偿为核心、认知+情境驱动、人机协作容错**的教学视频个性化学习支持系统，通过多模态分析学习者的观看行为与认知状态，**精准识别知识薄弱点并分层主动推送高质量补偿资源**，实现真正意义上的"一人一策"个性化教学。

[v7.0 优化] 新增"人机协作容错"理念，避免AI误判对学习体验的负面影响。

## 1.2 项目背景

本项目是在蒋国伟团队前期"教学视频解析"成果基础上，进行深度的功能进阶与目标重构。项目聚焦职业教育领域，旨在解决以下核心痛点：

- **学生被动看视频**：学习者大量依赖教学视频自学，但普遍缺乏针对性反馈
- **知识吸收效率低**：学习过程中常见行为包括暂停、回放、拖拽返回、长时间停留等，这些行为往往对应"知识点未掌握/理解困难"，但传统教学难以实时捕捉
- **行为归因不精准**：传统系统无法区分"深度思考"与"走神/离开"，导致误判
- **学习路径一刀切**：传统平台"千人一面"，无法提供主动、精准、即时的补偿
- **教师负担重**：教师无法实时掌握每位学生的具体卡点，学情监测成本高
- **职教安全风险**：高危实操场景缺乏安全预警机制
- **[v7.0 新增] AI误判风险**：光线不足、遮挡等环境因素可能导致多模态信号误判

## 1.3 核心愿景

- **懂学生的AI**：打造"教育版淘宝"的千人千面推荐能力，实现学习内容与路径的个性化匹配
- **认知驱动**：从单纯的行为数据分析升级为认知状态+情境感知的智能判定
- **安全优先**：职教场景下的安全熔断机制，保障实操学习安全
- **动态干预**：让AI从单纯的视频播放器，升级为能实时捕捉学习障碍、分层提供"补偿教育"的智能导师
- **[v7.0 新增] 人机协作**：AI辅助判断，人类最终确认，避免过度依赖AI导致的误判

## 1.4 项目目标（优先级排序）

### 1.4.1 核心目标

1. **精准认知状态识别 + 容错机制**（最高优先级）
   - 引入**信号不协和（Signal Dissonance）**检测
   - 区分"深度思考"、"困难卡顿"与"走神/离开"
   - **[v7.0 新增] 低置信度人工确认兜底**，避免误判
   - 认知状态识别准确率目标：≥ 85%（v1.0）

2. **主动智能补偿 + 个性化适配**（最高优先级）
   - 系统必须在学习者"卡住"时**主动干预**，而非等他求助
   - 响应时间：行为检测 → 补偿推送 ≤ 3-5分钟
   - 分层干预，避免干预疲劳
   - **[v7.0 新增] 基于个人认知步频的动态阈值**

3. **溯源式根本原因诊断 + 数据驱动图谱**
   - 若连续失败，回溯前置知识点而非重复当前知识点
   - 基于GNN知识依赖图计算最短回溯路径
   - **[v7.0 新增] 学习数据自动修正图谱依赖关系**

4. **职教安全保障 + 环境容错**
   - 高危场景安全熔断机制
   - 动作规范性实时评分
   - **[v7.0 新增] 环境因素干扰时的人工确认**

5. **自动生成高质量补偿资源 + 持续进化**
   - 补偿资源时长控制在90秒以内
   - 必须"**短、狠、准**"，直击痛点
   - 负反馈闭环保证资源质量
   - **[v7.0 新增] 细化反馈维度 + 修正资源灰度复核**

6. **[v7.0 新增] 教师决策支持**
   - 从被动的数据看板到主动的趋势预测
   - 提供具体的教学策略推荐

## 1.5 项目边界（本期不做/暂缓）

- ❌ 不做泛娱乐平台视频理解与推荐
- ❌ 不做完整LMS/教务系统替代，仅做"视频学习辅助闭环"
- ❌ 不追求全学科通用，优先聚焦**汽修（Auto Repair）**课程跑通闭环
- ❌ 不以"最强模型"作为指标，优先可用、可验证、可迭代
- ❌ 不做完整的用户注册登录系统（初期可简化）
- ❌ 不做移动端APP（优先Web端，但保留WebSocket同步协议）
- ❌ [v7.0 补充] 不追求100%自动化，预留人工确认接口保证容错

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

### 2.1.3 项目管理员（可选）
- **角色描述**：系统管理员、课程维护人员
- **核心需求**：
  - 课程/视频/资源维护
  - 策略阈值配置
  - 用户权限管理
  - 系统监控与日志查看
  - 安全规范库管理
  - **[v7.0 新增] 个性化基准线参数调优**

## 2.2 核心使用场景（用户故事）

### 场景1：学生观看视频遇到难点（认知状态精准识别 + v7.0容错）

**用户故事**：学生观看《汽修-发动机拆装》视频，在"曲轴拆卸"知识点处暂停超过10秒。

**系统行为（v7.0升级）**：
1. 系统检测到 `Behavior_Pause = True`
2. 启动 **3秒窗口期扫描**，进行多模态交叉验证：
   - 摄像头检测：视线是否在屏幕知识点区域？
   - 鼠标行为：是否在图表/关键区域悬停？
   - 微表情分析：是否表现为"专注/轻微皱眉"？
3. **[v7.0 新增] 置信度检查**：
   - **若置信度 ≥ 0.7**：直接判定认知状态
   - **若置信度 < 0.6**（光线暗/面部遮挡）：
     ```
     弹出轻量确认：
     "⚠️ 检测到环境较暗，无法准确判断您的学习状态。
      您是否在理解这个知识点时遇到了困难？
      [是，需要帮助] [否，我在思考]"
     ```
4. **认知状态判定**：
   - ✅ 深度思考（Deep Thinking）：视线在区域 + 鼠标悬停 + 专注表情 → 不干预，记录正向行为
   - ⚠️ 困难卡顿（Difficulty）：视线在区域 + 回放行为 + 困惑表情 **或学生确认需要帮助** → 触发L1干预
   - ❌ 无效停留（Off-task）：视线偏移>5s + 无微操作 + 人体缺位 → 暂停打卡验证
5. 若判定为"困难卡顿"，在5分钟内主动推送L1级补偿资源

**学生反馈闭环（v7.0升级）**：
- 资源下方显示**细化反馈按钮**：
  ```
  这个资源对你有帮助吗？
  [👍 有帮助]  
  [👎 太难了] [👎 讲解啰嗦] [👎 格式不喜欢] [👎 内容不符]
  ```

### 场景2：溯源式根本原因诊断（v7.0数据驱动图谱优化）

**用户故事**：学生在"曲轴拆卸"知识点测验中连续失败2次。

**系统行为（v7.0升级）**：
1. 检测到连续失败2次
2. **逻辑切换**：不再重复推送"曲轴拆卸"资源
3. **回溯诊断**：
   - 查询GNN知识依赖图
   - 计算最短回溯路径：发现"曲轴拆卸"依赖"发动机结构认知"
   - 自动测试前置知识点"发动机结构认知"
4. **[v7.0 新增] 隐性依赖学习**：
   - 系统记录：学生A未掌握"发动机结构"，卡在"曲轴拆卸"
   - 若班级数据显示：
     - 80%掌握"发动机结构"的学生轻松通过"曲轴拆卸"
     - 70%未掌握"发动机结构"的学生卡在"曲轴拆卸"
   - **系统自动增强依赖权重**：发动机结构 → 曲轴拆卸（权重 0.6 → 0.85）
5. 找到根本薄弱点后，生成针对性补偿路径

### 场景3：高危场景安全熔断（v7.0环境容错）

**用户故事**：学生观看《焊接操作》视频，环境光线较暗。

**系统行为（v7.0升级）**：
1. 视频播放前，CV模块（YOLOv8）实时检测PPE（个人防护装备）
2. **[v7.0 新增] 置信度检查**：
   - **若检测置信度 ≥ 0.85**：直接判定（已佩戴/未佩戴）
   - **若检测置信度 < 0.6**（光线暗/遮挡）：
     ```
     弹出非侵入式确认：
     "⚠️ 环境光线不足，无法确认防护装备佩戴情况。
      焊接操作前，请确认您已佩戴：
      □ 护目镜  □ 防护手套  □ 工作服
      [已确认，开始学习]"
     ```
3. **安全熔断触发**（仅高置信度违规）：
   - 明确检测到未戴护目镜（置信度>0.85）
   - 系统立即挂起当前视频
   - 强制弹出"安全规范确认"或"事故案例回顾"
4. **动作评分**：
   - 使用SlowFast提取动作轨迹
   - 与标准库进行DTW比对
   - 输出《动作偏差分析报告》

### 场景4：认知负荷预警（v7.0个性化基准线）

**用户故事**：学生在30分钟内触发了3次补偿资源推送。

**系统行为（v7.0升级）**：
1. **[v7.0 新增] 个人认知步频计算**：
   - 系统分析该生前3个知识点的平均停留时长：2分钟/知识点
   - 计算测验响应速度：平均15秒/题
   - 得出该生的**认知步频**：中速型（baseline = 2min）
2. **动态阈值判定**：
   - 当前知识点停留5分钟 = 个人基准×2.5倍
   - 超过个人基准×1.5倍（3分钟） → 判定为异常
3. **认知负荷预警**：
   - 检测到短时间内多次补偿 + 停留时长异常
   - 系统判定为"认知过载"
4. **强制干预**：
   - 暂停新知识推送
   - 弹出"建议休息5分钟"提示
   - 或引导回顾基础前置知识点

### 场景5：资源反馈与复核（v7.0细化+灰度）

**用户故事**：AI生成的"曲轴拆卸"补偿视频被连续3名学生标记为"讲解啰嗦"。

**系统行为（v7.0升级）**：
1. **细化反馈统计**：
   - 学生A：👎 讲解啰嗦
   - 学生B：👎 讲解啰嗦  
   - 学生C：👎 讲解啰嗦
2. **自动下架**：触发"连续3个负反馈"规则
3. **[v7.0 新增] 教师修正**：
   - 通知教师："资源R001因'讲解啰嗦'被下架"
   - 教师编辑：缩短视频至60秒，去除冗余讲解
4. **[v7.0 新增] 灰度复核**：
   - 修正后的资源标记为"测试版"
   - 优先推送给5名学生进行灰度验证
   - 若评分回升（3/5标记"有帮助"） → 正式转正
   - 若仍不佳 → 继续修正或人工介入

### 场景6：L3级干预自动触发（v7.0进度停滞检测）

**用户故事**：学生在"曲轴拆卸"知识点停留累计45分钟（含多次回放），L2干预无效。

**系统行为（v7.0升级）**：
1. **[v7.0 新增] 进度停滞检测**：
   - 知识点时长：8分钟
   - 学生累计停留：45分钟 = 5.6倍视频时长
   - L2干预已触发，练习正确率仍<50%
2. **自动触发L3**（无需学生主动求助）：
   ```
   🔴 红色预警 → 教师端
   "学生李明陷入学习死循环：
    - 知识点：K3 曲轴拆卸
    - 停留时长：45分钟（视频时长5.6倍）
    - L2干预已触发，但练习正确率40%
    - 建议立即介入"
   [1对1连线] [推荐同伴] [创建辅导]
   ```
3. **教师响应**：选择合适的干预方式

### 场景7：智能剪辑上下文保留（v7.0剪辑协议）

**用户故事**：系统为"曲轴拆卸"知识点生成补偿微视频。

**系统行为（v7.0升级）**：
1. **原始视频时间戳**：
   - K3 曲轴拆卸：3:45 - 5:30（105秒）
2. **[v7.0 新增] 上下文保留协议**：
   ```
   剪辑范围 = [start - 5s, end + 3s]
            = [3:40, 5:33]
            = 113秒
   ```
   - **前5秒背景引入**："接下来我们要拆卸曲轴，先回顾一下发动机整体结构..."
   - **核心知识点**：105秒
   - **后3秒总结**："曲轴拆卸完成后，下一步是检查轴承..."
3. **防止逻辑断裂**：
   - 学生看到完整的"铺垫→讲解→过渡"流程
   - 避免"掐头去尾"导致的理解困难

### 场景8：教师端趋势预测与策略推荐（v7.0决策支持）

**用户故事**：教师登录系统，查看《汽修-发动机拆装》课程的班级学情。

**系统展示（v7.0新增）**：
1. **全班共同盲点图表**（延续v6.0）
2. **[v7.0 新增] 趋势预测**：
   ```
   📈 未来一周预测
   基于当前学习曲线，以下知识点可能成为全班性难点：
   
   1. K8 气门调整（预测困难率：65%）
      - 当前进度：40%学生已学习
      - 当前困难率：55%
      - 预测依据：前置知识K6掌握率偏低（仅60%）
   
   2. K10 故障诊断（预测困难率：58%）
      - 预测依据：需要综合运用K3-K7知识，认知负荷高
   ```
3. **[v7.0 新增] 策略推荐**：
   ```
   💡 教学策略建议
   
   针对 K8 气门调整：
   ✓ 建议下周实操课预留15分钟重点演示"气门间隙测量工具"的使用
   ✓ 补充K6前置知识的复习材料
   ✓ 增加3-5道K8相关的练习题
   
   针对 K10 故障诊断：
   ✓ 建议设计综合案例，分步引导学生应用知识
   ✓ 可考虑分组讨论，降低个人认知负荷
   ```
4. **动作偏差统计**（延续v6.0 + 优化）：
   ```
   🔧 实操动作分析
   
   K3 曲轴拆卸动作评分：
   - 平均得分：0.78
   - 常见问题：
     * 40%学生工具握持角度偏离（建议加强示范）
     * 25%学生拆卸速度偏快（建议强调安全第一）
   
   → 建议线下重点演示：工具正确握持姿势
   ```

---

# 3. 核心功能模块详细设计

## 3.1 模块A：视频多模态语义解析与知识建模（基石）

### 3.1.1 模块目标
把视频内容结构化到"知识点-时间段-关键词-资源-安全规范"层面，为后续的个性化推荐提供准确的内容语义基础，**[v7.0新增] 并通过学习数据持续优化知识依赖关系**。

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
- **关联信息**：
  - 前置知识点列表（依赖关系）
  - 后置知识点列表
  - 重要程度评分（1-5分）
  - 安全规范关联（v6.0新增）：关联的安全条目
  - 手册章节关联（v6.0新增）：对应的实操手册内容
  - **[v7.0新增] 依赖强度权重**：数据驱动的动态权重

#### A3.3 知识图谱构建（GNN升级 + v7.0数据驱动）

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

**验证流程**：
1. 每周批量分析全班学习数据
2. 识别显著的依赖关系（通过率差异≥20%）
3. 自动增强GNN图谱中的依赖权重
4. 教师端展示修正建议，可人工审核

**效果**：
- 修正初始图谱的偏见
- 发现隐性依赖关系
- 持续优化溯源诊断准确率

#### A3.4 时间戳动态修正（v6.0新增）

**问题背景**：职教视频中常存在"操作与讲解异步"问题，静态时间戳往往不准确。

**修正逻辑**：
1. 记录多数学生在点击某知识点后实际倒退/快进到的具体时间点
2. 统计分析行为数据，计算实际有效时间范围
3. 自动修正该知识点在图谱中的起始和结束坐标
4. 修正阈值：当超过30%的学生行为偏离原时间戳时触发修正

#### A3.5 职教专属功能

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

### 3.1.5 验收标准
- ✅ 对选定课程样例视频，能生成不少于N个知识点切片（N由课程确定，如10-30）
- ✅ 每个知识点均具备可回放定位的时间戳（支持动态修正）
- ✅ 知识点识别准确率 ≥ 85%（v1.0）
- ✅ 支持人工在管理端调整知识点边界与名称（保证可控性）
- ✅ 知识点名称、摘要、关键词可人工编辑
- ✅ 安全规范正确关联率 ≥ 90%（v6.0新增）
- ✅ 动作偏差分析报告可生成（v6.0新增）
- ✅ **[v7.0新增] 依赖权重修正机制正常运行，每周自动优化**

---

## 3.2 模块B：学习行为采集与认知状态识别（v6.0重构 + v7.0容错）

### 3.2.1 模块目标
从单纯的行为数据分析升级为**认知+情境驱动**的智能判定，精准区分"深度思考"、"困难卡顿"与"无效停留"，**[v7.0新增] 并在低置信度时引入人机协作兜底机制**。

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

#### B2.2 多模态认知状态信号（v6.0新增）

| 信号类型 | 数据来源 | 采集内容 | **[v7.0新增] 置信度输出** |
|---------|---------|---------|--------------------------|
| **视线追踪** | 摄像头（需授权） | 视线位置（屏幕区域）、视线偏移时长 | 0.0-1.0 |
| **微表情** | 摄像头（需授权） | 表情分类（专注/困惑/走神/皱眉） | 0.0-1.0 |
| **鼠标行为** | 前端采集 | 鼠标位置、悬停区域、点击频率 | 1.0（确定性） |
| **键盘行为** | 前端采集 | 打字速度（笔记区）、快捷键使用 | 1.0（确定性） |
| **环境音** | 麦克风（需授权） | 环境杂音判定（教学相关/非教学相关） | 0.0-1.0 |
| **人体检测** | 摄像头（需授权） | 人体存在、大动作偏移 | 0.0-1.0 |

#### B2.3 **[v7.0新增] 个人认知步频计算**

```python
class CognitivePaceCalculator:
    """
    个人认知步频计算器
    """
    
    def calculate_baseline(self, user_id):
        """
        计算学生的个人认知基准线
        """
        # 获取前3个知识点的学习数据
        recent_kps = self.get_recent_knowledge_points(user_id, count=3)
        
        # 计算平均停留时长
        avg_duration = sum(kp.watch_duration for kp in recent_kps) / len(recent_kps)
        
        # 计算测验响应速度
        exercises = self.get_recent_exercises(user_id, count=5)
        avg_response_time = sum(ex.response_time for ex in exercises) / len(exercises)
        
        # 综合计算认知步频
        cognitive_pace = CognitivePace(
            baseline_duration=avg_duration,
            baseline_response_time=avg_response_time,
            pace_type=self._classify_pace(avg_duration, avg_response_time),
            user_id=user_id,
            calculated_at=datetime.now()
        )
        
        return cognitive_pace
    
    def _classify_pace(self, duration, response_time):
        """
        分类学习节奏类型
        """
        if duration < 1.5 and response_time < 10:
            return "fast"  # 快速型
        elif duration > 3.0 or response_time > 30:
            return "slow"  # 慢速型
        else:
            return "medium"  # 中速型
    
    def is_abnormal_duration(self, user_id, current_duration, kp_standard_duration):
        """
        判断当前停留时长是否异常
        """
        baseline = self.get_baseline(user_id)
        
        # [v7.0核心逻辑] 个性化阈值
        personal_threshold = baseline.baseline_duration * 1.5
        
        # 不使用统一的T1/T2，而是基于个人基准
        if current_duration > personal_threshold:
            return True, f"超过个人基准{((current_duration/baseline.baseline_duration)-1)*100:.0f}%"
        
        return False, "正常"
```

### 3.2.3 认知状态判定模型（v6.0核心重构 + v7.0容错）

#### B3.1 信号不协和检测（Signal Dissonance）+ **[v7.0新增] 置信度门控**

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
    
    def _generate_confirmation_prompt(self, reason, details):
        """
        生成人工确认提示语
        """
        prompts = {
            "environment_factors": {
                "title": "⚠️ 环境检测受限",
                "message": f"检测到{details}，无法准确判断您的学习状态。",
                "question": "您是否在理解这个知识点时遇到了困难？",
                "options": ["是，需要帮助", "否，我在思考"]
            },
            "ppe_detection": {
                "title": "⚠️ 安全装备确认",
                "message": "环境光线不足，无法确认防护装备佩戴情况。",
                "question": "请确认您已佩戴必需的防护装备",
                "options": ["已确认"]
            }
        }
        return prompts.get(reason)
```

**判定结果分类（v7.0升级）**：

| 认知状态 | 判定条件 | 置信度要求 | 系统响应 |
|---------|---------|-----------|---------|
| **深度思考** | 视线在区域 + 鼠标悬停 + 专注表情 | ≥ 0.7 | 不干预，记录正向行为 |
| **困难卡顿** | 视线在区域 + 回放行为 + 困惑表情 | ≥ 0.7 | 触发分层干预 |
| **无效停留** | 视线偏移>5s + 无微操作 + 人体缺位 | ≥ 0.7 | 暂停打卡验证 |
| **[v7.0新增] 不确定** | 置信度 < 0.6 | < 0.6 | **弹出轻量确认窗口** |

#### B3.2 多模态交叉验证（v6.0新增）

**目的**：防止误判"走神"或临时离开为学习困难

**验证逻辑**：
1. 当检测到长时间停留时
2. 交叉验证以下条件：
   - 视线是否在屏幕内？
   - 设备是否有微操作（鼠标移动/点击）？
3. 只有两者均为"否"时，才判定为"非学习状态"
4. 触发"暂停/打卡验证"，避免影响学习画像

#### B3.3 困难度分数计算（升级版 + v7.0个性化）

```python
# v7.0 困难度计算公式（含个性化基准）
Di = (
    w1 × cognitive_confusion_score +      # 认知困惑得分（微表情）
    w2 × behavior_difficulty_score +      # 行为困难得分（回放/暂停）
    w3 × knowledge_dependency_score +     # 知识依赖得分（前置缺失）
    w4 × personal_pace_anomaly_score     # [v7.0新增] 个人节奏异常得分
)

# [v7.0新增] 个人节奏异常得分计算
personal_pace_anomaly_score = max(0, (current_duration - personal_baseline) / personal_baseline)

# 权重配置（可调）
w1 = 0.3  # 认知信号权重
w2 = 0.25 # 行为信号权重
w3 = 0.2  # 知识依赖权重
w4 = 0.25 # [v7.0新增] 个人节奏权重
```

#### B3.4 公共难点识别
- 若某视频片段被多人（如≥5人）标记为"困难卡顿"，自动标记为"公共难点"
- 提升该知识点的优先级，供教师重点关注
- 自动加入"全班共同盲点图表"

#### B3.5 溯源式根本原因诊断（v6.0新增）

**触发条件**：学生在某知识点 $K_n$ 的测验中连续失败2次

**诊断逻辑**：
1. 系统逻辑由"重复学习 $K_n$"切换为"回溯测试前置知识点 $K_{n-1}$"
2. 使用GNN查询知识依赖图
3. 计算路径最短回溯节点
4. 对回溯节点进行快速诊断测试
5. 若回溯节点也失败，继续向前回溯
6. 直到找到真正的"根本薄弱点"

### 3.2.4 输出

**学生-知识点掌握状态**：
- **未学**：尚未观看该知识点
- **学习中**：正在观看，认知状态正常
- **深度思考**：检测到专注行为，正向信号（v6.0新增）
- **疑难**：检测到困难卡顿，需要干预
- **已掌握**：完成补偿后，练习正确率达标
- **根本薄弱**：溯源诊断发现的真正薄弱点（v6.0新增）
- **[v7.0新增] 不确定**：低置信度，需人工确认

### 3.2.5 验收标准
- ✅ 能对单个学生一次观看记录生成"疑难知识点TopK"及触发原因
- ✅ 认知状态分类准确率 ≥ 85%（v1.0）
- ✅ 教师端可查看班级层面的疑难分布（按知识点聚合）
- ✅ 难点判定必须给出触发原因（可解释性）
- ✅ 支持阈值可配置
- ✅ 溯源诊断能正确识别根本薄弱点（v6.0新增）
- ✅ **[v7.0新增] 低置信度时不误判，人工确认机制正常工作**
- ✅ **[v7.0新增] 个人认知步频计算准确，动态阈值有效**

---

## 3.3 模块C：个性化学习路径与智能补偿资源（v6.0升级 + v7.0反馈优化）

### 3.3.1 模块目标
基于学习者的认知状态与薄弱点，**主动、分层、精准**地推送补偿资源，实现真正的"智能补偿教育"，**[v7.0新增] 并通过细化反馈和灰度复核机制持续优化资源质量**。

### 3.3.2 个性化学习路径生成

#### C2.1 路径生成触发条件
- **实时触发**：检测到"困难卡顿"认知状态（模块B输出）
- **测验触发**：知识点测验失败
- **溯源触发**：连续失败2次，启动溯源诊断
- **[v7.0新增] 停滞触发**：累计停留时长超过视频时长5倍

#### C2.2 路径生成策略

**策略1：单点补偿（L1/L2干预）**
- 针对单个知识点的困难
- 推送该知识点的补偿资源
- 快速、轻量、精准

**策略2：溯源回补（v6.0新增）**
- 针对前置知识缺失
- 回溯GNN知识依赖图
- 找到根本薄弱点
- 生成从根本点到目标点的补偿路径

**策略3：认知负荷调节（v6.0新增 + v7.0个性化）**
- 检测到认知过载时
- 暂停新知识推送
- 引导休息或回顾基础知识
- **[v7.0优化] 基于个人认知步频动态判定**

**策略4：[v7.0新增] 进度停滞自动升级**
- 检测到长时间停滞（累计时长>5倍视频时长）
- L2干预无效时
- 自动触发L3级人类介入

### 3.3.3 智能补偿资源生成（短、狠、准 + v7.0反馈闭环）

#### C3.1 补偿资源类型

| 资源类型 | 触发场景 | 时长 | 生成方式 |
|---------|---------|------|---------|
| **知识卡片** | 首次困难（L1） | 30-60s阅读 | 自动生成摘要+关键图示 |
| **精准微视频** | 二次困难（L2） | 60-90s | AI智能剪辑+TTS旁白 |
| **针对性练习** | 诊断测试 | 3-5题 | 基于知识点的习题库 |
| **知识提示（Tips）** | 操作类知识点 | 15-30s | 关键步骤+注意事项 |
| **同伴经验（v6.0）** | L2后掌握 | 30s音频 | 学生录制分享 |

#### C3.2 **[v7.0优化] 资源评价细化机制**

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

#### C3.3 **[v7.0新增] 修正资源灰度复核机制**

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

#### C3.4 **[v7.0新增] 智能剪辑上下文保留协议**

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
            # 优先保留核心内容，压缩上下文
            core_duration = kp.end_time - kp.start_time
            if core_duration <= self.MAX_DURATION - (self.CONTEXT_BEFORE + self.CONTEXT_AFTER):
                # 核心内容可容纳，保留完整上下文
                pass
            else:
                # 核心内容过长，调整策略
                clip_start = kp.start_time - 3  # 缩短前置上下文
                clip_end = min(kp.start_time + self.MAX_DURATION - 3, kp.end_time + 2)
        
        # 执行剪辑
        clipped_video = self.video_editor.clip(
            video_path=video.file_path,
            start_time=clip_start,
            end_time=clip_end
        )
        
        # 生成字幕和旁白
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

### 3.3.4 分层干预策略（L1/L2/L3）（v6.0新增 + v7.0优化）

| 干预等级 | 触发条件 | 干预形式 | 资源优先级 | **[v7.0优化]** |
|---------|---------|---------|-----------|----------------|
| **L1：轻量提醒** | 首次T1异常停留 | 侧边栏浮窗（知识卡片） | 原创视频摘要 | 细化反馈 |
| **L2：交互修复** | 二次停留或测验失败 | 3min精准微视频 + 针对性练习 | AI智能剪辑片段 | 上下文保留 |
| **L3：人类介入** | **[v7.0新增] 进度停滞或**修复后持续低增益 | 触发"求助"按钮，推送至班级群或导师端 | 1对1连线/同伴互助 | **自动触发** |

#### C4.1 **[v7.0新增] L3级进度停滞自动触发机制**

```python
class InterventionEscalationService:
    """
    干预升级服务
    """
    
    STAGNATION_THRESHOLD = 5.0  # 停滞阈值：5倍视频时长
    L2_INEFFECTIVE_THRESHOLD = 0.5  # L2无效阈值：正确率<50%
    
    def check_escalation(self, user_id, kp_id):
        """
        [v7.0新增] 检查是否需要升级干预
        """
        # 获取学习记录
        learning_record = db.query(LearningRecord).filter(
            user_id=user_id,
            kp_id=kp_id
        ).first()
        
        kp = db.query(KnowledgePoint).get(kp_id)
        
        # 计算累计停留时长倍数
        total_duration = learning_record.total_watch_duration
        video_duration = kp.end_time - kp.start_time
        duration_ratio = total_duration / video_duration
        
        # [v7.0新增] 进度停滞检测
        if duration_ratio >= self.STAGNATION_THRESHOLD:
            # 检查L2干预是否已触发
            l2_interventions = db.query(Intervention).filter(
                user_id=user_id,
                kp_id=kp_id,
                level="L2"
            ).count()
            
            if l2_interventions > 0:
                # 检查L2效果
                exercises = db.query(Exercise).filter(
                    user_id=user_id,
                    kp_id=kp_id
                ).order_by(desc(created_at)).limit(5).all()
                
                if exercises:
                    correct_rate = sum(1 for e in exercises if e.is_correct) / len(exercises)
                    
                    # [v7.0核心逻辑] L2无效 + 进度停滞 → 自动触发L3
                    if correct_rate < self.L2_INEFFECTIVE_THRESHOLD:
                        self._trigger_l3_intervention(user_id, kp_id, duration_ratio, correct_rate)
                        return True
        
        return False
    
    def _trigger_l3_intervention(self, user_id, kp_id, duration_ratio, correct_rate):
        """
        [v7.0新增] 触发L3级人类介入
        """
        user = db.query(User).get(user_id)
        kp = db.query(KnowledgePoint).get(kp_id)
        
        # 创建L3干预记录
        intervention = Intervention(
            user_id=user_id,
            kp_id=kp_id,
            level="L3",
            trigger_reason="progress_stagnation_auto",  # [v7.0新增] 自动触发
            trigger_data={
                "duration_ratio": duration_ratio,
                "correct_rate": correct_rate,
                "description": f"停留时长{duration_ratio:.1f}倍，练习正确率{correct_rate:.0%}"
            },
            created_at=datetime.now(),
            status="pending"
        )
        db.save(intervention)
        
        # [v7.0新增] 发送红色预警至教师端
        alert = TeacherAlert(
            type="learning_deadloop",
            priority="high",
            user_id=user_id,
            kp_id=kp_id,
            title=f"🔴 红色预警：{user.name}陷入学习死循环",
            message=f"""
            学生：{user.name}
            知识点：{kp.name}
            停留时长：{duration_ratio:.1f}倍视频时长
            L2干预已触发，但练习正确率仍为{correct_rate:.0%}
            建议立即介入
            """,
            actions=[
                {"label": "1对1连线", "action": "video_call"},
                {"label": "推荐同伴", "action": "peer_help"},
                {"label": "创建辅导", "action": "create_tutoring"}
            ]
        )
        alert_service.send(alert)
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

---

## 3.4 模块D：教师端赋能工具（v6.0升级 + v7.0决策支持）

### 3.4.1 模块目标
从"被动审核员"转变为"主动教练"，**[v7.0新增] 从数据看板升级为趋势预测+策略推荐的决策支持系统**。

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
        # 获取当前学习数据
        current_progress = self._get_class_progress(class_id, course_id)
        
        # 获取所有知识点
        all_kps = db.query(KnowledgePoint).filter(
            course_id=course_id
        ).all()
        
        predictions = []
        
        for kp in all_kps:
            # 跳过已完成的知识点
            if kp.id in current_progress.completed_kps:
                continue
            
            # [v7.0核心逻辑] 预测困难率
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
        
        # 按预测困难率排序
        predictions.sort(key=lambda x: x["predicted_difficulty_rate"], reverse=True)
        
        return predictions
    
    def _predict_difficulty_rate(self, kp, current_progress, class_id):
        """
        预测困难率
        """
        # 因素1：前置知识点掌握情况
        prerequisite_score = self._analyze_prerequisite_mastery(kp, current_progress)
        
        # 因素2：知识点复杂度（认知负荷）
        complexity_score = self._calculate_complexity(kp)
        
        # 因素3：历史数据（其他班级）
        historical_difficulty = self._get_historical_difficulty(kp.id)
        
        # 加权计算
        predicted_rate = (
            0.4 * (1 - prerequisite_score) +  # 前置掌握率低 → 困难率高
            0.3 * complexity_score +          # 复杂度高 → 困难率高
            0.3 * historical_difficulty       # 历史困难率高 → 预测困难率高
        )
        
        return predicted_rate
    
    def generate_teaching_strategies(self, predictions, class_id):
        """
        [v7.0新增] 生成教学策略建议
        """
        strategies = []
        
        for pred in predictions[:3]:  # 取前3个预测难点
            kp = db.query(KnowledgePoint).get(pred["kp_id"])
            
            strategy = {
                "target_kp": kp.name,
                "predicted_difficulty": f"{pred['predicted_difficulty_rate']:.0%}",
                "recommendations": []
            }
            
            # [v7.0核心逻辑] 根据预测依据生成建议
            basis = pred["prediction_basis"]
            
            # 建议1：前置知识补强
            if "prerequisite_weak" in basis:
                weak_kp_name = basis["prerequisite_weak"]["name"]
                weak_kp_rate = basis["prerequisite_weak"]["mastery_rate"]
                strategy["recommendations"].append({
                    "type": "prerequisite_review",
                    "icon": "✓",
                    "text": f"建议补充{weak_kp_name}的复习材料（当前掌握率{weak_kp_rate:.0%}）"
                })
            
            # 建议2：实操课重点演示
            if kp.type == "practical" and pred["predicted_difficulty_rate"] >= 0.6:
                # 分析动作偏差数据
                action_analysis = self._analyze_action_deviations(kp.id, class_id)
                if action_analysis:
                    strategy["recommendations"].append({
                        "type": "practical_demo",
                        "icon": "✓",
                        "text": f"建议下周实操课预留15分钟重点演示'{action_analysis['common_error']}'（{action_analysis['error_rate']:.0%}学生存在问题）"
                    })
            
            # 建议3：增加练习题
            if pred["predicted_difficulty_rate"] >= 0.55:
                strategy["recommendations"].append({
                    "type": "add_exercises",
                    "icon": "✓",
                    "text": f"增加3-5道{kp.name}相关的练习题"
                })
            
            # 建议4：认知负荷管理
            if basis.get("high_complexity"):
                strategy["recommendations"].append({
                    "type": "cognitive_load",
                    "icon": "✓",
                    "text": "建议设计综合案例，分步引导学生应用知识"
                })
                strategy["recommendations"].append({
                    "type": "group_discussion",
                    "icon": "✓",
                    "text": "可考虑分组讨论，降低个人认知负荷"
                })
            
            strategies.append(strategy)
        
        return strategies
    
    def _explain_prediction(self, kp, current_progress):
        """
        解释预测依据
        """
        basis = {}
        
        # 检查前置知识掌握情况
        prerequisites = db.query(KnowledgeDependency).filter(
            target_kp_id=kp.id
        ).all()
        
        for prereq in prerequisites:
            source_kp = db.query(KnowledgePoint).get(prereq.source_kp_id)
            mastery_rate = current_progress.kp_mastery_rates.get(source_kp.id, 0)
            
            if mastery_rate < 0.7:  # 掌握率<70%
                basis["prerequisite_weak"] = {
                    "kp_id": source_kp.id,
                    "name": source_kp.name,
                    "mastery_rate": mastery_rate
                }
                break
        
        # 检查知识点复杂度
        if kp.complexity_score > 0.7:
            basis["high_complexity"] = True
        
        return basis
```

#### D2.3 **[v7.0优化] 动作偏差统计与建议**

```python
def generate_action_deviation_report(course_id, class_id):
    """
    [v7.0优化] 生成动作偏差统计报告
    """
    practical_kps = db.query(KnowledgePoint).filter(
        course_id=course_id,
        type="practical"
    ).all()
    
    report = []
    
    for kp in practical_kps:
        # 获取动作评分数据
        scores = db.query(ActionScore).filter(
            kp_id=kp.id,
            user_id.in_(get_class_students(class_id))
        ).all()
        
        if not scores:
            continue
        
        avg_score = sum(s.score for s in scores) / len(scores)
        
        # 分析常见问题
        common_errors = {}
        for score in scores:
            if score.deviation_details:
                for error_type, deviation in score.deviation_details.items():
                    if abs(deviation) > 0.1:  # 偏差>10%
                        common_errors[error_type] = common_errors.get(error_type, 0) + 1
        
        # 计算问题占比
        error_stats = {}
        for error_type, count in common_errors.items():
            error_rate = count / len(scores)
            if error_rate >= 0.25:  # 25%以上学生存在此问题
                error_stats[error_type] = {
                    "count": count,
                    "rate": error_rate,
                    "description": _translate_error_type(error_type)
                }
        
        if error_stats:
            # [v7.0新增] 生成建议
            main_error = max(error_stats.items(), key=lambda x: x[1]["rate"])
            
            report.append({
                "kp_name": kp.name,
                "avg_score": avg_score,
                "common_errors": error_stats,
                "recommendation": f"建议线下重点演示：{main_error[1]['description']}"
            })
    
    return report
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

### 3.4.3 输出
- 班级学情大屏（Web界面）
- 学生个体学习报告（PDF导出）
- **[v7.0新增] 趋势预测报告（JSON/PDF）**
- **[v7.0新增] 教学策略建议（结构化数据）**
- 动作偏差分析报告

### 3.4.4 验收标准
- ✅ 教师能查看全班共同盲点图表
- ✅ 支持L3级预警实时推送
- ✅ Coach Mode响应延迟 < 2秒
- ✅ 资源审核界面友好，支持在线编辑
- ✅ **[v7.0新增] 趋势预测准确率 ≥ 70%**
- ✅ **[v7.0新增] 策略建议具体可执行，教师满意度 ≥ 80%**
- ✅ **[v7.0新增] 动作偏差报告自动生成，包含具体改进建议**

---

# 4. 逻辑漏洞修复方案（v6.0 + v7.0容错增强）

本章节详细说明从v4.0到v7.0版本的逻辑漏洞修复方案。

## 4.1 行为归因的"排他性"逻辑修复（v6.0）+ **[v7.0容错增强]**

### 4.1.1 问题描述
**v4.0漏洞**：停留时长过长统一判定为"疑难"，可能是走神或临时离开
**v6.0修复**：引入多模态交叉验证
**[v7.0增强]**：低置信度时人工确认兜底

### 4.1.2 修复方案

**v6.0：多模态交叉验证**
```python
def classify_pause_behavior(pause_duration, gaze_on_screen, has_micro_operation, body_present):
    """
    v6.0分类暂停行为
    """
    if pause_duration > T1:
        # 交叉验证
        if not gaze_on_screen and not has_micro_operation and not body_present:
            return "off_task"  # 非学习状态
        elif gaze_on_screen and has_micro_operation:
            return "deep_thinking"  # 深度思考
        else:
            return "difficulty"  # 学习困难
    return "normal"
```

**[v7.0增强]：置信度门控 + 人工确认**
```python
def classify_pause_behavior_v7(pause_duration, multimodal_signals):
    """
    v7.0分类暂停行为（含置信度检查）
    """
    if pause_duration > get_personal_threshold(user_id):  # [v7.0] 个性化阈值
        # [v7.0新增] 计算整体置信度
        overall_confidence = calculate_overall_confidence(multimodal_signals)
        
        # [v7.0新增] 低置信度兜底
        if overall_confidence < 0.6:
            return {
                "state": "uncertain",
                "requires_confirmation": True,
                "prompt": "检测到环境受限，您是否遇到了学习困难？"
            }
        
        # 高置信度 - 正常分类逻辑
        if not multimodal_signals.gaze_on_screen and not multimodal_signals.has_micro_operation:
            return {"state": "off_task", "confidence": overall_confidence}
        elif multimodal_signals.gaze_on_screen and multimodal_signals.has_micro_operation:
            return {"state": "deep_thinking", "confidence": overall_confidence}
        else:
            return {"state": "difficulty", "confidence": overall_confidence}
    
    return {"state": "normal"}
```

## 4.2 补偿资源的"生成-反馈"负反馈闭环修复（v6.0）+ **[v7.0细化优化]**

### 4.2.1 问题描述
**v4.0漏洞**：AI生成补偿资源 → 直接推送，缺少质量校验
**v6.0修复**：实时反馈机制，连续负反馈自动下架
**[v7.0优化]**：细化反馈维度，灰度复核流程

### 4.2.2 **[v7.0优化]** 方案

详见第3.3.2节"资源评价细化机制"和"修正资源灰度复核机制"。

**核心升级**：
- 负面反馈从"无帮助"单一选项细化为4个维度
- 教师修正后的资源经过灰度验证再正式上线
- 防止反复推送低质量资源

## 4.3 知识点时间戳的"动态修正"逻辑修复（v6.0）

### 4.3.1 问题描述
**v4.0漏洞**：静态时间戳，职教视频"操作与讲解异步"导致不准确

### 4.3.2 修复方案

**用户行为辅助修正**：
```python
class TimestampCorrectionService:
    """
    时间戳动态修正服务
    """
    
    def record_actual_position(self, kp_id, user_id, clicked_position, actual_position):
        """
        记录用户点击知识点后实际定位到的位置
        """
        record = UserSeekBehavior(
            kp_id=kp_id,
            user_id=user_id,
            expected_position=clicked_position,
            actual_position=actual_position,
            deviation=actual_position - clicked_position,
            created_at=datetime.now()
        )
        db.save(record)
        
        # 检查是否需要修正
        self._check_correction(kp_id)
    
    def _check_correction(self, kp_id):
        """检查是否触发时间戳修正"""
        behaviors = db.query(UserSeekBehavior).filter(kp_id=kp_id).all()
        
        if len(behaviors) < 10:  # 最小样本数
            return
        
        # 统计偏离比例
        deviation_users = [b for b in behaviors if abs(b.deviation) > 5]
        deviation_ratio = len(deviation_users) / len(behaviors)
        
        if deviation_ratio >= 0.3:  # 30%用户偏离
            # 计算新的时间戳（中位数法）
            new_start = self._calculate_median_position(behaviors, "actual_position")
            self._update_timestamp(kp_id, new_start)
```

---

# 5. 职教特色增强设计（v6.0 + v7.0容错）

## 5.1 高危场景"安全熔断"机制（v6.0新增）+ **[v7.0容错增强]**

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
        
        # [v7.0新增] 检查检测置信度
        if ppe_result.confidence < self.PPE_CONFIDENCE_THRESHOLD:
            # 置信度不足 - 人工确认
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
        missing_ppe = []
        for ppe in required_ppe:
            if not ppe_result.has(ppe, confidence_threshold=self.PPE_CONFIDENCE_THRESHOLD):
                missing_ppe.append(ppe)
        
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

### 5.1.3 强制中断逻辑

**触发条件**（仅高置信度违规）：
1. PPE检测置信度 ≥ 0.85
2. 明确检测到未佩戴必需PPE
3. 或检测到明确的违规动作

**中断响应**：
- 立即挂起当前视频
- 强制弹出"安全规范确认"
- 或播放"事故案例回顾"
- 通过后方可继续

## 5.2 基于DTW的动作评分（v6.0新增）

### 5.2.1 技术方案

```python
class ActionScoringService:
    """
    动作评分服务
    """
    
    def score_action(self, user_action_video, standard_action_id):
        """
        对学生动作进行评分
        """
        # 提取动作轨迹（SlowFast）
        user_trajectory = self.slowfast_extractor.extract(user_action_video)
        
        # 加载标准动作
        standard_action = db.query(StandardAction).get(standard_action_id)
        standard_trajectory = standard_action.trajectory
        
        # DTW动态时间规整
        distance, path = fastdtw(user_trajectory, standard_trajectory)
        
        # 计算综合得分（越小越好，归一化到0-1）
        overall_score = 1 / (1 + distance / 100)
        
        # 详细偏差分析
        deviations = self._analyze_deviations(user_trajectory, standard_trajectory, path)
        
        return ActionScoreResult(
            overall_score=overall_score,
            speed_deviation=deviations["speed"],
            angle_deviation=deviations["angle"],
            sequence_correct=deviations["sequence_correct"],
            deviation_report={
                "speed": f"{'偏快' if deviations['speed'] > 0 else '偏慢'}{abs(deviations['speed']):.0%}",
                "angle": f"偏离{deviations['angle']:.1f}°",
                "recommendations": self._generate_recommendations(deviations)
            }
        )
```

## 5.3 虚实结合：手册联动（v6.0新增）

### 5.3.1 功能描述

当学生观看某个操作动作时：
- 侧边栏自动高亮显示手册中对应的"安全规范"
- 显示"参数配置"表格
- 显示"工具清单"

### 5.3.2 实现逻辑

```python
def get_manual_highlight(kp_id):
    """
    获取手册高亮内容
    """
    kp = db.query(KnowledgePoint).get(kp_id)
    
    # 查询关联的手册章节
    manual_section = db.query(ManualSection).filter(kp_id=kp_id).first()
    
    if manual_section:
        return {
            "section_id": manual_section.id,
            "page_number": manual_section.page_number,
            "safety_regulations": [
                reg.content for reg in manual_section.safety_regulations
            ],
            "parameters": manual_section.parameters_table,
            "tools": manual_section.tools_list
        }
    
    return None
```

---

# 6. 干预机制分层化设计（v6.0 + v7.0优化）

干预机制已在第3.3.4节详细说明，此处总结核心设计原则：

## 6.1 分层原则

| 等级 | 触发条件 | 干预形式 | 资源类型 | **[v7.0优化]** |
|------|---------|---------|---------|----------------|
| L1 | 首次困难 | 轻量提醒 | 知识卡片 | 细化反馈 |
| L2 | 二次困难 | 交互修复 | 微视频+练习 | 上下文保留 |
| L3 | 持续停滞 | 人类介入 | 1对1/同伴 | **自动触发** |

## 6.2 **[v7.0核心升级]**：L3自动触发机制

**v6.0局限**：仅依赖学生主动点击"求助"
**v7.0升级**：系统自动检测进度停滞并触发L3

**触发条件**：
1. 累计停留时长 ≥ 5倍视频时长
2. L2干预已触发
3. 练习正确率 < 50%

**响应机制**：
- 自动向教师端发送红色预警
- 提供1对1连线、同伴推荐等快速响应选项

## 6.3 认知负荷监测与干预频率控制（v6.0 + v7.0个性化）

**v6.0逻辑**：统一的T1/T2阈值
**[v7.0优化]**：基于个人认知步频的动态阈值

**干预频率控制**：
- 30分钟内触发≥3次补偿 → 认知过载预警
- 暂停新知识推送
- 引导休息或回顾基础知识

---

# 7. 系统架构与技术方案

## 7.1 整体架构（v6.0升级 + v7.0增强）

```
┌─────────────────────────────────────────────────────────┐
│                      前端层（Frontend）                  │
│  Vue.js 3 + Element Plus + Pinia                        │
│  - 学生端：视频播放 + 多模态采集 + 补偿资源展示         │
│  - 教师端：Coach Mode + 趋势预测 + 策略推荐 [v7.0]      │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    API网关层（Gateway）                  │
│  Kong / Nginx + WebSocket支持                           │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   业务服务层（Backend）                  │
│  FastAPI + SQLAlchemy                                   │
│  - 视频服务、用户服务、学习记录服务                      │
│  - 资源推送服务、干预管理服务                           │
│  - [v7.0] 趋势预测服务、策略推荐服务                     │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    AI引擎层（AI Engine）                 │
│  - 视频解析引擎：ASR + OCR + CV                          │
│  - 认知状态检测引擎 [v7.0置信度输出]                     │
│  - 知识图谱引擎（GNN）[v7.0数据驱动优化]                 │
│  - 资源生成引擎 [v7.0上下文保留]                        │
│  - [v7.0] 趋势预测引擎                                  │
└─────────────────────────────────────────────────────────┘
                           ▼
┌──────────────┬──────────────┬──────────────┬────────────┐
│ PostgreSQL   │ Redis        │ Neo4j        │ RabbitMQ   │
│ (关系数据)   │ (缓存/会话)  │ (知识图谱)   │ (消息队列) │
└──────────────┴──────────────┴──────────────┴────────────┘
```

## 7.2 核心技术栈

### 7.2.1 前端技术栈
- **框架**：Vue.js 3 + TypeScript
- **UI库**：Element Plus
- **状态管理**：Pinia
- **视频播放**：Video.js / DPlayer
- **图表**：ECharts
- **多模态采集**：
  - WebGazer.js（视线追踪）
  - face-api.js（微表情识别）
  - 原生Web API（鼠标、键盘事件）

### 7.2.2 后端技术栈
- **框架**：FastAPI（Python 3.9+）
- **ORM**：SQLAlchemy
- **数据库**：
  - PostgreSQL 13+（主数据库）
  - Redis 6+（缓存、会话）
  - Neo4j 4+（知识图谱）
- **消息队列**：RabbitMQ
- **实时通信**：WebSocket

### 7.2.3 AI技术栈
- **ASR**：Whisper / 讯飞开放平台
- **OCR**：PaddleOCR
- **CV**：YOLOv8（PPE检测）
- **动作识别**：SlowFast
- **动作匹配**：fastdtw
- **语义理解**：BERT-base-Chinese
- **语气分析**：Wav2Vec 2.0
- **GNN**：PyTorch Geometric
- **视频生成**：MoviePy（剪辑）+ TTS（旁白）
- **[v7.0新增] 趋势预测**：scikit-learn / LightGBM

## 7.3 关键组件设计

### 7.3.1 **[v7.0增强]** 认知状态检测服务

```python
class CognitiveStateDetectorServiceV7:
    """
    v7.0认知状态检测服务
    """
    
    def __init__(self):
        self.gaze_tracker = GazeTracker()
        self.expression_analyzer = FacialExpressionAnalyzer()
        self.pace_calculator = CognitivePaceCalculator()  # [v7.0新增]
    
    def detect(self, user_id, multimodal_signals):
        """
        检测认知状态
        """
        # [v7.0新增] 计算整体置信度
        overall_confidence = self._calculate_confidence(multimodal_signals)
        
        # [v7.0新增] 低置信度兜底
        if overall_confidence < 0.6:
            return self._handle_low_confidence(multimodal_signals)
        
        # [v7.0新增] 获取个人认知基准
        baseline = self.pace_calculator.get_baseline(user_id)
        
        # 认知状态分类
        state = self._classify_state(multimodal_signals, baseline)
        
        return CognitiveStateResult(
            state=state,
            confidence=overall_confidence,
            baseline_info=baseline
        )
```

### 7.3.2 **[v7.0新增]** 趋势预测服务

```python
class TrendPredictionService:
    """
    趋势预测服务
    """
    
    def __init__(self):
        self.model = self._load_prediction_model()
        self.feature_extractor = FeatureExtractor()
    
    def predict_difficulties(self, course_id, class_id):
        """
        预测未来难点
        """
        # 提取特征
        features = self.feature_extractor.extract(course_id, class_id)
        
        # 模型预测
        predictions = self.model.predict(features)
        
        # 生成策略建议
        strategies = self.strategy_advisor.generate(predictions)
        
        return {
            "predictions": predictions,
            "strategies": strategies
        }
```

---

# 8. 数据模型设计（v6.0 + v7.0扩展）

## 8.1 核心数据表

### 8.1.1 用户表 (User)
```sql
CREATE TABLE user (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8.1.2 视频表 (Video)
```sql
CREATE TABLE video (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    duration INT NOT NULL,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user(id)
);
```

### 8.1.3 知识点表 (KnowledgePoint)
```sql
CREATE TABLE knowledge_point (
    id VARCHAR(50) PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    keywords JSON,
    summary TEXT,
    difficulty_level ENUM('basic', 'intermediate', 'advanced'),
    is_exam_key BOOLEAN DEFAULT FALSE,                -- v6.0：考核重点
    timestamp_corrected BOOLEAN DEFAULT FALSE,         -- v6.0：时间戳已修正
    correction_count INT DEFAULT 0,                    -- v6.0：修正次数
    dependency_weight_map JSON,                        -- [v7.0新增]：依赖权重映射
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES video(id)
);
```

### 8.1.4 认知状态事件表 (CognitiveStateEvent) - v6.0新增
```sql
CREATE TABLE cognitive_state_event (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    video_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pause_duration FLOAT,
    gaze_on_screen BOOLEAN,
    facial_expression VARCHAR(50),
    expression_confidence FLOAT,                       -- [v7.0新增]：表情置信度
    has_micro_operation BOOLEAN,
    body_present BOOLEAN,
    cognitive_state ENUM('deep_thinking', 'difficulty', 'off_task', 'uncertain'),  -- [v7.0新增] uncertain
    confidence FLOAT,                                  -- [v7.0新增]：整体置信度
    requires_confirmation BOOLEAN DEFAULT FALSE,       -- [v7.0新增]：需要人工确认
    user_confirmation VARCHAR(50),                     -- [v7.0新增]：用户确认结果
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id)
);
```

### 8.1.5 **[v7.0新增]** 个人认知步频表 (CognitivePace)
```sql
CREATE TABLE cognitive_pace (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    baseline_duration FLOAT NOT NULL,                  -- 平均停留时长（分钟）
    baseline_response_time FLOAT NOT NULL,             -- 平均响应时间（秒）
    pace_type ENUM('fast', 'medium', 'slow') NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 8.1.6 资源反馈表 (ResourceFeedback) - **[v7.0扩展]**
```sql
CREATE TABLE resource_feedback (
    id VARCHAR(50) PRIMARY KEY,
    resource_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    negative_reason ENUM('too_hard', 'too_verbose', 'format_issue', 'content_mismatch'),  -- [v7.0新增]
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resource(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    INDEX idx_resource_feedback (resource_id, created_at)
);
```

### 8.1.7 **[v7.0新增]** 灰度测试反馈表 (TestingFeedback)
```sql
CREATE TABLE testing_feedback (
    id VARCHAR(50) PRIMARY KEY,
    resource_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resource(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 8.1.8 资源表 (Resource) - **[v7.0扩展]**
```sql
CREATE TABLE resource (
    id VARCHAR(50) PRIMARY KEY,
    kp_id VARCHAR(50) NOT NULL,
    type ENUM('knowledge_card', 'micro_video', 'exercise', 'knowledge_tip') NOT NULL,
    content_url VARCHAR(500),
    duration INT,
    status ENUM('active', 'removed_auto', 'testing', 'testing_failed') NOT NULL,  -- [v7.0扩展]
    removed_reason TEXT,
    testing_started_at TIMESTAMP,                      -- [v7.0新增]
    testing_target_count INT,                          -- [v7.0新增]
    testing_feedback_count INT DEFAULT 0,              -- [v7.0新增]
    approved_at TIMESTAMP,                             -- [v7.0新增]
    revised_by VARCHAR(50),                            -- [v7.0新增]
    has_context BOOLEAN DEFAULT FALSE,                 -- [v7.0新增]：是否保留上下文
    context_info JSON,                                 -- [v7.0新增]：上下文信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    FOREIGN KEY (revised_by) REFERENCES user(id)
);
```

### 8.1.9 干预记录表 (Intervention) - **[v7.0扩展]**
```sql
CREATE TABLE intervention (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    kp_id VARCHAR(50) NOT NULL,
    level ENUM('L1', 'L2', 'L3') NOT NULL,
    trigger_reason VARCHAR(100) NOT NULL,
    trigger_data JSON,                                 -- [v7.0新增]：触发详细数据
    status ENUM('pending', 'in_progress', 'resolved') DEFAULT 'pending',
    resource_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    FOREIGN KEY (resource_id) REFERENCES resource(id)
);
```

### 8.1.10 **[v7.0新增]** 教师预警表 (TeacherAlert)
```sql
CREATE TABLE teacher_alert (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,                         -- learning_deadloop, resource_removed等
    priority ENUM('low', 'medium', 'high') NOT NULL,
    user_id VARCHAR(50),
    kp_id VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    actions JSON,                                      -- 可执行操作列表
    status ENUM('pending', 'read', 'handled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    handled_at TIMESTAMP,
    handled_by VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(id),
    FOREIGN KEY (handled_by) REFERENCES user(id)
);
```

---

# 9. 接口设计（v7.0扩展）

## 9.1 **[v7.0新增]** 认知状态相关接口（含置信度）

### 9.1.1 上报多模态认知信号
- **接口**: `POST /api/v7/cognitive-state/signals`
- **描述**: 前端实时上报多模态认知信号（v7.0含置信度）
- **请求参数**:
```json
{
  "user_id": "U001",
  "video_id": "V001",
  "kp_id": "K3",
  "timestamp": "2026-01-28T10:30:00Z",
  "signals": {
    "gaze_on_screen": true,
    "gaze_confidence": 0.75,
    "facial_expression": "confused",
    "expression_confidence": 0.88,
    "has_micro_operation": true,
    "body_present": true,
    "pause_duration": 8.5
  }
}
```
- **响应**:
```json
{
  "code": 200,
  "data": {
    "cognitive_state": "difficulty",
    "confidence": 0.82,
    "requires_confirmation": false,
    "intervention": {
      "required": true,
      "level": "L1",
      "resource_id": "R001"
    }
  }
}
```

### 9.1.2 **[v7.0新增]** 用户确认接口
- **接口**: `POST /api/v7/cognitive-state/confirm`
- **描述**: 低置信度时用户手动确认
- **请求参数**:
```json
{
  "event_id": "CSE001",
  "user_confirmation": "need_help"  // "need_help" | "just_thinking"
}
```

### 9.1.3 获取个人认知步频
- **接口**: `GET /api/v7/cognitive-pace/{user_id}`
- **描述**: 获取学生的个人认知基准线
- **响应**:
```json
{
  "code": 200,
  "data": {
    "baseline_duration": 2.3,
    "baseline_response_time": 15.2,
    "pace_type": "medium",
    "personal_threshold": 3.45,
    "calculated_at": "2026-01-28T09:00:00Z"
  }
}
```

## 9.2 **[v7.0新增]** 资源反馈相关接口

### 9.2.1 提交细化反馈
- **接口**: `POST /api/v7/resource/feedback`
- **描述**: 提交资源反馈（细化维度）
- **请求参数**:
```json
{
  "resource_id": "R001",
  "user_id": "U001",
  "is_helpful": false,
  "negative_reason": "too_verbose",  // too_hard | too_verbose | format_issue | content_mismatch
  "feedback_text": "讲解过于冗长"
}
```

### 9.2.2 查看资源反馈统计
- **接口**: `GET /api/v7/resource/{resource_id}/feedback-stats`
- **描述**: 教师查看资源反馈统计
- **响应**:
```json
{
  "code": 200,
  "data": {
    "resource_id": "R001",
    "total_feedbacks": 10,
    "helpful_count": 4,
    "negative_distribution": {
      "too_verbose": 3,
      "too_hard": 2,
      "content_mismatch": 1
    },
    "status": "removed_auto",
    "main_issue": "too_verbose"
  }
}
```

### 9.2.3 **[v7.0新增]** 灰度测试接口
- **接口**: `POST /api/v7/resource/{resource_id}/republish`
- **描述**: 教师修正后重新上线资源
- **响应**:
```json
{
  "code": 200,
  "data": {
    "resource_id": "R001",
    "status": "testing",
    "testing_target_count": 5,
    "message": "资源已进入灰度测试阶段"
  }
}
```

## 9.3 **[v7.0新增]** 趋势预测与策略推荐接口

### 9.3.1 获取趋势预测
- **接口**: `GET /api/v7/teaching/trend-prediction`
- **描述**: 获取未来难点预测
- **请求参数**: `course_id`, `class_id`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "predictions": [
      {
        "kp_id": "K8",
        "kp_name": "气门调整",
        "predicted_difficulty_rate": 0.65,
        "current_progress": 0.40,
        "prediction_basis": {
          "prerequisite_weak": {
            "name": "配气机构认知",
            "mastery_rate": 0.60
          }
        }
      }
    ]
  }
}
```

### 9.3.2 获取教学策略建议
- **接口**: `GET /api/v7/teaching/strategy-recommendations`
- **描述**: 获取教学策略建议
- **请求参数**: `course_id`, `class_id`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "strategies": [
      {
        "target_kp": "气门调整",
        "predicted_difficulty": "65%",
        "recommendations": [
          {
            "type": "prerequisite_review",
            "icon": "✓",
            "text": "建议补充配气机构的复习材料（当前掌握率60%）"
          },
          {
            "type": "practical_demo",
            "icon": "✓",
            "text": "建议下周实操课预留15分钟重点演示'气门间隙测量工具'的使用"
          }
        ]
      }
    ]
  }
}
```

## 9.4 安全熔断相关接口（v6.0 + v7.0容错）

### 9.4.1 安全检查
- **接口**: `POST /api/safety/check`
- **描述**: PPE检测与安全检查（v7.0含置信度）
- **请求参数**:
```json
{
  "user_id": "U001",
  "video_id": "V001",
  "frame_data": "base64_encoded_image",
  "operation_type": "welding"
}
```
- **响应**:
```json
{
  "code": 200,
  "data": {
    "is_safe": "uncertain",
    "confidence": 0.55,
    "requires_confirmation": true,
    "confirmation_prompt": {
      "title": "⚠️ 安全装备确认",
      "message": "环境光线不足，无法确认防护装备佩戴情况。",
      "checklist": ["护目镜", "防护手套", "工作服"]
    }
  }
}
```

---

# 10. 用户界面设计（v7.0优化）

## 10.1 学生端界面

### 10.1.1 视频学习主界面

**布局**：
```
┌─────────────────────────────────────────────────┐
│ 【导航栏】课程名称 | 进度 | 个人中心            │
├───────────────────────────┬─────────────────────┤
│                           │ 【侧边栏】          │
│  【视频播放区】           │  - 知识点列表        │
│                           │  - 当前知识点信息    │
│  [视频控制条]             │  - 安全规范[v6.0]   │
│                           │  - [v7.0]个人节奏    │
├───────────────────────────┼─────────────────────┤
│ 【补偿资源区】            │ 【学习笔记区】      │
│  [L1] 知识卡片            │  - 可编辑笔记        │
│  [L2] 精准微视频          │  - 重点标记         │
└───────────────────────────┴─────────────────────┘
```

### 10.1.2 **[v7.0新增]** 人工确认弹窗

**低置信度确认弹窗**：
```
┌────────────────────────────────────┐
│  ⚠️ 环境检测受限                   │
├────────────────────────────────────┤
│  检测到光线不足或面部遮挡，        │
│  无法准确判断您的学习状态。        │
│                                    │
│  您是否在理解这个知识点时遇到了    │
│  困难？                            │
│                                    │
│  [是，需要帮助]  [否，我在思考]   │
└────────────────────────────────────┘
```

### 10.1.3 **[v7.0优化]** 资源反馈组件

```
┌─────────────────────────────────────────┐
│  【补偿资源】曲轴拆卸 - 精准微视频     │
│  [视频内容]                            │
│                                        │
│  这个资源对你有帮助吗？                │
│  [👍 有帮助]                           │
│  [👎 太难了]                           │
│  [👎 讲解啰嗦]                         │
│  [👎 格式不喜欢]                       │
│  [👎 内容不符]                         │
└─────────────────────────────────────────┘
```

## 10.2 教师端界面

### 10.2.1 班级学情大屏

**布局**：
```
┌────────────────────────────────────────────────────────┐
│  【课程】汽修-发动机拆装 | 【班级】2024级汽修1班       │
├────────────────────────────────────────────────────────┤
│  【全班共同盲点图表】[v6.0]                            │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐                          │
│  │K3│K5│K7│K2│K10│...                                 │
│  │65%│58%│52%│48%│45%│...  (困难率)                  │
│  └──┴──┴──┴──┴──┴──┴──┴──┘                          │
├────────────────────────────────────────────────────────┤
│  【[v7.0新增] 趋势预测】                               │
│  📈 未来一周预测                                       │
│  1. K8 气门调整（预测困难率：65%）                    │
│     - 当前进度：40%学生已学习                          │
│     - 预测依据：前置知识K6掌握率偏低（仅60%）         │
│                                                        │
│  💡 教学策略建议                                       │
│  针对 K8 气门调整：                                    │
│  ✓ 建议下周实操课预留15分钟重点演示                    │
│  ✓ 补充K6前置知识的复习材料                           │
│  ✓ 增加3-5道K8相关的练习题                            │
├────────────────────────────────────────────────────────┤
│  【动作偏差统计】[v6.0 + v7.0优化]                    │
│  K3 曲轴拆卸动作评分：                                 │
│  - 平均得分：0.78                                      │
│  - 常见问题：                                          │
│    * 40%学生工具握持角度偏离（建议加强示范）          │
│    * 25%学生拆卸速度偏快（建议强调安全第一）          │
│                                                        │
│  → 建议线下重点演示：工具正确握持姿势                  │
└────────────────────────────────────────────────────────┘
```

### 10.2.2 **[v7.0新增]** L3级预警弹窗

```
┌─────────────────────────────────────────────┐
│  🔴 红色预警：学生陷入学习死循环            │
├─────────────────────────────────────────────┤
│  学生：李明                                 │
│  知识点：K3 曲轴拆卸                        │
│  停留时长：45分钟（视频时长5.6倍）          │
│  L2干预已触发，但练习正确率仍为40%          │
│                                             │
│  建议立即介入                               │
│                                             │
│  [1对1连线] [推荐同伴] [创建辅导]          │
└─────────────────────────────────────────────┘
```

### 10.2.3 资源审核界面（v6.0 + v7.0反馈增强）

```
┌──────────────────────────────────────────────────┐
│  【资源审核】R001 - 曲轴拆卸补偿视频             │
├──────────────────────────────────────────────────┤
│  状态：已自动下架                                │
│  下架原因：连续负反馈（主因：讲解啰嗦）          │
│                                                  │
│  【[v7.0新增] 反馈统计】                         │
│  总反馈数：10                                    │
│  负面反馈分布：                                  │
│  - 讲解啰嗦：5次 (50%)                          │
│  - 内容太难：3次 (30%)                          │
│  - 格式不喜欢：2次 (20%)                        │
│                                                  │
│  【修正建议】                                    │
│  - 缩短视频至60秒，去除冗余讲解                  │
│  - 突出关键步骤                                  │
│                                                  │
│  [在线编辑] [重新上线(灰度测试)]               │
└──────────────────────────────────────────────────┘
```

---

# 11. 非功能性需求（v7.0补充）

## 11.1 性能需求

| 指标 | 要求 | **[v7.0补充]** |
|------|------|----------------|
| 认知状态检测延迟 | ≤ 2秒 | 含置信度计算 |
| 补偿资源推送延迟 | ≤ 5分钟 | 高置信度触发 |
| 视频播放启动时间 | ≤ 3秒 | - |
| 安全检测响应时间 | ≤ 1秒 | 含置信度判定 |
| 趋势预测生成时间 | ≤ 10秒 | [v7.0新增] |
| 并发用户数 | ≥ 1000 | - |

## 11.2 可用性需求

- 系统可用性：≥ 99.5%
- 数据备份：每日自动备份
- 灾难恢复：RTO ≤ 4小时，RPO ≤ 1小时

## 11.3 安全性需求

- 用户认证：JWT Token
- 数据传输：HTTPS/WSS加密
- 隐私保护：
  - 摄像头/麦克风需用户明确授权
  - 多模态数据加密存储
  - **[v7.0补充]** 低置信度数据不长期保存

## 11.4 可扩展性需求

- 水平扩展：支持服务器集群部署
- 模块化设计：AI引擎可独立升级
- **[v7.0补充]** 预测模型可热更新

---

# 12. 测试与验收标准（v7.0扩展）

## 12.1 功能测试

### 12.1.1 认知状态检测测试（v7.0升级）

| 测试场景 | 输入 | 预期输出 | v7.0验收标准 |
|---------|------|---------|-------------|
| 正常深度思考 | 视线在屏幕+专注表情+鼠标悬停 | 状态：deep_thinking | 置信度≥0.7 |
| 困难卡顿 | 视线在屏幕+困惑表情+回放 | 状态：difficulty，触发L1 | 置信度≥0.7 |
| **[v7.0]光线不足** | 表情置信度0.5+视线置信度0.4 | 状态：uncertain，弹出确认 | 正确弹窗 |
| **[v7.0]用户确认需帮助** | 低置信度+用户确认"need_help" | 触发L1干预 | 成功推送资源 |

### 12.1.2 资源反馈测试（v7.0新增）

| 测试场景 | 输入 | 预期输出 |
|---------|------|---------|
| 连续3个"讲解啰嗦" | 学生A/B/C标记"too_verbose" | 自动下架，通知教师，显示"主因：讲解啰嗦" |
| 灰度测试通过 | 5个学生测试，3个"有帮助" | 资源状态→active，正式上线 |
| 灰度测试失败 | 5个学生测试，2个"有帮助" | 资源状态→testing_failed，通知教师继续修正 |

### 12.1.3 L3自动触发测试（v7.0新增）

| 测试场景 | 输入 | 预期输出 |
|---------|------|---------|
| 进度停滞 | 停留45分钟（5.6倍），L2已触发，正确率40% | 自动触发L3，教师端收到红色预警 |
| 预警内容 | - | 显示学生姓名、知识点、停留时长、正确率 |
| 教师响应 | 点击"1对1连线" | 成功建立连线 |

### 12.1.4 趋势预测测试（v7.0新增）

| 测试场景 | 输入 | 预期输出 |
|---------|------|---------|
| 预测准确性 | 历史数据 | 预测准确率≥70% |
| 策略生成 | 预测困难率65% | 生成≥3条具体可执行建议 |

## 12.2 性能测试

- 并发1000用户视频播放：响应时间≤3秒
- 认知状态检测：延迟≤2秒
- 补偿资源推送：延迟≤5分钟
- **[v7.0新增]** 趋势预测：生成时间≤10秒

## 12.3 集成测试

- 完整学习流程：观看→检测→干预→反馈→修正
- **[v7.0新增]** 低置信度流程：检测→人工确认→干预
- **[v7.0新增]** L3自动触发流程：停滞→检测→预警→教师响应

---

# 13. 项目里程碑与任务规划（v7.0调整）

## 13.1 阶段划分

### 阶段1：基础框架搭建（2周）
- 前后端基础架构
- 数据库设计与部署
- 用户认证与视频播放

### 阶段2：AI引擎开发（4周）
- 视频解析引擎（ASR/OCR/CV）
- 知识点切分与标注
- **[v7.0]** 认知状态检测（含置信度输出）
- **[v7.0]** 个人认知步频计算

### 阶段3：核心功能开发（6周）
- 多模态行为采集
- **[v7.0]** 低置信度人工确认机制
- 个性化路径生成
- 补偿资源生成
- **[v7.0]** 智能剪辑上下文保留

### 阶段4：职教特色与反馈闭环（4周）
- 安全熔断机制（**v7.0容错增强**）
- 动作评分（DTW）
- **[v7.0]** 资源反馈细化
- **[v7.0]** 灰度复核流程
- **[v7.0]** L3自动触发机制

### 阶段5：教师端与决策支持（3周）
- 班级学情大屏
- **[v7.0新增]** 趋势预测引擎
- **[v7.0新增]** 策略推荐系统
- Coach Mode

### 阶段6：测试与优化（3周）
- 功能测试、性能测试
- **[v7.0]** 容错机制测试
- **[v7.0]** 预测准确率验证
- 用户体验优化

### 阶段7：部署与试运行（2周）
- 生产环境部署
- 汽修课程试点
- 数据收集与反馈

---

# 14. 风险与对策（v7.0补充）

## 14.1 技术风险

| 风险 | 影响 | 概率 | 对策 | **[v7.0补充]** |
|------|------|------|------|----------------|
| 多模态信号采集不稳定 | 高 | 中 | 提供降级方案，仅依赖行为数据 | **置信度门控+人工确认** |
| AI误判率过高 | 高 | 中 | 设置置信度阈值，人工审核 | **低置信度兜底机制** |
| 视频生成质量不佳 | 中 | 高 | 负反馈闭环，教师审核 | **细化反馈+灰度复核** |
| 知识图谱初始偏见 | 中 | 中 | 专家审核，持续优化 | **数据驱动权重修正** |
| 趋势预测不准确 | 中 | 中 | - | **设定70%准确率底线** |

## 14.2 业务风险

| 风险 | 影响 | 概率 | 对策 |
|------|------|------|------|
| 教师接受度低 | 高 | 中 | 强化"辅助而非替代"定位，提供培训 |
| 学生隐私顾虑 | 高 | 中 | 明确告知数据用途，提供关闭选项 |
| 补偿资源推送过度 | 中 | 高 | 认知负荷监测，干预频率控制（**v7.0个性化阈值**） |

## 14.3 项目风险

| 风险 | 影响 | 概率 | 对策 |
|------|------|------|------|
| 开发周期延误 | 高 | 中 | MVP优先，分阶段交付 |
| 团队技术能力不足 | 中 | 低 | 外部技术支持，培训 |
| 数据标注成本高 | 中 | 高 | 利用预训练模型，减少标注需求 |

---

# 15. 附录

## 15.1 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 认知状态 | Cognitive State | 学习者的认知状态（深度思考/困难卡顿/无效停留/不确定） |
| 信号不协和 | Signal Dissonance | v6.0引入的多模态信号交叉验证机制 |
| 溯源诊断 | Root Cause Diagnosis | v6.0引入的前置知识回溯机制 |
| 安全熔断 | Safety Circuit Breaker | v6.0引入的高危场景强制中断机制 |
| **[v7.0]置信度门控** | Confidence Gating | v7.0引入的低置信度人工确认机制 |
| **[v7.0]认知步频** | Cognitive Pace | v7.0引入的个人学习节奏基准线 |
| **[v7.0]灰度复核** | Grayscale Review | v7.0引入的修正资源验证机制 |
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

## 15.3 v7.0更新日志

### 容错增强
1. **低置信度人机协作兜底**：多模态信号置信度<0.6时，弹出轻量确认窗口
2. **PPE检测容错**：环境因素导致检测受限时，人工确认替代强制熔断

### 动态适配
3. **个人认知步频计算**：基于前3个知识点的平均停留时长和响应速度，计算个性化基准线
4. **动态阈值**：废除统一T1/T2，采用个人基准×1.5倍作为异常判定阈值

### 反馈优化
5. **资源评价细化**：从"有帮助/无帮助"扩展为4维度负面反馈
6. **灰度复核流程**：修正资源需经过5名学生验证，好评率≥60%方可正式上线

### 图谱进化
7. **隐性依赖发现**：分析学习数据，自动识别强依赖关系（通过率差异≥20%）
8. **权重修正**：每周批量分析，自动增强GNN图谱依赖权重

### 干预补全
9. **L3自动触发**：停留时长≥5倍视频时长+L2无效 → 自动触发L3，无需学生主动求助
10. **红色预警**：向教师端推送详细的停滞信息与快速响应选项

### 剪辑优化
11. **上下文保留协议**：剪辑范围=[start-5s, end+3s]，防止逻辑断裂

### 决策支持
12. **趋势预测**：基于当前学习曲线预测未来难点，准确率≥70%
13. **策略推荐**：生成具体可执行的教学策略建议

---

## 文档结束

**编写团队**：周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
**技术顾问**：蒋国伟
**指导老师**：王海霞
**版本**：v7.0
**日期**：2026年1月28日

---

本文档共计约15,000字，完整阐述了AI赋能职教视频个性化教学项目从v4.0到v7.0的完整演进路径，重点突出v7.0版本在容错、适配、反馈、预测等方面的核心升级。
