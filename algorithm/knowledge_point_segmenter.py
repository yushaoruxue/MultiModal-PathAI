"""
知识点自动切分算法

基于ASR转写文本和OCR识别文本，自动切分视频知识点。
使用语义相似度检测话题转换点，结合OCR幻灯片切换点进行切分。
"""

import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
import jieba
import jieba.analyse
from dataclasses import dataclass

# 导入语义相似度计算模块
try:
    from semantic_similarity import SemanticSimilarityCalculator
    SEMANTIC_SIMILARITY_AVAILABLE = True
except ImportError:
    SEMANTIC_SIMILARITY_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgePoint:
    """知识点数据类"""
    name: str
    start_time: float
    end_time: float
    keywords: List[str]
    summary: str
    difficulty: str = "medium"


class KnowledgePointSegmenter:
    """知识点切分器
    
    基于文本语义相似度进行知识点切分，识别话题转换点。
    结合OCR的幻灯片切换点进行切分，确保每个知识点时长在2-10分钟。
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        min_duration: float = 120.0,  # 2分钟
        max_duration: float = 600.0,  # 10分钟
        window_size: int = 3,
        use_advanced_similarity: bool = False
    ):
        """初始化知识点切分器
        
        Args:
            similarity_threshold: 语义相似度阈值，低于此值认为话题转换
            min_duration: 知识点最小时长（秒）
            max_duration: 知识点最大时长（秒）
            window_size: 滑动窗口大小，用于计算相似度
            use_advanced_similarity: 是否使用sentence-transformers（需要安装）
        """
        self.similarity_threshold = similarity_threshold
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.window_size = window_size
        
        # 初始化jieba
        jieba.initialize()
        
        # 初始化语义相似度计算器
        if SEMANTIC_SIMILARITY_AVAILABLE and use_advanced_similarity:
            self.similarity_calculator = SemanticSimilarityCalculator(use_advanced=True)
            logger.info("Using advanced similarity calculation (sentence-transformers)")
        else:
            self.similarity_calculator = None
            logger.info("Using simple similarity calculation")
        
        logger.info(f"KnowledgePointSegmenter initialized with threshold={similarity_threshold}")
    
    def segment(
        self,
        asr_texts: List[Dict],
        ocr_texts: Optional[List[Dict]] = None,
        subtitles: Optional[List[Dict]] = None
    ) -> List[KnowledgePoint]:
        """切分知识点
        
        算法流程：
        1. 合并ASR和OCR文本，按时间戳排序
        2. 使用滑动窗口计算语义相似度
        3. 识别话题转换点（相似度低于阈值）
        4. 结合OCR幻灯片切换点
        5. 根据时长要求调整切分点
        6. 生成知识点列表
        
        Args:
            asr_texts: ASR转写文本列表，格式：[{"start_time": float, "end_time": float, "text": str}, ...]
            ocr_texts: OCR识别文本列表，格式：[{"start_time": float, "end_time": float, "text": str, "slide_number": int}, ...]
            subtitles: 字幕文本列表（可选），格式：[{"start_time": float, "end_time": float, "text": str}, ...]
        
        Returns:
            知识点列表，每个知识点包含名称、起止时间、关键词、摘要等
        
        Raises:
            ValueError: 当输入数据格式不正确时
        """
        try:
            logger.info(f"Starting segmentation with {len(asr_texts)} ASR segments")
            
            # 1. 合并和排序文本
            merged_texts = self._merge_and_sort_texts(asr_texts, ocr_texts, subtitles)
            if not merged_texts:
                logger.warning("No texts to segment")
                return []
            
            # 2. 识别话题转换点
            topic_shifts = self.detect_topic_shift(merged_texts)
            logger.info(f"Detected {len(topic_shifts)} topic shifts")
            
            # 3. 结合OCR幻灯片切换点
            if ocr_texts:
                slide_shifts = self._detect_slide_shifts(ocr_texts)
                topic_shifts = self._merge_shifts(topic_shifts, slide_shifts)
            
            # 4. 根据时长要求调整切分点
            adjusted_shifts = self._adjust_by_duration(merged_texts, topic_shifts)
            
            # 5. 生成知识点列表
            knowledge_points = self._generate_knowledge_points(merged_texts, adjusted_shifts)
            
            logger.info(f"Generated {len(knowledge_points)} knowledge points")
            return knowledge_points
            
        except Exception as e:
            logger.error(f"Error in segmentation: {e}", exc_info=True)
            raise
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的语义相似度
        
        优先使用sentence-transformers（如果可用），否则使用关键词重叠。
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1），1表示完全相同，0表示完全不同
        """
        try:
            # 如果使用高级相似度计算器
            if self.similarity_calculator:
                return self.similarity_calculator.calculate(text1, text2)
            
            # 否则使用简单方法（关键词重叠）
            keywords1 = set(self.extract_keywords(text1, top_k=10))
            keywords2 = set(self.extract_keywords(text2, top_k=10))
            
            if not keywords1 or not keywords2:
                return 0.0
            
            # 计算Jaccard相似度
            intersection = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            
            similarity = intersection / union if union > 0 else 0.0
            
            return similarity
            
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0.0
    
    def detect_topic_shift(
        self,
        texts: List[Dict],
        window_size: Optional[int] = None
    ) -> List[int]:
        """检测话题转换点
        
        使用滑动窗口计算相邻文本段的相似度，
        当相似度低于阈值时，认为发生了话题转换。
        
        Args:
            texts: 文本列表，已按时间戳排序
            window_size: 滑动窗口大小，如果为None则使用self.window_size
        
        Returns:
            话题转换点的索引列表
        """
        if window_size is None:
            window_size = self.window_size
        
        if len(texts) < 2:
            return []
        
        topic_shifts = []
        
        for i in range(len(texts) - 1):
            # 获取当前窗口的文本
            current_text = texts[i].get("text", "")
            next_text = texts[i + 1].get("text", "")
            
            if not current_text or not next_text:
                continue
            
            # 计算相似度
            similarity = self.calculate_similarity(current_text, next_text)
            
            # 如果相似度低于阈值，认为是话题转换点
            if similarity < self.similarity_threshold:
                topic_shifts.append(i + 1)
                logger.debug(f"Topic shift detected at index {i+1}, similarity={similarity:.2f}")
        
        return topic_shifts
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词
        
        使用jieba的TF-IDF算法提取关键词。
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词
        
        Returns:
            关键词列表
        """
        try:
            if not text:
                return []
            
            # 使用jieba提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成文本摘要
        
        使用简单的方法生成摘要：提取前几个句子。
        后续可以替换为TextRank或AI模型生成。
        
        Args:
            text: 输入文本
            max_length: 摘要最大长度（字符数）
        
        Returns:
            摘要文本
        """
        try:
            if not text:
                return ""
            
            # 简单实现：取前几个句子
            sentences = text.split('。')
            summary = ""
            
            for sentence in sentences:
                if len(summary) + len(sentence) <= max_length:
                    summary += sentence + "。"
                else:
                    break
            
            # 如果太短，至少返回前max_length个字符
            if len(summary) < 50:
                summary = text[:max_length] + "..." if len(text) > max_length else text
            
            return summary.strip()
            
        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return text[:max_length] if text else ""
    
    def _merge_and_sort_texts(
        self,
        asr_texts: List[Dict],
        ocr_texts: Optional[List[Dict]],
        subtitles: Optional[List[Dict]]
    ) -> List[Dict]:
        """合并并排序文本
        
        将ASR、OCR和字幕文本合并，按时间戳排序。
        
        Args:
            asr_texts: ASR文本列表
            ocr_texts: OCR文本列表
            subtitles: 字幕文本列表
        
        Returns:
            合并并排序后的文本列表
        """
        merged = []
        
        # 添加ASR文本
        for item in asr_texts:
            merged.append({
                "start_time": item.get("start_time", 0.0),
                "end_time": item.get("end_time", 0.0),
                "text": item.get("text", ""),
                "source": "asr"
            })
        
        # 添加OCR文本
        if ocr_texts:
            for item in ocr_texts:
                merged.append({
                    "start_time": item.get("start_time", 0.0),
                    "end_time": item.get("end_time", 0.0),
                    "text": item.get("text", ""),
                    "source": "ocr",
                    "slide_number": item.get("slide_number")
                })
        
        # 添加字幕文本
        if subtitles:
            for item in subtitles:
                merged.append({
                    "start_time": item.get("start_time", 0.0),
                    "end_time": item.get("end_time", 0.0),
                    "text": item.get("text", ""),
                    "source": "subtitle"
                })
        
        # 按开始时间排序
        merged.sort(key=lambda x: x["start_time"])
        
        return merged
    
    def _detect_slide_shifts(self, ocr_texts: List[Dict]) -> List[int]:
        """检测OCR幻灯片切换点
        
        Args:
            ocr_texts: OCR文本列表
        
        Returns:
            幻灯片切换点的索引列表
        """
        shifts = []
        current_slide = None
        
        for i, item in enumerate(ocr_texts):
            slide_num = item.get("slide_number")
            if slide_num is not None and slide_num != current_slide:
                if current_slide is not None:
                    shifts.append(i)
                current_slide = slide_num
        
        return shifts
    
    def _merge_shifts(self, topic_shifts: List[int], slide_shifts: List[int]) -> List[int]:
        """合并话题转换点和幻灯片切换点
        
        Args:
            topic_shifts: 话题转换点索引列表
            slide_shifts: 幻灯片切换点索引列表
        
        Returns:
            合并后的切分点列表（去重并排序）
        """
        all_shifts = set(topic_shifts) | set(slide_shifts)
        return sorted(list(all_shifts))
    
    def _adjust_by_duration(
        self,
        texts: List[Dict],
        shifts: List[int]
    ) -> List[int]:
        """根据时长要求调整切分点
        
        确保每个知识点时长在min_duration和max_duration之间。
        
        Args:
            texts: 文本列表
            shifts: 原始切分点列表
        
        Returns:
            调整后的切分点列表
        """
        if not texts:
            return []
        
        adjusted_shifts = [0]  # 第一个知识点从0开始
        
        for shift in shifts:
            if shift >= len(texts):
                continue
            
            # 计算当前知识点时长
            start_idx = adjusted_shifts[-1]
            end_idx = shift
            
            start_time = texts[start_idx]["start_time"]
            end_time = texts[end_idx]["end_time"]
            duration = end_time - start_time
            
            # 如果时长超过最大值，需要提前切分
            if duration > self.max_duration:
                # 在中间位置添加切分点
                mid_idx = (start_idx + end_idx) // 2
                if mid_idx not in adjusted_shifts:
                    adjusted_shifts.append(mid_idx)
            
            # 如果时长小于最小值，尝试合并到下一个
            elif duration < self.min_duration and shift < len(texts) - 1:
                # 检查是否可以合并
                next_shift = shifts[shifts.index(shift) + 1] if shift in shifts else len(texts) - 1
                next_duration = texts[next_shift]["end_time"] - texts[shift]["end_time"]
                
                if duration + next_duration <= self.max_duration:
                    # 可以合并，跳过当前切分点
                    continue
            
            adjusted_shifts.append(shift)
        
        # 确保最后一个切分点
        if adjusted_shifts[-1] != len(texts) - 1:
            adjusted_shifts.append(len(texts) - 1)
        
        return sorted(list(set(adjusted_shifts)))
    
    def _generate_knowledge_points(
        self,
        texts: List[Dict],
        shifts: List[int]
    ) -> List[KnowledgePoint]:
        """生成知识点列表
        
        Args:
            texts: 文本列表
            shifts: 切分点列表
        
        Returns:
            知识点列表
        """
        knowledge_points = []
        
        for i in range(len(shifts) - 1):
            start_idx = shifts[i]
            end_idx = shifts[i + 1]
            
            # 获取该知识点的所有文本
            segment_texts = texts[start_idx:end_idx + 1]
            combined_text = " ".join([t.get("text", "") for t in segment_texts])
            
            if not combined_text.strip():
                continue
            
            # 计算起止时间
            start_time = segment_texts[0]["start_time"]
            end_time = segment_texts[-1]["end_time"]
            
            # 提取关键词
            keywords = self.extract_keywords(combined_text, top_k=10)
            
            # 生成摘要
            summary = self.generate_summary(combined_text, max_length=200)
            
            # 生成名称（使用第一个关键词或摘要的前几个字）
            if keywords:
                name = keywords[0]
            else:
                name = summary[:15] if summary else f"知识点{i+1}"
            
            # 估算难度（简单规则：根据文本长度和关键词数量）
            difficulty = self._estimate_difficulty(combined_text, keywords)
            
            # 创建知识点对象
            kp = KnowledgePoint(
                name=name,
                start_time=start_time,
                end_time=end_time,
                keywords=keywords,
                summary=summary,
                difficulty=difficulty
            )
            
            knowledge_points.append(kp)
        
        return knowledge_points
    
    def _estimate_difficulty(self, text: str, keywords: List[str]) -> str:
        """估算知识点难度
        
        简单规则：
        - 文本长度 > 500字 且 关键词 > 8个 -> hard
        - 文本长度 < 200字 且 关键词 < 5个 -> easy
        - 其他 -> medium
        
        Args:
            text: 文本内容
            keywords: 关键词列表
        
        Returns:
            难度等级：easy/medium/hard
        """
        text_length = len(text)
        keyword_count = len(keywords)
        
        if text_length > 500 and keyword_count > 8:
            return "hard"
        elif text_length < 200 and keyword_count < 5:
            return "easy"
        else:
            return "medium"


# 使用示例
if __name__ == "__main__":
    import sys
    import os
    # 添加tests目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
    from mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS
    
    # 创建切分器
    segmenter = KnowledgePointSegmenter(
        similarity_threshold=0.7,
        min_duration=120.0,
        max_duration=600.0
    )
    
    # 执行切分
    knowledge_points = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    
    # 输出结果
    print(f"\n生成了 {len(knowledge_points)} 个知识点：\n")
    for i, kp in enumerate(knowledge_points, 1):
        print(f"知识点 {i}: {kp.name}")
        print(f"  时间: {kp.start_time:.1f}s - {kp.end_time:.1f}s")
        print(f"  关键词: {', '.join(kp.keywords[:5])}")
        print(f"  摘要: {kp.summary[:100]}...")
        print(f"  难度: {kp.difficulty}")
        print()
