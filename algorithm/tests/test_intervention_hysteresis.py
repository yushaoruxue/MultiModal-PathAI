"""
干预抗震荡机制测试
"""

import pytest
from datetime import datetime, timedelta
from algorithm.intervention_hysteresis import (
    InterventionHysteresis,
    DifficultyResult,
    InterventionStatus
)


class TestInterventionHysteresis:
    """干预抗震荡机制测试类"""
    
    def test_init(self):
        """测试初始化"""
        hysteresis = InterventionHysteresis(
            cooldown_duration_minutes=5,
            default_trigger_threshold=6.0,
            default_release_threshold=4.0
        )
        
        assert hysteresis.cooldown_duration == timedelta(minutes=5)
        assert hysteresis.default_trigger_threshold == 6.0
        assert hysteresis.default_release_threshold == 4.0
    
    def test_check_cooldown_no_record(self):
        """测试检查冷静期（无记录）"""
        hysteresis = InterventionHysteresis()
        
        status = hysteresis.check_cooldown(1, 101)
        
        assert status["in_cooldown"] == False
        assert status["remaining_seconds"] == 0
        assert status["status"] == InterventionStatus.INACTIVE.value
    
    def test_should_trigger_intervention_high_score(self):
        """测试触发干预（高分，应该触发）"""
        hysteresis = InterventionHysteresis(
            cooldown_duration_minutes=5,
            default_trigger_threshold=6.0,
            default_release_threshold=4.0
        )
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.5,
            trigger_reasons=["回放次数过多"]
        )
        
        decision = hysteresis.should_trigger_intervention(
            difficulty_result, user_id=1, knowledge_point_id=101
        )
        
        assert decision.should_trigger == True
        assert decision.status == InterventionStatus.COOLDOWN
        assert decision.remaining_cooldown_seconds > 0
    
    def test_should_trigger_intervention_low_score(self):
        """测试触发干预（低分，不应该触发）"""
        hysteresis = InterventionHysteresis(
            default_trigger_threshold=6.0,
            default_release_threshold=4.0
        )
        
        difficulty_result = DifficultyResult(
            is_difficult=False,
            difficulty_score=3.0,
            trigger_reasons=[]
        )
        
        decision = hysteresis.should_trigger_intervention(
            difficulty_result, user_id=1, knowledge_point_id=101
        )
        
        assert decision.should_trigger == False
        assert decision.status == InterventionStatus.INACTIVE
    
    def test_cooldown_prevents_retrigger(self):
        """测试冷静期防止重复触发"""
        hysteresis = InterventionHysteresis(
            cooldown_duration_minutes=5,
            default_trigger_threshold=6.0
        )
        
        # 第一次触发
        difficulty_result1 = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.5,
            trigger_reasons=["回放次数过多"]
        )
        
        decision1 = hysteresis.should_trigger_intervention(
            difficulty_result1, user_id=1, knowledge_point_id=101
        )
        
        assert decision1.should_trigger == True
        
        # 立即再次尝试触发（应该在冷静期内）
        difficulty_result2 = DifficultyResult(
            is_difficult=True,
            difficulty_score=8.0,
            trigger_reasons=["暂停次数过多"]
        )
        
        decision2 = hysteresis.should_trigger_intervention(
            difficulty_result2, user_id=1, knowledge_point_id=101
        )
        
        assert decision2.should_trigger == False
        assert decision2.status == InterventionStatus.COOLDOWN
        assert decision2.remaining_cooldown_seconds > 0
    
    def test_hysteresis_effect(self):
        """测试滞后效应"""
        hysteresis = InterventionHysteresis(
            default_trigger_threshold=6.0,
            default_release_threshold=4.0
        )
        
        # 测试触发阈值
        should_trigger_high = hysteresis.apply_hysteresis(
            trigger_threshold=6.0,
            release_threshold=4.0,
            current_score=7.0,
            current_status=InterventionStatus.INACTIVE
        )
        assert should_trigger_high == True
        
        # 测试低于触发阈值
        should_trigger_low = hysteresis.apply_hysteresis(
            trigger_threshold=6.0,
            release_threshold=4.0,
            current_score=5.0,
            current_status=InterventionStatus.INACTIVE
        )
        assert should_trigger_low == False
        
        # 测试已激活状态（需要低于解除阈值才解除）
        should_trigger_active = hysteresis.apply_hysteresis(
            trigger_threshold=6.0,
            release_threshold=4.0,
            current_score=5.0,  # 在触发和解除阈值之间
            current_status=InterventionStatus.ACTIVE
        )
        assert should_trigger_active == False  # 已激活，不需要再次触发
    
    def test_get_remaining_cooldown(self):
        """测试获取剩余冷静期时间"""
        hysteresis = InterventionHysteresis(cooldown_duration_minutes=5)
        
        # 触发干预
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.5,
            trigger_reasons=["回放次数过多"]
        )
        
        hysteresis.should_trigger_intervention(
            difficulty_result, user_id=1, knowledge_point_id=101
        )
        
        # 获取剩余时间
        remaining = hysteresis.get_remaining_cooldown(1, 101)
        
        assert remaining > 0
        assert remaining <= 300  # 应该小于等于5分钟（300秒）
    
    def test_set_hysteresis_config(self):
        """测试设置滞后效应配置"""
        hysteresis = InterventionHysteresis()
        
        success = hysteresis.set_hysteresis_config(
            user_id=1,
            knowledge_point_id=101,
            trigger_threshold=7.0,
            release_threshold=3.0
        )
        
        assert success == True
        
        # 验证配置已设置
        config = hysteresis._get_hysteresis_config(1, 101)
        assert config.trigger_threshold == 7.0
        assert config.release_threshold == 3.0
    
    def test_get_cooldown_statistics(self):
        """测试获取冷静期统计"""
        hysteresis = InterventionHysteresis()
        
        # 触发几个干预
        for i in range(3):
            difficulty_result = DifficultyResult(
                is_difficult=True,
                difficulty_score=7.0 + i,
                trigger_reasons=["回放次数过多"]
            )
            hysteresis.should_trigger_intervention(
                difficulty_result, user_id=i + 1, knowledge_point_id=100 + i
            )
        
        stats = hysteresis.get_cooldown_statistics()
        
        assert stats["total_records"] == 3
        assert stats["cooldown"] == 3
        
        # 获取特定用户的统计
        stats_user1 = hysteresis.get_cooldown_statistics(user_id=1)
        assert stats_user1["total_records"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
