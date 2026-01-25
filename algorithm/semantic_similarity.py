"""
语义相似度计算模块

提供统一的语义相似度计算接口，支持多种实现方式：
1. 简单实现（基于关键词，无需额外依赖）
2. sentence-transformers实现（需要安装，效果更好）
"""

import logging
from typing import Optional
import warnings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using simple similarity")


class SemanticSimilarityCalculator:
    """语义相似度计算器
    
    支持两种模式：
    1. 简单模式：基于关键词重叠（无需额外依赖）
    2. 高级模式：使用sentence-transformers（需要安装，效果更好）
    """
    
    def __init__(self, use_advanced: bool = False, model_name: Optional[str] = None):
        """初始化语义相似度计算器
        
        Args:
            use_advanced: 是否使用sentence-transformers（需要先安装）
            model_name: 模型名称，如果为None则使用默认模型
        """
        self.use_advanced = use_advanced and SENTENCE_TRANSFORMERS_AVAILABLE
        self.model = None
        
        if self.use_advanced:
            try:
                # 使用中文语义相似度模型
                model_name = model_name or "paraphrase-multilingual-MiniLM-L12-v2"
                logger.info(f"Loading sentence-transformers model: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers model: {e}")
                logger.warning("Falling back to simple similarity")
                self.use_advanced = False
        
        if not self.use_advanced:
            logger.info("Using simple keyword-based similarity")
    
    def calculate(self, text1: str, text2: str) -> float:
        """计算两个文本的语义相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1），1表示完全相同，0表示完全不同
        """
        if not text1 or not text2:
            return 0.0
        
        if self.use_advanced and self.model:
            return self._calculate_advanced(text1, text2)
        else:
            return self._calculate_simple(text1, text2)
    
    def _calculate_advanced(self, text1: str, text2: str) -> float:
        """使用sentence-transformers计算相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1）
        """
        try:
            # 编码文本
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            
            # 计算余弦相似度
            from torch.nn.functional import cosine_similarity
            similarity = cosine_similarity(embeddings[0:1], embeddings[1:2]).item()
            
            # 归一化到0-1范围（余弦相似度范围是-1到1）
            similarity = (similarity + 1) / 2
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.warning(f"Error in advanced similarity calculation: {e}")
            return self._calculate_simple(text1, text2)
    
    def _calculate_simple(self, text1: str, text2: str) -> float:
        """使用简单方法计算相似度（基于关键词重叠）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1）
        """
        try:
            import jieba
            import jieba.analyse
            
            # 提取关键词
            keywords1 = set(jieba.analyse.extract_tags(text1, topK=10, withWeight=False))
            keywords2 = set(jieba.analyse.extract_tags(text2, topK=10, withWeight=False))
            
            if not keywords1 or not keywords2:
                # 如果无法提取关键词，使用词汇重叠
                words1 = set(text1.split())
                words2 = set(text2.split())
                if not words1 or not words2:
                    return 0.0
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                return intersection / union if union > 0 else 0.0
            
            # 计算Jaccard相似度
            intersection = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            
            similarity = intersection / union if union > 0 else 0.0
            
            return similarity
            
        except Exception as e:
            logger.warning(f"Error in simple similarity calculation: {e}")
            # 最后的备选方案：基于字符重叠
            words1 = set(text1)
            words2 = set(text2)
            if not words1 or not words2:
                return 0.0
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0


# 全局实例（延迟初始化）
_global_calculator: Optional[SemanticSimilarityCalculator] = None


def get_similarity_calculator(use_advanced: bool = False) -> SemanticSimilarityCalculator:
    """获取语义相似度计算器实例（单例模式）
    
    Args:
        use_advanced: 是否使用高级模式
    
    Returns:
        语义相似度计算器实例
    """
    global _global_calculator
    
    if _global_calculator is None:
        _global_calculator = SemanticSimilarityCalculator(use_advanced=use_advanced)
    
    return _global_calculator


def calculate_similarity(text1: str, text2: str, use_advanced: bool = False) -> float:
    """便捷函数：计算两个文本的相似度
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        use_advanced: 是否使用高级模式
    
    Returns:
        相似度分数（0-1）
    """
    calculator = get_similarity_calculator(use_advanced=use_advanced)
    return calculator.calculate(text1, text2)
