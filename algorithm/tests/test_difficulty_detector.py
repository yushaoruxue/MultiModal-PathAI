"""
难点识别算法单元测试
"""

import pytest
import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from difficulty_detector import (
    DifficultyDetector,
    BehaviorData,
    KnowledgePointInfo,
    DifficultyResult
)


class TestDifficultyDetector:
    """难点识别器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.detector = DifficultyDetector()
    
    def test_detect_basic(self):
        """测试基本检测功能"""
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=3,
            pause_count=5,
            total_watch_time=600.0,
            knowledge_point_duration=200.0,
            seek_count=2
        )
        
        result = self.detector.detect(behavior_data)
        
        assert isinstance(result, DifficultyResult)
        assert isinstance(result.is_difficult, bool)
        assert 0 <= result.difficulty_score <= 10
        assert isinstance(result.trigger_reasons, list)
        assert 0 <= result.confidence <= 1
    
    def test_calculate_difficulty_score(self):
        """测试困难度分数计算"""
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=2,
            pause_count=3,
            total_watch_time=600.0,
            knowledge_point_duration=200.0,
            seek_count=5
        )
        
        score = self.detector.calculate_difficulty_score(behavior_data)
        
        assert 0 <= score <= 10
        assert isinstance(score, float)
    
    def test_get_trigger_reasons(self):
        """测试触发原因获取"""
        # 回放次数过多
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=3,  # >= 2
            pause_count=1,
            total_watch_time=200.0,
            knowledge_point_duration=200.0,
            seek_count=1
        )
        
        reasons = self.detector.get_trigger_reasons(behavior_data)
        
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        assert any("回放" in reason for reason in reasons)
    
    def test_detect_no_difficulty(self):
        """测试无难点的情况"""
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=0,
            pause_count=1,
            total_watch_time=200.0,
            knowledge_point_duration=200.0,
            seek_count=1
        )
        
        result = self.detector.detect(behavior_data)
        
        # 应该不是疑难点
        assert result.is_difficult == False or len(result.trigger_reasons) == 0
    
    def test_detect_multiple_triggers(self):
        """测试多个触发条件"""
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=3,  # 触发
            pause_count=5,   # 触发
            total_watch_time=800.0,  # 触发（4倍）
            knowledge_point_duration=200.0,
            seek_count=6     # 触发
        )
        
        result = self.detector.detect(behavior_data)
        
        assert result.is_difficult == True
        assert len(result.trigger_reasons) >= 2
    
    def test_update_thresholds(self):
        """测试更新阈值"""
        new_thresholds = {"replay": 5.0, "pause": 10.0}
        self.detector.update_thresholds(new_thresholds)
        
        assert self.detector.thresholds["replay"] == 5.0
        assert self.detector.thresholds["pause"] == 10.0
    
    def test_update_weights(self):
        """测试更新权重"""
        new_weights = {"replay": 0.5, "pause": 0.5}
        self.detector.update_weights(new_weights)
        
        # 权重应该归一化
        total = sum(self.detector.weights.values())
        assert abs(total - 1.0) < 0.01
    
    def test_batch_detect(self):
        """测试批量检测"""
        behavior_data_list = [
            BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
            BehaviorData(user_id=2, knowledge_point_id=10, replay_count=0, pause_count=1,
                        total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=1),
        ]
        
        results = self.detector.batch_detect(behavior_data_list)
        
        assert len(results) == len(behavior_data_list)
        assert all(isinstance(r[1], DifficultyResult) for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
