"""
数据审计引擎

基于v10.0需求，检测和过滤异常/恶意反馈。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditResult(Enum):
    """审计结果枚举"""
    NORMAL = "normal"  # 正常
    ABNORMAL = "abnormal"  # 异常
    MALICIOUS = "malicious"  # 恶意


@dataclass
class FeedbackData:
    """反馈数据"""
    feedback_id: int
    user_id: int
    resource_id: int
    feedback_type: str  # helpful/not_helpful/too_verbose/too_simple/content_mismatch
    score: float  # 评分（0-1）
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


@dataclass
class ResourceDifficulty:
    """资源难度信息"""
    resource_id: int
    difficulty_level: str  # basic/intermediate/advanced
    difficulty_score: float  # 难度分数（0-1）


@dataclass
class AuditResultDetail:
    """审计结果详情"""
    feedback_id: int
    audit_result: AuditResult
    is_filtered: bool  # 是否被过滤
    reasons: List[str]  # 原因列表
    confidence: float  # 置信度（0-1）


@dataclass
class AnomalyPattern:
    """异常模式"""
    pattern_type: str  # 异常模式类型
    affected_feedbacks: List[int]  # 受影响的反馈ID列表
    severity: str  # 严重程度：low/medium/high
    description: str  # 描述


class DataAuditEngine:
    """数据审计引擎
    
    功能：
    1. 异常检测：检测异常反馈模式
    2. 恶意过滤：过滤恶意反馈，不计入资源质量统计
    3. 一致性校验：校验反馈与行为的一致性
    4. 难度保护区：高难资源自动下架阈值提高
    """
    
    # 一致性校验阈值
    MIN_WATCH_PERCENTAGE = 0.8  # 最小观看百分比（80%）
    
    # 异常检测阈值
    BATCH_FEEDBACK_THRESHOLD = 5  # 批量反馈阈值（短时间内超过此数量视为异常）
    BATCH_TIME_WINDOW_MINUTES = 10  # 批量反馈时间窗口（分钟）
    
    # 恶意反馈判定阈值
    MALICIOUS_SCORE_THRESHOLD = 0.3  # 恶意分数阈值
    
    def __init__(self):
        """初始化数据审计引擎"""
        # 存储审计结果
        self.audit_results: Dict[int, AuditResultDetail] = {}  # key: feedback_id
        
        # 存储异常模式
        self.anomaly_patterns: List[AnomalyPattern] = []
        
        # 存储用户反馈历史（用于检测批量反馈）
        self.user_feedback_history: Dict[int, List[FeedbackData]] = {}  # key: user_id
        
        logger.info("DataAuditEngine initialized")
    
    def audit_feedback(
        self,
        feedback: FeedbackData,
        behavior_data: Optional[BehaviorData] = None,
        resource_difficulty: Optional[ResourceDifficulty] = None
    ) -> AuditResultDetail:
        """审计反馈
        
        Args:
            feedback: 反馈数据
            behavior_data: 学习行为数据（可选）
            resource_difficulty: 资源难度信息（可选）
        
        Returns:
            审计结果详情
        """
        reasons = []
        is_filtered = False
        confidence = 1.0
        audit_result = AuditResult.NORMAL
        
        # 1. 一致性校验
        if behavior_data:
            consistency_check = self.check_consistency(feedback, behavior_data)
            if not consistency_check["is_consistent"]:
                reasons.append(consistency_check["reason"])
                is_filtered = True
                audit_result = AuditResult.ABNORMAL
                confidence = 0.5
        
        # 2. 检测异常模式
        anomaly_patterns = self.detect_anomaly_pattern(feedback.user_id)
        if anomaly_patterns:
            for pattern in anomaly_patterns:
                if pattern.severity in ["medium", "high"]:
                    reasons.append(f"异常模式：{pattern.description}")
                    is_filtered = True
                    if pattern.severity == "high":
                        audit_result = AuditResult.MALICIOUS
                        confidence = 0.2
                    else:
                        audit_result = AuditResult.ABNORMAL
                        confidence = 0.5
        
        # 3. 检测批量恶意反馈
        if self._is_batch_malicious_feedback(feedback.user_id):
            reasons.append("检测到批量恶意反馈模式")
            is_filtered = True
            audit_result = AuditResult.MALICIOUS
            confidence = 0.1
        
        # 4. 检测未观看就反馈
        if behavior_data and behavior_data.watch_percentage < 0.1:
            reasons.append(f"未观看就反馈（观看百分比：{behavior_data.watch_percentage:.1%}）")
            is_filtered = True
            audit_result = AuditResult.ABNORMAL
            confidence = 0.3
        
        # 5. 应用难度保护区（如果资源是高难资源）
        if resource_difficulty and resource_difficulty.difficulty_level == "advanced":
            protection_info = self.apply_difficulty_protection_zone(
                feedback.resource_id, resource_difficulty
            )
            if protection_info.get("is_protected"):
                reasons.append("高难资源受保护，需要更多证据")
                # 高难资源不直接过滤，但降低权重
        
        # 创建审计结果
        result = AuditResultDetail(
            feedback_id=feedback.feedback_id,
            audit_result=audit_result,
            is_filtered=is_filtered,
            reasons=reasons if reasons else ["正常"],
            confidence=confidence
        )
        
        self.audit_results[feedback.feedback_id] = result
        
        # 更新用户反馈历史
        if feedback.user_id not in self.user_feedback_history:
            self.user_feedback_history[feedback.user_id] = []
        self.user_feedback_history[feedback.user_id].append(feedback)
        
        # 只保留最近100条记录
        if len(self.user_feedback_history[feedback.user_id]) > 100:
            self.user_feedback_history[feedback.user_id] = \
                self.user_feedback_history[feedback.user_id][-100:]
        
        logger.info(
            f"Audited feedback={feedback.feedback_id}: "
            f"result={audit_result.value}, filtered={is_filtered}, "
            f"reasons={len(reasons)}"
        )
        
        return result
    
    def check_consistency(
        self,
        feedback: FeedbackData,
        behavior: BehaviorData
    ) -> Dict[str, Any]:
        """检查反馈与行为的一致性
        
        Args:
            feedback: 反馈数据
            behavior: 学习行为数据
        
        Returns:
            一致性检查结果字典
        """
        is_consistent = True
        reason = ""
        
        # 检查观看百分比
        if behavior.watch_percentage < self.MIN_WATCH_PERCENTAGE:
            is_consistent = False
            reason = (
                f"观看百分比({behavior.watch_percentage:.1%})低于阈值"
                f"({self.MIN_WATCH_PERCENTAGE:.1%})"
            )
        
        # 检查反馈类型与行为的一致性
        if feedback.feedback_type == "not_helpful":
            # 如果反馈"没有帮助"，但观看百分比很高，可能不一致
            if behavior.watch_percentage > 0.9:
                # 但如果练习正确率低，则一致
                if behavior.exercise_score is not None and behavior.exercise_score > 0.7:
                    is_consistent = False
                    reason = "反馈'没有帮助'但观看完整且练习正确率高，不一致"
        
        return {
            "is_consistent": is_consistent,
            "reason": reason if not is_consistent else "一致",
            "watch_percentage": behavior.watch_percentage
        }
    
    def detect_anomaly_pattern(
        self,
        user_id: int,
        time_window_minutes: int = BATCH_TIME_WINDOW_MINUTES
    ) -> List[AnomalyPattern]:
        """检测异常模式
        
        Args:
            user_id: 用户ID
            time_window_minutes: 时间窗口（分钟）
        
        Returns:
            异常模式列表
        """
        if user_id not in self.user_feedback_history:
            return []
        
        feedbacks = self.user_feedback_history[user_id]
        
        if len(feedbacks) < 2:
            return []
        
        patterns = []
        
        # 1. 检测批量反馈（短时间内大量反馈）
        now = datetime.now()
        time_window = timedelta(minutes=time_window_minutes)
        
        recent_feedbacks = [
            f for f in feedbacks
            if (now - f.created_at) <= time_window
        ]
        
        if len(recent_feedbacks) >= self.BATCH_FEEDBACK_THRESHOLD:
            # 检查是否都是负面反馈
            negative_count = sum(
                1 for f in recent_feedbacks
                if f.feedback_type in ["not_helpful", "content_mismatch"] or f.score < 0.3
            )
            
            if negative_count >= len(recent_feedbacks) * 0.8:
                patterns.append(AnomalyPattern(
                    pattern_type="batch_negative_feedback",
                    affected_feedbacks=[f.feedback_id for f in recent_feedbacks],
                    severity="high",
                    description=f"短时间内批量负面反馈（{len(recent_feedbacks)}条）"
                ))
            else:
                patterns.append(AnomalyPattern(
                    pattern_type="batch_feedback",
                    affected_feedbacks=[f.feedback_id for f in recent_feedbacks],
                    severity="medium",
                    description=f"短时间内大量反馈（{len(recent_feedbacks)}条）"
                ))
        
        # 2. 检测重复反馈（同一资源多次反馈）
        resource_feedback_count = defaultdict(int)
        for f in feedbacks:
            resource_feedback_count[f.resource_id] += 1
        
        for resource_id, count in resource_feedback_count.items():
            if count >= 3:
                resource_feedbacks = [
                    f for f in feedbacks if f.resource_id == resource_id
                ]
                patterns.append(AnomalyPattern(
                    pattern_type="repeated_feedback",
                    affected_feedbacks=[f.feedback_id for f in resource_feedbacks],
                    severity="medium",
                    description=f"同一资源重复反馈{count}次"
                ))
        
        # 3. 检测极端评分模式（全是0分或全是1分）
        if len(feedbacks) >= 5:
            scores = [f.score for f in feedbacks[-10:]]  # 最近10条
            if all(s < 0.1 for s in scores):
                patterns.append(AnomalyPattern(
                    pattern_type="extreme_low_scores",
                    affected_feedbacks=[f.feedback_id for f in feedbacks[-10:]],
                    severity="high",
                    description="极端低分模式（全部<0.1）"
                ))
            elif all(s > 0.9 for s in scores):
                patterns.append(AnomalyPattern(
                    pattern_type="extreme_high_scores",
                    affected_feedbacks=[f.feedback_id for f in feedbacks[-10:]],
                    severity="medium",
                    description="极端高分模式（全部>0.9）"
                ))
        
        if patterns:
            self.anomaly_patterns.extend(patterns)
        
        return patterns
    
    def filter_malicious_feedback(
        self,
        feedback_list: List[FeedbackData],
        behavior_data_map: Optional[Dict[int, BehaviorData]] = None
    ) -> List[FeedbackData]:
        """过滤恶意反馈
        
        Args:
            feedback_list: 反馈列表
            behavior_data_map: 行为数据映射（可选）
        
        Returns:
            过滤后的反馈列表
        """
        filtered = []
        
        for feedback in feedback_list:
            # 获取行为数据
            behavior_data = None
            if behavior_data_map and feedback.feedback_id in behavior_data_map:
                behavior_data = behavior_data_map[feedback.feedback_id]
            
            # 审计反馈
            audit_result = self.audit_feedback(feedback, behavior_data)
            
            # 只保留未被过滤的反馈
            if not audit_result.is_filtered:
                filtered.append(feedback)
        
        logger.info(
            f"Filtered feedbacks: {len(feedback_list)} -> {len(filtered)} "
            f"({len(feedback_list) - len(filtered)} filtered)"
        )
        
        return filtered
    
    def apply_difficulty_protection_zone(
        self,
        resource_id: int,
        resource_difficulty: ResourceDifficulty
    ) -> Dict[str, Any]:
        """应用难度保护区
        
        Args:
            resource_id: 资源ID
            resource_difficulty: 资源难度信息
        
        Returns:
            保护信息字典
        """
        if resource_difficulty.difficulty_level == "advanced":
            # 高难资源，提高下架阈值
            protection_threshold = 10  # 需要10个负面反馈才下架
            
            return {
                "is_protected": True,
                "protection_threshold": protection_threshold,
                "difficulty_level": resource_difficulty.difficulty_level,
                "message": "高难资源受保护，需要更多负面反馈证据才能下架"
            }
        elif resource_difficulty.difficulty_level == "intermediate":
            protection_threshold = 5
            return {
                "is_protected": True,
                "protection_threshold": protection_threshold,
                "difficulty_level": resource_difficulty.difficulty_level,
                "message": "中级资源受保护"
            }
        else:
            protection_threshold = 3
            return {
                "is_protected": False,
                "protection_threshold": protection_threshold,
                "difficulty_level": resource_difficulty.difficulty_level,
                "message": "基础资源正常阈值"
            }
    
    def _is_batch_malicious_feedback(self, user_id: int) -> bool:
        """检测是否为批量恶意反馈
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否为批量恶意反馈
        """
        if user_id not in self.user_feedback_history:
            return False
        
        feedbacks = self.user_feedback_history[user_id]
        
        if len(feedbacks) < self.BATCH_FEEDBACK_THRESHOLD:
            return False
        
        # 检查最近时间窗口内的反馈
        now = datetime.now()
        time_window = timedelta(minutes=self.BATCH_TIME_WINDOW_MINUTES)
        
        recent_feedbacks = [
            f for f in feedbacks
            if (now - f.created_at) <= time_window
        ]
        
        if len(recent_feedbacks) < self.BATCH_FEEDBACK_THRESHOLD:
            return False
        
        # 检查是否都是负面反馈
        negative_count = sum(
            1 for f in recent_feedbacks
            if f.feedback_type in ["not_helpful", "content_mismatch"] or f.score < 0.3
        )
        
        # 如果80%以上是负面反馈，判定为批量恶意反馈
        return negative_count >= len(recent_feedbacks) * 0.8
    
    def get_audit_statistics(
        self,
        resource_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取审计统计报告
        
        Args:
            resource_id: 资源ID（可选）
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        results = list(self.audit_results.values())
        
        # 过滤
        if resource_id is not None:
            # 需要从反馈数据中获取资源ID，这里简化处理
            pass
        
        if user_id is not None:
            # 需要从反馈数据中获取用户ID，这里简化处理
            pass
        
        if not results:
            return {
                "total_audited": 0,
                "normal": 0,
                "abnormal": 0,
                "malicious": 0,
                "filtered_count": 0,
                "filter_rate": 0.0
            }
        
        normal_count = sum(1 for r in results if r.audit_result == AuditResult.NORMAL)
        abnormal_count = sum(1 for r in results if r.audit_result == AuditResult.ABNORMAL)
        malicious_count = sum(1 for r in results if r.audit_result == AuditResult.MALICIOUS)
        filtered_count = sum(1 for r in results if r.is_filtered)
        
        return {
            "total_audited": len(results),
            "normal": normal_count,
            "abnormal": abnormal_count,
            "malicious": malicious_count,
            "filtered_count": filtered_count,
            "filter_rate": filtered_count / len(results) if results else 0.0,
            "average_confidence": sum(r.confidence for r in results) / len(results) if results else 0.0
        }
    
    def get_anomaly_patterns(
        self,
        severity: Optional[str] = None
    ) -> List[AnomalyPattern]:
        """获取异常模式列表
        
        Args:
            severity: 严重程度过滤（可选）
        
        Returns:
            异常模式列表
        """
        patterns = self.anomaly_patterns.copy()
        
        if severity is not None:
            patterns = [p for p in patterns if p.severity == severity]
        
        return patterns
