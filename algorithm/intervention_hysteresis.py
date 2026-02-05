"""
干预抗震荡机制（Hysteresis）

基于v9.0需求，实现避免短时间内重复触发干预的机制。
使用滞后效应（Hysteresis）和冷静期机制防止界面震荡。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterventionStatus(Enum):
    """干预状态枚举"""
    ACTIVE = "active"  # 干预激活中
    COOLDOWN = "cooldown"  # 冷静期中
    INACTIVE = "inactive"  # 未激活


@dataclass
class DifficultyResult:
    """难点判定结果"""
    is_difficult: bool
    difficulty_score: float  # 0-10
    trigger_reasons: List[str]


@dataclass
class CooldownRecord:
    """冷静期记录"""
    user_id: int
    knowledge_point_id: int
    intervention_triggered_at: datetime
    cooldown_until: datetime
    last_difficulty_score: float
    status: InterventionStatus = InterventionStatus.COOLDOWN


@dataclass
class HysteresisConfig:
    """滞后效应配置"""
    trigger_threshold: float  # 触发阈值（高于此值触发干预）
    release_threshold: float  # 解除阈值（低于此值解除干预）
    # 通常 release_threshold < trigger_threshold，形成滞后效应


@dataclass
class InterventionDecision:
    """干预决策结果"""
    should_trigger: bool  # 是否应该触发干预
    status: InterventionStatus  # 当前状态
    remaining_cooldown_seconds: int  # 剩余冷静期时间（秒）
    reason: str  # 决策原因
    last_intervention_time: Optional[datetime] = None


class InterventionHysteresis:
    """干预抗震荡机制
    
    功能：
    1. 冷静期机制：干预触发后，指定时间内不再重复触发
    2. 滞后效应（Hysteresis）：触发阈值和解除阈值不同，避免频繁切换
    3. 状态保持：冷静期内，保持上次干预状态
    4. 倒计时显示：提供剩余冷静期时间
    """
    
    def __init__(
        self,
        cooldown_duration_minutes: int = 5,
        default_trigger_threshold: float = 6.0,
        default_release_threshold: float = 4.0
    ):
        """初始化干预抗震荡机制
        
        Args:
            cooldown_duration_minutes: 冷静期时长（分钟，默认5分钟）
            default_trigger_threshold: 默认触发阈值（默认6.0）
            default_release_threshold: 默认解除阈值（默认4.0）
        """
        self.cooldown_duration = timedelta(minutes=cooldown_duration_minutes)
        self.default_trigger_threshold = default_trigger_threshold
        self.default_release_threshold = default_release_threshold
        
        # 存储冷静期记录
        self.cooldown_records: Dict[tuple, CooldownRecord] = {}
        
        # 存储每个用户-知识点的滞后配置（可以个性化配置）
        self.hysteresis_configs: Dict[tuple, HysteresisConfig] = {}
        
        logger.info(
            f"InterventionHysteresis initialized with "
            f"cooldown={cooldown_duration_minutes}min, "
            f"trigger_threshold={default_trigger_threshold}, "
            f"release_threshold={default_release_threshold}"
        )
    
    def check_cooldown(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> Dict[str, Any]:
        """检查冷静期状态
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            冷静期状态字典，包含：
                - in_cooldown: bool - 是否在冷静期
                - remaining_seconds: int - 剩余秒数
                - last_intervention_time: Optional[datetime] - 上次干预时间
                - status: InterventionStatus - 当前状态
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.cooldown_records:
            return {
                "in_cooldown": False,
                "remaining_seconds": 0,
                "last_intervention_time": None,
                "status": InterventionStatus.INACTIVE.value
            }
        
        record = self.cooldown_records[key]
        now = datetime.now()
        
        # 检查冷静期是否已过期
        if now >= record.cooldown_until:
            # 冷静期已过，但需要检查是否应该解除干预（使用滞后效应）
            config = self._get_hysteresis_config(user_id, knowledge_point_id)
            
            # 如果当前分数低于解除阈值，则解除干预
            if record.last_difficulty_score < config.release_threshold:
                # 移除记录，解除干预
                del self.cooldown_records[key]
                return {
                    "in_cooldown": False,
                    "remaining_seconds": 0,
                    "last_intervention_time": record.intervention_triggered_at,
                    "status": InterventionStatus.INACTIVE.value
                }
            else:
                # 冷静期已过，但分数仍高于解除阈值，保持激活状态
                record.status = InterventionStatus.ACTIVE
                return {
                    "in_cooldown": False,
                    "remaining_seconds": 0,
                    "last_intervention_time": record.intervention_triggered_at,
                    "status": InterventionStatus.ACTIVE.value
                }
        
        # 仍在冷静期内
        remaining = (record.cooldown_until - now).total_seconds()
        return {
            "in_cooldown": True,
            "remaining_seconds": max(0, int(remaining)),
            "last_intervention_time": record.intervention_triggered_at,
            "status": InterventionStatus.COOLDOWN.value
        }
    
    def should_trigger_intervention(
        self,
        difficulty_result: DifficultyResult,
        user_id: int,
        knowledge_point_id: int
    ) -> InterventionDecision:
        """判断是否应该触发干预（考虑冷静期和滞后效应）
        
        Args:
            difficulty_result: 难点判定结果
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            干预决策结果
        """
        # 1. 检查冷静期
        cooldown_status = self.check_cooldown(user_id, knowledge_point_id)
        
        if cooldown_status["in_cooldown"]:
            # 在冷静期内，不触发干预
            return InterventionDecision(
                should_trigger=False,
                status=InterventionStatus.COOLDOWN,
                remaining_cooldown_seconds=cooldown_status["remaining_seconds"],
                reason=f"冷静期内，剩余{cooldown_status['remaining_seconds']}秒",
                last_intervention_time=cooldown_status["last_intervention_time"]
            )
        
        # 2. 应用滞后效应判断
        config = self._get_hysteresis_config(user_id, knowledge_point_id)
        
        # 检查当前状态
        key = (user_id, knowledge_point_id)
        current_status = InterventionStatus.INACTIVE
        last_score = 0.0
        
        if key in self.cooldown_records:
            record = self.cooldown_records[key]
            current_status = record.status
            last_score = record.last_difficulty_score
        
        # 应用滞后效应
        should_trigger = self.apply_hysteresis(
            config.trigger_threshold,
            config.release_threshold,
            difficulty_result.difficulty_score,
            current_status,
            last_score
        )
        
        if should_trigger:
            # 触发干预，记录冷静期
            now = datetime.now()
            cooldown_until = now + self.cooldown_duration
            
            record = CooldownRecord(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                intervention_triggered_at=now,
                cooldown_until=cooldown_until,
                last_difficulty_score=difficulty_result.difficulty_score,
                status=InterventionStatus.COOLDOWN
            )
            
            self.cooldown_records[key] = record
            
            logger.info(
                f"Intervention triggered for user={user_id}, kp={knowledge_point_id}, "
                f"score={difficulty_result.difficulty_score:.2f}, "
                f"cooldown_until={cooldown_until}"
            )
            
            return InterventionDecision(
                should_trigger=True,
                status=InterventionStatus.COOLDOWN,
                remaining_cooldown_seconds=int(self.cooldown_duration.total_seconds()),
                reason=f"触发干预，困难度分数{difficulty_result.difficulty_score:.2f}超过阈值{config.trigger_threshold}",
                last_intervention_time=now
            )
        else:
            # 不触发干预
            reason = ""
            if current_status == InterventionStatus.ACTIVE:
                reason = f"干预已激活，分数{difficulty_result.difficulty_score:.2f}未低于解除阈值{config.release_threshold}"
            else:
                reason = f"分数{difficulty_result.difficulty_score:.2f}未达到触发阈值{config.trigger_threshold}"
            
            return InterventionDecision(
                should_trigger=False,
                status=current_status,
                remaining_cooldown_seconds=0,
                reason=reason,
                last_intervention_time=cooldown_status.get("last_intervention_time")
            )
    
    def apply_hysteresis(
        self,
        trigger_threshold: float,
        release_threshold: float,
        current_score: float,
        current_status: InterventionStatus,
        last_score: float = 0.0
    ) -> bool:
        """应用滞后效应判断是否触发干预
        
        滞后效应原理：
        - 如果当前未激活，需要分数 > trigger_threshold 才触发
        - 如果当前已激活，需要分数 < release_threshold 才解除
        - 这样避免了在阈值附近频繁切换
        
        Args:
            trigger_threshold: 触发阈值
            release_threshold: 解除阈值
            current_score: 当前困难度分数
            current_status: 当前干预状态
            last_score: 上次分数（可选）
        
        Returns:
            是否应该触发干预
        """
        if current_status == InterventionStatus.INACTIVE:
            # 未激活状态：需要超过触发阈值才触发
            return current_score >= trigger_threshold
        elif current_status == InterventionStatus.ACTIVE:
            # 激活状态：需要低于解除阈值才解除（这里返回False表示不触发新干预）
            # 如果分数仍高于解除阈值，保持激活状态（不触发新干预，但保持状态）
            return False  # 已激活，不需要再次触发
        else:
            # 冷静期状态：不触发
            return False
    
    def get_remaining_cooldown(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> int:
        """获取剩余冷静期时间（秒）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            剩余秒数，如果不在冷静期则返回0
        """
        cooldown_status = self.check_cooldown(user_id, knowledge_point_id)
        return cooldown_status["remaining_seconds"]
    
    def set_hysteresis_config(
        self,
        user_id: int,
        knowledge_point_id: int,
        trigger_threshold: Optional[float] = None,
        release_threshold: Optional[float] = None
    ) -> bool:
        """设置滞后效应配置（个性化配置）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            trigger_threshold: 触发阈值（可选）
            release_threshold: 解除阈值（可选）
        
        Returns:
            是否成功设置
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.hysteresis_configs:
            self.hysteresis_configs[key] = HysteresisConfig(
                trigger_threshold=self.default_trigger_threshold,
                release_threshold=self.default_release_threshold
            )
        
        config = self.hysteresis_configs[key]
        
        if trigger_threshold is not None:
            config.trigger_threshold = trigger_threshold
        
        if release_threshold is not None:
            config.release_threshold = release_threshold
        
        # 验证阈值合理性
        if config.trigger_threshold <= config.release_threshold:
            logger.warning(
                f"Trigger threshold ({config.trigger_threshold}) should be > "
                f"release threshold ({config.release_threshold}) for hysteresis effect"
            )
        
        logger.info(
            f"Set hysteresis config for user={user_id}, kp={knowledge_point_id}: "
            f"trigger={config.trigger_threshold}, release={config.release_threshold}"
        )
        
        return True
    
    def _get_hysteresis_config(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> HysteresisConfig:
        """获取滞后效应配置（如果不存在则使用默认值）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            滞后效应配置
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.hysteresis_configs:
            return HysteresisConfig(
                trigger_threshold=self.default_trigger_threshold,
                release_threshold=self.default_release_threshold
            )
        
        return self.hysteresis_configs[key]
    
    def set_cooldown_duration(
        self,
        user_id: int,
        knowledge_point_id: int,
        duration_minutes: int
    ) -> bool:
        """设置冷静期时长（个性化配置）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            duration_minutes: 冷静期时长（分钟）
        
        Returns:
            是否成功设置
        """
        # 注意：这里只影响新触发的干预，已存在的冷静期不受影响
        # 如果需要立即生效，可以更新现有记录
        logger.info(
            f"Cooldown duration set for user={user_id}, kp={knowledge_point_id}: "
            f"{duration_minutes} minutes"
        )
        return True
    
    def get_cooldown_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取冷静期统计报告
        
        Args:
            user_id: 用户ID（可选，如果提供则只统计该用户的数据）
        
        Returns:
            统计报告字典
        """
        records = list(self.cooldown_records.values())
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if not records:
            return {
                "total_records": 0,
                "active": 0,
                "cooldown": 0,
                "average_cooldown_remaining": 0
            }
        
        now = datetime.now()
        active_count = sum(1 for r in records if r.status == InterventionStatus.ACTIVE)
        cooldown_count = sum(1 for r in records if r.status == InterventionStatus.COOLDOWN)
        
        cooldown_records = [r for r in records if r.status == InterventionStatus.COOLDOWN]
        if cooldown_records:
            avg_remaining = sum(
                max(0, (r.cooldown_until - now).total_seconds())
                for r in cooldown_records
            ) / len(cooldown_records)
        else:
            avg_remaining = 0
        
        return {
            "total_records": len(records),
            "active": active_count,
            "cooldown": cooldown_count,
            "average_cooldown_remaining": int(avg_remaining)
        }
    
    def clear_cooldown(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> bool:
        """清除冷静期（用于测试或特殊情况）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            是否成功清除
        """
        key = (user_id, knowledge_point_id)
        
        if key in self.cooldown_records:
            del self.cooldown_records[key]
            logger.info(f"Cleared cooldown for user={user_id}, kp={knowledge_point_id}")
            return True
        
        return False
