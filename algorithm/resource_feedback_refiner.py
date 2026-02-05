"""
资源评价细化机制

基于v7.0需求，收集更详细的资源反馈信息。
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackDimension(Enum):
    """反馈维度枚举"""
    TOO_VERBOSE = "too_verbose"  # 太冗长
    TOO_SIMPLE = "too_simple"  # 太简单
    CONTENT_MISMATCH = "content_mismatch"  # 内容不匹配
    HELPFUL = "helpful"  # 有帮助


@dataclass
class RefinedFeedback:
    """细化反馈数据"""
    feedback_id: int
    user_id: int
    resource_id: int
    feedback_dimensions: Set[FeedbackDimension]  # 多维度反馈
    text_description: Optional[str] = None  # 文字说明
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeedbackAnalysis:
    """反馈分析结果"""
    resource_id: int
    total_feedbacks: int
    dimension_counts: Dict[FeedbackDimension, int]  # 各维度反馈数量
    dimension_percentages: Dict[FeedbackDimension, float]  # 各维度百分比
    overall_score: float  # 综合评分（0-1，1表示最好）
    dominant_dimension: Optional[FeedbackDimension]  # 主导维度
    needs_regeneration: bool  # 是否需要重新生成


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_type: str  # 建议类型
    description: str  # 建议描述
    priority: int  # 优先级（1-5，5最高）
    affected_dimensions: List[FeedbackDimension]  # 影响的维度


class ResourceFeedbackRefiner:
    """资源评价细化机制
    
    功能：
    1. 收集细化反馈（多维度）
    2. 分析反馈数据
    3. 生成优化建议
    4. 判断是否需要重新生成资源
    """
    
    # 重新生成阈值
    REGENERATION_THRESHOLD = 0.3  # 综合评分低于0.3时重新生成
    
    # 各维度的权重（用于计算综合评分）
    DIMENSION_WEIGHTS = {
        FeedbackDimension.HELPFUL: 1.0,  # 有帮助是正面反馈
        FeedbackDimension.TOO_VERBOSE: -0.3,  # 太冗长是负面反馈
        FeedbackDimension.TOO_SIMPLE: -0.3,  # 太简单是负面反馈
        FeedbackDimension.CONTENT_MISMATCH: -0.5  # 内容不匹配是严重负面反馈
    }
    
    def __init__(self):
        """初始化资源反馈细化器"""
        # 存储所有细化反馈
        self.refined_feedbacks: Dict[int, List[RefinedFeedback]] = {}  # key: resource_id
        
        logger.info("ResourceFeedbackRefiner initialized")
    
    def collect_refined_feedback(
        self,
        user_id: int,
        resource_id: int,
        feedback_dimensions: Set[FeedbackDimension],
        text_description: Optional[str] = None
    ) -> bool:
        """收集细化反馈
        
        Args:
            user_id: 用户ID
            resource_id: 资源ID
            feedback_dimensions: 反馈维度集合（可以多选）
            text_description: 文字说明（可选）
        
        Returns:
            是否成功收集
        """
        if not feedback_dimensions:
            logger.warning("Empty feedback dimensions provided")
            return False
        
        # 生成反馈ID（简化处理，实际应该从数据库获取）
        feedback_id = len(self.refined_feedbacks.get(resource_id, [])) + 1
        
        feedback = RefinedFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            resource_id=resource_id,
            feedback_dimensions=feedback_dimensions,
            text_description=text_description
        )
        
        if resource_id not in self.refined_feedbacks:
            self.refined_feedbacks[resource_id] = []
        
        self.refined_feedbacks[resource_id].append(feedback)
        
        logger.info(
            f"Collected refined feedback for resource={resource_id}, "
            f"user={user_id}, dimensions={[d.value for d in feedback_dimensions]}"
        )
        
        return True
    
    def analyze_feedback(self, resource_id: int) -> FeedbackAnalysis:
        """分析反馈数据
        
        Args:
            resource_id: 资源ID
        
        Returns:
            反馈分析结果
        """
        if resource_id not in self.refined_feedbacks:
            return FeedbackAnalysis(
                resource_id=resource_id,
                total_feedbacks=0,
                dimension_counts={},
                dimension_percentages={},
                overall_score=0.5,  # 无反馈时给中等分数
                dominant_dimension=None,
                needs_regeneration=False
            )
        
        feedbacks = self.refined_feedbacks[resource_id]
        total_count = len(feedbacks)
        
        if total_count == 0:
            return FeedbackAnalysis(
                resource_id=resource_id,
                total_feedbacks=0,
                dimension_counts={},
                dimension_percentages={},
                overall_score=0.5,
                dominant_dimension=None,
                needs_regeneration=False
            )
        
        # 统计各维度的反馈数量
        dimension_counts = defaultdict(int)
        for feedback in feedbacks:
            for dimension in feedback.feedback_dimensions:
                dimension_counts[dimension] += 1
        
        # 计算各维度百分比
        dimension_percentages = {
            dim: count / total_count
            for dim, count in dimension_counts.items()
        }
        
        # 计算综合评分
        overall_score = self._calculate_overall_score(
            dimension_percentages, total_count
        )
        
        # 找出主导维度（出现频率最高的）
        dominant_dimension = None
        if dimension_counts:
            dominant_dimension = max(
                dimension_counts.items(), key=lambda x: x[1]
            )[0]
        
        # 判断是否需要重新生成
        needs_regeneration = overall_score < self.REGENERATION_THRESHOLD
        
        analysis = FeedbackAnalysis(
            resource_id=resource_id,
            total_feedbacks=total_count,
            dimension_counts=dict(dimension_counts),
            dimension_percentages=dimension_percentages,
            overall_score=overall_score,
            dominant_dimension=dominant_dimension,
            needs_regeneration=needs_regeneration
        )
        
        logger.info(
            f"Feedback analysis for resource={resource_id}: "
            f"total={total_count}, score={overall_score:.2f}, "
            f"needs_regeneration={needs_regeneration}"
        )
        
        return analysis
    
    def _calculate_overall_score(
        self,
        dimension_percentages: Dict[FeedbackDimension, float],
        total_count: int
    ) -> float:
        """计算综合评分
        
        Args:
            dimension_percentages: 各维度百分比
            total_count: 总反馈数
        
        Returns:
            综合评分（0-1）
        """
        if not dimension_percentages:
            return 0.5
        
        # 使用加权平均计算评分
        score = 0.5  # 基础分数
        
        for dimension, percentage in dimension_percentages.items():
            weight = self.DIMENSION_WEIGHTS.get(dimension, 0.0)
            score += weight * percentage
        
        # 确保在[0, 1]范围内
        score = max(0.0, min(1.0, score))
        
        # 考虑反馈数量（反馈越多，评分越可靠）
        # 使用对数函数平滑处理
        import math
        confidence_factor = min(1.0, math.log(total_count + 1) / math.log(10))
        score = 0.5 + (score - 0.5) * confidence_factor
        
        return score
    
    def generate_optimization_suggestions(
        self,
        feedback_analysis: FeedbackAnalysis
    ) -> List[OptimizationSuggestion]:
        """生成优化建议
        
        Args:
            feedback_analysis: 反馈分析结果
        
        Returns:
            优化建议列表
        """
        suggestions = []
        
        if feedback_analysis.total_feedbacks == 0:
            return suggestions
        
        # 根据主导维度生成建议
        if feedback_analysis.dominant_dimension == FeedbackDimension.TOO_VERBOSE:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="simplify",
                description="简化内容，减少冗余信息，提高信息密度",
                priority=5,
                affected_dimensions=[FeedbackDimension.TOO_VERBOSE]
            ))
        
        if feedback_analysis.dominant_dimension == FeedbackDimension.TOO_SIMPLE:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="enrich",
                description="丰富内容，增加详细说明和示例，提高深度",
                priority=5,
                affected_dimensions=[FeedbackDimension.TOO_SIMPLE]
            ))
        
        if feedback_analysis.dominant_dimension == FeedbackDimension.CONTENT_MISMATCH:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="realign",
                description="重新对齐内容，确保与知识点匹配，检查内容准确性",
                priority=5,
                affected_dimensions=[FeedbackDimension.CONTENT_MISMATCH]
            ))
        
        # 如果多个负面维度同时出现
        negative_dimensions = [
            FeedbackDimension.TOO_VERBOSE,
            FeedbackDimension.TOO_SIMPLE,
            FeedbackDimension.CONTENT_MISMATCH
        ]
        
        negative_count = sum(
            feedback_analysis.dimension_counts.get(dim, 0)
            for dim in negative_dimensions
        )
        
        if negative_count > feedback_analysis.total_feedbacks * 0.5:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="comprehensive_review",
                description="进行全面的资源审查和重构，考虑重新生成",
                priority=4,
                affected_dimensions=negative_dimensions
            ))
        
        # 如果正面反馈较少
        helpful_count = feedback_analysis.dimension_counts.get(
            FeedbackDimension.HELPFUL, 0
        )
        if helpful_count < feedback_analysis.total_feedbacks * 0.3:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="improve_quality",
                description="提高资源质量，增加实用性和相关性",
                priority=3,
                affected_dimensions=[FeedbackDimension.HELPFUL]
            ))
        
        # 按优先级排序
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(
            f"Generated {len(suggestions)} optimization suggestions "
            f"for resource={feedback_analysis.resource_id}"
        )
        
        return suggestions
    
    def should_regenerate_resource(
        self,
        resource_id: int,
        feedback_score: Optional[float] = None
    ) -> bool:
        """判断是否需要重新生成资源
        
        Args:
            resource_id: 资源ID
            feedback_score: 反馈评分（可选，如果不提供则从分析中获取）
        
        Returns:
            是否需要重新生成
        """
        if feedback_score is None:
            analysis = self.analyze_feedback(resource_id)
            feedback_score = analysis.overall_score
        
        should_regenerate = feedback_score < self.REGENERATION_THRESHOLD
        
        logger.info(
            f"Regeneration decision for resource={resource_id}: "
            f"score={feedback_score:.2f}, regenerate={should_regenerate}"
        )
        
        return should_regenerate
    
    def get_feedback_statistics(
        self,
        resource_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取反馈统计报告
        
        Args:
            resource_id: 资源ID（可选，如果提供则只统计该资源）
        
        Returns:
            统计报告字典
        """
        if resource_id is not None:
            if resource_id not in self.refined_feedbacks:
                return {
                    "resource_id": resource_id,
                    "total_feedbacks": 0,
                    "dimension_counts": {},
                    "overall_score": 0.5
                }
            
            analysis = self.analyze_feedback(resource_id)
            
            return {
                "resource_id": resource_id,
                "total_feedbacks": analysis.total_feedbacks,
                "dimension_counts": {
                    dim.value: count
                    for dim, count in analysis.dimension_counts.items()
                },
                "dimension_percentages": {
                    dim.value: pct
                    for dim, pct in analysis.dimension_percentages.items()
                },
                "overall_score": analysis.overall_score,
                "needs_regeneration": analysis.needs_regeneration
            }
        
        # 统计所有资源
        total_resources = len(self.refined_feedbacks)
        total_feedbacks = sum(
            len(feedbacks) for feedbacks in self.refined_feedbacks.values()
        )
        
        # 统计各维度的总出现次数
        all_dimension_counts = defaultdict(int)
        for feedbacks in self.refined_feedbacks.values():
            for feedback in feedbacks:
                for dimension in feedback.feedback_dimensions:
                    all_dimension_counts[dimension] += 1
        
        return {
            "total_resources": total_resources,
            "total_feedbacks": total_feedbacks,
            "average_feedbacks_per_resource": (
                total_feedbacks / total_resources if total_resources > 0 else 0
            ),
            "dimension_counts": {
                dim.value: count
                for dim, count in all_dimension_counts.items()
            }
        }
    
    def get_feedback_trend(
        self,
        resource_id: int,
        time_window_days: int = 7
    ) -> Dict[str, Any]:
        """获取反馈趋势分析
        
        Args:
            resource_id: 资源ID
            time_window_days: 时间窗口（天）
        
        Returns:
            趋势分析字典
        """
        if resource_id not in self.refined_feedbacks:
            return {
                "resource_id": resource_id,
                "trend": "stable",
                "recent_score": 0.5,
                "historical_score": 0.5
            }
        
        feedbacks = self.refined_feedbacks[resource_id]
        
        if len(feedbacks) < 2:
            return {
                "resource_id": resource_id,
                "trend": "insufficient_data",
                "recent_score": 0.5,
                "historical_score": 0.5
            }
        
        # 按时间排序
        sorted_feedbacks = sorted(feedbacks, key=lambda x: x.created_at)
        
        # 分为早期和近期
        mid_point = len(sorted_feedbacks) // 2
        early_feedbacks = sorted_feedbacks[:mid_point]
        recent_feedbacks = sorted_feedbacks[mid_point:]
        
        # 计算早期和近期的评分
        early_analysis = self._analyze_feedback_subset(early_feedbacks)
        recent_analysis = self._analyze_feedback_subset(recent_feedbacks)
        
        # 判断趋势
        if recent_analysis["overall_score"] > early_analysis["overall_score"] + 0.1:
            trend = "improving"
        elif recent_analysis["overall_score"] < early_analysis["overall_score"] - 0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "resource_id": resource_id,
            "trend": trend,
            "recent_score": recent_analysis["overall_score"],
            "historical_score": early_analysis["overall_score"],
            "score_change": recent_analysis["overall_score"] - early_analysis["overall_score"]
        }
    
    def _analyze_feedback_subset(
        self,
        feedbacks: List[RefinedFeedback]
    ) -> Dict[str, Any]:
        """分析反馈子集（辅助方法）
        
        Args:
            feedbacks: 反馈列表
        
        Returns:
            分析结果字典
        """
        if not feedbacks:
            return {"overall_score": 0.5}
        
        dimension_counts = defaultdict(int)
        for feedback in feedbacks:
            for dimension in feedback.feedback_dimensions:
                dimension_counts[dimension] += 1
        
        dimension_percentages = {
            dim: count / len(feedbacks)
            for dim, count in dimension_counts.items()
        }
        
        overall_score = self._calculate_overall_score(
            dimension_percentages, len(feedbacks)
        )
        
        return {
            "overall_score": overall_score,
            "dimension_counts": dict(dimension_counts)
        }
