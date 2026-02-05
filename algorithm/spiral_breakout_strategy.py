"""
螺旋路径跳出策略

基于v9.0需求，如果螺旋路径反复失败，自动跳出并升级干预。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BreakoutAction(Enum):
    """跳出动作枚举"""
    UPGRADE_TO_L3 = "upgrade_to_l3"  # 升级到L3干预
    SKIP_KNOWLEDGE_POINT = "skip_kp"  # 跳过该知识点
    REGENERATE_PATH = "regenerate_path"  # 重新生成路径


@dataclass
class SpiralPath:
    """螺旋路径"""
    path_id: int
    user_id: int
    knowledge_point_ids: List[int]  # 知识点ID列表（循环）
    attempt_count: int = 0  # 尝试次数
    failure_count: int = 0  # 失败次数
    success_count: int = 0  # 成功次数
    created_at: datetime = field(default_factory=datetime.now)
    last_attempt_at: Optional[datetime] = None


@dataclass
class BreakoutRecord:
    """跳出记录"""
    user_id: int
    spiral_path_id: int
    breakout_action: BreakoutAction
    failure_count: int
    attempt_count: int
    reason: str
    skipped_knowledge_points: List[int]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BreakoutDecision:
    """跳出决策结果"""
    should_breakout: bool  # 是否应该跳出
    breakout_action: Optional[BreakoutAction]  # 跳出动作
    reason: str  # 原因
    failure_count: int  # 失败次数
    attempt_count: int  # 尝试次数


class SpiralBreakoutStrategy:
    """螺旋路径跳出策略
    
    功能：
    1. 失败计数：记录螺旋路径中的失败次数
    2. 跳出条件：如果三轮后仍失败，或失败次数≥阈值，触发跳出
    3. 跳出动作：跳出螺旋路径，触发L3干预或跳过该知识点
    4. 路径调整：跳出后，重新生成学习路径
    """
    
    # 默认跳出阈值
    DEFAULT_FAILURE_THRESHOLD = 3  # 失败次数阈值
    DEFAULT_ATTEMPT_THRESHOLD = 3  # 尝试次数阈值（三轮）
    
    def __init__(
        self,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        attempt_threshold: int = DEFAULT_ATTEMPT_THRESHOLD
    ):
        """初始化螺旋路径跳出策略
        
        Args:
            failure_threshold: 失败次数阈值（默认3次）
            attempt_threshold: 尝试次数阈值（默认3轮）
        """
        self.failure_threshold = failure_threshold
        self.attempt_threshold = attempt_threshold
        
        # 存储螺旋路径
        self.spiral_paths: Dict[int, SpiralPath] = {}  # key: path_id
        
        # 存储跳出记录
        self.breakout_records: List[BreakoutRecord] = []
        
        logger.info(
            f"SpiralBreakoutStrategy initialized with "
            f"failure_threshold={failure_threshold}, "
            f"attempt_threshold={attempt_threshold}"
        )
    
    def check_breakout_condition(
        self,
        spiral_path_id: int,
        failure_count: Optional[int] = None
    ) -> BreakoutDecision:
        """检查跳出条件
        
        Args:
            spiral_path_id: 螺旋路径ID
            failure_count: 失败次数（可选，如果不提供则从路径中获取）
        
        Returns:
            跳出决策结果
        """
        if spiral_path_id not in self.spiral_paths:
            return BreakoutDecision(
                should_breakout=False,
                breakout_action=None,
                reason="螺旋路径不存在",
                failure_count=0,
                attempt_count=0
            )
        
        path = self.spiral_paths[spiral_path_id]
        
        # 获取失败次数和尝试次数
        if failure_count is None:
            failure_count = path.failure_count
        
        attempt_count = path.attempt_count
        
        # 检查跳出条件
        should_breakout = False
        breakout_action = None
        reason = ""
        
        # 条件1：失败次数≥阈值
        if failure_count >= self.failure_threshold:
            should_breakout = True
            breakout_action = BreakoutAction.UPGRADE_TO_L3
            reason = f"失败次数({failure_count})达到阈值({self.failure_threshold})，升级到L3干预"
        
        # 条件2：尝试次数≥阈值且仍有失败
        elif attempt_count >= self.attempt_threshold and failure_count > 0:
            should_breakout = True
            # 如果失败率>50%，升级到L3；否则跳过知识点
            failure_rate = failure_count / attempt_count if attempt_count > 0 else 0.0
            if failure_rate > 0.5:
                breakout_action = BreakoutAction.UPGRADE_TO_L3
                reason = f"三轮后失败率({failure_rate:.1%})>50%，升级到L3干预"
            else:
                breakout_action = BreakoutAction.SKIP_KNOWLEDGE_POINT
                reason = f"三轮后仍有失败，跳过该知识点"
        
        if not should_breakout:
            reason = f"未达到跳出条件（失败={failure_count}/{self.failure_threshold}，尝试={attempt_count}/{self.attempt_threshold}）"
        
        decision = BreakoutDecision(
            should_breakout=should_breakout,
            breakout_action=breakout_action,
            reason=reason,
            failure_count=failure_count,
            attempt_count=attempt_count
        )
        
        if should_breakout:
            logger.warning(
                f"Breakout condition met for path={spiral_path_id}: {reason}"
            )
        
        return decision
    
    def execute_breakout(
        self,
        user_id: int,
        spiral_path_id: int,
        action: BreakoutAction,
        skipped_knowledge_points: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """执行跳出动作
        
        Args:
            user_id: 用户ID
            spiral_path_id: 螺旋路径ID
            action: 跳出动作
            skipped_knowledge_points: 跳过的知识点列表（可选）
        
        Returns:
            跳出执行结果字典
        """
        if spiral_path_id not in self.spiral_paths:
            return {
                "success": False,
                "message": "螺旋路径不存在"
            }
        
        path = self.spiral_paths[spiral_path_id]
        
        if skipped_knowledge_points is None:
            skipped_knowledge_points = path.knowledge_point_ids.copy()
        
        # 记录跳出
        record = BreakoutRecord(
            user_id=user_id,
            spiral_path_id=spiral_path_id,
            breakout_action=action,
            failure_count=path.failure_count,
            attempt_count=path.attempt_count,
            reason=f"执行跳出动作：{action.value}",
            skipped_knowledge_points=skipped_knowledge_points
        )
        
        self.breakout_records.append(record)
        
        # 根据动作执行相应操作
        result = {
            "success": True,
            "action": action.value,
            "spiral_path_id": spiral_path_id,
            "skipped_knowledge_points": skipped_knowledge_points,
            "failure_count": path.failure_count,
            "attempt_count": path.attempt_count
        }
        
        if action == BreakoutAction.UPGRADE_TO_L3:
            result["message"] = "已升级到L3干预，推送最高级别补偿资源"
            result["intervention_level"] = "L3"
        elif action == BreakoutAction.SKIP_KNOWLEDGE_POINT:
            result["message"] = f"已跳过知识点：{skipped_knowledge_points}"
            result["intervention_level"] = "skip"
        elif action == BreakoutAction.REGENERATE_PATH:
            result["message"] = "将重新生成学习路径"
            result["intervention_level"] = "regenerate"
        
        logger.info(
            f"Executed breakout for user={user_id}, path={spiral_path_id}: "
            f"action={action.value}, skipped_kps={len(skipped_knowledge_points)}"
        )
        
        return result
    
    def regenerate_path_after_breakout(
        self,
        user_id: int,
        skipped_knowledge_points: List[int]
    ) -> List[Dict[str, Any]]:
        """跳出后重新生成路径
        
        Args:
            user_id: 用户ID
            skipped_knowledge_points: 跳过的知识点列表
        
        Returns:
            重新生成的学习路径列表
        """
        # 这里应该调用学习路径生成器，重新生成路径
        # 简化处理，返回一个空路径列表，实际应该调用 learning_path_generator
        
        new_path = [
            {
                "knowledge_point_id": kp_id,
                "status": "skipped",
                "reason": "螺旋路径跳出后跳过"
            }
            for kp_id in skipped_knowledge_points
        ]
        
        logger.info(
            f"Regenerated path for user={user_id} after breakout, "
            f"skipped {len(skipped_knowledge_points)} knowledge points"
        )
        
        return new_path
    
    def record_breakout_history(
        self,
        user_id: int,
        spiral_path_id: int,
        reason: str
    ) -> bool:
        """记录跳出历史
        
        Args:
            user_id: 用户ID
            spiral_path_id: 螺旋路径ID
            reason: 跳出原因
        
        Returns:
            是否成功记录
        """
        if spiral_path_id not in self.spiral_paths:
            return False
        
        path = self.spiral_paths[spiral_path_id]
        
        record = BreakoutRecord(
            user_id=user_id,
            spiral_path_id=spiral_path_id,
            breakout_action=BreakoutAction.REGENERATE_PATH,  # 默认动作
            failure_count=path.failure_count,
            attempt_count=path.attempt_count,
            reason=reason,
            skipped_knowledge_points=path.knowledge_point_ids.copy()
        )
        
        self.breakout_records.append(record)
        
        logger.info(
            f"Recorded breakout history for user={user_id}, path={spiral_path_id}: {reason}"
        )
        
        return True
    
    def record_spiral_path_attempt(
        self,
        spiral_path_id: int,
        user_id: int,
        knowledge_point_ids: List[int],
        success: bool
    ) -> bool:
        """记录螺旋路径尝试
        
        Args:
            spiral_path_id: 螺旋路径ID
            user_id: 用户ID
            knowledge_point_ids: 知识点ID列表
            success: 是否成功
        
        Returns:
            是否成功记录
        """
        if spiral_path_id not in self.spiral_paths:
            path = SpiralPath(
                path_id=spiral_path_id,
                user_id=user_id,
                knowledge_point_ids=knowledge_point_ids
            )
            self.spiral_paths[spiral_path_id] = path
        else:
            path = self.spiral_paths[spiral_path_id]
        
        path.attempt_count += 1
        path.last_attempt_at = datetime.now()
        
        if success:
            path.success_count += 1
        else:
            path.failure_count += 1
        
        logger.debug(
            f"Recorded spiral path attempt: path={spiral_path_id}, "
            f"success={success}, attempts={path.attempt_count}, "
            f"failures={path.failure_count}"
        )
        
        return True
    
    def get_spiral_path_status(
        self,
        spiral_path_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取螺旋路径状态
        
        Args:
            spiral_path_id: 螺旋路径ID
        
        Returns:
            路径状态字典，如果不存在则返回None
        """
        if spiral_path_id not in self.spiral_paths:
            return None
        
        path = self.spiral_paths[spiral_path_id]
        
        # 检查跳出条件
        decision = self.check_breakout_condition(spiral_path_id)
        
        return {
            "path_id": spiral_path_id,
            "user_id": path.user_id,
            "knowledge_point_ids": path.knowledge_point_ids,
            "attempt_count": path.attempt_count,
            "failure_count": path.failure_count,
            "success_count": path.success_count,
            "success_rate": (
                path.success_count / path.attempt_count
                if path.attempt_count > 0 else 0.0
            ),
            "should_breakout": decision.should_breakout,
            "breakout_action": decision.breakout_action.value if decision.breakout_action else None,
            "breakout_reason": decision.reason
        }
    
    def get_breakout_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取跳出统计报告
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        records = self.breakout_records.copy()
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if not records:
            return {
                "total_breakouts": 0,
                "by_action": {},
                "average_failure_count": 0.0,
                "average_attempt_count": 0.0
            }
        
        # 按动作统计
        by_action = {}
        for action in BreakoutAction:
            count = sum(1 for r in records if r.breakout_action == action)
            by_action[action.value] = count
        
        avg_failure = sum(r.failure_count for r in records) / len(records)
        avg_attempt = sum(r.attempt_count for r in records) / len(records)
        
        return {
            "total_breakouts": len(records),
            "by_action": by_action,
            "average_failure_count": avg_failure,
            "average_attempt_count": avg_attempt,
            "total_skipped_kps": sum(
                len(r.skipped_knowledge_points) for r in records
            )
        }
    
    def set_breakout_thresholds(
        self,
        failure_threshold: Optional[int] = None,
        attempt_threshold: Optional[int] = None
    ) -> bool:
        """设置跳出阈值
        
        Args:
            failure_threshold: 失败次数阈值（可选）
            attempt_threshold: 尝试次数阈值（可选）
        
        Returns:
            是否成功设置
        """
        if failure_threshold is not None:
            if failure_threshold <= 0:
                logger.error(f"Invalid failure_threshold {failure_threshold}, must be > 0")
                return False
            self.failure_threshold = failure_threshold
        
        if attempt_threshold is not None:
            if attempt_threshold <= 0:
                logger.error(f"Invalid attempt_threshold {attempt_threshold}, must be > 0")
                return False
            self.attempt_threshold = attempt_threshold
        
        logger.info(
            f"Set breakout thresholds: failure={self.failure_threshold}, "
            f"attempt={self.attempt_threshold}"
        )
        
        return True
