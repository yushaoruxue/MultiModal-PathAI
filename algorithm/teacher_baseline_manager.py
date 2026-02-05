"""
教师预设基准线机制

基于v8.0需求，允许教师标记核心难点作为基准线。
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BaselineConfig:
    """基准线配置"""
    teacher_id: int
    video_id: int
    knowledge_point_ids: Set[int]  # 基准线知识点ID集合
    weight_multiplier: float = 1.5  # 权重倍数（默认1.5倍）
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str = ""  # 配置说明


@dataclass
class BaselineRecord:
    """基准线记录"""
    teacher_id: int
    video_id: int
    knowledge_point_id: int
    weight_multiplier: float
    created_at: datetime = field(default_factory=datetime.now)


class TeacherBaselineManager:
    """教师预设基准线管理器
    
    功能：
    1. 教师可以标记知识点为"核心难点"（基准线）
    2. 基准线知识点在难点识别时权重更高
    3. 基准线知识点在补偿推送时优先级更高
    4. 支持教师批量设置基准线
    """
    
    # 默认权重倍数
    DEFAULT_WEIGHT_MULTIPLIER = 1.5
    
    def __init__(self):
        """初始化教师基准线管理器"""
        # 存储基准线配置（按video_id组织）
        self.baseline_configs: Dict[tuple, BaselineConfig] = {}  # key: (teacher_id, video_id)
        
        # 存储基准线记录（按知识点快速查找）
        self.baseline_records: Dict[int, BaselineRecord] = {}  # key: knowledge_point_id
        
        logger.info("TeacherBaselineManager initialized")
    
    def set_baseline(
        self,
        knowledge_point_ids: List[int],
        teacher_id: int,
        video_id: int,
        weight_multiplier: Optional[float] = None,
        description: str = ""
    ) -> bool:
        """设置基准线
        
        Args:
            knowledge_point_ids: 知识点ID列表
            teacher_id: 教师ID
            video_id: 视频ID
            weight_multiplier: 权重倍数（可选，默认1.5）
            description: 配置说明（可选）
        
        Returns:
            是否成功设置
        """
        if not knowledge_point_ids:
            logger.warning("Empty knowledge point IDs provided")
            return False
        
        if weight_multiplier is None:
            weight_multiplier = self.DEFAULT_WEIGHT_MULTIPLIER
        
        if weight_multiplier <= 0:
            logger.error(f"Invalid weight multiplier {weight_multiplier}, must be > 0")
            return False
        
        key = (teacher_id, video_id)
        
        # 更新或创建配置
        if key in self.baseline_configs:
            config = self.baseline_configs[key]
            config.knowledge_point_ids = set(knowledge_point_ids)
            config.weight_multiplier = weight_multiplier
            config.description = description
            config.updated_at = datetime.now()
        else:
            config = BaselineConfig(
                teacher_id=teacher_id,
                video_id=video_id,
                knowledge_point_ids=set(knowledge_point_ids),
                weight_multiplier=weight_multiplier,
                description=description
            )
            self.baseline_configs[key] = config
        
        # 更新基准线记录
        for kp_id in knowledge_point_ids:
            record = BaselineRecord(
                teacher_id=teacher_id,
                video_id=video_id,
                knowledge_point_id=kp_id,
                weight_multiplier=weight_multiplier
            )
            self.baseline_records[kp_id] = record
        
        logger.info(
            f"Set baseline for teacher={teacher_id}, video={video_id}: "
            f"{len(knowledge_point_ids)} knowledge points, "
            f"weight_multiplier={weight_multiplier}"
        )
        
        return True
    
    def remove_baseline(
        self,
        knowledge_point_ids: List[int],
        teacher_id: int,
        video_id: int
    ) -> bool:
        """移除基准线
        
        Args:
            knowledge_point_ids: 知识点ID列表
            teacher_id: 教师ID
            video_id: 视频ID
        
        Returns:
            是否成功移除
        """
        key = (teacher_id, video_id)
        
        if key not in self.baseline_configs:
            logger.warning(
                f"No baseline config found for teacher={teacher_id}, video={video_id}"
            )
            return False
        
        config = self.baseline_configs[key]
        
        # 从配置中移除
        for kp_id in knowledge_point_ids:
            config.knowledge_point_ids.discard(kp_id)
            # 从记录中移除
            if kp_id in self.baseline_records:
                del self.baseline_records[kp_id]
        
        # 如果配置为空，删除配置
        if not config.knowledge_point_ids:
            del self.baseline_configs[key]
        
        logger.info(
            f"Removed baseline for teacher={teacher_id}, video={video_id}: "
            f"{len(knowledge_point_ids)} knowledge points"
        )
        
        return True
    
    def get_baseline_weight(self, knowledge_point_id: int) -> float:
        """获取基准线权重
        
        Args:
            knowledge_point_id: 知识点ID
        
        Returns:
            权重倍数，如果不是基准线则返回1.0
        """
        if knowledge_point_id in self.baseline_records:
            record = self.baseline_records[knowledge_point_id]
            return record.weight_multiplier
        
        return 1.0
    
    def is_baseline(self, knowledge_point_id: int) -> bool:
        """判断知识点是否为基准线
        
        Args:
            knowledge_point_id: 知识点ID
        
        Returns:
            是否为基准线
        """
        return knowledge_point_id in self.baseline_records
    
    def apply_baseline_to_difficulty_detection(
        self,
        knowledge_point_id: int,
        base_score: float
    ) -> float:
        """将基准线应用到难点识别
        
        Args:
            knowledge_point_id: 知识点ID
            base_score: 基础困难度分数
        
        Returns:
            调整后的困难度分数
        """
        weight = self.get_baseline_weight(knowledge_point_id)
        adjusted_score = base_score * weight
        
        logger.debug(
            f"Applied baseline weight to kp={knowledge_point_id}: "
            f"{base_score:.2f} * {weight:.2f} = {adjusted_score:.2f}"
        )
        
        return adjusted_score
    
    def get_baseline_knowledge_points(
        self,
        video_id: int,
        teacher_id: Optional[int] = None
    ) -> List[int]:
        """获取基准线知识点列表
        
        Args:
            video_id: 视频ID
            teacher_id: 教师ID（可选，如果提供则只返回该教师的基准线）
        
        Returns:
            基准线知识点ID列表
        """
        baseline_kps = []
        
        for (tid, vid), config in self.baseline_configs.items():
            if vid == video_id:
                if teacher_id is None or tid == teacher_id:
                    baseline_kps.extend(config.knowledge_point_ids)
        
        # 去重
        baseline_kps = list(set(baseline_kps))
        
        logger.debug(
            f"Found {len(baseline_kps)} baseline knowledge points "
            f"for video={video_id}, teacher={teacher_id}"
        )
        
        return baseline_kps
    
    def get_baseline_config(
        self,
        teacher_id: int,
        video_id: int
    ) -> Optional[BaselineConfig]:
        """获取基准线配置
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID
        
        Returns:
            基准线配置，如果不存在则返回None
        """
        key = (teacher_id, video_id)
        return self.baseline_configs.get(key)
    
    def get_priority_for_resource_push(
        self,
        knowledge_point_id: int
    ) -> int:
        """获取补偿推送优先级
        
        Args:
            knowledge_point_id: 知识点ID
        
        Returns:
            优先级（1-10，10最高），基准线知识点优先级更高
        """
        if self.is_baseline(knowledge_point_id):
            return 10  # 基准线知识点最高优先级
        return 5  # 普通知识点中等优先级
    
    def batch_set_baseline(
        self,
        teacher_id: int,
        video_id: int,
        knowledge_point_ids: List[int],
        weight_multiplier: Optional[float] = None
    ) -> Dict[int, bool]:
        """批量设置基准线
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID
            knowledge_point_ids: 知识点ID列表
            weight_multiplier: 权重倍数（可选）
        
        Returns:
            每个知识点的设置结果字典
        """
        # 直接调用set_baseline，它会处理批量设置
        success = self.set_baseline(
            knowledge_point_ids, teacher_id, video_id, weight_multiplier
        )
        
        # 返回每个知识点的结果（简化处理，实际应该逐个验证）
        results = {}
        for kp_id in knowledge_point_ids:
            results[kp_id] = success
        
        return results
    
    def get_baseline_statistics(
        self,
        teacher_id: Optional[int] = None,
        video_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取基准线统计报告
        
        Args:
            teacher_id: 教师ID（可选）
            video_id: 视频ID（可选）
        
        Returns:
            统计报告字典
        """
        configs = list(self.baseline_configs.values())
        records = list(self.baseline_records.values())
        
        if teacher_id is not None:
            configs = [c for c in configs if c.teacher_id == teacher_id]
            records = [r for r in records if r.teacher_id == teacher_id]
        
        if video_id is not None:
            configs = [c for c in configs if c.video_id == video_id]
            records = [r for r in records if r.video_id == video_id]
        
        total_knowledge_points = len(set(r.knowledge_point_id for r in records))
        
        # 统计权重倍数分布
        weight_distribution = {}
        for record in records:
            weight = record.weight_multiplier
            if weight not in weight_distribution:
                weight_distribution[weight] = 0
            weight_distribution[weight] += 1
        
        stats = {
            "total_configs": len(configs),
            "total_baseline_knowledge_points": total_knowledge_points,
            "weight_distribution": weight_distribution,
            "average_weight_multiplier": (
                sum(r.weight_multiplier for r in records) / len(records)
                if records else 0.0
            )
        }
        
        return stats
    
    def clear_baseline(
        self,
        teacher_id: int,
        video_id: int
    ) -> bool:
        """清除所有基准线
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID
        
        Returns:
            是否成功清除
        """
        key = (teacher_id, video_id)
        
        if key not in self.baseline_configs:
            return False
        
        config = self.baseline_configs[key]
        
        # 从记录中移除所有知识点
        for kp_id in config.knowledge_point_ids:
            if kp_id in self.baseline_records:
                del self.baseline_records[kp_id]
        
        # 删除配置
        del self.baseline_configs[key]
        
        logger.info(
            f"Cleared all baseline for teacher={teacher_id}, video={video_id}"
        )
        
        return True
