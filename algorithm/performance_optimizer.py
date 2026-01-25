"""
性能优化工具

提供性能优化建议和实现。
"""

import logging
from typing import List, Dict, Callable
import functools
import time
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        """初始化性能优化器"""
        self.cache: Dict[str, any] = {}
        self.call_stats: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "total_time": 0.0})
    
    def cache_result(self, key_func: Callable = None, ttl: int = 3600):
        """缓存装饰器
        
        缓存函数结果，避免重复计算。
        
        Args:
            key_func: 生成缓存键的函数
            ttl: 缓存过期时间（秒）
        
        Returns:
            装饰器函数
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # 检查缓存
                if cache_key in self.cache:
                    cached_result, cached_time = self.cache[cache_key]
                    if time.time() - cached_time < ttl:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cached_result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                self.cache[cache_key] = (result, time.time())
                
                return result
            
            return wrapper
        return decorator
    
    def profile_function(self, func: Callable):
        """性能分析装饰器
        
        记录函数调用次数和总耗时。
        
        Args:
            func: 要分析的函数
        
        Returns:
            装饰后的函数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # 记录统计信息
            func_name = func.__name__
            self.call_stats[func_name]["count"] += 1
            self.call_stats[func_name]["total_time"] += elapsed
            
            return result
        
        return wrapper
    
    def get_optimization_suggestions(self) -> List[Dict]:
        """获取优化建议
        
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 分析调用统计
        for func_name, stats in self.call_stats.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            
            if avg_time > 0.1:  # 如果平均时间超过100ms
                suggestions.append({
                    "function": func_name,
                    "issue": f"平均执行时间 {avg_time:.4f}秒，调用 {stats['count']} 次",
                    "suggestion": "考虑使用缓存或优化算法"
                })
        
        return suggestions
    
    def optimize_database_queries(self) -> List[str]:
        """数据库查询优化建议
        
        Returns:
            优化建议列表
        """
        suggestions = [
            "为常用查询字段添加索引",
            "使用批量查询代替循环查询",
            "使用连接查询代替子查询",
            "避免SELECT *，只查询需要的字段",
            "使用分页查询处理大量数据",
            "考虑使用Redis缓存热点数据"
        ]
        
        return suggestions
    
    def optimize_algorithm_complexity(self) -> List[Dict]:
        """算法复杂度优化建议
        
        Returns:
            优化建议列表
        """
        suggestions = [
            {
                "module": "知识点切分",
                "current": "O(n²) - 相似度计算",
                "optimization": "使用滑动窗口或批量计算，降低到O(n log n)"
            },
            {
                "module": "知识图谱构建",
                "current": "O(n²) - 关系检测",
                "optimization": "使用索引或哈希表，降低到O(n)"
            },
            {
                "module": "学习路径生成",
                "current": "O(n²) - 拓扑排序",
                "optimization": "使用优化的图算法，降低到O(n + m)"
            }
        ]
        
        return suggestions


def optimize_segmentation_with_cache(segmenter):
    """优化知识点切分：添加缓存"""
    original_segment = segmenter.segment
    
    @functools.lru_cache(maxsize=100)
    def cached_similarity(text1, text2):
        return segmenter.calculate_similarity(text1, text2)
    
    def optimized_segment(asr_texts, ocr_texts=None, subtitles=None):
        # 使用缓存的相似度计算
        segmenter.calculate_similarity = cached_similarity
        return original_segment(asr_texts, ocr_texts, subtitles)
    
    segmenter.segment = optimized_segment
    return segmenter


def optimize_batch_processing(detector):
    """优化批量处理：使用向量化计算"""
    original_batch_detect = detector.batch_detect
    
    def optimized_batch_detect(behavior_data_list):
        # 批量计算困难度分数
        scores = []
        for behavior_data in behavior_data_list:
            score = detector.calculate_difficulty_score(behavior_data)
            scores.append(score)
        
        # 批量判断
        results = []
        for i, behavior_data in enumerate(behavior_data_list):
            trigger_reasons = detector.get_trigger_reasons(behavior_data)
            is_difficult = len(trigger_reasons) > 0 or scores[i] >= 1.0
            confidence = detector._calculate_confidence(behavior_data, trigger_reasons, scores[i])
            
            from difficulty_detector import DifficultyResult
            result = DifficultyResult(
                is_difficult=is_difficult,
                difficulty_score=min(scores[i], 10.0),
                trigger_reasons=trigger_reasons,
                confidence=confidence
            )
            results.append((behavior_data, result))
        
        return results
    
    detector.batch_detect = optimized_batch_detect
    return detector


# 使用示例
if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    
    # 获取优化建议
    print("=" * 60)
    print("性能优化建议")
    print("=" * 60)
    
    print("\n数据库查询优化：")
    db_suggestions = optimizer.optimize_database_queries()
    for i, suggestion in enumerate(db_suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print("\n算法复杂度优化：")
    algo_suggestions = optimizer.optimize_algorithm_complexity()
    for suggestion in algo_suggestions:
        print(f"  - {suggestion['module']}: {suggestion['current']} -> {suggestion['optimization']}")
