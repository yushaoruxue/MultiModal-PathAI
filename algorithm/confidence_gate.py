"""
置信度门控机制

基于v7.0需求，实现低置信度时不误判，触发人工确认的机制。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfirmationStatus(Enum):
    """确认状态枚举"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    REJECTED = "rejected"  # 已拒绝
    IGNORED = "ignored"  # 忽略（学生未响应）


@dataclass
class DifficultyResult:
    """难点判定结果"""
    is_difficult: bool
    difficulty_score: float  # 0-10
    trigger_reasons: List[str]
    base_confidence: float = 1.0  # 基础置信度（0-1）


@dataclass
class MultimodalSignal:
    """多模态信号数据"""
    gaze_data: Optional[List[Dict]] = None  # 视线追踪数据
    emotion_data: Optional[List[Dict]] = None  # 微表情数据
    interaction_data: Optional[List[Dict]] = None  # 鼠标/键盘行为数据
    playback_data: Optional[List[Dict]] = None  # 播放行为数据


@dataclass
class HistoryAccuracy:
    """历史判定准确率"""
    total_detections: int = 0
    confirmed_difficult: int = 0
    confirmed_not_difficult: int = 0
    accuracy_rate: float = 0.0  # 准确率（0-1）


@dataclass
class GatedResult:
    """门控后的判定结果"""
    is_difficult: bool
    difficulty_score: float
    confidence: float  # 综合置信度（0-1）
    requires_confirmation: bool  # 是否需要人工确认
    status: str  # "auto_confirmed" | "pending_confirmation" | "under_observation"
    reason: str  # 门控原因说明


@dataclass
class ConfirmationRequest:
    """人工确认请求"""
    user_id: int
    knowledge_point_id: int
    difficulty_result: DifficultyResult
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    status: ConfirmationStatus = ConfirmationStatus.PENDING


