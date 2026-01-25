"""
知识点切分算法单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_point_segmenter import KnowledgePointSegmenter, KnowledgePoint
from tests.mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS


class TestKnowledgePointSegmenter:
    """知识点切分器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.segmenter = KnowledgePointSegmenter(
            similarity_threshold=0.7,
            min_duration=120.0,
            max_duration=600.0
        )
    
    def test_segment_basic(self):
        """测试基本切分功能"""
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        
        assert len(knowledge_points) > 0, "应该至少生成一个知识点"
        assert all(isinstance(kp, KnowledgePoint) for kp in knowledge_points), "所有结果应该是KnowledgePoint对象"
    
    def test_segment_output_format(self):
        """测试输出格式"""
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        
        for kp in knowledge_points:
            assert hasattr(kp, 'name'), "知识点应该有name属性"
            assert hasattr(kp, 'start_time'), "知识点应该有start_time属性"
            assert hasattr(kp, 'end_time'), "知识点应该有end_time属性"
            assert hasattr(kp, 'keywords'), "知识点应该有keywords属性"
            assert hasattr(kp, 'summary'), "知识点应该有summary属性"
            assert hasattr(kp, 'difficulty'), "知识点应该有difficulty属性"
            
            assert isinstance(kp.name, str), "name应该是字符串"
            assert isinstance(kp.start_time, float), "start_time应该是浮点数"
            assert isinstance(kp.end_time, float), "end_time应该是浮点数"
            assert isinstance(kp.keywords, list), "keywords应该是列表"
            assert isinstance(kp.summary, str), "summary应该是字符串"
            assert kp.difficulty in ["easy", "medium", "hard"], "difficulty应该是easy/medium/hard之一"
    
    def test_segment_time_range(self):
        """测试知识点时长范围"""
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        
        for kp in knowledge_points:
            duration = kp.end_time - kp.start_time
            assert duration >= self.segmenter.min_duration, f"知识点时长应该 >= {self.segmenter.min_duration}秒"
            assert duration <= self.segmenter.max_duration, f"知识点时长应该 <= {self.segmenter.max_duration}秒"
            assert kp.start_time < kp.end_time, "开始时间应该小于结束时间"
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        text1 = "函数是一种映射关系"
        text2 = "函数是一种映射关系"
        similarity = self.segmenter.calculate_similarity(text1, text2)
        
        assert 0 <= similarity <= 1, "相似度应该在0-1之间"
        assert similarity > 0.5, "相同文本的相似度应该较高"
    
    def test_calculate_similarity_different(self):
        """测试不同文本的相似度"""
        text1 = "函数是一种映射关系"
        text2 = "今天天气很好"
        similarity = self.segmenter.calculate_similarity(text1, text2)
        
        assert 0 <= similarity <= 1, "相似度应该在0-1之间"
        assert similarity < 0.5, "不同文本的相似度应该较低"
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"
        keywords = self.segmenter.extract_keywords(text, top_k=5)
        
        assert isinstance(keywords, list), "关键词应该是列表"
        assert len(keywords) <= 5, "关键词数量应该 <= top_k"
        assert all(isinstance(kw, str) for kw in keywords), "所有关键词应该是字符串"
    
    def test_generate_summary(self):
        """测试摘要生成"""
        text = "函数是一种映射关系。" * 10
        summary = self.segmenter.generate_summary(text, max_length=100)
        
        assert isinstance(summary, str), "摘要应该是字符串"
        assert len(summary) <= 100, "摘要长度应该 <= max_length"
        assert len(summary) > 0, "摘要不应该为空"
    
    def test_detect_topic_shift(self):
        """测试话题转换点检测"""
        texts = [
            {"start_time": 0.0, "end_time": 120.0, "text": "函数定义"},
            {"start_time": 120.0, "end_time": 240.0, "text": "函数参数"},
            {"start_time": 240.0, "end_time": 360.0, "text": "今天天气很好"},
        ]
        
        shifts = self.segmenter.detect_topic_shift(texts)
        
        assert isinstance(shifts, list), "切分点应该是列表"
        assert all(isinstance(s, int) for s in shifts), "所有切分点应该是整数"
    
    def test_segment_empty_input(self):
        """测试空输入"""
        knowledge_points = self.segmenter.segment([])
        
        assert len(knowledge_points) == 0, "空输入应该返回空列表"
    
    def test_segment_only_asr(self):
        """测试只有ASR文本的情况"""
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS)
        
        assert len(knowledge_points) > 0, "只有ASR文本也应该能切分"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
