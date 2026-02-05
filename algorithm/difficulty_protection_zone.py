"""
难度保护区机制

基于v10.0需求，保护高难资源不被恶意反馈误下架。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """难度等级枚举"""
    BASIC = "basic"  # 基础
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级


class ProtectionStatus(Enum):
    """保护状态枚举"""
    PROTECTED = "protected"  # 受保护
    UNPROTECTED = "unprotected"  # 未保护
    UNDER_REVIEW = "under_review"  # 审核中


@dataclass
class FeedbackEvidence:
    """反馈证据"""
    feedback_id: int
    user_id: int
    evidence_type: str  # content_mismatch/too_difficult/too_easy/other
    description: str  # 详细说明
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProtectionRecord:
    """保护记录"""
    resource_id: int
    difficulty_level: DifficultyLevel
    protection_threshold: int
    negative_feedback_count: int
    status: ProtectionStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DowngradeEvaluation:
    """下架评估结果"""
    should_downgrade: bool  # 是否应该下架
    protection_status: ProtectionStatus
    current_feedback_count: int
    required_feedback_count: int
    has_sufficient_evidence: bool
    reason: str
    recommendation: str


class DifficultyProtectionZone:
    """难度保护区机制
    
    功能：
    1. 根据资源难度分级设置不同的下架阈值
    2. 高难资源（advanced）的下架阈值提高到10
    3. 高难资源下架需要提供内容不匹配的证据
    4. 自动调整下架阈值
    """
    
    # 默认下架阈值（根据难度等级）
    DEFAULT_THRESHOLDS = {
        DifficultyLevel.BASIC: 3,  # 基础资源：3个负面反馈
        DifficultyLevel.INTERMEDIATE: 5,  # 中级资源：5个负面反馈
        DifficultyLevel.ADVANCED: 10  # 高级资源：10个负面反馈
    }
    
    def __init__(
        self,
        custom_thresholds: Optional[Dict[DifficultyLevel, int]] = None
    ):
        """初始化难度保护区
        
        Args:
            custom_thresholds: 自定义阈值字典（可选）
        """
        self.protection_thresholds = custom_thresholds or self.DEFAULT_THRESHOLDS.copy()
        
        # 存储保护记录
        self.protection_records: Dict[int, ProtectionRecord] = {}
        
        # 存储反馈证据
        self.feedback_evidence: Dict[int, List[FeedbackEvidence]] = {}
        
        logger.info(
            f"DifficultyProtectionZone initialized with thresholds: "
            f"{[(level.value, threshold) for level, threshold in self.protection_thresholds.items()]}"
        )
    
    def get_protection_threshold(self, difficulty_level: DifficultyLevel) -> int:
        """获取保护阈值
        
        Args:
            difficulty_level: 难度等级
        
        Returns:
            保护阈值（需要的负面反馈数量）
        """
        threshold = self.protection_thresholds.get(difficulty_level, 3)
        
        logger.debug(
            f"Protection threshold for {difficulty_level.value}: {threshold}"
        )
        
        return threshold
    
    def check_protection_status(
        self,
        resource_id: int,
        difficulty_level: DifficultyLevel,
        negative_feedback_count: int
    ) -> Dict[str, Any]:
        """检查保护状态
        
        Args:
            resource_id: 资源ID
            difficulty_level: 难度等级
            negative_feedback_count: 负面反馈数量
        
        Returns:
            保护状态字典
        """
        threshold = self.get_protection_threshold(difficulty_level)
        
        # 判断是否达到下架阈值
        if negative_feedback_count >= threshold:
            status = ProtectionStatus.UNPROTECTED
            is_protected = False
        else:
            status = ProtectionStatus.PROTECTED
            is_protected = True
        
        # 更新或创建保护记录
        if resource_id in self.protection_records:
            record = self.protection_records[resource_id]
            record.negative_feedback_count = negative_feedback_count
            record.status = status
            record.updated_at = datetime.now()
        else:
            record = ProtectionRecord(
                resource_id=resource_id,
                difficulty_level=difficulty_level,
                protection_threshold=threshold,
                negative_feedback_count=negative_feedback_count,
                status=status
            )
            self.protection_records[resource_id] = record
        
        result = {
            "resource_id": resource_id,
            "difficulty_level": difficulty_level.value,
            "protection_threshold": threshold,
            "negative_feedback_count": negative_feedback_count,
            "is_protected": is_protected,
            "status": status.value,
            "remaining_to_threshold": max(0, threshold - negative_feedback_count)
        }
        
        logger.info(
            f"Protection status for resource={resource_id}: "
            f"level={difficulty_level.value}, "
            f"feedback={negative_feedback_count}/{threshold}, "
            f"protected={is_protected}"
        )
        
        return result
    
    def require_evidence_for_advanced(self, difficulty_level: DifficultyLevel) -> bool:
        """判断高级资源是否需要证据
        
        Args:
            difficulty_level: 难度等级
        
        Returns:
            是否需要证据
        """
        return difficulty_level == DifficultyLevel.ADVANCED
    
    def evaluate_downgrade_request(
        self,
        resource_id: int,
        difficulty_level: DifficultyLevel,
        negative_feedback_count: int,
        feedback_evidence: Optional[List[FeedbackEvidence]] = None
    ) -> DowngradeEvaluation:
        """评估下架请求
        
        Args:
            resource_id: 资源ID
            difficulty_level: 难度等级
            negative_feedback_count: 负面反馈数量
            feedback_evidence: 反馈证据列表（可选）
        
        Returns:
            下架评估结果
        """
        threshold = self.get_protection_threshold(difficulty_level)
        requires_evidence = self.require_evidence_for_advanced(difficulty_level)
        
        # 检查是否达到阈值
        if negative_feedback_count < threshold:
            return DowngradeEvaluation(
                should_downgrade=False,
                protection_status=ProtectionStatus.PROTECTED,
                current_feedback_count=negative_feedback_count,
                required_feedback_count=threshold,
                has_sufficient_evidence=False,
                reason=f"负面反馈数量({negative_feedback_count})未达到阈值({threshold})",
                recommendation="继续观察，收集更多反馈"
            )
        
        # 如果达到阈值，检查是否需要证据
        if requires_evidence:
            if not feedback_evidence:
                return DowngradeEvaluation(
                    should_downgrade=False,
                    protection_status=ProtectionStatus.UNDER_REVIEW,
                    current_feedback_count=negative_feedback_count,
                    required_feedback_count=threshold,
                    has_sufficient_evidence=False,
                    reason=f"高级资源需要提供内容不匹配的证据，当前无证据",
                    recommendation="需要提供内容不匹配的证据才能下架"
                )
            
            # 检查证据是否充分（至少需要3个内容不匹配的证据）
            content_mismatch_count = sum(
                1 for evidence in feedback_evidence
                if evidence.evidence_type == "content_mismatch"
            )
            
            if content_mismatch_count < 3:
                return DowngradeEvaluation(
                    should_downgrade=False,
                    protection_status=ProtectionStatus.UNDER_REVIEW,
                    current_feedback_count=negative_feedback_count,
                    required_feedback_count=threshold,
                    has_sufficient_evidence=False,
                    reason=f"高级资源需要至少3个内容不匹配的证据，当前只有{content_mismatch_count}个",
                    recommendation=f"需要至少3个内容不匹配的证据，当前{content_mismatch_count}个"
                )
            
            # 证据充分，可以下架
            return DowngradeEvaluation(
                should_downgrade=True,
                protection_status=ProtectionStatus.UNPROTECTED,
                current_feedback_count=negative_feedback_count,
                required_feedback_count=threshold,
                has_sufficient_evidence=True,
                reason=f"达到阈值({threshold})且证据充分({content_mismatch_count}个内容不匹配证据)",
                recommendation="可以下架"
            )
        else:
            # 不需要证据，达到阈值即可下架
            return DowngradeEvaluation(
                should_downgrade=True,
                protection_status=ProtectionStatus.UNPROTECTED,
                current_feedback_count=negative_feedback_count,
                required_feedback_count=threshold,
                has_sufficient_evidence=True,
                reason=f"达到阈值({threshold})",
                recommendation="可以下架"
            )
    
    def add_feedback_evidence(
        self,
        resource_id: int,
        evidence: FeedbackEvidence
    ) -> bool:
        """添加反馈证据
        
        Args:
            resource_id: 资源ID
            evidence: 反馈证据
        
        Returns:
            是否成功添加
        """
        if resource_id not in self.feedback_evidence:
            self.feedback_evidence[resource_id] = []
        
        self.feedback_evidence[resource_id].append(evidence)
        
        logger.info(
            f"Added feedback evidence for resource={resource_id}: "
            f"type={evidence.evidence_type}, user={evidence.user_id}"
        )
        
        return True
    
    def get_feedback_evidence(
        self,
        resource_id: int
    ) -> List[FeedbackEvidence]:
        """获取反馈证据列表
        
        Args:
            resource_id: 资源ID
        
        Returns:
            反馈证据列表
        """
        return self.feedback_evidence.get(resource_id, [])
    
    def set_protection_threshold(
        self,
        difficulty_level: DifficultyLevel,
        threshold: int
    ) -> bool:
        """设置保护阈值
        
        Args:
            difficulty_level: 难度等级
            threshold: 阈值（必须>0）
        
        Returns:
            是否成功设置
        """
        if threshold <= 0:
            logger.error(f"Invalid threshold {threshold}, must be > 0")
            return False
        
        self.protection_thresholds[difficulty_level] = threshold
        
        logger.info(
            f"Set protection threshold for {difficulty_level.value}: {threshold}"
        )
        
        return True
    
    def get_protection_statistics(
        self,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> Dict[str, Any]:
        """获取保护统计报告
        
        Args:
            difficulty_level: 难度等级（可选，如果提供则只统计该等级）
        
        Returns:
            统计报告字典
        """
        records = list(self.protection_records.values())
        
        if difficulty_level is not None:
            records = [r for r in records if r.difficulty_level == difficulty_level]
        
        if not records:
            return {
                "total_resources": 0,
                "protected": 0,
                "unprotected": 0,
                "under_review": 0,
                "average_feedback_count": 0.0
            }
        
        protected_count = sum(
            1 for r in records if r.status == ProtectionStatus.PROTECTED
        )
        unprotected_count = sum(
            1 for r in records if r.status == ProtectionStatus.UNPROTECTED
        )
        under_review_count = sum(
            1 for r in records if r.status == ProtectionStatus.UNDER_REVIEW
        )
        
        avg_feedback = sum(r.negative_feedback_count for r in records) / len(records)
        
        stats = {
            "total_resources": len(records),
            "protected": protected_count,
            "unprotected": unprotected_count,
            "under_review": under_review_count,
            "average_feedback_count": avg_feedback,
            "protection_rate": protected_count / len(records) if records else 0.0
        }
        
        return stats
    
    def get_protection_record(
        self,
        resource_id: int
    ) -> Optional[ProtectionRecord]:
        """获取保护记录
        
        Args:
            resource_id: 资源ID
        
        Returns:
            保护记录，如果不存在则返回None
        """
        return self.protection_records.get(resource_id)
