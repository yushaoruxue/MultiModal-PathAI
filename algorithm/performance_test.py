"""
性能测试脚本

测试各个算法模块的性能，识别性能瓶颈。
"""

import time
import logging
import sys
import os
from typing import Dict, List
import cProfile
import pstats
from io import StringIO

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from knowledge_point_segmenter import KnowledgePointSegmenter
from knowledge_point_annotator import KnowledgePointAnnotator
from knowledge_graph_builder import KnowledgeGraphBuilder, KnowledgePointInfo
from difficulty_detector import DifficultyDetector, BehaviorData
from public_difficulty_detector import PublicDifficultyDetector
from learning_path_generator import LearningPathGenerator
from path_adjuster import PathAdjuster, LearningEvent
from remedial_resource_strategy import RemedialResourceStrategy, DifficultyLevel
from knowledge_card_generator import KnowledgeCardGenerator, KnowledgePointInfo as KPInfo
from exercise_generator import ExerciseGenerator
from tests.mock_data import (
    MOCK_ASR_TEXTS, MOCK_OCR_TEXTS, MOCK_BEHAVIOR_DATA,
    MOCK_MASTERY_STATUS, MOCK_DEPENDENCIES, MOCK_KNOWLEDGE_POINT
)

# 配置日志
logging.basicConfig(level=logging.WARNING)  # 减少日志输出
logger = logging.getLogger(__name__)


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        """初始化性能测试器"""
        self.results: Dict[str, Dict] = {}
    
    def test_module_a_segmentation(self, iterations: int = 10) -> Dict:
        """测试模块A：知识点切分性能"""
        print(f"\n测试模块A：知识点切分（{iterations}次迭代）")
        print("-" * 60)
        
        segmenter = KnowledgePointSegmenter()
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            knowledge_points = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
            elapsed = time.time() - start_time
            times.append(elapsed)
            if i == 0:
                print(f"  首次运行: {elapsed:.4f}秒，生成 {len(knowledge_points)} 个知识点")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        result = {
            "module": "知识点切分",
            "iterations": iterations,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "throughput": 1.0 / avg_time if avg_time > 0 else 0
        }
        
        print(f"  平均时间: {avg_time:.4f}秒")
        print(f"  最小时间: {min_time:.4f}秒")
        print(f"  最大时间: {max_time:.4f}秒")
        print(f"  吞吐量: {result['throughput']:.2f} 次/秒")
        
        self.results["segmentation"] = result
        return result
    
    def test_module_a_annotation(self, iterations: int = 10) -> Dict:
        """测试模块A：知识点标注性能"""
        print(f"\n测试模块A：知识点标注（{iterations}次迭代）")
        print("-" * 60)
        
        annotator = KnowledgePointAnnotator()
        kp_text = "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            annotation = annotator.annotate(kp_text, MOCK_ASR_TEXTS[:3], MOCK_OCR_TEXTS[:2])
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        result = {
            "module": "知识点标注",
            "iterations": iterations,
            "avg_time": avg_time,
            "throughput": 1.0 / avg_time if avg_time > 0 else 0
        }
        
        print(f"  平均时间: {avg_time:.4f}秒")
        print(f"  吞吐量: {result['throughput']:.2f} 次/秒")
        
        self.results["annotation"] = result
        return result
    
    def test_module_b_difficulty_detection(self, iterations: int = 100) -> Dict:
        """测试模块B：难点识别性能"""
        print(f"\n测试模块B：难点识别（{iterations}次迭代）")
        print("-" * 60)
        
        detector = DifficultyDetector()
        behavior_data = BehaviorData(
            user_id=1, knowledge_point_id=10,
            replay_count=3, pause_count=5,
            total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2
        )
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = detector.detect(behavior_data)
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        result = {
            "module": "难点识别",
            "iterations": iterations,
            "avg_time": avg_time,
            "throughput": 1.0 / avg_time if avg_time > 0 else 0
        }
        
        print(f"  平均时间: {avg_time:.4f}秒")
        print(f"  吞吐量: {result['throughput']:.2f} 次/秒")
        
        self.results["difficulty_detection"] = result
        return result
    
    def test_module_c_path_generation(self, iterations: int = 50) -> Dict:
        """测试模块C：学习路径生成性能"""
        print(f"\n测试模块C：学习路径生成（{iterations}次迭代）")
        print("-" * 60)
        
        generator = LearningPathGenerator()
        mastery_status = MOCK_MASTERY_STATUS
        dependencies = MOCK_DEPENDENCIES
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            path = generator.generate_path(1, mastery_status, dependencies)
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        result = {
            "module": "学习路径生成",
            "iterations": iterations,
            "avg_time": avg_time,
            "throughput": 1.0 / avg_time if avg_time > 0 else 0
        }
        
        print(f"  平均时间: {avg_time:.4f}秒")
        print(f"  吞吐量: {result['throughput']:.2f} 次/秒")
        
        self.results["path_generation"] = result
        return result
    
    def test_module_d_resource_generation(self, iterations: int = 20) -> Dict:
        """测试模块D：资源生成性能"""
        print(f"\n测试模块D：资源生成（{iterations}次迭代）")
        print("-" * 60)
        
        card_generator = KnowledgeCardGenerator()
        exercise_generator = ExerciseGenerator()
        
        kp_info = KPInfo(
            id=10,
            name="函数定义",
            summary="函数是一种映射关系。",
            keywords=["函数", "映射"],
            difficulty="medium"
        )
        
        # 测试知识卡片生成
        card_times = []
        for i in range(iterations):
            start_time = time.time()
            card = card_generator.generate_card(kp_info, asr_text="函数定义")
            elapsed = time.time() - start_time
            card_times.append(elapsed)
        
        # 测试练习题生成
        exercise_times = []
        for i in range(iterations):
            start_time = time.time()
            exercises = exercise_generator.generate_exercises(kp_info, count=5)
            elapsed = time.time() - start_time
            exercise_times.append(elapsed)
        
        avg_card_time = sum(card_times) / len(card_times)
        avg_exercise_time = sum(exercise_times) / len(exercise_times)
        
        result = {
            "module": "资源生成",
            "iterations": iterations,
            "card_avg_time": avg_card_time,
            "exercise_avg_time": avg_exercise_time,
            "total_avg_time": avg_card_time + avg_exercise_time
        }
        
        print(f"  知识卡片平均时间: {avg_card_time:.4f}秒")
        print(f"  练习题平均时间: {avg_exercise_time:.4f}秒")
        print(f"  总平均时间: {result['total_avg_time']:.4f}秒")
        
        self.results["resource_generation"] = result
        return result
    
    def test_batch_operations(self) -> Dict:
        """测试批量操作性能"""
        print(f"\n测试批量操作性能")
        print("-" * 60)
        
        # 批量难点识别
        detector = DifficultyDetector()
        behavior_list = [
            BehaviorData(user_id=i, knowledge_point_id=10,
                        replay_count=3, pause_count=5,
                        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2)
            for i in range(100)
        ]
        
        start_time = time.time()
        results = detector.batch_detect(behavior_list)
        batch_time = time.time() - start_time
        
        # 单个操作时间
        single_start = time.time()
        for behavior in behavior_list[:10]:
            detector.detect(behavior)
        single_time = (time.time() - single_start) / 10
        
        result = {
            "module": "批量操作",
            "batch_size": len(behavior_list),
            "batch_time": batch_time,
            "single_time": single_time,
            "speedup": (single_time * len(behavior_list)) / batch_time if batch_time > 0 else 0
        }
        
        print(f"  批量处理 {len(behavior_list)} 条记录: {batch_time:.4f}秒")
        print(f"  单个处理时间: {single_time:.4f}秒")
        print(f"  加速比: {result['speedup']:.2f}x")
        
        self.results["batch_operations"] = result
        return result
    
    def profile_module(self, module_name: str, func, *args, **kwargs):
        """性能分析（使用cProfile）"""
        print(f"\n性能分析：{module_name}")
        print("-" * 60)
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # 生成分析报告
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # 显示前20个最耗时的函数
        
        print(s.getvalue())
        
        return result
    
    def generate_report(self) -> str:
        """生成性能测试报告"""
        report = "\n" + "=" * 60 + "\n"
        report += "性能测试报告\n"
        report += "=" * 60 + "\n\n"
        
        # 汇总结果
        report += "## 性能汇总\n\n"
        report += "| 模块 | 平均时间(秒) | 吞吐量(次/秒) |\n"
        report += "|------|-------------|--------------|\n"
        
        for key, result in self.results.items():
            module = result.get("module", key)
            avg_time = result.get("avg_time", result.get("total_avg_time", 0))
            throughput = result.get("throughput", 0)
            
            report += f"| {module} | {avg_time:.4f} | {throughput:.2f} |\n"
        
        # 性能瓶颈分析
        report += "\n## 性能瓶颈分析\n\n"
        
        # 找出最慢的模块
        slowest = max(
            self.results.items(),
            key=lambda x: x[1].get("avg_time", x[1].get("total_avg_time", 0))
        )
        
        report += f"**最慢的模块**：{slowest[1].get('module', slowest[0])}\n"
        report += f"- 平均时间：{slowest[1].get('avg_time', slowest[1].get('total_avg_time', 0)):.4f}秒\n"
        
        # 优化建议
        report += "\n## 优化建议\n\n"
        
        for key, result in self.results.items():
            avg_time = result.get("avg_time", result.get("total_avg_time", 0))
            if avg_time > 0.1:  # 如果超过100ms
                module = result.get("module", key)
                report += f"- **{module}**：平均时间 {avg_time:.4f}秒，建议优化\n"
        
        return report
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("=" * 60)
        print("开始性能测试")
        print("=" * 60)
        
        # 测试各个模块
        self.test_module_a_segmentation(iterations=10)
        self.test_module_a_annotation(iterations=10)
        self.test_module_b_difficulty_detection(iterations=100)
        self.test_module_c_path_generation(iterations=50)
        self.test_module_d_resource_generation(iterations=20)
        self.test_batch_operations()
        
        # 生成报告
        report = self.generate_report()
        print(report)
        
        # 保存报告
        with open("algorithm/性能测试报告.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n性能测试报告已保存到：algorithm/性能测试报告.md")


if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_all_tests()
