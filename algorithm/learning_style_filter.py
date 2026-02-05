"""
学习风格自适应过滤器算法

基于v8.0需求，根据学生学习风格过滤和匹配补偿资源。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    """学习风格枚举"""
    VISUAL = "visual"  # 视觉型
    AUDITORY = "auditory"  # 听觉型
    TEXTUAL = "textual"  # 文本型
    KINESTHETIC = "kinesthetic"  # 动觉型
    MIXED = "mixed"  # 混合型


class ResourceType(Enum):
    """资源类型枚举"""
    VIDEO = "video"  # 视频
    AUDIO = "audio"  # 音频
    TEXT = "text"  # 文本
    IMAGE = "image"  # 图片
    INTERACTIVE = "interactive"  # 交互式


@dataclass
class Resource:
    """补偿资源"""
    resource_id: int
    resource_type: ResourceType
    learning_styles: List[LearningStyle]  # 支持的学习风格列表
    title: str
    description: str
    base_match_score: float = 0.5  # 基础匹配分数


@dataclass
class FeedbackRecord:
    """反馈记录"""
    user_id: int
    resource_id: int
    resource_type: ResourceType
    feedback_score: float  # 反馈分数（0-1）
    learning_effectiveness: float  # 学习效果（0-1）
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LearningStyleProfile:
    """学习风格画像"""
    user_id: int
    primary_style: LearningStyle  # 主要学习风格
    style_scores: Dict[LearningStyle, float]  # 各风格分数（0-1）
    confidence: float  # 置信度（0-1）
    inferred_at: datetime = field(default_factory=datetime.now)


@dataclass
class StyleMatchResult:
    """风格匹配结果"""
    resource_id: int
    base_match_score: float
    style_match_score: float  # 风格匹配分数
    adjusted_match_score: float  # 调整后的匹配分数
    match_improvement: float  # 匹配度提升（≥20%）
    matched_styles: List[LearningStyle]  # 匹配的风格列表


class LearningStyleFilter:
    """学习风格自适应过滤器
    
    功能：
    1. 学习风格推断：基于学生反馈数据推断学习风格
    2. 资源标签：为每个补偿资源标注学习风格标签
    3. 风格匹配：优先推送匹配学生风格的资源
    4. 匹配度提升：风格匹配后，资源匹配度提升≥20%
    """
    
    # 匹配度提升阈值
    MIN_MATCH_IMPROVEMENT = 0.2  # 最小匹配度提升（20%）
    
    # 风格推断最小样本数
    MIN_FEEDBACK_SAMPLES = 5
    
    def __init__(self):
        """初始化学习风格过滤器"""
        # 存储学习风格画像
        self.learning_styles: Dict[int, LearningStyleProfile] = {}  # key: user_id
        
        # 存储反馈历史
        self.feedback_history: Dict[int, List[FeedbackRecord]] = {}  # key: user_id
        
        # 资源类型到学习风格的映射
        self.resource_type_to_styles = {
            ResourceType.VIDEO: [LearningStyle.VISUAL, LearningStyle.AUDITORY],
            ResourceType.AUDIO: [LearningStyle.AUDITORY],
            ResourceType.TEXT: [LearningStyle.TEXTUAL],
            ResourceType.IMAGE: [LearningStyle.VISUAL],
            ResourceType.INTERACTIVE: [LearningStyle.KINESTHETIC, LearningStyle.VISUAL]
        }
        
        logger.info("LearningStyleFilter initialized")
    
    def infer_learning_style(
        self,
        user_id: int,
        feedback_history: Optional[List[FeedbackRecord]] = None
    ) -> LearningStyleProfile:
        """推断学习风格
        
        Args:
            user_id: 用户ID
            feedback_history: 反馈历史（可选，如果不提供则使用存储的历史）
        
        Returns:
            学习风格画像
        """
        if feedback_history is None:
            feedback_history = self.feedback_history.get(user_id, [])
        
        if len(feedback_history) < self.MIN_FEEDBACK_SAMPLES:
            # 样本不足，返回默认混合型
            return LearningStyleProfile(
                user_id=user_id,
                primary_style=LearningStyle.MIXED,
                style_scores={LearningStyle.MIXED: 1.0},
                confidence=0.3
            )
        
        # 统计各资源类型的学习效果
        type_effectiveness = defaultdict(list)
        for feedback in feedback_history:
            type_effectiveness[feedback.resource_type].append(
                feedback.learning_effectiveness
            )
        
        # 计算各资源类型的平均效果
        type_avg_effectiveness = {}
        for resource_type, effectiveness_list in type_effectiveness.items():
            if effectiveness_list:
                type_avg_effectiveness[resource_type] = sum(effectiveness_list) / len(effectiveness_list)
        
        # 根据资源类型效果推断学习风格
        style_scores = defaultdict(float)
        
        for resource_type, avg_effectiveness in type_avg_effectiveness.items():
            # 获取该资源类型对应的学习风格
            associated_styles = self.resource_type_to_styles.get(resource_type, [])
            
            # 根据效果分配分数
            for style in associated_styles:
                style_scores[style] += avg_effectiveness
        
        # 归一化分数
        total_score = sum(style_scores.values())
        if total_score > 0:
            style_scores = {
                style: score / total_score
                for style, score in style_scores.items()
            }
        else:
            # 如果没有数据，使用均匀分布
            style_scores = {LearningStyle.MIXED: 1.0}
        
        # 找出主要学习风格
        if style_scores:
            primary_style = max(style_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_style = LearningStyle.MIXED
        
        # 计算置信度（基于样本数量和分数差异）
        sample_count = len(feedback_history)
        max_score = max(style_scores.values()) if style_scores else 0.0
        second_max_score = sorted(style_scores.values(), reverse=True)[1] if len(style_scores) > 1 else 0.0
        
        # 置信度 = 样本数量因子 * 分数差异因子
        sample_factor = min(1.0, sample_count / 20.0)
        score_diff_factor = min(1.0, (max_score - second_max_score) * 2.0)
        confidence = (sample_factor + score_diff_factor) / 2.0
        
        profile = LearningStyleProfile(
            user_id=user_id,
            primary_style=primary_style,
            style_scores=dict(style_scores),
            confidence=confidence
        )
        
        # 存储画像
        self.learning_styles[user_id] = profile
        
        logger.info(
            f"Inferred learning style for user={user_id}: "
            f"primary={primary_style.value}, confidence={confidence:.2f}"
        )
        
        return profile
    
    def filter_by_style(
        self,
        resources: List[Resource],
        learning_style: LearningStyle
    ) -> List[Resource]:
        """根据学习风格过滤资源
        
        Args:
            resources: 资源列表
            learning_style: 学习风格
        
        Returns:
            过滤后的资源列表（包含匹配风格标签的资源）
        """
        filtered = []
        
        for resource in resources:
            # 检查资源是否支持该学习风格
            if learning_style in resource.learning_styles:
                filtered.append(resource)
        
        logger.info(
            f"Filtered resources by style {learning_style.value}: "
            f"{len(resources)} -> {len(filtered)}"
        )
        
        return filtered
    
    def calculate_style_match_score(
        self,
        resource: Resource,
        learning_style: LearningStyle
    ) -> float:
        """计算风格匹配分数
        
        Args:
            resource: 资源
            learning_style: 学习风格
        
        Returns:
            风格匹配分数（0-1）
        """
        if learning_style in resource.learning_styles:
            # 完全匹配
            return 1.0
        elif LearningStyle.MIXED in resource.learning_styles:
            # 混合型资源，部分匹配
            return 0.6
        else:
            # 不匹配
            return 0.0
    
    def rank_resources_by_match(
        self,
        resources: List[Resource],
        learning_style: LearningStyle
    ) -> List[StyleMatchResult]:
        """按风格匹配度排序资源
        
        Args:
            resources: 资源列表
            learning_style: 学习风格
        
        Returns:
            排序后的匹配结果列表
        """
        results = []
        
        for resource in resources:
            # 计算风格匹配分数
            style_match_score = self.calculate_style_match_score(resource, learning_style)
            
            # 计算调整后的匹配分数
            # 如果风格匹配，提升匹配度≥20%
            if style_match_score > 0:
                match_improvement = max(
                    self.MIN_MATCH_IMPROVEMENT,
                    style_match_score * 0.3  # 最多提升30%
                )
                adjusted_match_score = min(
                    1.0,
                    resource.base_match_score + match_improvement
                )
            else:
                match_improvement = 0.0
                adjusted_match_score = resource.base_match_score
            
            # 找出匹配的风格
            matched_styles = [
                style for style in resource.learning_styles
                if style == learning_style or style == LearningStyle.MIXED
            ]
            
            result = StyleMatchResult(
                resource_id=resource.resource_id,
                base_match_score=resource.base_match_score,
                style_match_score=style_match_score,
                adjusted_match_score=adjusted_match_score,
                match_improvement=match_improvement,
                matched_styles=matched_styles
            )
            
            results.append(result)
        
        # 按调整后的匹配分数排序
        results.sort(key=lambda x: x.adjusted_match_score, reverse=True)
        
        logger.info(
            f"Ranked {len(results)} resources by style match "
            f"(style={learning_style.value})"
        )
        
        return results
    
    def add_feedback(
        self,
        user_id: int,
        resource_id: int,
        resource_type: ResourceType,
        feedback_score: float,
        learning_effectiveness: float
    ) -> bool:
        """添加反馈记录
        
        Args:
            user_id: 用户ID
            resource_id: 资源ID
            resource_type: 资源类型
            feedback_score: 反馈分数
            learning_effectiveness: 学习效果
        
        Returns:
            是否成功添加
        """
        feedback = FeedbackRecord(
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            feedback_score=feedback_score,
            learning_effectiveness=learning_effectiveness
        )
        
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        
        self.feedback_history[user_id].append(feedback)
        
        # 只保留最近100条记录
        if len(self.feedback_history[user_id]) > 100:
            self.feedback_history[user_id] = self.feedback_history[user_id][-100:]
        
        # 重新推断学习风格（如果样本足够）
        if len(self.feedback_history[user_id]) >= self.MIN_FEEDBACK_SAMPLES:
            self.infer_learning_style(user_id)
        
        logger.debug(
            f"Added feedback for user={user_id}, resource={resource_id}, "
            f"effectiveness={learning_effectiveness:.2f}"
        )
        
        return True
    
    def get_learning_style(
        self,
        user_id: int
    ) -> Optional[LearningStyleProfile]:
        """获取学习风格画像
        
        Args:
            user_id: 用户ID
        
        Returns:
            学习风格画像，如果不存在则返回None
        """
        if user_id in self.learning_styles:
            return self.learning_styles[user_id]
        
        # 如果不存在，尝试推断
        if user_id in self.feedback_history:
            return self.infer_learning_style(user_id)
        
        return None
    
    def get_style_match_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取风格匹配统计
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        if user_id is not None:
            profile = self.get_learning_style(user_id)
            if profile is None:
                return {
                    "user_id": user_id,
                    "has_profile": False,
                    "primary_style": None
                }
            
            return {
                "user_id": user_id,
                "has_profile": True,
                "primary_style": profile.primary_style.value,
                "confidence": profile.confidence,
                "style_scores": {
                    style.value: score
                    for style, score in profile.style_scores.items()
                }
            }
        
        # 统计所有用户
        total_users = len(self.learning_styles)
        
        if total_users == 0:
            return {
                "total_users": 0,
                "style_distribution": {}
            }
        
        # 统计风格分布
        style_distribution = defaultdict(int)
        for profile in self.learning_styles.values():
            style_distribution[profile.primary_style.value] += 1
        
        return {
            "total_users": total_users,
            "style_distribution": dict(style_distribution),
            "average_confidence": sum(
                p.confidence for p in self.learning_styles.values()
            ) / total_users
        }
