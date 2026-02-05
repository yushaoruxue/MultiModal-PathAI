"""
教师激进系数调节算法

基于v10.0需求，允许教师统一调节干预敏感度。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DifficultyResult:
    """难点判定结果"""
    is_difficult: bool
    difficulty_score: float  # 0-10
    trigger_reasons: List[str]


@dataclass
class CoefficientConfig:
    """激进系数配置"""
    teacher_id: int
    coefficient: float  # 0.1-2.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str = ""  # 配置说明


@dataclass
class CoefficientHistory:
    """系数历史记录"""
    teacher_id: int
    coefficient: float
    changed_at: datetime
    changed_by: Optional[int] = None  # 如果由管理员修改
    reason: str = ""  # 修改原因


@dataclass
class AdjustedDetectionResult:
    """调整后的判定结果"""
    is_difficult: bool
    difficulty_score: float
    base_threshold: float
    adjusted_threshold: float
    coefficient: float
    would_trigger_without_coefficient: bool
    actually_triggers: bool


class TeacherAggressionCoefficient:
    """教师激进系数调节算法
    
    功能：
    1. 允许教师设置激进系数（0.1-2.0）
    2. 根据系数调整干预阈值
    3. 统一调节所有知识点的干预敏感度
    4. 记录系数历史和使用统计
    """
    
    # 系数范围
    MIN_COEFFICIENT = 0.1
    MAX_COEFFICIENT = 2.0
    DEFAULT_COEFFICIENT = 1.0
    
    def __init__(self):
        """初始化教师激进系数管理器"""
        # 存储每个教师的系数配置
        self.coefficient_configs: Dict[int, CoefficientConfig] = {}
        
        # 存储系数历史记录
        self.coefficient_history: List[CoefficientHistory] = []
        
        logger.info("TeacherAggressionCoefficient initialized")
    
    def set_aggression_coefficient(
        self,
        teacher_id: int,
        coefficient: float,
        description: str = ""
    ) -> bool:
        """设置教师的激进系数
        
        Args:
            teacher_id: 教师ID
            coefficient: 激进系数（0.1-2.0）
                - 0.1：非常保守，几乎不触发干预
                - 1.0：默认值，正常触发
                - 2.0：非常激进，容易触发干预
            description: 配置说明（可选）
        
        Returns:
            是否成功设置
        """
        # 验证系数范围
        if coefficient < self.MIN_COEFFICIENT or coefficient > self.MAX_COEFFICIENT:
            logger.error(
                f"Invalid coefficient {coefficient}, must be in "
                f"[{self.MIN_COEFFICIENT}, {self.MAX_COEFFICIENT}]"
            )
            return False
        
        # 获取旧配置（如果存在）
        old_coefficient = None
        if teacher_id in self.coefficient_configs:
            old_coefficient = self.coefficient_configs[teacher_id].coefficient
        
        # 创建或更新配置
        if teacher_id in self.coefficient_configs:
            config = self.coefficient_configs[teacher_id]
            config.coefficient = coefficient
            config.updated_at = datetime.now()
            config.description = description
        else:
            config = CoefficientConfig(
                teacher_id=teacher_id,
                coefficient=coefficient,
                description=description
            )
            self.coefficient_configs[teacher_id] = config
        
        # 记录历史
        if old_coefficient is None or old_coefficient != coefficient:
            history = CoefficientHistory(
                teacher_id=teacher_id,
                coefficient=coefficient,
                changed_at=datetime.now(),
                reason=description or f"系数从{old_coefficient}调整为{coefficient}" if old_coefficient else f"设置系数为{coefficient}"
            )
            self.coefficient_history.append(history)
        
        logger.info(
            f"Set aggression coefficient for teacher={teacher_id}: {coefficient} "
            f"(old={old_coefficient})"
        )
        
        return True
    
    def adjust_intervention_threshold(
        self,
        base_threshold: float,
        coefficient: float
    ) -> float:
        """调整干预阈值
        
        公式：adjusted_threshold = base_threshold / coefficient
        
        说明：
        - coefficient > 1.0：阈值降低，更容易触发干预（激进）
        - coefficient < 1.0：阈值提高，更难触发干预（保守）
        - coefficient = 1.0：阈值不变（默认）
        
        Args:
            base_threshold: 基础干预阈值
            coefficient: 激进系数
        
        Returns:
            调整后的阈值
        """
        if coefficient <= 0:
            logger.warning(f"Invalid coefficient {coefficient}, using default 1.0")
            coefficient = self.DEFAULT_COEFFICIENT
        
        adjusted_threshold = base_threshold / coefficient
        
        logger.debug(
            f"Adjusted threshold: {base_threshold} / {coefficient} = {adjusted_threshold:.2f}"
        )
        
        return adjusted_threshold
    
    def apply_coefficient_to_detection(
        self,
        difficulty_result: DifficultyResult,
        teacher_id: int,
        base_threshold: float = 6.0
    ) -> AdjustedDetectionResult:
        """将激进系数应用到难点判定
        
        Args:
            difficulty_result: 难点判定结果
            teacher_id: 教师ID
            base_threshold: 基础干预阈值（默认6.0）
        
        Returns:
            调整后的判定结果
        """
        # 获取教师的激进系数
        coefficient = self.get_coefficient_config(teacher_id)
        
        # 计算调整后的阈值
        adjusted_threshold = self.adjust_intervention_threshold(
            base_threshold, coefficient
        )
        
        # 判断是否触发（基于调整后的阈值）
        would_trigger_without = difficulty_result.difficulty_score >= base_threshold
        actually_triggers = difficulty_result.difficulty_score >= adjusted_threshold
        
        result = AdjustedDetectionResult(
            is_difficult=difficulty_result.is_difficult,
            difficulty_score=difficulty_result.difficulty_score,
            base_threshold=base_threshold,
            adjusted_threshold=adjusted_threshold,
            coefficient=coefficient,
            would_trigger_without_coefficient=would_trigger_without,
            actually_triggers=actually_triggers
        )
        
        logger.info(
            f"Applied coefficient {coefficient} to detection: "
            f"score={difficulty_result.difficulty_score:.2f}, "
            f"base_threshold={base_threshold:.2f}, "
            f"adjusted_threshold={adjusted_threshold:.2f}, "
            f"triggers={actually_triggers}"
        )
        
        return result
    
    def get_coefficient_config(self, teacher_id: int) -> float:
        """获取教师的激进系数配置
        
        Args:
            teacher_id: 教师ID
        
        Returns:
            激进系数，如果未配置则返回默认值1.0
        """
        if teacher_id in self.coefficient_configs:
            return self.coefficient_configs[teacher_id].coefficient
        
        return self.DEFAULT_COEFFICIENT
    
    def get_coefficient_config_full(self, teacher_id: int) -> Optional[CoefficientConfig]:
        """获取完整的系数配置对象
        
        Args:
            teacher_id: 教师ID
        
        Returns:
            系数配置对象，如果不存在则返回None
        """
        return self.coefficient_configs.get(teacher_id)
    
    def get_coefficient_history(
        self,
        teacher_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[CoefficientHistory]:
        """获取系数历史记录
        
        Args:
            teacher_id: 教师ID（可选，如果提供则只返回该教师的历史）
            limit: 限制返回数量（可选）
        
        Returns:
            历史记录列表（按时间倒序）
        """
        history = self.coefficient_history.copy()
        
        if teacher_id is not None:
            history = [h for h in history if h.teacher_id == teacher_id]
        
        # 按时间倒序排序
        history.sort(key=lambda x: x.changed_at, reverse=True)
        
        if limit is not None:
            history = history[:limit]
        
        return history
    
    def get_coefficient_statistics(
        self,
        teacher_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取系数效果统计
        
        Args:
            teacher_id: 教师ID（可选，如果提供则只统计该教师的数据）
        
        Returns:
            统计报告字典
        """
        configs = list(self.coefficient_configs.values())
        
        if teacher_id is not None:
            configs = [c for c in configs if c.teacher_id == teacher_id]
        
        if not configs:
            return {
                "total_teachers": 0,
                "average_coefficient": self.DEFAULT_COEFFICIENT,
                "min_coefficient": self.DEFAULT_COEFFICIENT,
                "max_coefficient": self.DEFAULT_COEFFICIENT,
                "conservative_count": 0,  # < 1.0
                "normal_count": 0,  # = 1.0
                "aggressive_count": 0  # > 1.0
            }
        
        coefficients = [c.coefficient for c in configs]
        
        stats = {
            "total_teachers": len(configs),
            "average_coefficient": sum(coefficients) / len(coefficients),
            "min_coefficient": min(coefficients),
            "max_coefficient": max(coefficients),
            "conservative_count": sum(1 for c in coefficients if c < 1.0),
            "normal_count": sum(1 for c in coefficients if c == 1.0),
            "aggressive_count": sum(1 for c in coefficients if c > 1.0)
        }
        
        return stats
    
    def reset_to_default(self, teacher_id: int) -> bool:
        """重置为默认系数
        
        Args:
            teacher_id: 教师ID
        
        Returns:
            是否成功重置
        """
        return self.set_aggression_coefficient(
            teacher_id,
            self.DEFAULT_COEFFICIENT,
            "重置为默认值"
        )
    
    def batch_set_coefficient(
        self,
        teacher_ids: List[int],
        coefficient: float,
        description: str = ""
    ) -> Dict[int, bool]:
        """批量设置系数
        
        Args:
            teacher_ids: 教师ID列表
            coefficient: 激进系数
            description: 配置说明
        
        Returns:
            每个教师的设置结果字典
        """
        results = {}
        
        for teacher_id in teacher_ids:
            results[teacher_id] = self.set_aggression_coefficient(
                teacher_id, coefficient, description
            )
        
        logger.info(
            f"Batch set coefficient {coefficient} for {len(teacher_ids)} teachers: "
            f"{sum(results.values())} succeeded"
        )
        
        return results
    
    def get_effect_description(self, coefficient: float) -> str:
        """获取系数效果描述
        
        Args:
            coefficient: 激进系数
        
        Returns:
            效果描述字符串
        """
        if coefficient < 0.5:
            return "非常保守，几乎不触发干预"
        elif coefficient < 1.0:
            return "保守，较少触发干预"
        elif coefficient == 1.0:
            return "正常，标准触发频率"
        elif coefficient < 1.5:
            return "激进，较多触发干预"
        else:
            return "非常激进，容易触发干预"
    
    def calculate_trigger_probability_change(
        self,
        base_threshold: float,
        coefficient: float,
        sample_scores: List[float]
    ) -> Dict[str, Any]:
        """计算系数对触发概率的影响
        
        Args:
            base_threshold: 基础阈值
            coefficient: 激进系数
            sample_scores: 样本分数列表
        
        Returns:
            影响分析字典
        """
        if not sample_scores:
            return {
                "base_trigger_count": 0,
                "adjusted_trigger_count": 0,
                "base_trigger_rate": 0.0,
                "adjusted_trigger_rate": 0.0,
                "change_rate": 0.0
            }
        
        adjusted_threshold = self.adjust_intervention_threshold(
            base_threshold, coefficient
        )
        
        base_trigger_count = sum(1 for score in sample_scores if score >= base_threshold)
        adjusted_trigger_count = sum(1 for score in sample_scores if score >= adjusted_threshold)
        
        base_trigger_rate = base_trigger_count / len(sample_scores)
        adjusted_trigger_rate = adjusted_trigger_count / len(sample_scores)
        
        if base_trigger_rate > 0:
            change_rate = (adjusted_trigger_rate - base_trigger_rate) / base_trigger_rate
        else:
            change_rate = float('inf') if adjusted_trigger_rate > 0 else 0.0
        
        return {
            "base_trigger_count": base_trigger_count,
            "adjusted_trigger_count": adjusted_trigger_count,
            "base_trigger_rate": base_trigger_rate,
            "adjusted_trigger_rate": adjusted_trigger_rate,
            "change_rate": change_rate,
            "base_threshold": base_threshold,
            "adjusted_threshold": adjusted_threshold,
            "coefficient": coefficient
        }
