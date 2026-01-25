"""
知识点自动标注单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_point_annotator import KnowledgePointAnnotator
from tests.mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS


class TestKnowledgePointAnnotator:
    """知识点标注器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.annotator = KnowledgePointAnnotator()
    
    def test_annotate_basic(self):
        """测试基本标注功能"""
        text = "函数是一种映射关系，它将输入映射到输出。"
        result = self.annotator.annotate(text)
        
        assert "name" in result
        assert "summary" in result
        assert "keywords" in result
        assert "difficulty" in result
        assert "type" in result
        assert "metadata" in result
    
    def test_generate_name(self):
        """测试名称生成"""
        text = "函数是一种映射关系，它将输入映射到输出。"
        name = self.annotator.generate_name(text)
        
        assert isinstance(name, str)
        assert len(name) > 0
        assert len(name) <= self.annotator.name_max_length
    
    def test_generate_summary(self):
        """测试摘要生成"""
        text = "函数是一种映射关系。" * 10
        summary = self.annotator.generate_summary(text)
        
        assert isinstance(summary, str)
        assert len(summary) >= self.annotator.summary_min_length
        assert len(summary) <= self.annotator.summary_max_length
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"
        keywords = self.annotator.extract_keywords(text, top_k=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert all(isinstance(kw, str) for kw in keywords)
        assert all(len(kw) > 1 for kw in keywords)  # 过滤单字符
    
    def test_estimate_difficulty(self):
        """测试难度估算"""
        # 简单文本
        easy_text = "函数是映射。"
        easy_difficulty = self.annotator.estimate_difficulty(easy_text)
        assert easy_difficulty in ["easy", "medium", "hard"]
        
        # 复杂文本
        hard_text = "函数是一种映射关系。" * 50
        hard_difficulty = self.annotator.estimate_difficulty(hard_text)
        assert hard_difficulty in ["easy", "medium", "hard"]
    
    def test_classify_type(self):
        """测试类型分类"""
        # 概念定义
        concept_text = "函数是一种映射关系的定义。"
        concept_type = self.annotator.classify_type(concept_text)
        assert concept_type in ["concept", "example", "practice", "summary"]
        
        # 例题
        example_text = "让我们看一个例子。"
        example_type = self.annotator.classify_type(example_text)
        assert example_type in ["concept", "example", "practice", "summary"]
    
    def test_annotate_with_asr_ocr(self):
        """测试使用ASR和OCR文本进行标注"""
        text = "函数定义"
        result = self.annotator.annotate(
            knowledge_point_text=text,
            asr_texts=MOCK_ASR_TEXTS[:3],
            ocr_texts=MOCK_OCR_TEXTS[:2]
        )
        
        assert "name" in result
        assert "summary" in result
        assert len(result["keywords"]) > 0
    
    def test_annotate_empty_text(self):
        """测试空文本"""
        result = self.annotator.annotate("")
        
        assert result["name"] == "未命名知识点"
        assert isinstance(result["summary"], str)
    
    def test_extract_keywords_empty(self):
        """测试空文本关键词提取"""
        keywords = self.annotator.extract_keywords("")
        assert keywords == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
