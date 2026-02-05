# AI算法模块

## 模块说明

本模块包含AI赋能职教视频个性化教学系统的核心算法实现。

## 目录结构

```
algorithm/
├── __init__.py
│
├── 核心算法模块（v1.0-v5.0）
├── knowledge_point_segmenter.py    # 知识点切分算法
├── knowledge_point_annotator.py    # 知识点自动标注
├── knowledge_graph_builder.py      # 知识图谱构建
├── difficulty_detector.py          # 难点识别算法
├── public_difficulty_detector.py   # 公共难点识别
├── learning_path_generator.py      # 学习路径生成算法
├── path_adjuster.py                # 动态路径调整
├── remedial_resource_strategy.py   # 补偿资源推送策略
├── knowledge_card_generator.py     # 知识卡片生成
├── exercise_generator.py           # 练习题生成
├── resource_pusher.py              # 资源推送机制
├── resource_quality_evaluator.py   # 资源质量评估
│
├── v6.0-v10.0 新功能模块
├── confidence_gate.py              # v7_b5: 置信度门控机制
├── intervention_hysteresis.py      # v9_c7: 干预抗震荡机制
├── teacher_aggression_coefficient.py # v10_c9: 教师激进系数调节
├── cognitive_pace_calculator.py    # v7_b6: 个人认知步频计算
├── difficulty_protection_zone.py  # v10_d11: 难度保护区机制
├── feedback_behavior_consistency.py # v10_d12: 反馈-行为一致性校验
├── signal_loss_handler.py          # v8_b8: 监控信号丢失处理
├── resource_feedback_refiner.py    # v7_d6: 资源评价细化机制
├── progress_stagnation_handler.py  # v7_c5: 进度停滞自动升级
├── teacher_baseline_manager.py     # v8_a7: 教师预设基准线机制
├── ai_generation_lock_manager.py   # v9_a9: 教师一键禁用AI生成
├── gray_review_mechanism.py        # v7_d7: 修正资源灰度复核
├── difficulty_coefficient_weighted.py # v8_b7: 认知步频难度系数加权
├── data_audit_engine.py            # v10_d10: 数据审计引擎
├── weak_network_degradation.py     # v9_b9: 弱网环境降级策略
├── hardware_degradation.py         # v10_b10: 硬件画像驱动降级
├── signal_dissonance_detector.py   # v6_b3: 信号不协和检测
├── social_learning_module.py       # v6_d5: 社会学习模块（知识锦囊）
├── smart_clip_context_preserver.py # v7_d8: 智能剪辑上下文保留
├── learning_style_filter.py        # v8_d9: 学习风格自适应过滤
├── multimodal_timestamp_aligner.py  # v9_a8: 多模态时间戳对齐
├── dependency_weight_corrector.py   # v7_a5: 依赖权重修正算法
├── spiral_breakout_strategy.py     # v9_c8: 螺旋路径跳出策略
├── write_lock_lease_manager.py     # v10_a10: 写锁租约机制
├── cross_course_prototype_matcher.py # v10_a11: 跨课原型匹配冷启动
│
├── 工具和优化模块
├── semantic_similarity.py          # 语义相似度计算
├── performance_optimizer.py        # 性能优化器
├── optimized_segmenter.py          # 优化版切分器
│
├── tests/                          # 测试文件
│   ├── mock_data.py                # 模拟数据
│   ├── test_segmenter.py           # 切分算法测试
│   ├── test_annotator.py           # 标注算法测试
│   ├── test_graph_builder.py       # 图谱构建测试
│   ├── test_difficulty_detector.py # 难点检测测试
│   ├── test_public_detector.py     # 公共难点测试
│   ├── test_learning_path.py       # 学习路径测试
│   ├── test_resource_generation.py # 资源生成测试
│   ├── test_spiral_breakout.py     # 螺旋跳出测试
│   ├── test_confidence_gate.py     # 置信度门控测试
│   ├── test_intervention_hysteresis.py # 干预抗震荡测试
│   ├── test_write_lock_lease.py    # 写锁租约测试
│   ├── test_cross_course_prototype.py # 跨课匹配测试
│   └── integration_test.py         # 集成测试
│
├── requirements.txt                # 依赖包
├── README.md                       # 本文件
├── v6-v10_功能实现总结.md          # v6-v10功能实现总结
├── 性能优化实现.md                 # 性能优化文档
├── 性能优化总结.md                 # 性能优化总结
└── 开发进度.md                     # 开发进度跟踪
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 知识点切分算法

```python
from knowledge_point_segmenter import KnowledgePointSegmenter
from tests.mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS

