"""
学习路径生成算法单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path_generator import LearningPathGenerator, NextSuggestion
from tests.mock_data import MOCK_MASTERY_STATUS, MOCK_DEPENDENCIES


class TestLearningPathGenerator:
    """学习路径生成器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.generator = LearningPathGenerator()
    
    def test_generate_path_basic(self):
        """测试基本路径生成"""
        mastery_status = {1: "未学", 2: "未学", 3: "未学"}
        dependencies = [(1, 2, "prerequisite"), (2, 3, "prerequisite")]
        
        path = self.generator.generate_path(
            user_id=1,
            mastery_status=mastery_status,
            dependencies=dependencies
        )
        
        assert isinstance(path, list)
        assert len(path) > 0
    
    def test_filter_mastered(self):
        """测试过滤已掌握的知识点"""
        knowledge_points = [1, 2, 3, 4]
        mastery_status = {1: "已掌握", 2: "未学", 3: "学习中", 4: "已掌握"}
        
        unmastered = self.generator.filter_mastered(knowledge_points, mastery_status)
        
        assert 1 not in unmastered
        assert 4 not in unmastered
        assert 2 in unmastered
        assert 3 in unmastered
    
    def test_get_next_suggestion(self):
        """测试获取下一步建议"""
        path = [
            {"knowledge_point_id": 1, "order": 1, "reason": "基础", "node_type": "knowledge_point"},
            {"knowledge_point_id": 2, "order": 2, "reason": "进阶", "node_type": "knowledge_point"},
        ]
        
        suggestion = self.generator.get_next_suggestion(path, current_position=0)
        
        assert suggestion is not None
        assert isinstance(suggestion, NextSuggestion)
        assert suggestion.next_knowledge_point_id == 1
        assert suggestion.estimated_time > 0


class TestPathAdjuster:
    """路径调整器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        from path_adjuster import PathAdjuster, LearningEvent
        from datetime import datetime
        
        self.adjuster = PathAdjuster()
        self.current_path = [
            {"knowledge_point_id": 1, "order": 1, "reason": "基础", "node_type": "knowledge_point"},
            {"knowledge_point_id": 2, "order": 2, "reason": "进阶", "node_type": "knowledge_point"},
        ]
        self.datetime = datetime
    
    def test_adjust_path_mastered(self):
        """测试掌握事件调整"""
        from path_adjuster import LearningEvent
        
        event = LearningEvent(
            event_type="mastered",
            knowledge_point_id=1,
            timestamp=self.datetime.now()
        )
        
        result = self.adjuster.adjust_path(self.current_path, event)
        
        assert len(result.adjusted_path) < len(self.current_path)
        assert all(node["knowledge_point_id"] != 1 for node in result.adjusted_path 
                  if node.get("node_type") == "knowledge_point")
    
    def test_adjust_path_difficult(self):
        """测试疑难事件调整"""
        from path_adjuster import LearningEvent
        
        event = LearningEvent(
            event_type="difficult",
            knowledge_point_id=2,
            timestamp=self.datetime.now()
        )
        
        result = self.adjuster.adjust_path(self.current_path, event)
        
        # 应该插入补偿资源节点
        has_remedial = any(
            node.get("node_type") == "remedial_resource" 
            and node.get("knowledge_point_id") == 2
            for node in result.adjusted_path
        )
        assert has_remedial


class TestRemedialResourceStrategy:
    """补偿资源推送策略测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        from remedial_resource_strategy import RemedialResourceStrategy, DifficultyLevel
        
        self.strategy = RemedialResourceStrategy()
        self.DifficultyLevel = DifficultyLevel
    
    def test_should_push_resource(self):
        """测试是否应该推送资源"""
        result = self.strategy.should_push_resource(1, 1)
        assert isinstance(result, bool)
    
    def test_get_push_strategy(self):
        """测试获取推送策略"""
        strategy = self.strategy.get_push_strategy(self.DifficultyLevel.FIRST, 1)
        
        assert strategy.level == self.DifficultyLevel.FIRST
        assert "knowledge_card" in strategy.resources
        assert "exercise" in strategy.resources
    
    def test_handle_feedback(self):
        """测试处理反馈"""
        # 先推送资源
        push_strategy = self.strategy.get_push_strategy(self.DifficultyLevel.FIRST, 1)
        self.strategy.push_resource(1, 10, push_strategy)
        
        # 处理反馈
        result = self.strategy.handle_feedback(
            user_id=1,
            resource_id=10,
            feedback_type="mastered",
            exercise_score=0.9
        )
        
        assert "action" in result
        assert result["action"] == "continue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
