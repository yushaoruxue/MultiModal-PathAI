# AI赋能职教视频个性化教学项目需求规格说明书（第十稿-Final）

## 【Final Release Notes】

- **版本定位**：v10.0（Final Production Ready Version），可直接进入**开发与架构设计**阶段的最终定稿版本。
- **继承关系**：本版本**继承 v9.0 的全部需求与设计**（详见 `AI赋能职教视频个性化教学项目需求规格说明书（第九稿-完整版）.md`），并在此基础上补齐“最终落地”所需的**冲突处理、硬件适配、自动化冷启动、教师策略统一调参、数据审计**五大能力。
- **v10.0 为何必要**：v9.0 已补齐边界异常（弱网、对齐误差、抗震荡、教师主权、螺旋跳出），但在真实职教场景仍会遇到：
  - 人机协作下的**并发写入冲突**（教师手改 vs AI后台更新）
  - 设备老旧下的**算力不足**（前端多模态导致卡顿）
  - 老师忙碌下的**冷启动无人标注**（仅靠专家基准不够）
  - 教师需要“一键调风格”的**干预敏感度统一控制**
  - 恶意反馈/异常数据对资源闭环的**污染风险**

---

## 文档版本信息

- **版本号**: v10.0
- **编写日期**: 2026年1月
- **编写团队**: 周东吴（组长）、成怡、杨雅娟、张亚鹏、雷宇
- **技术顾问**: 蒋国伟
- **指导老师**: 王海霞
- **文档状态**: Final Production Ready
- **版本说明**: 基于v9.0进行终版补齐（冲突处理/硬件适配/自动化冷启动/教师统一调参/数据审计）

---

## 版本演进说明

### v10.0 主要更新内容

| 更新类别 | 更新内容 | 影响模块 | 标记 |
|---------|---------|---------|------|
| 冲突处理 | 专家标注模式写锁（Write Lock）+ 原子化发布/交还AI托管 | 模块A/D | [v10.0 新增] |
| 硬件适配 | 硬件画像驱动三级降级（全量/精简/仅日志） | 模块B | [v10.0 新增] |
| 冷启动自动化 | 跨课原型匹配（Prototype Matching）复用相似课程基准 | 模块A/B | [v10.0 新增] |
| 教师定制 | 教师策略编辑器：干预激进系数（0.1-2.0） | 模块D/C | [v10.0 新增] |
| 数据可信 | 数据审计引擎：异常/恶意反馈过滤与审计回放 | 模块C/D | [v10.0 新增] |

### v9.0 vs v10.0 核心差异

| 维度 | v9.0 | v10.0 |
|------|------|------|
| **人机协作** | 教师可禁用AI，但缺少并发冲突协议 | **写锁+原子发布+交还托管** |
| **硬件适配** | 主要考虑弱网与信号误判 | **加入算力画像与降级矩阵** |
| **冷启动** | 教师专家基准为主 | **跨课原型匹配半自动冷启动** |
| **教师定制** | 侧重“禁用AI/专家标注” | **可统一调节干预敏感度** |
| **数据可信** | 反馈闭环/灰度复核 | **审计引擎过滤恶意差评** |

---

## 目录

