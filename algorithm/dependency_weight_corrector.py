"""
依赖权重修正算法

基于v7.0需求，基于实际学习数据动态调整知识点依赖关系的权重。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """知识点依赖关系"""
    source_kp_id: int
    target_kp_id: int
    initial_weight: float  # 初始权重（基于语义相似度和时序关系）
    current_weight: float  # 当前权重
    weight_history: List[Tuple[datetime, float]] = field(default_factory=list)  # 权重历史


@dataclass
class LearningData:
    """学生学习数据"""
    user_id: int
    knowledge_point_id: int
    mastery_rate: float  # 掌握率（0-1）
    difficulty_score: float  # 困难度分数（0-1）
    study_duration: float  # 学习时长（分钟）
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WeightChange:
    """权重变化记录"""
    source_kp_id: int
    target_kp_id: int
    old_weight: float
    new_weight: float
    change_amount: float
    change_percentage: float
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WeightReport:
    """权重变化报告"""
    total_dependencies: int
    updated_count: int
    average_change: float
    significant_changes: List[WeightChange]  # 显著变化（变化>10%）
    weight_distribution: Dict[str, int]  # 权重分布


class DependencyWeightCorrector:
    """依赖权重修正算法
    
    功能：
    1. 初始权重：基于语义相似度和时序关系
    2. 动态修正：基于学生学习数据（掌握率、困难度）
    3. 权重更新公式：w_new = w_old × (1 - α) + w_data × α
       - α是学习率（默认0.1）
       - w_data是基于学习数据计算的权重
    """
    
    # 默认学习率
    DEFAULT_LEARNING_RATE = 0.1
    
    # 显著变化阈值（10%）
    SIGNIFICANT_CHANGE_THRESHOLD = 0.1
    
    def __init__(self, learning_rate: float = DEFAULT_LEARNING_RATE):
        """初始化依赖权重修正器
        
        Args:
            learning_rate: 学习率α（默认0.1）
        """
        self.learning_rate = learning_rate
        
        # 存储依赖关系
        self.dependencies: Dict[Tuple[int, int], Dependency] = {}  # key: (source, target)
        
        # 存储学习数据
        self.learning_data: Dict[int, List[LearningData]] = {}  # key: kp_id
        
        # 存储权重变化历史
        self.weight_changes: List[WeightChange] = []
        
        logger.info(
            f"DependencyWeightCorrector initialized with learning_rate={learning_rate}"
        )
    
    def correct_weights(
        self,
        dependencies: List[Tuple[int, int, float]],
        learning_data: List[LearningData]
    ) -> Dict[Tuple[int, int], float]:
        """修正依赖权重
        
        Args:
            dependencies: 依赖关系列表（(source_kp_id, target_kp_id, initial_weight)）
            learning_data: 学生学习数据列表
        
        Returns:
            修正后的权重字典
        """
        # 1. 更新依赖关系
        for source_id, target_id, initial_weight in dependencies:
            key = (source_id, target_id)
            
            if key not in self.dependencies:
                dep = Dependency(
                    source_kp_id=source_id,
                    target_kp_id=target_id,
                    initial_weight=initial_weight,
                    current_weight=initial_weight
                )
                self.dependencies[key] = dep
            else:
                self.dependencies[key].initial_weight = initial_weight
        
        # 2. 更新学习数据
        for data in learning_data:
            if data.knowledge_point_id not in self.learning_data:
                self.learning_data[data.knowledge_point_id] = []
            
            self.learning_data[data.knowledge_point_id].append(data)
            
            # 只保留最近100条记录
            if len(self.learning_data[data.knowledge_point_id]) > 100:
                self.learning_data[data.knowledge_point_id] = \
                    self.learning_data[data.knowledge_point_id][-100:]
        
        # 3. 计算数据驱动的权重
        corrected_weights = {}
        
        for key, dep in self.dependencies.items():
            source_id, target_id = key
            
            # 计算基于学习数据的权重
            data_weight = self.calculate_data_driven_weight(
                (source_id, target_id),
                learning_data
            )
            
            # 更新权重
            old_weight = dep.current_weight
            new_weight = self.update_weights(
                {key: old_weight},
                {key: data_weight},
                self.learning_rate
            )[key]
            
            # 记录权重变化
            change_amount = new_weight - old_weight
            change_percentage = (change_amount / old_weight * 100) if old_weight > 0 else 0.0
            
            if abs(change_percentage) > 0.01:  # 变化超过1%才记录
                change = WeightChange(
                    source_kp_id=source_id,
                    target_kp_id=target_id,
                    old_weight=old_weight,
                    new_weight=new_weight,
                    change_amount=change_amount,
                    change_percentage=change_percentage,
                    reason=f"基于学习数据修正（掌握率、困难度）"
                )
                self.weight_changes.append(change)
                
                # 更新依赖关系的权重历史
                dep.current_weight = new_weight
                dep.weight_history.append((datetime.now(), new_weight))
                
                # 只保留最近50条历史
                if len(dep.weight_history) > 50:
                    dep.weight_history = dep.weight_history[-50:]
            
            corrected_weights[key] = new_weight
        
        logger.info(
            f"Corrected weights for {len(corrected_weights)} dependencies, "
            f"{len(self.weight_changes)} changes recorded"
        )
        
        return corrected_weights
    
    def calculate_data_driven_weight(
        self,
        kp_pair: Tuple[int, int],
        learning_data: List[LearningData]
    ) -> float:
        """计算基于学习数据的权重
        
        Args:
            kp_pair: 知识点对（(source_id, target_id)）
            learning_data: 学习数据列表
        
        Returns:
            数据驱动的权重（0-1）
        """
        source_id, target_id = kp_pair
        
        # 获取源知识点和目标知识点的学习数据
        source_data = [d for d in learning_data if d.knowledge_point_id == source_id]
        target_data = [d for d in learning_data if d.knowledge_point_id == target_id]
        
        if not source_data or not target_data:
            # 数据不足，返回默认权重
            return self.dependencies.get(kp_pair, Dependency(0, 0, 0.5, 0.5)).current_weight
        
        # 计算源知识点的平均掌握率
        avg_source_mastery = sum(d.mastery_rate for d in source_data) / len(source_data)
        
        # 计算目标知识点的平均困难度
        avg_target_difficulty = sum(d.difficulty_score for d in target_data) / len(target_data)
        
        # 计算目标知识点的平均掌握率
        avg_target_mastery = sum(d.mastery_rate for d in target_data) / len(target_data)
        
        # 权重计算逻辑：
        # 1. 如果源知识点掌握率高，且目标知识点困难度高，说明依赖关系强
        # 2. 如果目标知识点掌握率低，说明需要前置知识点，依赖关系强
        # 3. 综合考虑这些因素
        
        # 因子1：源知识点掌握率（掌握率高，依赖关系可能更强）
        source_factor = avg_source_mastery
        
        # 因子2：目标知识点困难度（困难度高，依赖关系可能更强）
        difficulty_factor = avg_target_difficulty
        
        # 因子3：目标知识点掌握率（掌握率低，说明需要前置，依赖关系强）
        target_mastery_factor = 1.0 - avg_target_mastery
        
        # 综合权重（加权平均）
        data_weight = (
            source_factor * 0.3 +
            difficulty_factor * 0.4 +
            target_mastery_factor * 0.3
        )
        
        # 确保在[0, 1]范围内
        data_weight = max(0.0, min(1.0, data_weight))
        
        logger.debug(
            f"Calculated data-driven weight for {kp_pair}: {data_weight:.3f} "
            f"(source_mastery={avg_source_mastery:.2f}, "
            f"target_difficulty={avg_target_difficulty:.2f}, "
            f"target_mastery={avg_target_mastery:.2f})"
        )
        
        return data_weight
    
    def update_weights(
        self,
        old_weights: Dict[Tuple[int, int], float],
        new_weights: Dict[Tuple[int, int], float],
        alpha: Optional[float] = None
    ) -> Dict[Tuple[int, int], float]:
        """更新权重
        
        使用公式：w_new = w_old × (1 - α) + w_data × α
        
        Args:
            old_weights: 旧权重字典
            new_weights: 新权重字典（基于数据）
            alpha: 学习率（可选，默认使用初始化时的学习率）
        
        Returns:
            更新后的权重字典
        """
        if alpha is None:
            alpha = self.learning_rate
        
        updated_weights = {}
        
        for key in old_weights:
            old_weight = old_weights[key]
            new_weight = new_weights.get(key, old_weight)
            
            # 应用更新公式
            updated_weight = old_weight * (1 - alpha) + new_weight * alpha
            
            updated_weights[key] = updated_weight
        
        return updated_weights
    
    def generate_weight_report(
        self,
        weight_changes: Optional[List[WeightChange]] = None
    ) -> WeightReport:
        """生成权重变化报告
        
        Args:
            weight_changes: 权重变化列表（可选，如果不提供则使用存储的变化）
        
        Returns:
            权重变化报告
        """
        if weight_changes is None:
            weight_changes = self.weight_changes
        
        if not weight_changes:
            return WeightReport(
                total_dependencies=len(self.dependencies),
                updated_count=0,
                average_change=0.0,
                significant_changes=[],
                weight_distribution={}
            )
        
        # 计算平均变化
        avg_change = sum(abs(c.change_amount) for c in weight_changes) / len(weight_changes)
        
        # 找出显著变化（变化>10%）
        significant_changes = [
            c for c in weight_changes
            if abs(c.change_percentage) >= self.SIGNIFICANT_CHANGE_THRESHOLD * 100
        ]
        
        # 统计权重分布
        weight_distribution = defaultdict(int)
        for dep in self.dependencies.values():
            if dep.current_weight < 0.3:
                weight_distribution["weak"] += 1
            elif dep.current_weight < 0.7:
                weight_distribution["medium"] += 1
            else:
                weight_distribution["strong"] += 1
        
        report = WeightReport(
            total_dependencies=len(self.dependencies),
            updated_count=len(weight_changes),
            average_change=avg_change,
            significant_changes=significant_changes,
            weight_distribution=dict(weight_distribution)
        )
        
        logger.info(
            f"Generated weight report: {report.updated_count}/{report.total_dependencies} "
            f"updated, {len(significant_changes)} significant changes"
        )
        
        return report
    
    def get_weight_history(
        self,
        source_kp_id: int,
        target_kp_id: int
    ) -> List[Tuple[datetime, float]]:
        """获取权重历史
        
        Args:
            source_kp_id: 源知识点ID
            target_kp_id: 目标知识点ID
        
        Returns:
            权重历史列表（(时间戳, 权重)）
        """
        key = (source_kp_id, target_kp_id)
        
        if key in self.dependencies:
            return self.dependencies[key].weight_history
        
        return []
    
    def get_current_weight(
        self,
        source_kp_id: int,
        target_kp_id: int
    ) -> Optional[float]:
        """获取当前权重
        
        Args:
            source_kp_id: 源知识点ID
            target_kp_id: 目标知识点ID
        
        Returns:
            当前权重，如果不存在则返回None
        """
        key = (source_kp_id, target_kp_id)
        
        if key in self.dependencies:
            return self.dependencies[key].current_weight
        
        return None
    
    def batch_update_weights(
        self,
        weight_updates: Dict[Tuple[int, int], float],
        alpha: Optional[float] = None
    ) -> Dict[Tuple[int, int], float]:
        """批量更新权重
        
        Args:
            weight_updates: 权重更新字典
            alpha: 学习率（可选）
        
        Returns:
            更新后的权重字典
        """
        # 获取当前权重
        old_weights = {
            key: dep.current_weight
            for key, dep in self.dependencies.items()
        }
        
        # 更新权重
        updated_weights = self.update_weights(old_weights, weight_updates, alpha)
        
        # 更新依赖关系
        for key, new_weight in updated_weights.items():
            if key in self.dependencies:
                old_weight = self.dependencies[key].current_weight
                self.dependencies[key].current_weight = new_weight
                
                # 记录变化
                change = WeightChange(
                    source_kp_id=key[0],
                    target_kp_id=key[1],
                    old_weight=old_weight,
                    new_weight=new_weight,
                    change_amount=new_weight - old_weight,
                    change_percentage=(new_weight - old_weight) / old_weight * 100 if old_weight > 0 else 0.0,
                    reason="批量更新"
                )
                self.weight_changes.append(change)
        
        logger.info(f"Batch updated {len(updated_weights)} weights")
        
        return updated_weights
    
    def get_weight_statistics(
        self
    ) -> Dict[str, Any]:
        """获取权重统计
        
        Returns:
            统计报告字典
        """
        if not self.dependencies:
            return {
                "total_dependencies": 0,
                "average_weight": 0.0,
                "min_weight": 0.0,
                "max_weight": 0.0
            }
        
        weights = [dep.current_weight for dep in self.dependencies.values()]
        
        return {
            "total_dependencies": len(self.dependencies),
            "average_weight": sum(weights) / len(weights),
            "min_weight": min(weights),
            "max_weight": max(weights),
            "weight_std": (
                (sum((w - sum(weights) / len(weights)) ** 2 for w in weights) / len(weights)) ** 0.5
                if weights else 0.0
            ),
            "total_changes": len(self.weight_changes)
        }
