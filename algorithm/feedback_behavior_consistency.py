"""
反馈-行为一致性校验

基于v10.0需求，确保反馈的真实性。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """反馈类型枚举"""
    HELPFUL = "helpful"  # 有帮助
    NOT_HELPFUL = "not_helpful"  # 没有帮助
    TOO_VERBOSE = "too_verbose"  # 太冗长
    TOO_SIMPLE = "too_simple"  # 太简单
    CONTENT_MISMATCH = "content_mismatch"  # 内容不匹配


class ConsistencyStatus(Enum):
    """一致性状态枚举"""
    CONSISTENT = "consistent"  # 一致
    INCONSISTENT = "inconsistent"  # 不一致
    SUSPICIOUS = "suspicious"  # 可疑


@dataclass
class FeedbackData:
    """反馈数据"""
    feedback_id: int
    user_id: int
    resource_id: int
    feedback_type: FeedbackType
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BehaviorData:
    """学习行为数据"""
    user_id: int
    resource_id: int
    watch_percentage: float  # 观看百分比（0-1）
    total_watch_time: float  # 总观看时长（秒）
    resource_duration: float  # 资源总时长（秒）
    exercise_completed: bool  # 是否完成练习
    exercise_score: Optional[float] = None  # 练习正确率（0-1）
    interaction_count: int = 0  # 交互次数（点击、暂停等）


@dataclass
class ConsistencyResult:
    """一致性校验结果"""
    feedback_id: int
    is_consistent: bool
    consistency_status: ConsistencyStatus
    consistency_score: float  # 一致性分数（0-1）
    watch_percentage: float
    adjusted_weight: float  # 调整后的反馈权重
    is_anomaly: bool  # 是否标记为异常
    reason: str  # 原因说明
    details: Dict[str, Any]  # 详细信息


@dataclass
class AnomalyRecord:
    """异常记录"""
    feedback_id: int
    user_id: int
    resource_id: int
    reason: str
    consistency_score: float
    created_at: datetime = field(default_factory=datetime.now)


class FeedbackBehaviorConsistency:
    """反馈-行为一致性校验
    
    功能：
    1. 校验反馈与学习行为的一致性
    2. 观看百分比≥80%才计入统计
    3. 根据一致性调整反馈权重
    4. 标记异常反馈
    """
    
    # 默认阈值
    MIN_WATCH_PERCENTAGE = 0.8  # 最小观看百分比（80%）
    DEFAULT_WEIGHT = 1.0  # 默认权重
    CONSISTENT_WEIGHT = 1.0  # 一致时的权重
    INCONSISTENT_WEIGHT = 0.3  # 不一致时的权重
    SUSPICIOUS_WEIGHT = 0.1  # 可疑时的权重
    
    def __init__(
        self,
        min_watch_percentage: float = MIN_WATCH_PERCENTAGE
    ):
        """初始化一致性校验器
        
        Args:
            min_watch_percentage: 最小观看百分比阈值（默认0.8）
        """
        self.min_watch_percentage = min_watch_percentage
        
        # 存储一致性历史记录
        self.consistency_history: List[ConsistencyResult] = []
        
        # 存储异常记录
        self.anomaly_records: Dict[int, AnomalyRecord] = {}
        
        logger.info(
            f"FeedbackBehaviorConsistency initialized with "
            f"min_watch_percentage={min_watch_percentage}"
        )
    
    def check_consistency(
        self,
        feedback: FeedbackData,
        behavior_data: BehaviorData
    ) -> ConsistencyResult:
        """检查反馈与行为的一致性
        
        Args:
            feedback: 反馈数据
            behavior_data: 学习行为数据
        
        Returns:
            一致性校验结果
        """
        # 验证用户ID和资源ID是否匹配
        if feedback.user_id != behavior_data.user_id:
            logger.warning(
                f"User ID mismatch: feedback.user_id={feedback.user_id}, "
                f"behavior.user_id={behavior_data.user_id}"
            )
        
        if feedback.resource_id != behavior_data.resource_id:
            logger.warning(
                f"Resource ID mismatch: feedback.resource_id={feedback.resource_id}, "
                f"behavior.resource_id={behavior_data.resource_id}"
            )
        
        # 计算观看百分比
        watch_percentage = self.calculate_watch_percentage(behavior_data)
        
        # 检查是否达到最小观看百分比
        if watch_percentage < self.min_watch_percentage:
            # 未达到阈值，标记为不一致
            return ConsistencyResult(
                feedback_id=feedback.feedback_id,
                is_consistent=False,
                consistency_status=ConsistencyStatus.INCONSISTENT,
                consistency_score=0.0,
                watch_percentage=watch_percentage,
                adjusted_weight=0.0,  # 不计入统计
                is_anomaly=True,
                reason=f"观看百分比({watch_percentage:.1%})低于阈值({self.min_watch_percentage:.1%})",
                details={
                    "watch_percentage": watch_percentage,
                    "min_threshold": self.min_watch_percentage,
                    "total_watch_time": behavior_data.total_watch_time,
                    "resource_duration": behavior_data.resource_duration
                }
            )
        
        # 根据反馈类型进行一致性校验
        consistency_score = self._calculate_consistency_score(
            feedback, behavior_data, watch_percentage
        )
        
        # 判断一致性状态
        if consistency_score >= 0.8:
            status = ConsistencyStatus.CONSISTENT
            is_consistent = True
            weight = self.CONSISTENT_WEIGHT
            is_anomaly = False
            reason = "反馈与行为一致"
        elif consistency_score >= 0.5:
            status = ConsistencyStatus.SUSPICIOUS
            is_consistent = False
            weight = self.SUSPICIOUS_WEIGHT
            is_anomaly = True
            reason = "反馈与行为部分一致，存在可疑"
        else:
            status = ConsistencyStatus.INCONSISTENT
            is_consistent = False
            weight = self.INCONSISTENT_WEIGHT
            is_anomaly = True
            reason = "反馈与行为不一致"
        
        # 调整权重
        adjusted_weight = self.adjust_feedback_weight(feedback, consistency_score)
        
        result = ConsistencyResult(
            feedback_id=feedback.feedback_id,
            is_consistent=is_consistent,
            consistency_status=status,
            consistency_score=consistency_score,
            watch_percentage=watch_percentage,
            adjusted_weight=adjusted_weight,
            is_anomaly=is_anomaly,
            reason=reason,
            details={
                "watch_percentage": watch_percentage,
                "exercise_completed": behavior_data.exercise_completed,
                "exercise_score": behavior_data.exercise_score,
                "interaction_count": behavior_data.interaction_count
            }
        )
        
        # 记录历史
        self.consistency_history.append(result)
        
        # 如果标记为异常，记录异常
        if is_anomaly:
            self.mark_anomaly(feedback.feedback_id, reason, consistency_score, feedback.user_id, feedback.resource_id)
        
        logger.info(
            f"Consistency check for feedback={feedback.feedback_id}: "
            f"status={status.value}, score={consistency_score:.2f}, "
            f"weight={adjusted_weight:.2f}, anomaly={is_anomaly}"
        )
        
        return result
    
    def _calculate_consistency_score(
        self,
        feedback: FeedbackData,
        behavior_data: BehaviorData,
        watch_percentage: float
    ) -> float:
        """计算一致性分数
        
        Args:
            feedback: 反馈数据
            behavior_data: 学习行为数据
            watch_percentage: 观看百分比
        
        Returns:
            一致性分数（0-1）
        """
        score_components = []
        weights = []
        
        # 1. 观看百分比一致性（权重0.4）
        watch_score = min(1.0, watch_percentage / self.min_watch_percentage)
        score_components.append(watch_score)
        weights.append(0.4)
        
        # 2. 反馈类型与行为的一致性（权重0.4）
        type_consistency = self._check_feedback_type_consistency(
            feedback.feedback_type, behavior_data
        )
        score_components.append(type_consistency)
        weights.append(0.4)
        
        # 3. 练习完成情况（权重0.2）
        exercise_score = 1.0 if behavior_data.exercise_completed else 0.5
        if behavior_data.exercise_score is not None:
            exercise_score = behavior_data.exercise_score
        score_components.append(exercise_score)
        weights.append(0.2)
        
        # 加权平均
        total_weight = sum(weights)
        consistency_score = sum(
            comp * weight for comp, weight in zip(score_components, weights)
        ) / total_weight if total_weight > 0 else 0.0
        
        return max(0.0, min(1.0, consistency_score))
    
    def _check_feedback_type_consistency(
        self,
        feedback_type: FeedbackType,
        behavior_data: BehaviorData
    ) -> float:
        """检查反馈类型与行为的一致性
        
        Args:
            feedback_type: 反馈类型
            behavior_data: 学习行为数据
        
        Returns:
            一致性分数（0-1）
        """
        if feedback_type == FeedbackType.HELPFUL:
            # 如果反馈"有帮助"，应该完成练习且正确率较高
            if behavior_data.exercise_completed:
                if behavior_data.exercise_score is not None:
                    return behavior_data.exercise_score  # 使用练习正确率
                return 0.8  # 完成练习但无分数，给予中等分数
            return 0.3  # 未完成练习，一致性低
        
        elif feedback_type == FeedbackType.NOT_HELPFUL:
            # 如果反馈"没有帮助"，但观看百分比高，可能不一致
            # 但如果练习正确率低，则一致
            if behavior_data.exercise_score is not None:
                return 1.0 - behavior_data.exercise_score  # 正确率低则一致
            return 0.5  # 无练习数据，给予中等分数
        
        elif feedback_type == FeedbackType.CONTENT_MISMATCH:
            # 内容不匹配：如果观看百分比高但练习正确率低，可能一致
            if behavior_data.exercise_completed and behavior_data.exercise_score is not None:
                if behavior_data.exercise_score < 0.5:
                    return 0.8  # 正确率低，可能确实不匹配
                return 0.3  # 正确率高，不一致
            return 0.5
        
        else:
            # 其他反馈类型（too_verbose, too_simple）
            # 如果观看百分比高，给予中等一致性
            return 0.6
    
    def calculate_watch_percentage(self, behavior_data: BehaviorData) -> float:
        """计算观看百分比
        
        Args:
            behavior_data: 学习行为数据
        
        Returns:
            观看百分比（0-1）
        """
        if behavior_data.resource_duration <= 0:
            logger.warning(
                f"Invalid resource duration: {behavior_data.resource_duration}"
            )
            return 0.0
        
        watch_percentage = behavior_data.total_watch_time / behavior_data.resource_duration
        
        # 确保在[0, 1]范围内
        watch_percentage = max(0.0, min(1.0, watch_percentage))
        
        return watch_percentage
    
    def adjust_feedback_weight(
        self,
        feedback: FeedbackData,
        consistency_score: float
    ) -> float:
        """调整反馈权重
        
        Args:
            feedback: 反馈数据
            consistency_score: 一致性分数
        
        Returns:
            调整后的权重
        """
        if consistency_score >= 0.8:
            weight = self.CONSISTENT_WEIGHT
        elif consistency_score >= 0.5:
            weight = self.SUSPICIOUS_WEIGHT
        else:
            weight = self.INCONSISTENT_WEIGHT
        
        # 根据一致性分数线性调整
        adjusted_weight = weight * consistency_score
        
        logger.debug(
            f"Adjusted feedback weight for feedback={feedback.feedback_id}: "
            f"{self.DEFAULT_WEIGHT} -> {adjusted_weight:.2f} "
            f"(consistency={consistency_score:.2f})"
        )
        
        return adjusted_weight
    
    def mark_anomaly(
        self,
        feedback_id: int,
        reason: str,
        consistency_score: float,
        user_id: Optional[int] = None,
        resource_id: Optional[int] = None
    ) -> bool:
        """标记异常反馈
        
        Args:
            feedback_id: 反馈ID
            reason: 异常原因
            consistency_score: 一致性分数
            user_id: 用户ID（可选）
            resource_id: 资源ID（可选）
        
        Returns:
            是否成功标记
        """
        record = AnomalyRecord(
            feedback_id=feedback_id,
            user_id=user_id or 0,
            resource_id=resource_id or 0,
            reason=reason,
            consistency_score=consistency_score
        )
        
        self.anomaly_records[feedback_id] = record
        
        logger.warning(
            f"Marked anomaly for feedback={feedback_id}: {reason} "
            f"(consistency_score={consistency_score:.2f})"
        )
        
        return True
    
    def get_consistency_statistics(
        self,
        user_id: Optional[int] = None,
        resource_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取一致性统计报告
        
        Args:
            user_id: 用户ID（可选）
            resource_id: 资源ID（可选）
        
        Returns:
            统计报告字典
        """
        results = self.consistency_history.copy()
        
        if user_id is not None:
            # 需要从反馈数据中获取用户ID，这里简化处理
            pass
        
        if resource_id is not None:
            # 需要从反馈数据中获取资源ID，这里简化处理
            pass
        
        if not results:
            return {
                "total_feedbacks": 0,
                "consistent": 0,
                "inconsistent": 0,
                "suspicious": 0,
                "anomalies": 0,
                "average_consistency_score": 0.0,
                "average_weight": 0.0
            }
        
        consistent_count = sum(1 for r in results if r.is_consistent)
        inconsistent_count = sum(
            1 for r in results 
            if r.consistency_status == ConsistencyStatus.INCONSISTENT
        )
        suspicious_count = sum(
            1 for r in results 
            if r.consistency_status == ConsistencyStatus.SUSPICIOUS
        )
        anomaly_count = sum(1 for r in results if r.is_anomaly)
        
        avg_consistency = sum(r.consistency_score for r in results) / len(results)
        avg_weight = sum(r.adjusted_weight for r in results) / len(results)
        
        stats = {
            "total_feedbacks": len(results),
            "consistent": consistent_count,
            "inconsistent": inconsistent_count,
            "suspicious": suspicious_count,
            "anomalies": anomaly_count,
            "average_consistency_score": avg_consistency,
            "average_weight": avg_weight,
            "consistency_rate": consistent_count / len(results) if results else 0.0
        }
        
        return stats
    
    def get_anomaly_records(
        self,
        user_id: Optional[int] = None
    ) -> List[AnomalyRecord]:
        """获取异常记录列表
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            异常记录列表
        """
        records = list(self.anomaly_records.values())
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        # 按时间倒序排序
        records.sort(key=lambda x: x.created_at, reverse=True)
        
        return records
