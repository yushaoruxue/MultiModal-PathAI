"""
认知步频难度系数加权算法

基于v8.0需求，避免"虚假繁荣"误报。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DifficultyCoefficient:
    """难度系数"""
    knowledge_point_id: int
    coefficient: float  # 难度系数（>0，越大越难）
    global_avg_duration: float  # 全网平均学习时长（分钟）
    calculated_at: datetime = field(default_factory=datetime.now)
    sample_size: int = 0  # 样本数量


@dataclass
class WeightedPaceResult:
    """加权步频结果"""
    original_pace: float  # 原始认知步频
    difficulty_coefficient: float  # 难度系数
    weighted_pace: float  # 加权后的认知步频
    adjustment_factor: float  # 调整系数


@dataclass
class FalseProsperityCheck:
    """虚假繁荣检查结果"""
    is_false_prosperity: bool  # 是否为虚假繁荣
    difficulty_score: float  # 困难度分数
    weighted_pace: float  # 加权步频
    reason: str  # 原因说明
    recommendation: str  # 建议


class DifficultyCoefficientWeighted:
    """认知步频难度系数加权算法
    
    功能：
    1. 难度系数计算：基于全网平均学习时长计算知识点难度系数
    2. 步频加权：在计算认知步频时，考虑知识点难度系数
    3. 避免误报：快速学习高难知识点时，不误判为"已掌握"
    4. 加权公式：adjusted_pace = pace × (1 / difficulty_coefficient)
    """
    
    # 参考学习时长（分钟），用于归一化难度系数
    REFERENCE_DURATION = 30.0
    
    # 虚假繁荣判定阈值
    FALSE_PROSPERITY_PACE_THRESHOLD = 3.0  # 步频阈值（知识点/小时）
    FALSE_PROSPERITY_DIFFICULTY_THRESHOLD = 0.3  # 困难度分数阈值
    
    def __init__(self):
        """初始化难度系数加权器"""
        # 存储难度系数
        self.difficulty_coefficients: Dict[int, DifficultyCoefficient] = {}
        
        # 存储难度系数历史
        self.coefficient_history: Dict[int, List[float]] = {}  # key: kp_id
        
        logger.info("DifficultyCoefficientWeighted initialized")
    
    def calculate_difficulty_coefficient(
        self,
        knowledge_point_id: int,
        global_avg_duration: float,
        sample_size: int = 0
    ) -> float:
        """计算难度系数
        
        难度系数 = global_avg_duration / REFERENCE_DURATION
        
        说明：
        - 如果平均时长为60分钟，难度系数 = 60/30 = 2.0（较难）
        - 如果平均时长为15分钟，难度系数 = 15/30 = 0.5（较易）
        - 如果平均时长为30分钟，难度系数 = 30/30 = 1.0（中等）
        
        Args:
            knowledge_point_id: 知识点ID
            global_avg_duration: 全网平均学习时长（分钟）
            sample_size: 样本数量（可选）
        
        Returns:
            难度系数（>0）
        """
        if global_avg_duration <= 0:
            logger.warning(
                f"Invalid global_avg_duration {global_avg_duration}, using default 1.0"
            )
            coefficient = 1.0
        else:
            coefficient = global_avg_duration / self.REFERENCE_DURATION
        
        # 确保系数在合理范围内（0.1-10.0）
        coefficient = max(0.1, min(10.0, coefficient))
        
        # 存储难度系数
        diff_coeff = DifficultyCoefficient(
            knowledge_point_id=knowledge_point_id,
            coefficient=coefficient,
            global_avg_duration=global_avg_duration,
            sample_size=sample_size
        )
        
        self.difficulty_coefficients[knowledge_point_id] = diff_coeff
        
        # 记录历史
        if knowledge_point_id not in self.coefficient_history:
            self.coefficient_history[knowledge_point_id] = []
        
        self.coefficient_history[knowledge_point_id].append(coefficient)
        
        # 只保留最近100次记录
        if len(self.coefficient_history[knowledge_point_id]) > 100:
            self.coefficient_history[knowledge_point_id] = \
                self.coefficient_history[knowledge_point_id][-100:]
        
        logger.debug(
            f"Calculated difficulty coefficient for kp={knowledge_point_id}: "
            f"{coefficient:.2f} (avg_duration={global_avg_duration:.1f} min)"
        )
        
        return coefficient
    
    def get_difficulty_coefficient(self, knowledge_point_id: int) -> float:
        """获取难度系数
        
        Args:
            knowledge_point_id: 知识点ID
        
        Returns:
            难度系数，如果不存在则返回默认值1.0
        """
        if knowledge_point_id in self.difficulty_coefficients:
            return self.difficulty_coefficients[knowledge_point_id].coefficient
        
        return 1.0  # 默认中等难度
    
    def apply_difficulty_weight(
        self,
        pace: float,
        difficulty_coefficient: float
    ) -> WeightedPaceResult:
        """应用难度权重到认知步频
        
        加权公式：adjusted_pace = pace × (1 / difficulty_coefficient)
        
        说明：
        - 如果难度系数=2.0（较难），调整系数=0.5，步频降低
        - 如果难度系数=0.5（较易），调整系数=2.0，步频提高
        - 如果难度系数=1.0（中等），调整系数=1.0，步频不变
        
        Args:
            pace: 原始认知步频（知识点/小时）
            difficulty_coefficient: 难度系数
        
        Returns:
            加权步频结果
        """
        if difficulty_coefficient <= 0:
            logger.warning(
                f"Invalid difficulty coefficient {difficulty_coefficient}, using 1.0"
            )
            difficulty_coefficient = 1.0
        
        adjustment_factor = 1.0 / difficulty_coefficient
        weighted_pace = pace * adjustment_factor
        
        result = WeightedPaceResult(
            original_pace=pace,
            difficulty_coefficient=difficulty_coefficient,
            weighted_pace=weighted_pace,
            adjustment_factor=adjustment_factor
        )
        
        logger.debug(
            f"Applied difficulty weight: pace={pace:.2f}, "
            f"coefficient={difficulty_coefficient:.2f}, "
            f"weighted_pace={weighted_pace:.2f}"
        )
        
        return result
    
    def adjust_difficulty_threshold(
        self,
        base_threshold: float,
        weighted_pace: float,
        reference_pace: float = 2.0
    ) -> float:
        """调整难点判定阈值
        
        根据加权步频调整阈值：
        - 如果加权步频很高，提高阈值（更严格）
        - 如果加权步频很低，降低阈值（更宽松）
        
        Args:
            base_threshold: 基础阈值
            weighted_pace: 加权后的认知步频
            reference_pace: 参考步频（默认2.0知识点/小时）
        
        Returns:
            调整后的阈值
        """
        if weighted_pace > reference_pace * 1.5:
            # 步频很高，提高阈值（更严格，避免误判）
            adjustment_factor = 1.2
        elif weighted_pace < reference_pace * 0.5:
            # 步频很低，降低阈值（更宽松，识别困难）
            adjustment_factor = 0.8
        else:
            # 步频正常，不调整
            adjustment_factor = 1.0
        
        adjusted_threshold = base_threshold * adjustment_factor
        
        logger.debug(
            f"Adjusted difficulty threshold: {base_threshold:.2f} -> "
            f"{adjusted_threshold:.2f} (weighted_pace={weighted_pace:.2f})"
        )
        
        return adjusted_threshold
    
    def prevent_false_prosperity(
        self,
        difficulty_score: float,
        weighted_pace: float,
        knowledge_point_id: int
    ) -> FalseProsperityCheck:
        """防止虚假繁荣误报
        
        虚假繁荣：快速学习高难知识点时，不误判为"已掌握"
        
        检测条件：
        1. 加权步频很高（>3.0知识点/小时）
        2. 但困难度分数也较高（>0.3）
        3. 知识点难度系数较高（>1.5）
        
        Args:
            difficulty_score: 困难度分数（0-1，越高越困难）
            weighted_pace: 加权后的认知步频
            knowledge_point_id: 知识点ID
        
        Returns:
            虚假繁荣检查结果
        """
        difficulty_coefficient = self.get_difficulty_coefficient(knowledge_point_id)
        
        is_false = False
        reasons = []
        
        # 检查条件1：加权步频很高
        if weighted_pace > self.FALSE_PROSPERITY_PACE_THRESHOLD:
            reasons.append(f"加权步频过高({weighted_pace:.2f} kp/h)")
        
        # 检查条件2：困难度分数较高
        if difficulty_score > self.FALSE_PROSPERITY_DIFFICULTY_THRESHOLD:
            reasons.append(f"困难度分数较高({difficulty_score:.2f})")
        
        # 检查条件3：知识点难度系数较高
        if difficulty_coefficient > 1.5:
            reasons.append(f"知识点难度系数较高({difficulty_coefficient:.2f})")
        
        # 如果同时满足多个条件，判定为虚假繁荣
        if (weighted_pace > self.FALSE_PROSPERITY_PACE_THRESHOLD and
            difficulty_score > self.FALSE_PROSPERITY_DIFFICULTY_THRESHOLD and
            difficulty_coefficient > 1.5):
            is_false = True
        
        reason_str = "；".join(reasons) if reasons else "正常"
        
        if is_false:
            recommendation = (
                "检测到虚假繁荣：快速学习高难知识点，但困难度分数较高，"
                "建议不判定为'已掌握'，继续观察学习效果"
            )
        else:
            recommendation = "学习状态正常"
        
        result = FalseProsperityCheck(
            is_false_prosperity=is_false,
            difficulty_score=difficulty_score,
            weighted_pace=weighted_pace,
            reason=reason_str,
            recommendation=recommendation
        )
        
        if is_false:
            logger.warning(
                f"False prosperity detected for kp={knowledge_point_id}: {reason_str}"
            )
        
        return result
    
    def batch_calculate_coefficients(
        self,
        knowledge_point_durations: Dict[int, float],
        sample_sizes: Optional[Dict[int, int]] = None
    ) -> Dict[int, float]:
        """批量计算难度系数
        
        Args:
            knowledge_point_durations: 知识点ID到平均时长的映射
            sample_sizes: 知识点ID到样本数量的映射（可选）
        
        Returns:
            知识点ID到难度系数的映射
        """
        coefficients = {}
        
        for kp_id, avg_duration in knowledge_point_durations.items():
            sample_size = sample_sizes.get(kp_id, 0) if sample_sizes else 0
            coefficient = self.calculate_difficulty_coefficient(
                kp_id, avg_duration, sample_size
            )
            coefficients[kp_id] = coefficient
        
        logger.info(
            f"Batch calculated coefficients for {len(coefficients)} knowledge points"
        )
        
        return coefficients
    
    def get_coefficient_statistics(
        self,
        knowledge_point_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取难度系数统计报告
        
        Args:
            knowledge_point_id: 知识点ID（可选，如果提供则只统计该知识点）
        
        Returns:
            统计报告字典
        """
        if knowledge_point_id is not None:
            if knowledge_point_id not in self.difficulty_coefficients:
                return {
                    "knowledge_point_id": knowledge_point_id,
                    "current_coefficient": 1.0,
                    "history_count": 0,
                    "average_coefficient": 1.0,
                    "coefficient_trend": "stable"
                }
            
            coeff = self.difficulty_coefficients[knowledge_point_id]
            history = self.coefficient_history.get(knowledge_point_id, [])
            
            if history:
                avg_coeff = sum(history) / len(history)
                # 判断趋势
                if len(history) >= 2:
                    recent_avg = sum(history[-5:]) / min(5, len(history))
                    early_avg = sum(history[:5]) / min(5, len(history))
                    
                    if recent_avg > early_avg * 1.1:
                        trend = "increasing"
                    elif recent_avg < early_avg * 0.9:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"
            else:
                avg_coeff = coeff.coefficient
                trend = "stable"
            
            return {
                "knowledge_point_id": knowledge_point_id,
                "current_coefficient": coeff.coefficient,
                "global_avg_duration": coeff.global_avg_duration,
                "sample_size": coeff.sample_size,
                "history_count": len(history),
                "average_coefficient": avg_coeff,
                "coefficient_trend": trend
            }
        
        # 统计所有知识点
        all_coefficients = list(self.difficulty_coefficients.values())
        
        if not all_coefficients:
            return {
                "total_knowledge_points": 0,
                "average_coefficient": 1.0,
                "min_coefficient": 1.0,
                "max_coefficient": 1.0
            }
        
        coefficients = [c.coefficient for c in all_coefficients]
        
        return {
            "total_knowledge_points": len(all_coefficients),
            "average_coefficient": sum(coefficients) / len(coefficients),
            "min_coefficient": min(coefficients),
            "max_coefficient": max(coefficients),
            "easy_count": sum(1 for c in coefficients if c < 0.7),  # 较易
            "medium_count": sum(1 for c in coefficients if 0.7 <= c <= 1.5),  # 中等
            "hard_count": sum(1 for c in coefficients if c > 1.5)  # 较难
        }
