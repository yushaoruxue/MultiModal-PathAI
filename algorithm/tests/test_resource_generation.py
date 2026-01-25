"""
补偿资源生成模块单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_card_generator import KnowledgeCardGenerator, KnowledgePointInfo as KPInfo
from exercise_generator import ExerciseGenerator, Exercise
from resource_pusher import ResourcePusher, Resource
from resource_quality_evaluator import ResourceQualityEvaluator, QualityScore


class TestKnowledgeCardGenerator:
    """知识卡片生成器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.generator = KnowledgeCardGenerator(use_ai=False)
        self.kp_info = KPInfo(
            id=10,
            name="函数定义",
            summary="函数是一种映射关系，它将输入映射到输出。",
            keywords=["函数", "映射", "定义"],
            difficulty="medium"
        )
    
    def test_generate_card(self):
        """测试生成知识卡片"""
        card = self.generator.generate_card(self.kp_info)
        
        assert isinstance(card, str)
        assert len(card) > 0
        assert "函数定义" in card  # 应该包含知识点名称
    
    def test_extract_core_concept(self):
        """测试提取核心概念"""
        text = "函数是一种映射关系，它将输入映射到输出。"
        concept = self.generator.extract_core_concept(text, self.kp_info)
        
        assert isinstance(concept, str)
        assert len(concept) > 0
    
    def test_extract_formulas(self):
        """测试提取公式"""
        text = "函数 f(x) = x + 1 是一个简单的例子。"
        formulas = self.generator.extract_formulas(text)
        
        assert isinstance(formulas, list)


class TestExerciseGenerator:
    """练习题生成器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.generator = ExerciseGenerator(use_ai=False)
        self.kp_info = KPInfo(
            id=10,
            name="函数定义",
            summary="函数是一种映射关系。",
            keywords=["函数", "映射"],
            difficulty="medium"
        )
    
    def test_generate_exercises(self):
        """测试生成练习题"""
        exercises = self.generator.generate_exercises(self.kp_info, count=3)
        
        assert isinstance(exercises, list)
        assert len(exercises) > 0
        assert all(isinstance(ex, Exercise) for ex in exercises)
    
    def test_generate_choice_question(self):
        """测试生成选择题"""
        exercise = self.generator.generate_choice_question(self.kp_info)
        
        assert exercise.type == "choice"
        assert exercise.options is not None
        assert len(exercise.options) >= 2
        assert exercise.correct_answer in ["A", "B", "C", "D"]
    
    def test_validate_question(self):
        """测试验证题目"""
        exercise = Exercise(
            question="测试题目？",
            type="choice",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="解析",
            difficulty="medium"
        )
        
        is_valid = self.generator.validate_question(exercise)
        assert isinstance(is_valid, bool)


class TestResourcePusher:
    """资源推送器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.pusher = ResourcePusher(push_method="database")
    
    def test_push_resource(self):
        """测试推送资源"""
        success = self.pusher.push_resource(
            user_id=1,
            knowledge_point_id=10,
            resource_type="knowledge_card",
            resource_content="# 测试卡片"
        )
        
        assert isinstance(success, bool)
    
    def test_get_pending_resources(self):
        """测试获取待推送资源"""
        # 先推送一个资源
        self.pusher.push_resource(1, 10, "knowledge_card", "# 测试")
        
        # 获取待推送资源
        pending = self.pusher.get_pending_resources(1)
        
        assert isinstance(pending, list)
    
    def test_mark_as_read(self):
        """测试标记为已读"""
        # 先推送一个资源
        self.pusher.push_resource(1, 10, "knowledge_card", "# 测试")
        
        # 获取资源ID
        pending = self.pusher.get_pending_resources(1)
        if pending:
            resource_id = pending[0]["resource_id"]
            success = self.pusher.mark_as_read(1, resource_id)
            assert success


class TestResourceQualityEvaluator:
    """资源质量评估器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.evaluator = ResourceQualityEvaluator()
    
    def test_evaluate_content_quality(self):
        """测试评估内容质量"""
        content = "# 测试\n\n这是测试内容。"
        result = self.evaluator.evaluate_content_quality(content)
        
        assert "accuracy" in result
        assert "completeness" in result
        assert "clarity" in result
        assert "overall" in result
    
    def test_evaluate_relevance(self):
        """测试评估相关性"""
        content = "函数是一种映射关系。"
        kp_info = {"name": "函数定义", "keywords": ["函数", "映射"]}
        
        relevance = self.evaluator.evaluate_relevance(content, kp_info)
        
        assert 0 <= relevance <= 1
    
    def test_get_quality_score(self):
        """测试获取质量分数"""
        content = "# 函数定义\n\n函数是一种映射关系。"
        kp_info = {"name": "函数定义", "keywords": ["函数"]}
        
        score = self.evaluator.get_quality_score(
            resource_id="test_001",
            resource_content=content,
            knowledge_point_info=kp_info,
            student_feedback="mastered",
            exercise_score=0.9
        )
        
        assert isinstance(score, QualityScore)
        assert 0 <= score.overall_score <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
