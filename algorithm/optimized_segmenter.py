"""
优化版知识点切分器

实现性能优化：缓存、批量计算等。
"""

import logging
from functools import lru_cache
from typing import List, Dict, Optional
from knowledge_point_segmenter import KnowledgePointSegmenter, KnowledgePoint

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizedKnowledgePointSegmenter(KnowledgePointSegmenter):
    """优化版知识点切分器
    
    优化点：
    1. 使用LRU缓存缓存相似度计算结果
    2. 优化话题转换点检测算法（只计算相邻文本段）
    3. 批量处理相似度计算
    """
    
    def __init__(self, *args, **kwargs):
        """初始化优化版切分器"""
        super().__init__(*args, **kwargs)
        
        # 使用LRU缓存缓存相似度计算结果
        self._cached_similarity = lru_cache(maxsize=1000)(self._calculate_similarity_impl)
        
        logger.info("OptimizedKnowledgePointSegmenter initialized with caching")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算相似度（使用缓存）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数
        """
        # 使用缓存的相似度计算
        return self._cached_similarity(text1, text2)
    
    def _calculate_similarity_impl(self, text1: str, text2: str) -> float:
        """相似度计算实现（被缓存包装）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数
        """
        # 调用父类的计算逻辑
        return super().calculate_similarity(text1, text2)
    
    def detect_topic_shift(
        self,
        texts: List[Dict],
        window_size: Optional[int] = None
    ) -> List[int]:
        """优化版话题转换点检测
        
        只计算相邻文本段的相似度，复杂度从O(n²)降到O(n)。
        
        Args:
            texts: 文本列表
            window_size: 滑动窗口大小（未使用，保持接口兼容）
        
        Returns:
            话题转换点索引列表
        """
        if len(texts) < 2:
            return []
        
        topic_shifts = []
        
        # 只计算相邻文本段的相似度
        for i in range(len(texts) - 1):
            current_text = texts[i].get("text", "")
            next_text = texts[i + 1].get("text", "")
            
            if not current_text or not next_text:
                continue
            
            # 使用缓存的相似度计算
            similarity = self.calculate_similarity(current_text, next_text)
            
            if similarity < self.similarity_threshold:
                topic_shifts.append(i + 1)
                logger.debug(f"Topic shift detected at index {i+1}, similarity={similarity:.2f}")
        
        return topic_shifts
    
    def clear_cache(self):
        """清空缓存"""
        self._cached_similarity.cache_clear()
        logger.info("Cache cleared")


# 使用示例
if __name__ == "__main__":
    from tests.mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS
    import time
    
    # 创建优化版切分器
    segmenter = OptimizedKnowledgePointSegmenter()
    
    # 测试性能
    print("测试优化版切分器性能...")
    
    # 第一次运行（需要计算）
    start_time = time.time()
    kps1 = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    time1 = time.time() - start_time
    print(f"第一次运行: {time1:.4f}秒，生成 {len(kps1)} 个知识点")
    
    # 第二次运行（使用缓存）
    start_time = time.time()
    kps2 = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    time2 = time.time() - start_time
    print(f"第二次运行（使用缓存）: {time2:.4f}秒，生成 {len(kps2)} 个知识点")
    
    if time1 > 0:
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"性能提升: {speedup:.2f}x")
