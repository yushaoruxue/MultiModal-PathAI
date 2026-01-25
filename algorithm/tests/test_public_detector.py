"""
公共难点识别单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from public_difficulty_detector import PublicDifficultyDetector, PublicDifficultyResult
from difficulty_detector import BehaviorData


class TestPublicDifficultyDetector:
    """公共难点识别器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.detector = PublicDifficultyDetector(difficulty_ratio_threshold=0.3)
    
    def test_detect_public_difficulty(self):
        """测试公共难点检测"""
        # 创建多个学生的行为数据（大部分困难）
        all_students_behavior = [
            BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
            BehaviorData(user_id=2, knowledge_point_id=10, replay_count=2, pause_count=4,
                        total_watch_time=500.0, knowledge_point_duration=200.0, seek_count=1),
            BehaviorData(user_id=3, knowledge_point_id=10, replay_count=0, pause_count=1,
                        total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
        ]
        
        result = self.detector.detect_public_difficulty(10, all_students_behavior)
        
        assert isinstance(result, PublicDifficultyResult)
        assert result.knowledge_point_id == 10
        assert isinstance(result.is_public_difficulty, bool)
        assert 0 <= result.difficulty_ratio <= 1
        assert 0 <= result.average_difficulty_score <= 10
        assert isinstance(result.affected_students, list)
        assert isinstance(result.recommendation, str)
    
    def test_calculate_difficulty_ratio(self):
        """测试困难学生比例计算"""
        behavior_data = [
            BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
            BehaviorData(user_id=2, knowledge_point_id=10, replay_count=0, pause_count=1,
                        total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
        ]
        
        ratio = self.detector.calculate_difficulty_ratio(10, behavior_data)
        
        assert 0 <= ratio <= 1
    
    def test_get_recommendation(self):
        """测试教学建议生成"""
        # 高困难比例
        recommendation1 = self.detector.get_recommendation(0.6, 8.0)
        assert "严重难点" in recommendation1 or len(recommendation1) > 0
        
        # 中等困难比例
        recommendation2 = self.detector.get_recommendation(0.3, 5.0)
        assert len(recommendation2) > 0
        
        # 低困难比例
        recommendation3 = self.detector.get_recommendation(0.1, 2.0)
        assert len(recommendation3) > 0
    
    def test_batch_detect(self):
        """测试批量检测"""
        knowledge_point_behaviors = {
            1: [
                BehaviorData(user_id=1, knowledge_point_id=1, replay_count=3, pause_count=5,
                            total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
            ],
            2: [
                BehaviorData(user_id=1, knowledge_point_id=2, replay_count=0, pause_count=1,
                            total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
            ],
        }
        
        results = self.detector.batch_detect(1, knowledge_point_behaviors)
        
        assert len(results) == 2
        assert all(isinstance(r, PublicDifficultyResult) for r in results)
    
    def test_generate_statistics_report(self):
        """测试统计报告生成"""
        results = [
            PublicDifficultyResult(
                knowledge_point_id=1,
                is_public_difficulty=True,
                difficulty_ratio=0.5,
                average_difficulty_score=7.0,
                affected_students=[1, 2],
                recommendation="严重难点"
            ),
            PublicDifficultyResult(
                knowledge_point_id=2,
                is_public_difficulty=False,
                difficulty_ratio=0.1,
                average_difficulty_score=2.0,
                affected_students=[],
                recommendation="正常"
            ),
        ]
        
        report = self.detector.generate_statistics_report(results)
        
        assert "total_knowledge_points" in report
        assert "public_difficulties" in report
        assert report["total_knowledge_points"] == 2
        assert report["public_difficulties"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