# 创建切分器
segmenter = KnowledgePointSegmenter(
    similarity_threshold=0.7,
    min_duration=120.0,  # 2分钟
    max_duration=600.0   # 10分钟
)

# 执行切分
knowledge_points = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)

# 查看结果
for kp in knowledge_points:
    print(f"知识点: {kp.name}")
    print(f"时间: {kp.start_time:.1f}s - {kp.end_time:.1f}s")
    print(f"关键词: {', '.join(kp.keywords)}")
    print(f"摘要: {kp.summary}")
    print(f"难度: {kp.difficulty}")
    print()
```

### v6.0-v10.0 新功能使用示例

#### 置信度门控机制（v7_b5）

```python
from confidence_gate import ConfidenceGate

gate = ConfidenceGate(confidence_threshold=0.7)
result = gate.gate_difficulty_detection(
    difficulty_score=0.85,
    multimodal_signals={'gaze': 0.8, 'emotion': 0.7, 'interaction': 0.9},
    student_id="student_001",
    knowledge_point_id="kp_001"
)
if result['requires_confirmation']:
    print("需要人工确认")
```

#### 干预抗震荡机制（v9_c7）

```python
from intervention_hysteresis import InterventionHysteresis

hysteresis = InterventionHysteresis(cooldown_minutes=5)
should_trigger = hysteresis.should_trigger_intervention(
    student_id="student_001",
    current_score=0.85,
    trigger_threshold=0.8,
    release_threshold=0.6
)
```

#### 教师激进系数调节（v10_c9）

```python
from teacher_aggression_coefficient import TeacherAggressionCoefficient

coefficient_manager = TeacherAggressionCoefficient()
coefficient_manager.set_aggression_coefficient(
    teacher_id="teacher_001",
    coefficient=1.5  # 更激进的干预策略
)
adjusted_threshold = coefficient_manager.adjust_intervention_threshold(
    base_threshold=0.8,
    teacher_id="teacher_001"
)
```

#### 认知步频计算（v7_b6）

```python
from cognitive_pace_calculator import CognitivePaceCalculator

calculator = CognitivePaceCalculator()
pace = calculator.calculate_pace(
    student_id="student_001",
    time_window_hours=24
)
dynamic_threshold = calculator.calculate_dynamic_threshold(
    student_id="student_001",
    base_threshold=0.8
)
```

#### 学习风格自适应过滤（v8_d9）

```python
from learning_style_filter import LearningStyleFilter

filter_engine = LearningStyleFilter()
learning_style = filter_engine.infer_learning_style(
    student_id="student_001",
    feedback_history=[]
)
filtered_resources = filter_engine.filter_by_style(
    resources=available_resources,
    student_id="student_001"
)
```

更多使用示例请参考各模块的文档字符串和 `v6-v10_功能实现总结.md`。

## 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_segmenter.py -v

# 运行集成测试
pytest tests/integration_test.py -v -s

# 或者使用脚本
python 运行集成测试.py

# 运行测试并查看覆盖率
pytest tests/ --cov=algorithm --cov-report=html

# 运行性能测试
python performance_test.py
```

## 开发进度

### 核心算法模块（v1.0-v5.0）

- [x] 知识点切分算法（KnowledgePointSegmenter）
- [x] 知识点自动标注（KnowledgePointAnnotator）
- [x] 知识图谱构建（KnowledgeGraphBuilder）
- [x] 难点识别算法（DifficultyDetector）
- [x] 公共难点识别（PublicDifficultyDetector）
- [x] 学习路径生成算法（LearningPathGenerator）
- [x] 动态路径调整（PathAdjuster）
- [x] 补偿资源推送策略（RemedialResourceStrategy）
- [x] 知识卡片生成（KnowledgeCardGenerator）
- [x] 练习题生成（ExerciseGenerator）
- [x] 资源推送机制（ResourcePusher）
- [x] 资源质量评估（ResourceQualityEvaluator）

### v6.0-v10.0 新功能模块（25/28 完成，89.3%）