class ConfidenceGate:
    """置信度门控机制
    
    功能：
    1. 计算综合置信度（基于多模态信号一致性、历史准确率等）
    2. 门控阈值判断（置信度<0.7时，不自动判定）
    3. 触发人工确认（低置信度时）
    4. 处理盲区（学生不确认时标记为"待观察"）
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        signal_consistency_weight: float = 0.4,
        history_accuracy_weight: float = 0.3,
        base_confidence_weight: float = 0.3
    ):
        """初始化置信度门控
        
        Args:
            confidence_threshold: 置信度阈值，低于此值需要人工确认（默认0.7）
            signal_consistency_weight: 信号一致性权重（默认0.4）
            history_accuracy_weight: 历史准确率权重（默认0.3）
            base_confidence_weight: 基础置信度权重（默认0.3）
        """
        self.confidence_threshold = confidence_threshold
        self.signal_consistency_weight = signal_consistency_weight
        self.history_accuracy_weight = history_accuracy_weight
        self.base_confidence_weight = base_confidence_weight
        
        # 验证权重总和为1
        total_weight = (
            signal_consistency_weight + 
            history_accuracy_weight + 
            base_confidence_weight
        )
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            self.signal_consistency_weight /= total_weight
            self.history_accuracy_weight /= total_weight
            self.base_confidence_weight /= total_weight
        
        # 存储确认请求历史
        self.confirmation_requests: Dict[tuple, ConfirmationRequest] = {}
        
        logger.info(
            f"ConfidenceGate initialized with threshold={confidence_threshold}, "
            f"weights=({signal_consistency_weight}, {history_accuracy_weight}, {base_confidence_weight})"
        )
    
    def calculate_confidence(
        self,
        difficulty_result: DifficultyResult,
        signals: Optional[MultimodalSignal] = None,
        history: Optional[HistoryAccuracy] = None
    ) -> float:
        """计算综合置信度
        
        Args:
            difficulty_result: 难点判定结果
            signals: 多模态信号数据（可选）
            history: 历史判定准确率（可选）
        
        Returns:
            综合置信度（0-1）
        """
        confidence_components = []
        weights = []
        
        # 1. 信号一致性置信度
        if signals:
            signal_consistency = self._calculate_signal_consistency(signals)
            confidence_components.append(signal_consistency)
            weights.append(self.signal_consistency_weight)
        else:
            # 如果没有信号数据，使用默认值
            confidence_components.append(0.5)
            weights.append(self.signal_consistency_weight)
        
        # 2. 历史准确率置信度
        if history and history.total_detections > 0:
            history_confidence = history.accuracy_rate
            confidence_components.append(history_confidence)
            weights.append(self.history_accuracy_weight)
        else:
            # 如果没有历史数据，使用默认值
            confidence_components.append(0.7)
            weights.append(self.history_accuracy_weight)
        
        # 3. 基础置信度（从难点判定结果中获取）
        base_confidence = difficulty_result.base_confidence
        confidence_components.append(base_confidence)
        weights.append(self.base_confidence_weight)
        
        # 加权平均计算综合置信度
        total_weight = sum(weights)
        if total_weight > 0:
            confidence = sum(
                comp * weight for comp, weight in zip(confidence_components, weights)
            ) / total_weight
        else:
            confidence = sum(confidence_components) / len(confidence_components)
        
        # 确保置信度在[0, 1]范围内
        confidence = max(0.0, min(1.0, confidence))
        
        logger.debug(
            f"Calculated confidence: {confidence:.3f} "
            f"(signal={confidence_components[0]:.3f}, "
            f"history={confidence_components[1]:.3f}, "
            f"base={confidence_components[2]:.3f})"
        )
        
        return confidence
    
    def _calculate_signal_consistency(self, signals: MultimodalSignal) -> float:
        """计算多模态信号一致性
        
        Args:
            signals: 多模态信号数据
        
        Returns:
            信号一致性分数（0-1），1表示完全一致，0表示完全不一致
        """
        if not signals:
            return 0.5  # 默认中等一致性
        
        # 提取各信号源的认知状态指示
        signal_states = []
        
        # 1. 视线追踪信号（注意力水平）
        if signals.gaze_data:
            attention_levels = [
                item.get("attention_level", 0.5) 
                for item in signals.gaze_data 
                if isinstance(item, dict)
            ]
            if attention_levels:
                avg_attention = sum(attention_levels) / len(attention_levels)
                signal_states.append(("gaze", avg_attention))
        
        # 2. 微表情信号（困惑/理解程度）
        if signals.emotion_data:
            # 假设困惑度越高，越可能遇到难点
            confusion_levels = [
                1.0 - item.get("confidence", 0.5) 
                for item in signals.emotion_data 
                if isinstance(item, dict)
            ]
            if confusion_levels:
                avg_confusion = sum(confusion_levels) / len(confusion_levels)
                signal_states.append(("emotion", avg_confusion))
        
        # 3. 交互行为信号（鼠标/键盘活动）
        if signals.interaction_data:
            # 假设交互频率高可能表示困惑
            interaction_frequency = len(signals.interaction_data) / 60.0  # 每分钟交互次数
            normalized_frequency = min(1.0, interaction_frequency / 10.0)  # 归一化
            signal_states.append(("interaction", normalized_frequency))
        
        # 4. 播放行为信号（回放、暂停等）
        if signals.playback_data:
            # 统计回放和暂停事件
            replay_pause_count = sum(
                1 for item in signals.playback_data 
                if isinstance(item, dict) and 
                item.get("event_type") in ["replay", "pause"]
            )
            normalized_count = min(1.0, replay_pause_count / 5.0)  # 归一化
            signal_states.append(("playback", normalized_count))
        
        if not signal_states:
            return 0.5  # 没有信号数据，返回默认值
        
        # 计算信号之间的方差（方差越小，一致性越高）
        if len(signal_states) > 1:
            values = [state[1] for state in signal_states]
            mean_value = sum(values) / len(values)
            variance = sum((v - mean_value) ** 2 for v in values) / len(values)
            # 将方差转换为一致性分数（方差越小，一致性越高）
            consistency = 1.0 - min(1.0, variance * 2)  # 乘以2是为了放大差异
        else:
            consistency = 0.7  # 只有一个信号源，给予中等一致性
        
        return max(0.0, min(1.0, consistency))
    
    def gate_difficulty_detection(
        self,
        difficulty_result: DifficultyResult,
        confidence: float,
        user_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None
    ) -> GatedResult:
        """门控难点判定结果
        
        Args:
            difficulty_result: 原始难点判定结果
            confidence: 综合置信度
            user_id: 用户ID（可选，用于创建确认请求）
            knowledge_point_id: 知识点ID（可选，用于创建确认请求）
        
        Returns:
            门控后的判定结果
        """
        requires_confirmation = confidence < self.confidence_threshold
        
        if requires_confirmation:
            # 低置信度，需要人工确认
            status = "pending_confirmation"
            reason = f"置信度{confidence:.2f}低于阈值{self.confidence_threshold}，需要人工确认"
            
            # 创建确认请求
            if user_id is not None and knowledge_point_id is not None:
                self.request_human_confirmation(
                    user_id, knowledge_point_id, difficulty_result, confidence
                )
        else:
            # 高置信度，自动确认
            status = "auto_confirmed"
            reason = f"置信度{confidence:.2f}达到阈值{self.confidence_threshold}，自动确认"
        
        # 门控后的判定结果
        # 如果置信度低，暂时不判定为疑难点，等待确认
        gated_is_difficult = (
            difficulty_result.is_difficult 
            if not requires_confirmation 
            else False  # 低置信度时不自动判定
        )
        
        result = GatedResult(
            is_difficult=gated_is_difficult,
            difficulty_score=difficulty_result.difficulty_score,
            confidence=confidence,
            requires_confirmation=requires_confirmation,
            status=status,
            reason=reason
        )
        
        logger.info(
            f"Gated difficulty detection: is_difficult={gated_is_difficult}, "
            f"confidence={confidence:.3f}, requires_confirmation={requires_confirmation}"
        )
        
        return result
    
    def request_human_confirmation(
        self,
        user_id: int,
        knowledge_point_id: int,
        difficulty_result: DifficultyResult,
        confidence: float
    ) -> bool:
        """请求人工确认
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            difficulty_result: 难点判定结果
            confidence: 置信度
        
        Returns:
            是否成功创建确认请求
        """
        key = (user_id, knowledge_point_id)
        
        # 检查是否已有待确认的请求
        if key in self.confirmation_requests:
            existing = self.confirmation_requests[key]
            if existing.status == ConfirmationStatus.PENDING:
                logger.warning(
                    f"Confirmation request already exists for user={user_id}, "
                    f"kp={knowledge_point_id}"
                )
                return False
        
        # 创建新的确认请求
        request = ConfirmationRequest(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            difficulty_result=difficulty_result,
            confidence=confidence
        )
        
        self.confirmation_requests[key] = request
        
        logger.info(
            f"Created confirmation request for user={user_id}, "
            f"kp={knowledge_point_id}, confidence={confidence:.3f}"
        )
        
        return True
    
    def handle_confirmation_response(
        self,
        user_id: int,
        knowledge_point_id: int,
        confirmed: bool
    ) -> Dict[str, Any]:
        """处理确认响应
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            confirmed: 是否确认为疑难点
        
        Returns:
            处理结果字典
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.confirmation_requests:
            logger.warning(
                f"No confirmation request found for user={user_id}, kp={knowledge_point_id}"
            )
            return {
                "success": False,
                "message": "未找到确认请求"
            }
        
        request = self.confirmation_requests[key]
        
        if request.status != ConfirmationStatus.PENDING:
            logger.warning(
                f"Confirmation request already processed: status={request.status}"
            )
            return {
                "success": False,
                "message": f"确认请求已处理，状态：{request.status.value}"
            }
        
        # 更新确认状态
        if confirmed:
            request.status = ConfirmationStatus.CONFIRMED
            is_difficult = True
        else:
            request.status = ConfirmationStatus.REJECTED
            is_difficult = False
        
        result = {
            "success": True,
            "is_difficult": is_difficult,
            "difficulty_score": request.difficulty_result.difficulty_score,
            "confidence": request.confidence,
            "status": request.status.value
        }
        
        logger.info(
            f"Confirmation response processed: user={user_id}, kp={knowledge_point_id}, "
            f"confirmed={confirmed}, is_difficult={is_difficult}"
        )
        
        return result
    
    def mark_as_under_observation(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> bool:
        """标记为待观察（学生未响应确认请求）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            是否成功标记
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.confirmation_requests:
            return False
        
        request = self.confirmation_requests[key]
        
        if request.status == ConfirmationStatus.PENDING:
            request.status = ConfirmationStatus.IGNORED
            logger.info(
                f"Marked as under observation: user={user_id}, kp={knowledge_point_id}"
            )
            return True
        
        return False
    
    def get_confirmation_request(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> Optional[ConfirmationRequest]:
        """获取确认请求
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            确认请求对象，如果不存在则返回None
        """
        key = (user_id, knowledge_point_id)
        return self.confirmation_requests.get(key)
    
    def get_pending_confirmations(self, user_id: Optional[int] = None) -> List[ConfirmationRequest]:
        """获取待确认的请求列表
        
        Args:
            user_id: 用户ID（可选，如果提供则只返回该用户的请求）
        
        Returns:
            待确认请求列表
        """
        pending = [
            req for req in self.confirmation_requests.values()
            if req.status == ConfirmationStatus.PENDING
        ]
        
        if user_id is not None:
            pending = [req for req in pending if req.user_id == user_id]
        
        return pending
    
    def get_confidence_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取置信度统计报告
        
        Args:
            user_id: 用户ID（可选，如果提供则只统计该用户的数据）
        
        Returns:
            统计报告字典
        """
        requests = list(self.confirmation_requests.values())
        
        if user_id is not None:
            requests = [req for req in requests if req.user_id == user_id]
        
        if not requests:
            return {
                "total_requests": 0,
                "pending": 0,
                "confirmed": 0,
                "rejected": 0,
                "ignored": 0,
                "average_confidence": 0.0
            }
        
        stats = {
            "total_requests": len(requests),
            "pending": sum(1 for req in requests if req.status == ConfirmationStatus.PENDING),
            "confirmed": sum(1 for req in requests if req.status == ConfirmationStatus.CONFIRMED),
            "rejected": sum(1 for req in requests if req.status == ConfirmationStatus.REJECTED),
            "ignored": sum(1 for req in requests if req.status == ConfirmationStatus.IGNORED),
            "average_confidence": sum(req.confidence for req in requests) / len(requests)
        }
        
        return stats
