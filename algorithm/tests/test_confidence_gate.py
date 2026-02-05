"""
置信度门控机制测试
"""

import pytest
from datetime import datetime
from algorithm.confidence_gate import (
    ConfidenceGate,
    DifficultyResult,
    MultimodalSignal,
    HistoryAccuracy,
    ConfirmationStatus
)


class TestConfidenceGate:
    """置信度门控测试类"""
    
    def test_init(self):
        """测试初始化"""
        gate = ConfidenceGate(confidence_threshold=0.7)
        assert gate.confidence_threshold == 0.7
        assert gate.signal_consistency_weight > 0
        assert gate.history_accuracy_weight > 0
        assert gate.base_confidence_weight > 0
    
    def test_calculate_confidence_with_all_data(self):
        """测试计算置信度（包含所有数据）"""
        gate = ConfidenceGate()
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.5,
            trigger_reasons=["回放次数过多", "暂停次数过多"],
            base_confidence=0.8
        )
        
        signals = MultimodalSignal(
            gaze_data=[
                {"timestamp": 100, "attention_level": 0.6},
                {"timestamp": 200, "attention_level": 0.5}
            ],
            emotion_data=[
                {"timestamp": 100, "confidence": 0.3, "emotion_type": "confused"}
            ],
            playback_data=[
                {"timestamp": 100, "event_type": "replay"},
                {"timestamp": 200, "event_type": "pause"}
            ]
        )
        
        history = HistoryAccuracy(
            total_detections=100,
            confirmed_difficult=80,
            confirmed_not_difficult=15,
            accuracy_rate=0.85
        )
        
        confidence = gate.calculate_confidence(difficulty_result, signals, history)
        
        assert 0.0 <= confidence <= 1.0
        print(f"Calculated confidence: {confidence:.3f}")
    
    def test_calculate_confidence_without_signals(self):
        """测试计算置信度（无信号数据）"""
        gate = ConfidenceGate()
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.5,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.8
        )
        
        history = HistoryAccuracy(
            total_detections=50,
            confirmed_difficult=40,
            accuracy_rate=0.8
        )
        
        confidence = gate.calculate_confidence(difficulty_result, None, history)
        
        assert 0.0 <= confidence <= 1.0
        print(f"Calculated confidence (no signals): {confidence:.3f}")
    
    def test_gate_difficulty_detection_high_confidence(self):
        """测试门控判定（高置信度，自动确认）"""
        gate = ConfidenceGate(confidence_threshold=0.7)
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=8.0,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.9
        )
        
        confidence = 0.85  # 高于阈值
        gated_result = gate.gate_difficulty_detection(difficulty_result, confidence)
        
        assert gated_result.is_difficult == True
        assert gated_result.confidence == 0.85
        assert gated_result.requires_confirmation == False
        assert gated_result.status == "auto_confirmed"
    
    def test_gate_difficulty_detection_low_confidence(self):
        """测试门控判定（低置信度，需要确认）"""
        gate = ConfidenceGate(confidence_threshold=0.7)
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=6.0,
            trigger_reasons=["暂停次数过多"],
            base_confidence=0.5
        )
        
        confidence = 0.6  # 低于阈值
        gated_result = gate.gate_difficulty_detection(
            difficulty_result, confidence, user_id=1, knowledge_point_id=101
        )
        
        assert gated_result.is_difficult == False  # 低置信度时不自动判定
        assert gated_result.confidence == 0.6
        assert gated_result.requires_confirmation == True
        assert gated_result.status == "pending_confirmation"
        
        # 检查是否创建了确认请求
        request = gate.get_confirmation_request(1, 101)
        assert request is not None
        assert request.status == ConfirmationStatus.PENDING
    
    def test_request_human_confirmation(self):
        """测试请求人工确认"""
        gate = ConfidenceGate()
        
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.0,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.6
        )
        
        success = gate.request_human_confirmation(
            user_id=1,
            knowledge_point_id=101,
            difficulty_result=difficulty_result,
            confidence=0.65
        )
        
        assert success == True
        
        request = gate.get_confirmation_request(1, 101)
        assert request is not None
        assert request.user_id == 1
        assert request.knowledge_point_id == 101
        assert request.confidence == 0.65
        assert request.status == ConfirmationStatus.PENDING
    
    def test_handle_confirmation_response_confirmed(self):
        """测试处理确认响应（已确认）"""
        gate = ConfidenceGate()
        
        # 先创建确认请求
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.0,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.6
        )
        
        gate.request_human_confirmation(1, 101, difficulty_result, 0.65)
        
        # 处理确认响应
        result = gate.handle_confirmation_response(1, 101, confirmed=True)
        
        assert result["success"] == True
        assert result["is_difficult"] == True
        assert result["status"] == "confirmed"
        
        request = gate.get_confirmation_request(1, 101)
        assert request.status == ConfirmationStatus.CONFIRMED
    
    def test_handle_confirmation_response_rejected(self):
        """测试处理确认响应（已拒绝）"""
        gate = ConfidenceGate()
        
        # 先创建确认请求
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.0,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.6
        )
        
        gate.request_human_confirmation(1, 101, difficulty_result, 0.65)
        
        # 处理拒绝响应
        result = gate.handle_confirmation_response(1, 101, confirmed=False)
        
        assert result["success"] == True
        assert result["is_difficult"] == False
        assert result["status"] == "rejected"
        
        request = gate.get_confirmation_request(1, 101)
        assert request.status == ConfirmationStatus.REJECTED
    
    def test_mark_as_under_observation(self):
        """测试标记为待观察"""
        gate = ConfidenceGate()
        
        # 先创建确认请求
        difficulty_result = DifficultyResult(
            is_difficult=True,
            difficulty_score=7.0,
            trigger_reasons=["回放次数过多"],
            base_confidence=0.6
        )
        
        gate.request_human_confirmation(1, 101, difficulty_result, 0.65)
        
        # 标记为待观察
        success = gate.mark_as_under_observation(1, 101)
        
        assert success == True
        
        request = gate.get_confirmation_request(1, 101)
        assert request.status == ConfirmationStatus.IGNORED
    
    def test_get_pending_confirmations(self):
        """测试获取待确认请求列表"""
        gate = ConfidenceGate()
        
        # 创建多个确认请求
        for i in range(3):
            difficulty_result = DifficultyResult(
                is_difficult=True,
                difficulty_score=7.0 + i,
                trigger_reasons=["回放次数过多"],
                base_confidence=0.6
            )
            gate.request_human_confirmation(i + 1, 100 + i, difficulty_result, 0.65)
        
        # 确认一个请求
        gate.handle_confirmation_response(1, 100, confirmed=True)
        
        # 获取待确认请求
        pending = gate.get_pending_confirmations()
        
        assert len(pending) == 2  # 应该还有2个待确认
        
        # 获取特定用户的待确认请求
        pending_user2 = gate.get_pending_confirmations(user_id=2)
        assert len(pending_user2) == 1
        assert pending_user2[0].user_id == 2
    
    def test_get_confidence_statistics(self):
        """测试获取置信度统计"""
        gate = ConfidenceGate()
        
        # 创建多个确认请求
        for i in range(5):
            difficulty_result = DifficultyResult(
                is_difficult=True,
                difficulty_score=7.0 + i,
                trigger_reasons=["回放次数过多"],
                base_confidence=0.6 + i * 0.05
            )
            gate.request_human_confirmation(i + 1, 100 + i, difficulty_result, 0.6 + i * 0.05)
        
        # 处理一些确认响应
        gate.handle_confirmation_response(1, 100, confirmed=True)
        gate.handle_confirmation_response(2, 101, confirmed=False)
        gate.mark_as_under_observation(3, 102)
        
        # 获取统计
        stats = gate.get_confidence_statistics()
        
        assert stats["total_requests"] == 5
        assert stats["pending"] == 2
        assert stats["confirmed"] == 1
        assert stats["rejected"] == 1
        assert stats["ignored"] == 1
        assert stats["average_confidence"] > 0
        
        print(f"Statistics: {stats}")
    
    def test_signal_consistency_calculation(self):
        """测试信号一致性计算"""
        gate = ConfidenceGate()
        
        # 测试高一致性信号（所有信号都指向困难）
        signals_high = MultimodalSignal(
            gaze_data=[
                {"timestamp": 100, "attention_level": 0.3},  # 低注意力
                {"timestamp": 200, "attention_level": 0.2}
            ],
            emotion_data=[
                {"timestamp": 100, "confidence": 0.2, "emotion_type": "confused"}  # 高困惑
            ],
            playback_data=[
                {"timestamp": 100, "event_type": "replay"},
                {"timestamp": 200, "event_type": "pause"},
                {"timestamp": 300, "event_type": "replay"}
            ]
        )
        
        consistency_high = gate._calculate_signal_consistency(signals_high)
        print(f"High consistency signals: {consistency_high:.3f}")
        assert 0.0 <= consistency_high <= 1.0
        
        # 测试低一致性信号（信号互相矛盾）
        signals_low = MultimodalSignal(
            gaze_data=[
                {"timestamp": 100, "attention_level": 0.9}  # 高注意力
            ],
            emotion_data=[
                {"timestamp": 100, "confidence": 0.9, "emotion_type": "happy"}  # 低困惑
            ],
            playback_data=[
                {"timestamp": 100, "event_type": "replay"}  # 但有回放
            ]
        )
        
        consistency_low = gate._calculate_signal_consistency(signals_low)
        print(f"Low consistency signals: {consistency_low:.3f}")
        assert 0.0 <= consistency_low <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
