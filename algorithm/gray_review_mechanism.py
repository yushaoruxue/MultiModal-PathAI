"""
修正资源灰度复核机制

基于v7.0需求，修正资源前先灰度发布，收集反馈后再正式发布。
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReleaseStatus(Enum):
    """发布状态枚举"""
    DRAFT = "draft"  # 草稿
    GRAY = "gray"  # 灰度发布
    PRODUCTION = "production"  # 正式发布
    REJECTED = "rejected"  # 已拒绝


@dataclass
class GrayReleaseConfig:
    """灰度发布配置"""
    resource_id: int
    gray_ratio: float  # 灰度比例（0-1）
    target_user_count: int  # 目标用户数
    actual_user_count: int = 0  # 实际用户数
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ReleaseStatus = ReleaseStatus.GRAY


@dataclass
class GrayFeedback:
    """灰度反馈"""
    feedback_id: int
    user_id: int
    resource_id: int
    feedback_type: str  # helpful/not_helpful/too_verbose/too_simple/content_mismatch
    score: float  # 评分（0-1）
    comment: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityEvaluation:
    """质量评估结果"""
    resource_id: int
    total_feedbacks: int
    average_score: float  # 平均评分（0-1）
    positive_rate: float  # 正面反馈率
    quality_score: float  # 综合质量分数（0-1）
    meets_threshold: bool  # 是否达到质量阈值
    recommendation: str  # 建议：promote/reject/optimize


class GrayReviewMechanism:
    """修正资源灰度复核机制
    
    功能：
    1. 灰度发布：修正资源先发布给部分学生（如10%）
    2. 反馈收集：收集灰度用户的反馈
    3. 质量评估：基于反馈评估修正资源质量
    4. 正式发布：如果质量达标，正式发布；否则继续优化
    """
    
    # 默认灰度比例
    DEFAULT_GRAY_RATIO = 0.1  # 10%
    
    # 默认质量阈值
    DEFAULT_QUALITY_THRESHOLD = 0.7  # 70%
    
    # 最小反馈数量
    MIN_FEEDBACK_COUNT = 5
    
    def __init__(
        self,
        default_gray_ratio: float = DEFAULT_GRAY_RATIO,
        default_quality_threshold: float = DEFAULT_QUALITY_THRESHOLD
    ):
        """初始化灰度复核机制
        
        Args:
            default_gray_ratio: 默认灰度比例（0-1）
            default_quality_threshold: 默认质量阈值（0-1）
        """
        self.default_gray_ratio = default_gray_ratio
        self.default_quality_threshold = default_quality_threshold
        
        # 存储灰度发布配置
        self.gray_releases: Dict[int, GrayReleaseConfig] = {}  # key: resource_id
        
        # 存储灰度反馈
        self.gray_feedbacks: Dict[int, List[GrayFeedback]] = {}  # key: resource_id
        
        # 存储所有用户ID（用于灰度选择）
        self.all_user_ids: Set[int] = set()
        
        logger.info(
            f"GrayReviewMechanism initialized with "
            f"gray_ratio={default_gray_ratio}, "
            f"quality_threshold={default_quality_threshold}"
        )
    
    def gray_release_resource(
        self,
        resource_id: int,
        gray_ratio: Optional[float] = None,
        target_user_ids: Optional[List[int]] = None
    ) -> bool:
        """灰度发布资源
        
        Args:
            resource_id: 资源ID
            gray_ratio: 灰度比例（可选，默认使用初始化时的比例）
            target_user_ids: 目标用户ID列表（可选，如果不提供则自动选择）
        
        Returns:
            是否成功发布
        """
        if gray_ratio is None:
            gray_ratio = self.default_gray_ratio
        
        if gray_ratio <= 0 or gray_ratio > 1:
            logger.error(f"Invalid gray ratio {gray_ratio}, must be in (0, 1]")
            return False
        
        # 如果资源已经在灰度发布中，不允许重复发布
        if resource_id in self.gray_releases:
            existing = self.gray_releases[resource_id]
            if existing.status == ReleaseStatus.GRAY:
                logger.warning(
                    f"Resource {resource_id} is already in gray release"
                )
                return False
        
        # 选择目标用户
        if target_user_ids is None:
            if not self.all_user_ids:
                logger.warning("No users available for gray release")
                return False
            
            target_count = max(1, int(len(self.all_user_ids) * gray_ratio))
            target_user_ids = random.sample(
                list(self.all_user_ids), min(target_count, len(self.all_user_ids))
            )
        
        # 创建灰度发布配置
        config = GrayReleaseConfig(
            resource_id=resource_id,
            gray_ratio=gray_ratio,
            target_user_count=len(target_user_ids),
            actual_user_count=0,  # 初始为0，实际使用时更新
            status=ReleaseStatus.GRAY
        )
        
        self.gray_releases[resource_id] = config
        
        # 初始化反馈列表
        if resource_id not in self.gray_feedbacks:
            self.gray_feedbacks[resource_id] = []
        
        logger.info(
            f"Gray release started for resource={resource_id}: "
            f"ratio={gray_ratio:.1%}, target_users={len(target_user_ids)}"
        )
        
        return True
    
    def collect_gray_feedback(
        self,
        resource_id: int,
        user_id: int,
        feedback_type: str,
        score: float,
        comment: Optional[str] = None
    ) -> bool:
        """收集灰度反馈
        
        Args:
            resource_id: 资源ID
            user_id: 用户ID
            feedback_type: 反馈类型
            score: 评分（0-1）
            comment: 评论（可选）
        
        Returns:
            是否成功收集
        """
        if resource_id not in self.gray_releases:
            logger.warning(
                f"Resource {resource_id} is not in gray release, "
                f"feedback will be ignored"
            )
            return False
        
        config = self.gray_releases[resource_id]
        
        if config.status != ReleaseStatus.GRAY:
            logger.warning(
                f"Resource {resource_id} is not in gray status, "
                f"current status: {config.status.value}"
            )
            return False
        
        # 创建反馈
        feedback_id = len(self.gray_feedbacks.get(resource_id, [])) + 1
        
        feedback = GrayFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            resource_id=resource_id,
            feedback_type=feedback_type,
            score=score,
            comment=comment
        )
        
        if resource_id not in self.gray_feedbacks:
            self.gray_feedbacks[resource_id] = []
        
        self.gray_feedbacks[resource_id].append(feedback)
        
        # 更新实际用户数
        unique_users = set(f.user_id for f in self.gray_feedbacks[resource_id])
        config.actual_user_count = len(unique_users)
        
        logger.info(
            f"Collected gray feedback for resource={resource_id}, "
            f"user={user_id}, type={feedback_type}, score={score:.2f}"
        )
        
        return True
    
    def evaluate_gray_quality(
        self,
        resource_id: int,
        quality_threshold: Optional[float] = None
    ) -> QualityEvaluation:
        """评估灰度资源质量
        
        Args:
            resource_id: 资源ID
            quality_threshold: 质量阈值（可选，默认使用初始化时的阈值）
        
        Returns:
            质量评估结果
        """
        if resource_id not in self.gray_releases:
            return QualityEvaluation(
                resource_id=resource_id,
                total_feedbacks=0,
                average_score=0.0,
                positive_rate=0.0,
                quality_score=0.0,
                meets_threshold=False,
                recommendation="资源未进行灰度发布"
            )
        
        if resource_id not in self.gray_feedbacks:
            return QualityEvaluation(
                resource_id=resource_id,
                total_feedbacks=0,
                average_score=0.0,
                positive_rate=0.0,
                quality_score=0.0,
                meets_threshold=False,
                recommendation="暂无反馈数据"
            )
        
        feedbacks = self.gray_feedbacks[resource_id]
        
        if len(feedbacks) < self.MIN_FEEDBACK_COUNT:
            return QualityEvaluation(
                resource_id=resource_id,
                total_feedbacks=len(feedbacks),
                average_score=0.0,
                positive_rate=0.0,
                quality_score=0.0,
                meets_threshold=False,
                recommendation=f"反馈数量不足（{len(feedbacks)}/{self.MIN_FEEDBACK_COUNT}），需要更多反馈"
            )
        
        # 计算平均评分
        average_score = sum(f.score for f in feedbacks) / len(feedbacks)
        
        # 计算正面反馈率（helpful或评分>=0.7）
        positive_count = sum(
            1 for f in feedbacks
            if f.feedback_type == "helpful" or f.score >= 0.7
        )
        positive_rate = positive_count / len(feedbacks)
        
        # 计算综合质量分数（加权平均）
        quality_score = (average_score * 0.6 + positive_rate * 0.4)
        
        if quality_threshold is None:
            quality_threshold = self.default_quality_threshold
        
        meets_threshold = quality_score >= quality_threshold
        
        # 生成建议
        if meets_threshold:
            recommendation = "质量达标，可以正式发布"
        else:
            # 分析主要问题
            negative_feedbacks = [
                f for f in feedbacks
                if f.feedback_type in ["not_helpful", "too_verbose", "too_simple", "content_mismatch"]
            ]
            
            if negative_feedbacks:
                main_issues = {}
                for f in negative_feedbacks:
                    if f.feedback_type not in main_issues:
                        main_issues[f.feedback_type] = 0
                    main_issues[f.feedback_type] += 1
                
                top_issue = max(main_issues.items(), key=lambda x: x[1])[0]
                recommendation = f"质量未达标，主要问题：{top_issue}，建议继续优化"
            else:
                recommendation = "质量未达标，建议继续优化"
        
        evaluation = QualityEvaluation(
            resource_id=resource_id,
            total_feedbacks=len(feedbacks),
            average_score=average_score,
            positive_rate=positive_rate,
            quality_score=quality_score,
            meets_threshold=meets_threshold,
            recommendation=recommendation
        )
        
        logger.info(
            f"Quality evaluation for resource={resource_id}: "
            f"score={quality_score:.2f}, meets_threshold={meets_threshold}"
        )
        
        return evaluation
    
    def promote_to_production(
        self,
        resource_id: int,
        quality_score: Optional[float] = None
    ) -> bool:
        """提升到正式发布
        
        Args:
            resource_id: 资源ID
            quality_score: 质量分数（可选，如果不提供则重新评估）
        
        Returns:
            是否成功提升
        """
        if resource_id not in self.gray_releases:
            logger.warning(f"Resource {resource_id} is not in gray release")
            return False
        
        config = self.gray_releases[resource_id]
        
        if config.status != ReleaseStatus.GRAY:
            logger.warning(
                f"Resource {resource_id} is not in gray status, "
                f"current status: {config.status.value}"
            )
            return False
        
        # 评估质量
        if quality_score is None:
            evaluation = self.evaluate_gray_quality(resource_id)
            quality_score = evaluation.quality_score
            
            if not evaluation.meets_threshold:
                logger.warning(
                    f"Resource {resource_id} quality score {quality_score:.2f} "
                    f"does not meet threshold {self.default_quality_threshold}"
                )
                return False
        
        # 提升到正式发布
        config.status = ReleaseStatus.PRODUCTION
        config.end_time = datetime.now()
        
        logger.info(
            f"Promoted resource {resource_id} to production, "
            f"quality_score={quality_score:.2f}"
        )
        
        return True
    
    def reject_gray_resource(
        self,
        resource_id: int,
        reason: str = ""
    ) -> bool:
        """拒绝灰度资源（不正式发布）
        
        Args:
            resource_id: 资源ID
            reason: 拒绝原因（可选）
        
        Returns:
            是否成功拒绝
        """
        if resource_id not in self.gray_releases:
            logger.warning(f"Resource {resource_id} is not in gray release")
            return False
        
        config = self.gray_releases[resource_id]
        
        if config.status != ReleaseStatus.GRAY:
            logger.warning(
                f"Resource {resource_id} is not in gray status, "
                f"current status: {config.status.value}"
            )
            return False
        
        config.status = ReleaseStatus.REJECTED
        config.end_time = datetime.now()
        
        logger.info(
            f"Rejected gray resource {resource_id}, reason: {reason or '质量未达标'}"
        )
        
        return True
    
    def get_gray_release_status(
        self,
        resource_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取灰度发布状态
        
        Args:
            resource_id: 资源ID
        
        Returns:
            灰度发布状态字典，如果不存在则返回None
        """
        if resource_id not in self.gray_releases:
            return None
        
        config = self.gray_releases[resource_id]
        feedbacks = self.gray_feedbacks.get(resource_id, [])
        
        return {
            "resource_id": resource_id,
            "status": config.status.value,
            "gray_ratio": config.gray_ratio,
            "target_user_count": config.target_user_count,
            "actual_user_count": config.actual_user_count,
            "feedback_count": len(feedbacks),
            "start_time": config.start_time.isoformat(),
            "end_time": config.end_time.isoformat() if config.end_time else None
        }
    
    def get_gray_release_statistics(
        self,
        teacher_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取灰度发布统计报告
        
        Args:
            teacher_id: 教师ID（可选）
        
        Returns:
            统计报告字典
        """
        releases = list(self.gray_releases.values())
        
        if not releases:
            return {
                "total_gray_releases": 0,
                "in_gray": 0,
                "promoted": 0,
                "rejected": 0,
                "average_quality_score": 0.0
            }
        
        in_gray = sum(1 for r in releases if r.status == ReleaseStatus.GRAY)
        promoted = sum(1 for r in releases if r.status == ReleaseStatus.PRODUCTION)
        rejected = sum(1 for r in releases if r.status == ReleaseStatus.REJECTED)
        
        # 计算平均质量分数（只统计已评估的）
        quality_scores = []
        for resource_id in self.gray_releases.keys():
            if resource_id in self.gray_feedbacks:
                evaluation = self.evaluate_gray_quality(resource_id)
                if evaluation.total_feedbacks > 0:
                    quality_scores.append(evaluation.quality_score)
        
        avg_quality = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores else 0.0
        )
        
        return {
            "total_gray_releases": len(releases),
            "in_gray": in_gray,
            "promoted": promoted,
            "rejected": rejected,
            "promotion_rate": promoted / len(releases) if releases else 0.0,
            "average_quality_score": avg_quality
        }
    
    def register_user(self, user_id: int) -> bool:
        """注册用户（用于灰度选择）
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否成功注册
        """
        self.all_user_ids.add(user_id)
        return True
    
    def unregister_user(self, user_id: int) -> bool:
        """注销用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否成功注销
        """
        if user_id in self.all_user_ids:
            self.all_user_ids.remove(user_id)
            return True
        return False
