"""
测试螺旋路径跳出策略
"""

import pytest
from datetime import datetime
from algorithm.spiral_breakout_strategy import (
    SpiralBreakoutStrategy,
    BreakoutAction,
    SpiralPath,
    BreakoutRecord
)


class TestSpiralBreakoutStrategy:
    """测试螺旋路径跳出策略"""
    
    def test_init(self):
        """测试初始化"""
        strategy = SpiralBreakoutStrategy(
            failure_threshold=3,
            attempt_threshold=3
        )
        
        assert strategy.failure_threshold == 3
        assert strategy.attempt_threshold == 3
        assert len(strategy.spiral_paths) == 0
        assert len(strategy.breakout_records) == 0
    
    def test_record_spiral_path_attempt(self):
        """测试记录螺旋路径尝试"""
        strategy = SpiralBreakoutStrategy()
        
        # 记录成功尝试
        result = strategy.record_spiral_path_attempt(
            spiral_path_id=1,
            user_id=100,
            knowledge_point_ids=[1, 2, 3],
            success=True
        )
        
        assert result is True
        assert 1 in strategy.spiral_paths
        assert strategy.spiral_paths[1].attempt_count == 1
        assert strategy.spiral_paths[1].success_count == 1
        assert strategy.spiral_paths[1].failure_count == 0
        
        # 记录失败尝试
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        assert strategy.spiral_paths[1].attempt_count == 2
        assert strategy.spiral_paths[1].success_count == 1
        assert strategy.spiral_paths[1].failure_count == 1
    
    def test_check_breakout_condition_failure_threshold(self):
        """测试跳出条件：失败次数达到阈值"""
        strategy = SpiralBreakoutStrategy(failure_threshold=3, attempt_threshold=3)
        
        # 创建路径并记录3次失败
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        decision = strategy.check_breakout_condition(1)
        
        assert decision.should_breakout is True
        assert decision.breakout_action == BreakoutAction.UPGRADE_TO_L3
        assert decision.failure_count == 3
        assert "失败次数" in decision.reason
    
    def test_check_breakout_condition_attempt_threshold(self):
        """测试跳出条件：尝试次数达到阈值且失败率高"""
        strategy = SpiralBreakoutStrategy(failure_threshold=3, attempt_threshold=3)
        
        # 记录3次尝试，2次失败（失败率>50%）
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        
        decision = strategy.check_breakout_condition(1)
        
        assert decision.should_breakout is True
        assert decision.breakout_action == BreakoutAction.UPGRADE_TO_L3
        assert "失败率" in decision.reason
    
    def test_check_breakout_condition_low_failure_rate(self):
        """测试跳出条件：尝试次数达到阈值但失败率低"""
        strategy = SpiralBreakoutStrategy(failure_threshold=3, attempt_threshold=3)
        
        # 记录3次尝试，1次失败（失败率<50%）
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        decision = strategy.check_breakout_condition(1)
        
        assert decision.should_breakout is True
        assert decision.breakout_action == BreakoutAction.SKIP_KNOWLEDGE_POINT
        assert "跳过" in decision.reason
    
    def test_check_breakout_condition_no_breakout(self):
        """测试未达到跳出条件"""
        strategy = SpiralBreakoutStrategy(failure_threshold=3, attempt_threshold=3)
        
        # 记录2次尝试，1次失败
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        decision = strategy.check_breakout_condition(1)
        
        assert decision.should_breakout is False
        assert decision.breakout_action is None
    
    def test_execute_breakout_upgrade_l3(self):
        """测试执行跳出：升级到L3"""
        strategy = SpiralBreakoutStrategy()
        
        # 创建路径
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        result = strategy.execute_breakout(
            user_id=100,
            spiral_path_id=1,
            action=BreakoutAction.UPGRADE_TO_L3,
            skipped_knowledge_points=[1, 2, 3]
        )
        
        assert result["success"] is True
        assert result["action"] == "upgrade_to_l3"
        assert result["intervention_level"] == "L3"
        assert len(strategy.breakout_records) == 1
    
    def test_execute_breakout_skip_kp(self):
        """测试执行跳出：跳过知识点"""
        strategy = SpiralBreakoutStrategy()
        
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        result = strategy.execute_breakout(
            user_id=100,
            spiral_path_id=1,
            action=BreakoutAction.SKIP_KNOWLEDGE_POINT,
            skipped_knowledge_points=[1, 2]
        )
        
        assert result["success"] is True
        assert result["action"] == "skip_kp"
        assert result["intervention_level"] == "skip"
        assert result["skipped_knowledge_points"] == [1, 2]
    
    def test_regenerate_path_after_breakout(self):
        """测试跳出后重新生成路径"""
        strategy = SpiralBreakoutStrategy()
        
        new_path = strategy.regenerate_path_after_breakout(
            user_id=100,
            skipped_knowledge_points=[1, 2, 3]
        )
        
        assert len(new_path) == 3
        assert all(kp["status"] == "skipped" for kp in new_path)
        assert all(kp["reason"] == "螺旋路径跳出后跳过" for kp in new_path)
    
    def test_record_breakout_history(self):
        """测试记录跳出历史"""
        strategy = SpiralBreakoutStrategy()
        
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        result = strategy.record_breakout_history(
            user_id=100,
            spiral_path_id=1,
            reason="测试跳出"
        )
        
        assert result is True
        assert len(strategy.breakout_records) == 1
        assert strategy.breakout_records[0].reason == "测试跳出"
    
    def test_get_spiral_path_status(self):
        """测试获取螺旋路径状态"""
        strategy = SpiralBreakoutStrategy(failure_threshold=3, attempt_threshold=3)
        
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=True)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        status = strategy.get_spiral_path_status(1)
        
        assert status is not None
        assert status["path_id"] == 1
        assert status["user_id"] == 100
        assert status["attempt_count"] == 2
        assert status["failure_count"] == 1
        assert status["success_count"] == 1
        assert "success_rate" in status
        assert "should_breakout" in status
    
    def test_get_breakout_statistics(self):
        """测试获取跳出统计"""
        strategy = SpiralBreakoutStrategy()
        
        # 记录一些跳出
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        
        strategy.execute_breakout(100, 1, BreakoutAction.UPGRADE_TO_L3, [1, 2, 3])
        
        stats = strategy.get_breakout_statistics()
        
        assert stats["total_breakouts"] == 1
        assert stats["by_action"]["upgrade_to_l3"] == 1
        assert stats["average_failure_count"] > 0
        assert stats["average_attempt_count"] > 0
    
    def test_get_breakout_statistics_by_user(self):
        """测试按用户获取跳出统计"""
        strategy = SpiralBreakoutStrategy()
        
        # 用户100的跳出
        strategy.record_spiral_path_attempt(1, 100, [1, 2, 3], success=False)
        strategy.execute_breakout(100, 1, BreakoutAction.UPGRADE_TO_L3, [1, 2, 3])
        
        # 用户200的跳出
        strategy.record_spiral_path_attempt(2, 200, [4, 5, 6], success=False)
        strategy.execute_breakout(200, 2, BreakoutAction.SKIP_KNOWLEDGE_POINT, [4, 5])
        
        stats_100 = strategy.get_breakout_statistics(user_id=100)
        stats_200 = strategy.get_breakout_statistics(user_id=200)
        
        assert stats_100["total_breakouts"] == 1
        assert stats_200["total_breakouts"] == 1
        assert stats_100["by_action"]["upgrade_to_l3"] == 1
        assert stats_200["by_action"]["skip_kp"] == 1
    
    def test_set_breakout_thresholds(self):
        """测试设置跳出阈值"""
        strategy = SpiralBreakoutStrategy()
        
        result = strategy.set_breakout_thresholds(
            failure_threshold=5,
            attempt_threshold=4
        )
        
        assert result is True
        assert strategy.failure_threshold == 5
        assert strategy.attempt_threshold == 4
    
    def test_set_breakout_thresholds_invalid(self):
        """测试设置无效阈值"""
        strategy = SpiralBreakoutStrategy()
        
        result = strategy.set_breakout_thresholds(failure_threshold=0)
        
        assert result is False
        assert strategy.failure_threshold == 3  # 保持默认值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
