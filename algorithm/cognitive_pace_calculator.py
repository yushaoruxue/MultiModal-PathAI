"""
个人认知步频计算算法

基于v7.0需求，动态计算每个学生的学习速度。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LearningRecord:
    """学习记录"""
    knowledge_point_id: int
    start_time: datetime
    end_time: datetime
    mastery_time: Optional[datetime] = None  # 掌握时间
    exercise_score: float = 0.0  # 练习正确率（0-1）
    mastery_quality: float = 0.0  # 掌握质量（0-1），基于练习正确率和学习时长


@dataclass
class KnowledgePointDifficulty:
    """知识点难度信息"""
    knowledge_point_id: int
    difficulty: str  # easy/medium/hard
    estimated_duration: float  # 预计学习时长（分钟）


@dataclass
class PaceResult:
    """认知步频计算结果"""
    pace: float  # 认知步频（知识点/小时）
    total_knowledge_points: int  # 总知识点数
    total_time_hours: float  # 总学习时长（小时）
    average_mastery_time: float  # 平均掌握时间（分钟）
    mastery_quality: float  # 平均掌握质量（0-1）
    trend: str  # 趋势：increasing/stable/decreasing


@dataclass
class DynamicThresholdResult:
    """动态阈值调整结果"""
    base_threshold: float
    adjusted_threshold: float
    adjustment_factor: float  # 调整系数
    pace: float
    reason: str


class CognitivePaceCalculator:
    """个人认知步频计算器
    
    功能：
    1. 计算个人认知步频（单位时间内掌握的知识点数量）
    2. 基于个人历史数据，动态调整难点判定阈值
    3. 在难点判定时，考虑个人认知步频
    4. 检测虚假繁荣（快速学习但深度理解不足）
    """
    
    def __init__(
        self,
        default_time_window_days: int = 7,
        min_learning_records: int = 3,
        false_prosperity_threshold: float = 0.7  # 掌握质量阈值
    ):
        """初始化认知步频计算器
        
        Args:
            default_time_window_days: 默认时间窗口（天，默认7天）
            min_learning_records: 最少学习记录数（默认3条）
            false_prosperity_threshold: 虚假繁荣检测阈值（掌握质量低于此值视为虚假繁荣）
        """
        self.default_time_window = timedelta(days=default_time_window_days)
        self.min_learning_records = min_learning_records
        self.false_prosperity_threshold = false_prosperity_threshold
        
        # 存储用户的学习记录（用于缓存和趋势分析）
        self.user_learning_records: Dict[int, deque] = {}
        
        logger.info(
            f"CognitivePaceCalculator initialized with "
            f"time_window={default_time_window_days} days, "
            f"min_records={min_learning_records}"
        )
    
    def calculate_pace(
        self,
        user_id: int,
        learning_records: List[LearningRecord],
        time_window: Optional[timedelta] = None
    ) -> PaceResult:
        """计算个人认知步频
        
        Args:
            user_id: 用户ID
            learning_records: 学习记录列表
            time_window: 时间窗口（可选，默认使用初始化时的窗口）
        
        Returns:
            认知步频计算结果
        """
        if time_window is None:
            time_window = self.default_time_window
        
        # 过滤时间窗口内的记录
        now = datetime.now()
        window_start = now - time_window
        
        filtered_records = [
            record for record in learning_records
            if record.start_time >= window_start and record.mastery_time is not None
        ]
        
        if len(filtered_records) < self.min_learning_records:
            logger.warning(
                f"Insufficient learning records for user={user_id}: "
                f"{len(filtered_records)} < {self.min_learning_records}"
            )
            # 返回默认值
            return PaceResult(
                pace=0.0,
                total_knowledge_points=0,
                total_time_hours=0.0,
                average_mastery_time=0.0,
                mastery_quality=0.0,
                trend="stable"
            )
        
        # 计算总学习时长（从第一个记录开始到最后一个记录结束）
        if filtered_records:
            first_start = min(r.start_time for r in filtered_records)
            last_end = max(r.end_time for r in filtered_records)
            total_time = (last_end - first_start).total_seconds() / 3600.0  # 转换为小时
        else:
            total_time = 0.0
        
        # 计算平均掌握时间
        mastery_times = [
            (r.mastery_time - r.start_time).total_seconds() / 60.0  # 转换为分钟
            for r in filtered_records
            if r.mastery_time is not None
        ]
        average_mastery_time = sum(mastery_times) / len(mastery_times) if mastery_times else 0.0
        
        # 计算平均掌握质量
        mastery_qualities = [r.mastery_quality for r in filtered_records if r.mastery_quality > 0]
        average_mastery_quality = (
            sum(mastery_qualities) / len(mastery_qualities)
            if mastery_qualities else 0.0
        )
        
        # 计算认知步频（知识点/小时）
        # 使用实际学习时长，而不是时间窗口
        if total_time > 0:
            pace = len(filtered_records) / total_time
        else:
            pace = 0.0
        
        # 分析趋势（与历史数据对比）
        trend = self._analyze_trend(user_id, pace, filtered_records)
        
        # 更新用户记录缓存
        if user_id not in self.user_learning_records:
            self.user_learning_records[user_id] = deque(maxlen=100)  # 最多保存100条记录
        
        for record in filtered_records:
            self.user_learning_records[user_id].append(record)
        
        result = PaceResult(
            pace=pace,
            total_knowledge_points=len(filtered_records),
            total_time_hours=total_time,
            average_mastery_time=average_mastery_time,
            mastery_quality=average_mastery_quality,
            trend=trend
        )
        
        logger.info(
            f"Calculated pace for user={user_id}: {pace:.2f} kp/hour, "
            f"quality={average_mastery_quality:.2f}, trend={trend}"
        )
        
        return result
    
    def _analyze_trend(
        self,
        user_id: int,
        current_pace: float,
        current_records: List[LearningRecord]
    ) -> str:
        """分析步频趋势
        
        Args:
            user_id: 用户ID
            current_pace: 当前步频
            current_records: 当前记录列表
        
        Returns:
            趋势：increasing/stable/decreasing
        """
        if user_id not in self.user_learning_records:
            return "stable"
        
        historical_records = list(self.user_learning_records[user_id])
        
        if len(historical_records) < self.min_learning_records:
            return "stable"
        
        # 计算历史步频（使用更早的时间窗口）
        # 这里简化处理，使用历史记录的前半部分
        mid_point = len(historical_records) // 2
        if mid_point < self.min_learning_records:
            return "stable"
        
        historical_records_early = historical_records[:mid_point]
        historical_records_late = historical_records[mid_point:]
        
        # 计算早期和晚期的平均掌握时间
        early_times = [
            (r.mastery_time - r.start_time).total_seconds() / 3600.0
            for r in historical_records_early
            if r.mastery_time is not None
        ]
        late_times = [
            (r.mastery_time - r.start_time).total_seconds() / 3600.0
            for r in historical_records_late
            if r.mastery_time is not None
        ]
        
        if not early_times or not late_times:
            return "stable"
        
        early_avg_time = sum(early_times) / len(early_times)
        late_avg_time = sum(late_times) / len(late_times)
        
        # 如果平均时间减少，说明步频增加
        if late_avg_time < early_avg_time * 0.9:  # 减少超过10%
            return "increasing"
        elif late_avg_time > early_avg_time * 1.1:  # 增加超过10%
            return "decreasing"
        else:
            return "stable"
    
    def calculate_dynamic_threshold(
        self,
        user_id: int,
        base_threshold: float,
        learning_records: List[LearningRecord],
        time_window: Optional[timedelta] = None
    ) -> DynamicThresholdResult:
        """计算动态阈值调整
        
        Args:
            user_id: 用户ID
            base_threshold: 基础阈值
            learning_records: 学习记录列表
            time_window: 时间窗口（可选）
        
        Returns:
            动态阈值调整结果
        """
        # 计算当前步频
        pace_result = self.calculate_pace(user_id, learning_records, time_window)
        
        if pace_result.pace == 0.0:
            # 没有足够数据，使用基础阈值
            return DynamicThresholdResult(
                base_threshold=base_threshold,
                adjusted_threshold=base_threshold,
                adjustment_factor=1.0,
                pace=0.0,
                reason="数据不足，使用基础阈值"
            )
        
        # 根据步频调整阈值
        # 步频越高，阈值应该相应提高（因为学习速度快，可能理解不够深入）
        # 步频越低，阈值可以适当降低（因为学习慢，可能确实遇到困难）
        
        # 参考步频：假设正常步频为2知识点/小时
        reference_pace = 2.0
        
        # 计算调整系数
        if pace_result.pace > reference_pace * 1.5:
            # 步频很高，提高阈值（更严格）
            adjustment_factor = 1.2
            reason = f"步频较高({pace_result.pace:.2f} kp/h)，提高阈值以避免误判"
        elif pace_result.pace < reference_pace * 0.5:
            # 步频很低，降低阈值（更宽松）
            adjustment_factor = 0.8
            reason = f"步频较低({pace_result.pace:.2f} kp/h)，降低阈值以识别困难"
        else:
            # 步频正常，不调整
            adjustment_factor = 1.0
            reason = f"步频正常({pace_result.pace:.2f} kp/h)，使用基础阈值"
        
        # 考虑掌握质量
        if pace_result.mastery_quality < self.false_prosperity_threshold:
            # 掌握质量低，可能是虚假繁荣，进一步提高阈值
            adjustment_factor *= 1.1
            reason += f"，掌握质量较低({pace_result.mastery_quality:.2f})，进一步调整"
        
        adjusted_threshold = base_threshold * adjustment_factor
        
        result = DynamicThresholdResult(
            base_threshold=base_threshold,
            adjusted_threshold=adjusted_threshold,
            adjustment_factor=adjustment_factor,
            pace=pace_result.pace,
            reason=reason
        )
        
        logger.info(
            f"Dynamic threshold for user={user_id}: "
            f"{base_threshold:.2f} -> {adjusted_threshold:.2f} "
            f"(factor={adjustment_factor:.2f})"
        )
        
        return result
    
    def apply_pace_weight(
        self,
        difficulty_score: float,
        pace: float,
        reference_pace: float = 2.0
    ) -> float:
        """应用步频加权到难点分数
        
        Args:
            difficulty_score: 原始困难度分数
            pace: 个人认知步频
            reference_pace: 参考步频（默认2.0知识点/小时）
        
        Returns:
            加权后的困难度分数
        """
        if pace <= 0:
            return difficulty_score
        
        # 如果步频高于参考值，加权降低分数（因为学习快，可能不是真的困难）
        # 如果步频低于参考值，加权提高分数（因为学习慢，可能确实困难）
        
        pace_ratio = pace / reference_pace
        
        if pace_ratio > 1.5:
            # 步频很高，降低分数权重
            weight = 0.8
        elif pace_ratio < 0.5:
            # 步频很低，提高分数权重
            weight = 1.2
        else:
            # 步频正常，不调整
            weight = 1.0
        
        weighted_score = difficulty_score * weight
        
        logger.debug(
            f"Applied pace weight: score={difficulty_score:.2f}, "
            f"pace={pace:.2f}, weight={weight:.2f}, "
            f"weighted_score={weighted_score:.2f}"
        )
        
        return weighted_score
    
    def detect_false_prosperity(
        self,
        pace: float,
        mastery_quality: float,
        average_mastery_time: float,
        reference_mastery_time: float = 30.0  # 参考掌握时间（分钟）
    ) -> Tuple[bool, str]:
        """检测虚假繁荣
        
        虚假繁荣：快速学习但深度理解不足
        
        Args:
            pace: 认知步频
            mastery_quality: 掌握质量
            average_mastery_time: 平均掌握时间（分钟）
            reference_mastery_time: 参考掌握时间（分钟）
        
        Returns:
            (是否虚假繁荣, 原因说明)
        """
        # 检测条件：
        # 1. 步频很高（>3知识点/小时）
        # 2. 但掌握质量低（<0.7）
        # 3. 或掌握时间过短（<参考时间的50%）
        
        is_false = False
        reasons = []
        
        if pace > 3.0:
            reasons.append(f"步频过高({pace:.2f} kp/h)")
        
        if mastery_quality < self.false_prosperity_threshold:
            reasons.append(f"掌握质量低({mastery_quality:.2f})")
            is_false = True
        
        if average_mastery_time < reference_mastery_time * 0.5:
            reasons.append(f"掌握时间过短({average_mastery_time:.1f}分钟)")
            is_false = True
        
        # 如果步频高且（掌握质量低或时间短），判定为虚假繁荣
        if pace > 3.0 and (mastery_quality < self.false_prosperity_threshold or 
                          average_mastery_time < reference_mastery_time * 0.5):
            is_false = True
        
        reason_str = "；".join(reasons) if reasons else "正常"
        
        if is_false:
            logger.warning(f"Detected false prosperity: {reason_str}")
        
        return is_false, reason_str
    
    def get_pace_statistics(
        self,
        user_id: int,
        learning_records: List[LearningRecord],
        time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """获取步频统计信息
        
        Args:
            user_id: 用户ID
            learning_records: 学习记录列表
            time_window: 时间窗口（可选）
        
        Returns:
            统计信息字典
        """
        pace_result = self.calculate_pace(user_id, learning_records, time_window)
        
        # 检测虚假繁荣
        is_false, false_reason = self.detect_false_prosperity(
            pace_result.pace,
            pace_result.mastery_quality,
            pace_result.average_mastery_time
        )
        
        stats = {
            "user_id": user_id,
            "pace": pace_result.pace,
            "total_knowledge_points": pace_result.total_knowledge_points,
            "total_time_hours": pace_result.total_time_hours,
            "average_mastery_time_minutes": pace_result.average_mastery_time,
            "mastery_quality": pace_result.mastery_quality,
            "trend": pace_result.trend,
            "is_false_prosperity": is_false,
            "false_prosperity_reason": false_reason
        }
        
        return stats
