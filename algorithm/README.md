# AI算法模块

## 模块说明

本模块包含AI赋能职教视频个性化教学系统的核心算法实现。

## 目录结构

```
algorithm/
├── __init__.py
├── knowledge_point_segmenter.py    # 知识点切分算法
├── knowledge_point_annotator.py    # 知识点自动标注（待实现）
├── knowledge_graph_builder.py      # 知识图谱构建（待实现）
├── difficulty_detector.py          # 难点识别算法（待实现）
├── learning_path_generator.py      # 学习路径生成算法（待实现）
├── tests/                          # 测试文件
│   ├── mock_data.py                # 模拟数据
│   └── test_segmenter.py           # 切分算法测试
├── requirements.txt                # 依赖包
└── README.md                       # 本文件
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

## 注意事项

1. 当前使用jieba进行关键词提取和相似度计算，后续可以升级为sentence-transformers获得更好的语义理解
2. 所有算法都使用模拟数据进行开发和测试，后续会对接真实数据源
3. 代码遵循PEP 8规范，使用类型注解和详细文档字符串