#### v6.0 模块
- [x] v6_b3: 信号不协和检测算法（SignalDissonanceDetector）
- [x] v6_d5: 社会学习模块（知识锦囊）（SocialLearningModule）
- [ ] v6_a4: GNN知识依赖图构建（待实现，依赖项）
- [ ] v6_b4: 溯源式根本原因诊断算法（待实现，依赖v6_a4）
- [ ] v6_c4: 溯源回补路径生成算法（待实现，依赖v6_a4）

#### v7.0 模块
- [x] v7_a5: 依赖权重修正算法（DependencyWeightCorrector）
- [x] v7_b5: 置信度门控机制（ConfidenceGate）
- [x] v7_b6: 个人认知步频计算算法（CognitivePaceCalculator）
- [x] v7_c5: 进度停滞自动升级（L3自动触发）（ProgressStagnationHandler）
- [x] v7_d6: 资源评价细化机制（多维度反馈）（ResourceFeedbackRefiner）
- [x] v7_d7: 修正资源灰度复核机制（GrayReviewMechanism）
- [x] v7_d8: 智能剪辑上下文保留协议（前5s+后3s）（SmartClipContextPreserver）

#### v8.0 模块
- [x] v8_a7: 教师预设基准线机制（TeacherBaselineManager）
- [x] v8_b7: 认知步频难度系数加权算法（避免虚假繁荣）（DifficultyCoefficientWeighted）
- [x] v8_b8: 监控信号丢失处理机制（心跳检测）（SignalLossHandler）
- [x] v8_d9: 学习风格自适应过滤器算法（LearningStyleFilter）
- [ ] v8_a6: 逻辑环路检测与螺旋路径生成算法（待实现，依赖v6_a4）
- [ ] v8_c6: 螺旋上升路径生成算法（环路处理）（待实现，依赖v6_a4）

#### v9.0 模块
- [x] v9_a8: 多模态时间戳对齐协议（±3秒窗口）（MultimodalTimestampAligner）
- [x] v9_a9: 教师一键禁用AI自动生成机制（AIGenerationLockManager）
- [x] v9_b9: 弱网环境降级策略矩阵（WeakNetworkDegradation）
- [x] v9_c7: 干预抗震荡机制（Hysteresis冷静期）（InterventionHysteresis）
- [x] v9_c8: 螺旋路径跳出策略（反复失败→L3）（SpiralBreakoutStrategy）

#### v10.0 模块
- [x] v10_a10: 写锁租约机制（30分钟超时）（WriteLockLeaseManager）
- [x] v10_a11: 跨课原型匹配冷启动算法（CrossCoursePrototypeMatcher）
- [x] v10_b10: 硬件画像驱动三级降级算法（全量/精简/仅日志）（HardwareDegradation）
- [x] v10_c9: 教师激进系数调节算法（0.1-2.0）（TeacherAggressionCoefficient）
- [x] v10_d10: 数据审计引擎（异常/恶意反馈过滤）（DataAuditEngine）
- [x] v10_d11: 难度保护区机制（高难资源下架阈值保护）（DifficultyProtectionZone）
- [x] v10_d12: 反馈-行为一致性校验（80%门槛）（FeedbackBehaviorConsistency）

## 注意事项

1. **依赖管理**: 当前使用jieba进行关键词提取和相似度计算，后续可以升级为sentence-transformers获得更好的语义理解
2. **数据源**: 所有算法都使用模拟数据进行开发和测试，后续会对接真实数据源
3. **代码规范**: 代码遵循PEP 8规范，使用类型注解和详细文档字符串
4. **功能完整性**: v6.0-v10.0 新功能模块已完成 25/28（89.3%），剩余3个功能依赖GNN知识依赖图构建（v6_a4）
5. **测试覆盖**: 所有新功能模块都包含对应的测试文件，建议在修改代码后运行相关测试
6. **性能优化**: 部分模块已实现性能优化，详见 `性能优化实现.md` 和 `性能优化总结.md`
7. **功能文档**: 详细的v6-v10功能实现说明请参考 `v6-v10_功能实现总结.md`

## 相关文档

- [v6-v10功能实现总结](v6-v10_功能实现总结.md) - 详细的功能实现说明和进度跟踪
- [性能优化实现](性能优化实现.md) - 性能优化的具体实现方案
- [性能优化总结](性能优化总结.md) - 性能优化的总结和效果分析
- [开发进度](开发进度.md) - 整体开发进度跟踪
