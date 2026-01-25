"""
模拟数据文件 - 用于算法开发和测试
"""

# 模拟ASR转写文本（带时间戳）
MOCK_ASR_TEXTS = [
    {"start_time": 0.0, "end_time": 120.0, "text": "大家好，今天我们来学习Python函数的概念。函数是编程中非常重要的概念。"},
    {"start_time": 120.0, "end_time": 240.0, "text": "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"},
    {"start_time": 240.0, "end_time": 360.0, "text": "函数的定义包括函数名、参数列表和函数体。让我们看一个简单的例子。"},
    {"start_time": 360.0, "end_time": 480.0, "text": "def add(a, b): return a + b。这就是一个简单的加法函数。"},
    {"start_time": 480.0, "end_time": 600.0, "text": "接下来我们学习函数的参数。函数可以有位置参数、关键字参数和默认参数。"},
    {"start_time": 600.0, "end_time": 720.0, "text": "位置参数是按照顺序传递的，关键字参数可以指定参数名，默认参数有预设值。"},
    {"start_time": 720.0, "end_time": 840.0, "text": "现在我们来学习函数的返回值。函数可以使用return语句返回结果。"},
    {"start_time": 840.0, "end_time": 960.0, "text": "如果函数没有return语句，默认返回None。多个值可以通过元组返回。"},
    {"start_time": 960.0, "end_time": 1080.0, "text": "最后我们学习作用域的概念。局部变量和全局变量有不同的作用域。"},
    {"start_time": 1080.0, "end_time": 1200.0, "text": "在函数内部定义的变量是局部变量，在函数外部定义的是全局变量。"},
]

# 模拟OCR识别的PPT文字（带时间戳）
MOCK_OCR_TEXTS = [
    {"start_time": 0.0, "end_time": 120.0, "text": "函数定义", "slide_number": 1},
    {"start_time": 120.0, "end_time": 240.0, "text": "函数是一种映射关系", "slide_number": 1},
    {"start_time": 240.0, "end_time": 360.0, "text": "def 函数名(参数):", "slide_number": 2},
    {"start_time": 360.0, "end_time": 480.0, "text": "示例：def add(a, b)", "slide_number": 2},
    {"start_time": 480.0, "end_time": 600.0, "text": "函数参数类型", "slide_number": 3},
    {"start_time": 600.0, "end_time": 720.0, "text": "位置参数、关键字参数、默认参数", "slide_number": 3},
    {"start_time": 720.0, "end_time": 840.0, "text": "函数返回值", "slide_number": 4},
    {"start_time": 840.0, "end_time": 960.0, "text": "return 语句", "slide_number": 4},
    {"start_time": 960.0, "end_time": 1080.0, "text": "作用域", "slide_number": 5},
    {"start_time": 1080.0, "end_time": 1200.0, "text": "局部变量 vs 全局变量", "slide_number": 5},
]

# 模拟观看行为数据
MOCK_BEHAVIOR_DATA = {
    "user_id": 1,
    "knowledge_point_id": 10,
    "replay_count": 3,
    "pause_count": 5,
    "total_watch_time": 600.0,
    "knowledge_point_duration": 200.0,
    "seek_count": 2,
    "last_watch_time": "2025-01-25T10:00:00Z",
}

# 模拟知识点掌握状态
MOCK_MASTERY_STATUS = {
    1: "已掌握",
    2: "学习中",
    3: "疑难",
    4: "未学",
    5: "已掌握",
    6: "疑难",
}

# 模拟知识点依赖关系
MOCK_DEPENDENCIES = [
    (1, 2, "prerequisite"),  # 知识点1是知识点2的前置
    (2, 3, "prerequisite"),
    (3, 4, "prerequisite"),
    (1, 5, "related"),  # 知识点1和知识点5相关
]

# 模拟知识点信息
MOCK_KNOWLEDGE_POINT = {
    "id": 10,
    "name": "函数定义",
    "summary": "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。",
    "keywords": ["函数", "映射", "定义", "def"],
    "difficulty": "medium",
    "start_time": 0.0,
    "end_time": 240.0,
}
