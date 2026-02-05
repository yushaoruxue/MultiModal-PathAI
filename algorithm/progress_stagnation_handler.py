"""
进度停滞自动升级机制

基于v7.0需求，检测学习进度停滞并自动触发L3干预。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterventionLevel(Enum):
    """干预等级枚举"""
    L1 = "L1"  # 基础干预：知识卡片+诊断练习
    L2 = "L2"  # 中级干预：知识卡片+诊断练习+例题讲解
    L3 = "L3"  # 高级干预：知识卡片+练习+视频+1对1答疑入口


@dataclass
class LearningProgress:
    """学习进度数据"""
    user_id: int
    knowledge_point_id: int
    current_knowledge_point_id: int
    start_time: datetime  # 开始学习当前知识点的时间
    last_activity_time: datetime  # 最后活动时间
    total_study_time: float  # 总学习时长（分钟）
    intervention_level: InterventionLevel = InterventionLevel.L1
    attempt_count: int = 0  # 尝试次数


@dataclass
class StagnationDetection:
    """停滞检测结果"""
    is_stagnant: bool
    duration_minutes: float  # 停滞时长（分钟）
    current_knowledge_point_id: int
    threshold_minutes: float
    reason: str


@dataclass
class L3InterventionConfig:
    """L3干预配置"""
    knowledge_card: bool = True  # 知识卡片
    exercise: bool = True  # 诊断练习
    video: bool = True  # 微视频
    one_on_one_tutoring: bool = True  # 1对1答疑入口
    priority: int = 5  # 优先级（1-5，5最高）


@dataclass
class StagnationRecord:
    """停滞记录"""
    user_id: int
    knowledge_point_id: int
    start_time: datetime
    duration_minutes: float
    intervention_level_before: InterventionLevel
    intervention_level_after: InterventionLevel
    l3_triggered: bool
    teacher_notified: bool
    created_at: datetime = field(default_factory=datetime.now)


class ProgressStagnationHandler:
    """进度停滞自动升级机制
    
    功能：
    1. 检测学习进度停滞（在同一知识点停留超过阈值时间）
    2. 自动从L1/L2升级到L3干预
    3. L3干预：推送最高级别补偿资源
    4. 通知教师
    """
    
    # 默认停滞阈值（分钟）
    DEFAULT_STAGNATION_THRESHOLD = 30.0
    
    def __init__(
        self,
        stagnation_threshold_minutes: float = DEFAULT_STAGNATION_THRESHOLD
    ):
        """初始化进度停滞处理器
        
        Args:
            stagnation_threshold_minutes: 停滞阈值（分钟，默认30分钟）
        """
        self.stagnation_threshold = timedelta(minutes=stagnation_threshold_minutes)
        
        # 存储学习进度
        self.learning_progress: Dict[tuple, LearningProgress] = {}  # key: (user_id, kp_id)
        
        # 存储停滞记录
        self.stagnation_records: List[StagnationRecord] = []
        
        logger.info(
            f"ProgressStagnationHandler initialized with "
            f"threshold={stagnation_threshold_minutes} minutes"
        )
    
    def detect_stagnation(
        self,
        user_id: int,
        knowledge_point_id: int,
        time_threshold_minutes: Optional[float] = None
    ) -> StagnationDetection:
        """检测学习进度停滞
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            time_threshold_minutes: 时间阈值（分钟，可选，默认使用初始化时的阈值）
        
        Returns:
            停滞检测结果
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.learning_progress:
            # 没有学习进度记录，不算停滞
            return StagnationDetection(
                is_stagnant=False,
                duration_minutes=0.0,
                current_knowledge_point_id=knowledge_point_id,
                threshold_minutes=time_threshold_minutes or self.stagnation_threshold.total_seconds() / 60,
                reason="无学习进度记录"
            )
        
        progress = self.learning_progress[key]
        
        # 检查是否还在学习同一个知识点
        if progress.current_knowledge_point_id != knowledge_point_id:
            return StagnationDetection(
                is_stagnant=False,
                duration_minutes=0.0,
                current_knowledge_point_id=progress.current_knowledge_point_id,
                threshold_minutes=time_threshold_minutes or self.stagnation_threshold.total_seconds() / 60,
                reason=f"已切换到其他知识点（当前：{progress.current_knowledge_point_id}）"
            )
        
        # 计算停滞时长（从开始学习当前知识点到现在）
        now = datetime.now()
        threshold = timedelta(
            minutes=time_threshold_minutes
        ) if time_threshold_minutes else self.stagnation_threshold
        
        duration = (now - progress.start_time).total_seconds() / 60.0  # 转换为分钟
        
        is_stagnant = duration >= threshold.total_seconds() / 60.0
        
        reason = ""
        if is_stagnant:
            reason = (
                f"在同一知识点停留{duration:.1f}分钟，超过阈值{threshold.total_seconds() / 60:.1f}分钟"
            )
        else:
            reason = (
                f"停留时长{duration:.1f}分钟，未超过阈值{threshold.total_seconds() / 60:.1f}分钟"
            )
        
        detection = StagnationDetection(
            is_stagnant=is_stagnant,
            duration_minutes=duration,
            current_knowledge_point_id=knowledge_point_id,
            threshold_minutes=threshold.total_seconds() / 60,
            reason=reason
        )
        
        if is_stagnant:
            logger.warning(
                f"Stagnation detected for user={user_id}, kp={knowledge_point_id}: "
                f"duration={duration:.1f} minutes"
            )
        
        return detection
    
    def auto_upgrade_to_l3(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> bool:
        """自动升级到L3干预
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            是否成功升级
        """
        key = (user_id, knowledge_point_id)
        
        if key not in self.learning_progress:
            logger.warning(
                f"No learning progress found for user={user_id}, kp={knowledge_point_id}"
            )
            return False
        
        progress = self.learning_progress[key]
        
        # 如果已经是L3，不需要升级
        if progress.intervention_level == InterventionLevel.L3:
            logger.info(
                f"Already at L3 intervention for user={user_id}, kp={knowledge_point_id}"
            )
            return False
        
        # 记录升级前的干预等级
        old_level = progress.intervention_level
        
        # 升级到L3
        progress.intervention_level = InterventionLevel.L3
        progress.attempt_count += 1
        
        logger.info(
            f"Auto upgraded to L3 for user={user_id}, kp={knowledge_point_id}: "
            f"{old_level.value} -> {InterventionLevel.L3.value}"
        )
        
        return True
    
    def trigger_l3_intervention(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> Dict[str, Any]:
        """触发L3干预
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            L3干预配置字典
        """
        # 先升级到L3
        self.auto_upgrade_to_l3(user_id, knowledge_point_id)
        
        # 创建L3干预配置
        config = L3InterventionConfig()
        
        intervention_config = {
            "user_id": user_id,
            "knowledge_point_id": knowledge_point_id,
            "intervention_level": InterventionLevel.L3.value,
            "resources": {
                "knowledge_card": config.knowledge_card,
                "exercise": config.exercise,
                "video": config.video,
                "one_on_one_tutoring": config.one_on_one_tutoring
            },
            "priority": config.priority,
            "triggered_at": datetime.now().isoformat(),
            "message": "检测到学习进度停滞，已自动升级到L3干预，推送最高级别补偿资源"
        }
        
        logger.info(
            f"L3 intervention triggered for user={user_id}, kp={knowledge_point_id}"
        )
        
        return intervention_config
    
    def notify_teacher(
        self,
        user_id: int,
        knowledge_point_id: int,
        stagnation_info: StagnationDetection
    ) -> bool:
        """通知教师
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            stagnation_info: 停滞检测信息
        
        Returns:
            是否成功通知
        """
        # 这里应该调用通知服务，实际实现中需要对接通知系统
        # 现在只是记录日志
        
        notification = {
            "type": "stagnation_alert",
            "user_id": user_id,
            "knowledge_point_id": knowledge_point_id,
            "stagnation_duration": stagnation_info.duration_minutes,
            "intervention_level": "L3",
            "timestamp": datetime.now().isoformat(),
            "message": (
                f"学生{user_id}在知识点{knowledge_point_id}停留"
                f"{stagnation_info.duration_minutes:.1f}分钟，已自动触发L3干预"
            )
        }
        
        logger.info(
            f"Teacher notification sent: user={user_id}, kp={knowledge_point_id}, "
            f"duration={stagnation_info.duration_minutes:.1f} minutes"
        )
        
        # 在实际实现中，这里应该：
        # 1. 调用通知服务API
        # 2. 发送邮件或站内消息
        # 3. 记录通知历史
        
        return True
    
    def update_learning_progress(
        self,
        user_id: int,
        knowledge_point_id: int,
        current_knowledge_point_id: int,
        last_activity_time: Optional[datetime] = None
    ) -> bool:
        """更新学习进度
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID（用于标识记录）
            current_knowledge_point_id: 当前学习的知识点ID
            last_activity_time: 最后活动时间（可选，默认使用当前时间）
        
        Returns:
            是否成功更新
        """
        key = (user_id, knowledge_point_id)
        now = datetime.now()
        
        if key not in self.learning_progress:
            # 创建新的学习进度记录
            progress = LearningProgress(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                current_knowledge_point_id=current_knowledge_point_id,
                start_time=now,
                last_activity_time=last_activity_time or now,
                total_study_time=0.0
            )
            self.learning_progress[key] = progress
        else:
            # 更新现有记录
            progress = self.learning_progress[key]
            
            # 如果切换到新知识点，重置开始时间
            if progress.current_knowledge_point_id != current_knowledge_point_id:
                progress.current_knowledge_point_id = current_knowledge_point_id
                progress.start_time = now
                progress.last_activity_time = now
                # 重置干预等级（新知识点从L1开始）
                progress.intervention_level = InterventionLevel.L1
                progress.attempt_count = 0
            else:
                # 更新最后活动时间
                progress.last_activity_time = last_activity_time or now
                # 更新总学习时长
                progress.total_study_time = (
                    (progress.last_activity_time - progress.start_time).total_seconds() / 60.0
                )
        
        return True
    
    def handle_stagnation(
        self,
        user_id: int,
        knowledge_point_id: int,
        time_threshold_minutes: Optional[float] = None
    ) -> Dict[str, Any]:
        """处理停滞（检测+升级+通知）
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            time_threshold_minutes: 时间阈值（分钟，可选）
        
        Returns:
            处理结果字典
        """
        # 1. 检测停滞
        detection = self.detect_stagnation(
            user_id, knowledge_point_id, time_threshold_minutes
        )
        
        if not detection.is_stagnant:
            return {
                "is_stagnant": False,
                "detection": detection,
                "action_taken": "none"
            }
        
        # 2. 触发L3干预
        intervention_config = self.trigger_l3_intervention(user_id, knowledge_point_id)
        
        # 3. 通知教师
        teacher_notified = self.notify_teacher(user_id, knowledge_point_id, detection)
        
        # 4. 记录停滞
        key = (user_id, knowledge_point_id)
        progress = self.learning_progress.get(key)
        
        record = StagnationRecord(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            start_time=progress.start_time if progress else datetime.now(),
            duration_minutes=detection.duration_minutes,
            intervention_level_before=progress.intervention_level if progress else InterventionLevel.L1,
            intervention_level_after=InterventionLevel.L3,
            l3_triggered=True,
            teacher_notified=teacher_notified
        )
        
        self.stagnation_records.append(record)
        
        result = {
            "is_stagnant": True,
            "detection": {
                "duration_minutes": detection.duration_minutes,
                "threshold_minutes": detection.threshold_minutes,
                "reason": detection.reason
            },
            "intervention_config": intervention_config,
            "teacher_notified": teacher_notified,
            "action_taken": "upgraded_to_l3"
        }
        
        logger.info(
            f"Stagnation handled for user={user_id}, kp={knowledge_point_id}: "
            f"L3 triggered, teacher notified={teacher_notified}"
        )
        
        return result
    
    def get_stagnation_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取停滞统计报告
        
        Args:
            user_id: 用户ID（可选，如果提供则只统计该用户的数据）
        
        Returns:
            统计报告字典
        """
        records = self.stagnation_records.copy()
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if not records:
            return {
                "total_stagnation_events": 0,
                "average_duration": 0.0,
                "l3_triggered_count": 0,
                "teacher_notified_count": 0
            }
        
        avg_duration = sum(r.duration_minutes for r in records) / len(records)
        l3_count = sum(1 for r in records if r.l3_triggered)
        notified_count = sum(1 for r in records if r.teacher_notified)
        
        return {
            "total_stagnation_events": len(records),
            "average_duration": avg_duration,
            "l3_triggered_count": l3_count,
            "teacher_notified_count": notified_count,
            "l3_trigger_rate": l3_count / len(records) if records else 0.0
        }
    
    def set_stagnation_threshold(
        self,
        threshold_minutes: float
    ) -> bool:
        """设置停滞阈值
        
        Args:
            threshold_minutes: 阈值（分钟）
        
        Returns:
            是否成功设置
        """
        if threshold_minutes <= 0:
            logger.error(f"Invalid threshold {threshold_minutes}, must be > 0")
            return False
        
        self.stagnation_threshold = timedelta(minutes=threshold_minutes)
        
        logger.info(f"Stagnation threshold set to {threshold_minutes} minutes")
        
        return True