1. [继承说明（与v9.0关系）](#1-继承说明与v90关系)
2. [v10.0新增：系统自愈与冲突处理（写锁/原子化）](#2-v100新增系统自愈与冲突处理写锁原子化)
3. [v10.0新增：硬件适配矩阵（设备画像驱动三级降级）](#3-v100新增硬件适配矩阵设备画像驱动三级降级)
4. [v10.0新增：冷启动自动化（跨课原型匹配）](#4-v100新增冷启动自动化跨课原型匹配)
5. [v10.0新增：教师策略编辑器（干预激进系数）](#5-v100新增教师策略编辑器干预激进系数)
6. [v10.0新增：数据审计引擎（异常反馈过滤）](#6-v100新增数据审计引擎异常反馈过滤)
7. [数据模型增量（v10.0）](#7-数据模型增量v100)
8. [接口设计增量（v10.0）](#8-接口设计增量v100)
9. [最终验收补充（v10.0）](#9-最终验收补充v100)
10. [v10.0更新日志](#10-v100更新日志)

---

# 1. 继承说明（与v9.0关系）

本文件为 v10.0 **终极完结版增量补丁**：

- **基础需求/架构/数据模型（v4.0-v9.0）**：以 `AI赋能职教视频个性化教学项目需求规格说明书（第九稿-完整版）.md` 为准。
- **v10.0新增内容**：以本文件第2-10章为准；若与v9.0存在冲突，以v10.0为最终解释。

---

# 2. v10.0新增：系统自愈与冲突处理（写锁/原子化）

## 2.1 问题定义：人机同步冲突

- **冲突场景**：AI后台正在生成/更新某视频的知识图谱（例如5.0版），教师在前端同时编辑旧版本（例如4.0版）。
- **风险**：
  - 教师提交被AI后写覆盖（丢失人工更改）
  - AI生成基于旧快照（发布出错）
  - 图谱版本链断裂（不可追溯）

## 2.2 解决方案：写锁（Write Lock）+ 原子化发布

### 2.2.1 写锁规则（Write Lock）

- **触发**：教师进入“专家标注模式”时。
- **对象**：`video_id` 级别写锁（覆盖知识点切分、依赖关系、资源绑定、图谱版本发布）。
- **效果**：
  - 暂停该 `video_id` 的所有 AI 自动更新任务（队列消费停止或任务直接拒绝）
  - 禁止其他教师对同一视频发起写操作（仅允许只读浏览）

### 2.2.1.1 **[v10.0补充] 锁定租约（Lease Time）与强制解除（Timeout Lock）**

- **问题**：教师在“专家标注模式”编辑到一半，突然关掉浏览器/停电，可能造成视频长期被锁，AI更新永久暂停（死锁）。
- **协议**：写锁采用**租约机制（Lease）**，默认有效期 **30分钟**。
- **规则**：
  - **默认租约**：30分钟
  - **续租条件**：教师有“有效编辑行为”（保存草稿/移动分段/修改依赖/新增知识点等）即刷新 `last_heartbeat_at`
  - **超时释放**：若 `now - last_heartbeat_at > 30min`，系统自动释放写锁
  - **状态对齐**：释放写锁后触发一次“状态对齐（State Reconcile）”
    - 将未发布的草稿标记为 `stale_draft`（可回收/可恢复）
    - **回滚到最近稳定版本**：将线上生效版本指向最近一次 `published` 的 `knowledge_graph_version`（确保AI补偿/推荐不受半成品草稿影响）
    - 恢复该 `video_id` 的AI托管任务为 `running`
    - 生成一条审计记录：谁持锁、何时超时、释放原因、对齐结果

#### 2.2.1.2 Lease参考实现（伪代码）

```python
class KnowledgeGraphWriteLockServiceV10:
    """
    [v10.0新增/补充] 知识图谱写锁服务（含Lease与超时释放）
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

### 2.2.2 原子化发布（Atomic Publish）

教师点击“发布并交还AI托管”时，必须一次性完成：

- 校验：版本号、编辑快照、差异变更集合法性
- 提交：写入新图谱版本（不可部分成功）
- 解锁：释放写锁
- 托管：恢复AI更新任务，并以最新版本为基线

### 2.2.3 参考实现（伪代码）

```python
class KnowledgeGraphWriteLockServiceV10:
    """
    [v10.0新增] 知识图谱写锁服务（人机冲突处理）
    """

    def acquire_write_lock(self, video_id, teacher_id, ttl_seconds=3600):
        # Redis/DB均可：保证互斥
        # 成功返回 lock_token；失败返回占用者信息
        pass

    def release_write_lock(self, video_id, lock_token):
        pass

    def is_locked(self, video_id):
        pass


class ExpertAnnotationAtomicPublisherV10:
    """
    [v10.0新增] 专家标注原子化发布器
    """

    def publish_and_handover(self, video_id, teacher_id, lock_token, change_set):
        # 1) 校验锁
        # 2) 事务：写入 graph_version + knowledge_points + dependencies + bindings
        # 3) 发布成功：释放锁 + 恢复AI托管
        # 4) 发布失败：回滚事务（不改变线上版本）
        pass
```

## 2.3 状态机（必须落库）

- `annotation_mode`: `ai_managed` | `expert_only`
- `graph_version_status`: `draft` | `published` | `rollbacked`
- `ai_job_status`: `running` | `paused_by_lock` | `rejected_by_lock`

---

# 3. v10.0新增：硬件适配矩阵（设备画像驱动三级降级）

## 3.1 目标

在设备老旧/无独显/CPU飙高时，系统必须**自动切换计算模式**，避免页面卡死，同时保持“可用的学习闭环”。

## 3.2 设备画像采集（客户端）

- **采集指标**（前端周期性采样）：
  - CPU占用（或近似：页面帧率、长任务占比、JS主线程阻塞）
  - 内存占用（近似：资源加载失败、GC频率）
  - GPU可用性（WebGL/硬件加速能力探测）
  - 摄像头分辨率/帧率可达性

## 3.3 三级降级矩阵（v10.0）

| 等级 | 触发条件（示例） | 监控能力 | 说明 |
|------|------------------|----------|------|
| **L0 全量** | CPU≤60% 且 FPS≥30 | 视线+微表情+姿态+人体+环境音+行为 | 高性能设备全开 |
| **L1 精简** | CPU 60-80% 或 FPS 20-30 | 关闭微表情/姿态，仅保留视线(低采样)+人体+行为+ASR | 控制开销 |
| **L2 仅日志** | CPU>80% 或 FPS<20 或无GPU | 仅ASR+行为日志（暂停/回看/拖拽/笔记） | 保证不卡死 |

### 3.3.1 **[v10.0补充] 降级特征补偿（特征插值/权重修正）**

- **问题**：进入“仅日志模式”后失去微表情等视觉信号，模块B认知画像准确率可能断崖式下跌。
- **策略**：当 `device_mode == L2_only_log` 时，自动执行“降级算法权重修正”，用更稳定的行为信号补偿缺失模态。

**规则**：
- **鼠标轨迹/停留/悬停权重**：例如从 `0.4 → 0.8`
- **暂停/回看频次权重**：例如从 `0.4 → 0.8`
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

### v9.0弱网降级协同规则

- 弱网降级（v9.0）与硬件降级（v10.0）**取更严格者**：
  - 任何一个判定进入“仅日志”，最终即为“仅日志”。

---

# 4. v10.0新增：冷启动自动化（跨课原型匹配）

## 4.1 问题定义

当新课程上传且教师未提供专家基准时，系统不能“空转等待标注”，必须具备半自动冷启动能力。

## 4.2 解决方案：Prototype Matching（跨课原型匹配）

### 4.2.1 核心规则

- 从新课程视频中提取**核心术语频率向量**（ASR文本 + OCR关键词）。
- 与课程库中已成熟课程原型计算语义相似度：
  - 若 `sim(new, prototype) > 0.8`：复用其**难度基准**与**步频阈值**作为初始值。
  - 若 `0.6 < sim ≤ 0.8`：复用但标记为“低置信度冷启动”，同时提示教师轻量确认。
  - 若 `sim ≤ 0.6`：退化为默认行业基准（或等待数据积累/教师标注）。

### 4.2.2 复用内容范围

- `knowledge_point_difficulty` 初始化（全网平均时长缺失时）
- `cognitive_pace` 初始阈值（personal_threshold的初始倍率）
- `intervention` 默认触发敏感度（可被教师激进系数再调）

---

# 5. v10.0新增：教师策略编辑器（干预激进系数）

## 5.1 功能描述

教师端提供**干预激进系数（0.1-2.0）**滑块，用于“一键调整全班干预敏感度”：

- `0.1`：非常保守（少干预）
- `1.0`：默认策略
- `2.0`：非常激进（更早干预）

## 5.2 生效范围与优先级

- **范围**：按 `course_id + class_id` 生效（可选：按视频/知识点覆盖）。
- **优先级**：
  - 安全熔断（最高）不受影响
  - 个体化阈值（认知步频/难度系数）为基线
  - 教师激进系数作为**全局乘子**作用于“异常阈值倍率”

示例：
\[
threshold = personal\_baseline \times 1.5 \div aggression
\]

---

# 6. v10.0新增：数据审计引擎（异常反馈过滤）

## 6.1 问题定义

资源反馈体系可能被以下因素污染：

- 学生“情绪化差评”
- 同一账号批量点踩
- 同一IP/设备短时间刷票
- 与学习行为矛盾的反馈（比如未观看就评价）

## 6.2 审计引擎规则（最小可行）

- **一致性校验**：必须满足“看过/触发过资源”才可反馈
- **速率限制**：同一用户对同一资源 24h 内最多 N 次
- **异常模式识别**（规则优先，模型可后续加入）：
  - 低停留时长 + 立刻差评（可疑）
  - 多资源连续差评且无学习行为变化（可疑）
  - 班级内极端离群（可疑）
- **处置**：
  - 标记为 `audit_suspected`
  - 不参与“连续3个差评自动下架”的统计
  - 教师端可查看审计原因并手动放行/驳回

### 6.3 **[v10.0补充] 难度保护区（Difficulty Protection Zone）**

- **问题**：班级可能因进度压力/畏难情绪对“高难但必要”的资源集体差评，导致AI误下架优质资源。
- **规则**：当满足以下条件时，启用“难度保护区”，提高自动下架阈值：
  - `expert_difficulty_coefficient > 1.8`（例如教师预设难度系数/停留系数）
  - 或知识点被标记为 `is_core_difficulty = true`

**阈值调整**：
- 普通资源：连续负反馈阈值 `3`
- 难度保护区资源：连续负反馈阈值 `10`（或更高，且必须包含至少1条“内容不符”类证据才允许下架）

### 6.4 **[v10.0补充] 下架仲裁：反馈-行为一致性强制校验（80%门槛）**

- **问题**：即使提高阈值，仍可能被恶意刷票；同时“未看先评”会污染资源评价体系。
- **强制规则**：任何“差评/无帮助”在计入下架统计前，必须通过**反馈-行为一致性校验**：
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
```

```python
def get_auto_remove_threshold(expert_difficulty_coefficient: float, is_core_difficulty: bool):
    """
    [v10.0补充] 难度保护区：提高自动下架阈值，防止优质高难资源被误杀
    """
    if is_core_difficulty or (expert_difficulty_coefficient and expert_difficulty_coefficient > 1.8):
        return 10
    return 3
```

---

# 7. 数据模型增量（v10.0）

建议新增（或在v9.0表上扩展字段）：

- `knowledge_graph_write_lock`
- `knowledge_graph_version`
- `device_profile_log`
- `course_prototype`
- `teacher_strategy_profile`
- `feedback_audit_log`

---

# 8. 接口设计增量（v10.0）

建议新增接口：

- `POST /api/v10/lock/acquire` / `POST /api/v10/lock/release`
- `POST /api/v10/lock/heartbeat`
- `POST /api/v10/expert/publish-handover`
- `POST /api/v10/device/profile/report`
- `GET /api/v10/course/prototype/match`

### 8.1 **[v10.0补充]** 写锁接口契约（Lease Timeout消歧义）

为避免实现歧义，写锁（Write Lock）必须在接口层显式声明**租约、心跳与超时释放回滚**策略。

#### 8.1.1 获取写锁（Acquire）
- **接口**：`POST /api/v10/lock/acquire`
- **描述**：获取 `video_id` 写锁并进入专家标注工作区；成功后暂停该 `video_id` 的AI后台写入任务。
- **关键规则**：
  - **租约默认值**：`lease_seconds = 1800`（30分钟）
  - **续租方式**：前端需周期性调用 `POST /api/v10/lock/heartbeat`（建议每60秒一次），或在每次“有效编辑行为”后触发续租
  - **超时自动释放**：若 `now - last_heartbeat_at > lease_seconds`，系统强制释放写锁
  - **超时释放后状态对齐**：
    - 将未发布草稿标记为 `stale_draft`
    - **回滚线上图谱到最近一次 `published` 稳定版本**
    - 恢复该 `video_id` 的AI托管任务为 `running`
    - 写入审计：持锁人、超时原因、回滚版本、对齐结果
- **请求参数**：
```json
{
  "video_id": "V001",
  "teacher_id": "T001",
  "lease_seconds": 1800
}
```
- **响应**：
```json
{
  "code": 200,
  "data": {
    "lock_token": "LT_xxx",
    "lease_seconds": 1800,
    "locked_at": "2026-01-28T10:00:00Z",
    "last_heartbeat_at": "2026-01-28T10:00:00Z"
  }
}
```

#### 8.1.2 续租心跳（Heartbeat）
- **接口**：`POST /api/v10/lock/heartbeat`
- **描述**：续租写锁，刷新 `last_heartbeat_at`，防止编辑过程中锁超时释放。
- **请求参数**：
```json
{
  "video_id": "V001",
  "lock_token": "LT_xxx"
}
```

#### 8.1.3 释放写锁（Release）
- **接口**：`POST /api/v10/lock/release`
- **描述**：释放写锁（通常在“发布并交还AI托管”原子流程成功后由后端自动调用）。
- **请求参数**：
```json
{
  "video_id": "V001",
  "lock_token": "LT_xxx",
  "reason": "manual_release"
}
```
- `POST /api/v10/teacher/strategy/aggression`
- `GET /api/v10/audit/feedback/{resource_id}`
- `POST /api/v10/audit/feedback/override`

---

# 9. 最终验收补充（v10.0）

- ✅ **并发冲突验收**：教师进入专家标注后，AI任务必须暂停；发布后恢复；全过程无覆盖/丢写。
- ✅ **硬件降级验收**：CPU>80%自动降级到“仅日志”，页面保持流畅，学习记录不丢。
- ✅ **原型匹配验收**：新课无专家基准时能自动找到相似课并初始化阈值；低置信度时提示教师确认。
- ✅ **激进系数验收**：滑块调整后，全班干预触发频率按系数可观测变化；安全熔断不受影响。
- ✅ **审计引擎验收**：异常反馈被标记且不计入自动下架；教师可回放审计原因并放行。

---

# 10. v10.0更新日志

1. **系统自愈与冲突处理**：专家标注模式写锁+原子发布+交还AI托管
2. **硬件适配矩阵**：设备画像驱动三级降级（全量/精简/仅日志），并与弱网降级协同
3. **冷启动自动化**：跨课原型匹配复用相似课程基准，实现半自动冷启动
4. **教师策略编辑器**：干预激进系数（0.1-2.0）支持全班级统一调参
5. **数据审计引擎**：过滤异常/恶意反馈，保护资源评价体系真实性

---

## 文档结束

**版本**：v10.0（Final Production Ready Version）  
**日期**：2026年1月

