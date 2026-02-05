"""
信号不协和检测算法

基于v6.0需求，检测多模态信号之间的不一致性。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """认知状态枚举"""
    UNDERSTANDING = "understanding"  # 理解中
    CONFUSED = "confused"  # 困惑
    DISTRACTED = "distracted"  # 分心
    ENGAGED = "engaged"  # 专注


@dataclass
class GazeData:
    """视线追踪数据"""
    timestamp: float
    x: float  # 屏幕X坐标
    y: float  # 屏幕Y坐标
    attention_level: float  # 注意力水平（0-1）


@dataclass
class EmotionData:
    """微表情数据"""
    timestamp: float
    emotion_type: str  # confused/happy/neutral/surprised
    confidence: float  # 置信度（0-1）


@dataclass
class InteractionData:
    """鼠标/键盘行为数据"""
    timestamp: float
    event_type: str  # click/keypress/scroll/pause
    data: Dict[str, Any]  # 事件数据


@dataclass
class PlaybackData:
    """播放行为数据"""
    timestamp: float
    event_type: str  # play/pause/seek/replay
    position: float  # 播放位置（秒）


@dataclass
class MultimodalSignals:
    """多模态信号数据"""
    gaze_data: List[GazeData]
    emotion_data: List[EmotionData]
    interaction_data: List[InteractionData]
    playback_data: List[PlaybackData]


@dataclass
class DissonanceResult:
    """不协和检测结果"""
    is_dissonant: bool  # 是否不协和
    confidence: float  # 置信度（0-1）
    dissonance_score: float  # 不协和分数（0-1，越高越不协和）
    conflicting_signals: List[str]  # 冲突的信号列表
    signal_states: Dict[str, CognitiveState]  # 各信号的认知状态


@dataclass
class CrossValidationResult:
    """交叉验证结果"""
    base_difficulty_score: float  # 基础困难度分数
    validated_difficulty_score: float  # 验证后的困难度分数
    validation_confidence: float  # 验证置信度（0-1）
    signal_agreement: float  # 信号一致性（0-1）
    validation_result: str  # 验证结果：confirmed/rejected/uncertain


class SignalDissonanceDetector:
    """信号不协和检测器
    
    功能：
    1. 多模态信号：视线追踪、微表情、鼠标/键盘行为、视频播放行为
    2. 不协和检测：如果多个信号指向不同的认知状态，标记为不协和
    3. 交叉验证：使用多模态信号交叉验证难点判定结果
    4. 安全熔断：不协和时降低置信度，触发人工确认
    """
    
    # 不协和阈值
    DISSONANCE_THRESHOLD = 0.5  # 不协和分数阈值
    
    # 安全熔断阈值
    SAFETY_FUSE_THRESHOLD = 0.7  # 安全熔断阈值（不协和分数超过此值触发）
    
    def __init__(self):
        """初始化信号不协和检测器"""
        # 存储检测历史
        self.detection_history: List[DissonanceResult] = []
        
        logger.info("SignalDissonanceDetector initialized")
    
    def detect_dissonance(
        self,
        signals: MultimodalSignals
    ) -> DissonanceResult:
        """检测信号不协和
        
        Args:
            signals: 多模态信号数据
        
        Returns:
            不协和检测结果
        """
        # 1. 从各信号推断认知状态
        signal_states = {}
        
        # 视线追踪信号 -> 认知状态
        gaze_state = self._infer_state_from_gaze(signals.gaze_data)
        signal_states["gaze"] = gaze_state
        
        # 微表情信号 -> 认知状态
        emotion_state = self._infer_state_from_emotion(signals.emotion_data)
        signal_states["emotion"] = emotion_state
        
        # 交互行为信号 -> 认知状态
        interaction_state = self._infer_state_from_interaction(signals.interaction_data)
        signal_states["interaction"] = interaction_state
        
        # 播放行为信号 -> 认知状态
        playback_state = self._infer_state_from_playback(signals.playback_data)
        signal_states["playback"] = playback_state
        
        # 2. 计算信号一致性
        consistency = self.calculate_signal_consistency(signal_states)
        
        # 3. 计算不协和分数（1 - 一致性）
        dissonance_score = 1.0 - consistency
        
        # 4. 判断是否不协和
        is_dissonant = dissonance_score >= self.DISSONANCE_THRESHOLD
        
        # 5. 找出冲突的信号
        conflicting_signals = self._find_conflicting_signals(signal_states)
        
        # 6. 计算置信度
        confidence = consistency if not is_dissonant else (1.0 - dissonance_score)
        
        result = DissonanceResult(
            is_dissonant=is_dissonant,
            confidence=confidence,
            dissonance_score=dissonance_score,
            conflicting_signals=conflicting_signals,
            signal_states=signal_states
        )
        
        # 记录历史
        self.detection_history.append(result)
        
        if is_dissonant:
            logger.warning(
                f"Signal dissonance detected: score={dissonance_score:.2f}, "
                f"conflicting_signals={conflicting_signals}"
            )
        
        return result
    
    def _infer_state_from_gaze(
        self,
        gaze_data: List[GazeData]
    ) -> CognitiveState:
        """从视线追踪数据推断认知状态
        
        Args:
            gaze_data: 视线追踪数据列表
        
        Returns:
            认知状态
        """
        if not gaze_data:
            return CognitiveState.UNDERSTANDING  # 默认状态
        
        # 计算平均注意力水平
        avg_attention = sum(g.attention_level for g in gaze_data) / len(gaze_data)
        
        if avg_attention < 0.3:
            return CognitiveState.DISTRACTED
        elif avg_attention < 0.6:
            return CognitiveState.CONFUSED
        else:
            return CognitiveState.ENGAGED
    
    def _infer_state_from_emotion(
        self,
        emotion_data: List[EmotionData]
    ) -> CognitiveState:
        """从微表情数据推断认知状态
        
        Args:
            emotion_data: 微表情数据列表
        
        Returns:
            认知状态
        """
        if not emotion_data:
            return CognitiveState.UNDERSTANDING
        
        # 统计情绪类型
        emotion_counts = defaultdict(int)
        for e in emotion_data:
            emotion_counts[e.emotion_type] += 1
        
        # 找出主要情绪
        if emotion_counts:
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
            
            if dominant_emotion == "confused":
                return CognitiveState.CONFUSED
            elif dominant_emotion in ["happy", "neutral"]:
                return CognitiveState.UNDERSTANDING
            else:
                return CognitiveState.DISTRACTED
        
        return CognitiveState.UNDERSTANDING
    
    def _infer_state_from_interaction(
        self,
        interaction_data: List[InteractionData]
    ) -> CognitiveState:
        """从交互行为数据推断认知状态
        
        Args:
            interaction_data: 交互行为数据列表
        
        Returns:
            认知状态
        """
        if not interaction_data:
            return CognitiveState.UNDERSTANDING
        
        # 统计事件类型
        pause_count = sum(
            1 for i in interaction_data if i.event_type == "pause"
        )
        click_count = sum(
            1 for i in interaction_data if i.event_type == "click"
        )
        
        # 如果暂停次数多，可能是困惑
        if pause_count > 3:
            return CognitiveState.CONFUSED
        elif click_count > 10:
            # 点击次数多，可能是分心（频繁切换）
            return CognitiveState.DISTRACTED
        else:
            return CognitiveState.ENGAGED
    
    def _infer_state_from_playback(
        self,
        playback_data: List[PlaybackData]
    ) -> CognitiveState:
        """从播放行为数据推断认知状态
        
        Args:
            playback_data: 播放行为数据列表
        
        Returns:
            认知状态
        """
        if not playback_data:
            return CognitiveState.UNDERSTANDING
        
        # 统计回放次数
        replay_count = sum(
            1 for p in playback_data if p.event_type == "replay"
        )
        
        # 统计暂停次数
        pause_count = sum(
            1 for p in playback_data if p.event_type == "pause"
        )
        
        if replay_count > 2 or pause_count > 3:
            return CognitiveState.CONFUSED
        else:
            return CognitiveState.ENGAGED
    
    def calculate_signal_consistency(
        self,
        signal_states: Dict[str, CognitiveState]
    ) -> float:
        """计算信号一致性
        
        Args:
            signal_states: 各信号的认知状态字典
        
        Returns:
            一致性分数（0-1），1表示完全一致
        """
        if not signal_states:
            return 1.0
        
        if len(signal_states) == 1:
            return 1.0
        
        # 统计各状态的出现次数
        state_counts = defaultdict(int)
        for state in signal_states.values():
            state_counts[state] += 1
        
        # 找出主导状态
        if state_counts:
            dominant_state = max(state_counts.items(), key=lambda x: x[1])[0]
            dominant_count = state_counts[dominant_state]
            
            # 一致性 = 主导状态数量 / 总信号数量
            consistency = dominant_count / len(signal_states)
        else:
            consistency = 0.0
        
        return consistency
    
    def _find_conflicting_signals(
        self,
        signal_states: Dict[str, CognitiveState]
    ) -> List[str]:
        """找出冲突的信号
        
        Args:
            signal_states: 各信号的认知状态字典
        
        Returns:
            冲突的信号名称列表
        """
        if not signal_states:
            return []
        
        # 找出主导状态
        state_counts = defaultdict(int)
        for state in signal_states.values():
            state_counts[state] += 1
        
        if not state_counts:
            return []
        
        dominant_state = max(state_counts.items(), key=lambda x: x[1])[0]
        
        # 找出与主导状态不一致的信号
        conflicting = [
            signal_name for signal_name, state in signal_states.items()
            if state != dominant_state
        ]
        
        return conflicting
    
    def cross_validate_difficulty(
        self,
        signals: MultimodalSignals,
        base_difficulty_score: float
    ) -> CrossValidationResult:
        """交叉验证难点判定结果
        
        Args:
            signals: 多模态信号数据
            base_difficulty_score: 基础困难度分数
        
        Returns:
            交叉验证结果
        """
        # 1. 检测不协和
        dissonance_result = self.detect_dissonance(signals)
        
        # 2. 从信号推断困难度
        signal_difficulty_scores = []
        
        # 从各信号推断困难度
        if signals.gaze_data:
            gaze_avg_attention = sum(g.attention_level for g in signals.gaze_data) / len(signals.gaze_data)
            # 注意力低 -> 困难度高
            signal_difficulty_scores.append(1.0 - gaze_avg_attention)
        
        if signals.emotion_data:
            confused_count = sum(1 for e in signals.emotion_data if e.emotion_type == "confused")
            confused_rate = confused_count / len(signals.emotion_data) if signals.emotion_data else 0.0
            signal_difficulty_scores.append(confused_rate)
        
        if signals.playback_data:
            replay_count = sum(1 for p in signals.playback_data if p.event_type == "replay")
            # 回放次数多 -> 困难度高
            replay_rate = min(1.0, replay_count / 5.0)  # 归一化
            signal_difficulty_scores.append(replay_rate)
        
        # 3. 计算信号推断的平均困难度
        if signal_difficulty_scores:
            signal_avg_difficulty = sum(signal_difficulty_scores) / len(signal_difficulty_scores)
        else:
            signal_avg_difficulty = base_difficulty_score
        
        # 4. 计算信号一致性
        signal_agreement = 1.0 - abs(base_difficulty_score - signal_avg_difficulty)
        
        # 5. 验证结果
        if signal_agreement >= 0.7:
            validation_result = "confirmed"
            validated_score = base_difficulty_score
            validation_confidence = signal_agreement
        elif signal_agreement >= 0.5:
            validation_result = "uncertain"
            # 取平均值
            validated_score = (base_difficulty_score + signal_avg_difficulty) / 2.0
            validation_confidence = signal_agreement
        else:
            validation_result = "rejected"
            # 使用信号推断的结果
            validated_score = signal_avg_difficulty
            validation_confidence = 1.0 - signal_agreement
        
        # 6. 如果不协和，降低置信度
        if dissonance_result.is_dissonant:
            validation_confidence *= (1.0 - dissonance_result.dissonance_score * 0.5)
        
        result = CrossValidationResult(
            base_difficulty_score=base_difficulty_score,
            validated_difficulty_score=validated_score,
            validation_confidence=validation_confidence,
            signal_agreement=signal_agreement,
            validation_result=validation_result
        )
        
        logger.info(
            f"Cross validation: base={base_difficulty_score:.2f}, "
            f"validated={validated_score:.2f}, "
            f"confidence={validation_confidence:.2f}, "
            f"result={validation_result}"
        )
        
        return result
    
    def trigger_safety_fuse(
        self,
        dissonance_level: float
    ) -> Dict[str, Any]:
        """触发安全熔断
        
        Args:
            dissonance_level: 不协和水平（0-1）
        
        Returns:
            安全熔断结果字典
        """
        if dissonance_level < self.SAFETY_FUSE_THRESHOLD:
            return {
                "triggered": False,
                "confidence_reduction": 0.0,
                "requires_confirmation": False,
                "message": "不协和水平未达到安全熔断阈值"
            }
        
        # 计算置信度降低幅度
        confidence_reduction = (dissonance_level - self.SAFETY_FUSE_THRESHOLD) / (1.0 - self.SAFETY_FUSE_THRESHOLD)
        confidence_reduction = min(0.5, confidence_reduction)  # 最多降低50%
        
        result = {
            "triggered": True,
            "confidence_reduction": confidence_reduction,
            "requires_confirmation": True,
            "message": f"不协和水平{dissonance_level:.2f}超过安全熔断阈值{self.SAFETY_FUSE_THRESHOLD}，触发人工确认"
        }
        
        logger.warning(
            f"Safety fuse triggered: dissonance_level={dissonance_level:.2f}, "
            f"confidence_reduction={confidence_reduction:.2f}"
        )
        
        return result
    
    def get_dissonance_statistics(
        self
    ) -> Dict[str, Any]:
        """获取不协和检测统计
        
        Returns:
            统计报告字典
        """
        if not self.detection_history:
            return {
                "total_detections": 0,
                "dissonant_count": 0,
                "average_dissonance_score": 0.0,
                "average_confidence": 0.0
            }
        
        dissonant_count = sum(1 for r in self.detection_history if r.is_dissonant)
        avg_dissonance = sum(r.dissonance_score for r in self.detection_history) / len(self.detection_history)
        avg_confidence = sum(r.confidence for r in self.detection_history) / len(self.detection_history)
        
        return {
            "total_detections": len(self.detection_history),
            "dissonant_count": dissonant_count,
            "dissonant_rate": dissonant_count / len(self.detection_history) if self.detection_history else 0.0,
            "average_dissonance_score": avg_dissonance,
            "average_confidence": avg_confidence
        }
