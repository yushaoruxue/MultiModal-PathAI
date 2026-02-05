"""
教师一键禁用AI自动生成机制

基于v9.0需求，允许教师锁定知识点，进入专家标注模式。
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LockStatus(Enum):
    """锁定状态枚举"""
    LOCKED = "locked"  # 已锁定（AI禁用）
    UNLOCKED = "unlocked"  # 未锁定（AI启用）
    EXPERT_MODE = "expert_mode"  # 专家标注模式


@dataclass
class LockRecord:
    """锁定记录"""
    video_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None
    teacher_id: int = 0
    status: LockStatus = LockStatus.LOCKED
    locked_at: datetime = field(default_factory=datetime.now)
    unlocked_at: Optional[datetime] = None
    reason: str = ""  # 锁定原因


@dataclass
class LockHistory:
    """锁定历史"""
    video_id: Optional[int]
    knowledge_point_id: Optional[int]
    teacher_id: int
    action: str  # "lock" or "unlock"
    timestamp: datetime
    reason: str


class AIGenerationLockManager:
    """AI自动生成锁定管理器
    
    功能：
    1. 教师可以一键禁用AI自动生成（锁定知识点）
    2. 锁定后，系统不再自动生成知识点标注
    3. 进入专家标注模式，教师手动标注
    4. 支持批量锁定/解锁
    """
    
    def __init__(self):
        """初始化AI生成锁定管理器"""
        # 存储视频级别的锁定状态
        self.video_locks: Dict[int, LockRecord] = {}  # key: video_id
        
        # 存储知识点级别的锁定状态
        self.knowledge_point_locks: Dict[int, LockRecord] = {}  # key: knowledge_point_id
        
        # 存储锁定历史
        self.lock_history: List[LockHistory] = []
        
        logger.info("AIGenerationLockManager initialized")
    
    def lock_ai_generation(
        self,
        teacher_id: int,
        video_id: Optional[int] = None,
        knowledge_point_ids: Optional[List[int]] = None,
        reason: str = ""
    ) -> bool:
        """锁定AI自动生成
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID（可选，如果提供则锁定整个视频）
            knowledge_point_ids: 知识点ID列表（可选，如果提供则锁定指定知识点）
            reason: 锁定原因（可选）
        
        Returns:
            是否成功锁定
        """
        if video_id is None and not knowledge_point_ids:
            logger.warning("Either video_id or knowledge_point_ids must be provided")
            return False
        
        success = True
        
        # 锁定视频级别
        if video_id is not None:
            record = LockRecord(
                video_id=video_id,
                teacher_id=teacher_id,
                status=LockStatus.LOCKED,
                reason=reason or f"教师{teacher_id}禁用AI自动生成"
            )
            self.video_locks[video_id] = record
            
            # 记录历史
            history = LockHistory(
                video_id=video_id,
                knowledge_point_id=None,
                teacher_id=teacher_id,
                action="lock",
                timestamp=datetime.now(),
                reason=reason
            )
            self.lock_history.append(history)
            
            logger.info(
                f"Locked AI generation for video={video_id}, teacher={teacher_id}"
            )
        
        # 锁定知识点级别
        if knowledge_point_ids:
            for kp_id in knowledge_point_ids:
                record = LockRecord(
                    knowledge_point_id=kp_id,
                    teacher_id=teacher_id,
                    status=LockStatus.LOCKED,
                    reason=reason or f"教师{teacher_id}禁用知识点{kp_id}的AI自动生成"
                )
                self.knowledge_point_locks[kp_id] = record
                
                # 记录历史
                history = LockHistory(
                    video_id=video_id,
                    knowledge_point_id=kp_id,
                    teacher_id=teacher_id,
                    action="lock",
                    timestamp=datetime.now(),
                    reason=reason
                )
                self.lock_history.append(history)
            
            logger.info(
                f"Locked AI generation for {len(knowledge_point_ids)} knowledge points, "
                f"teacher={teacher_id}"
            )
        
        return success
    
    def unlock_ai_generation(
        self,
        teacher_id: int,
        video_id: Optional[int] = None,
        knowledge_point_ids: Optional[List[int]] = None,
        reason: str = ""
    ) -> bool:
        """解锁AI自动生成
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID（可选）
            knowledge_point_ids: 知识点ID列表（可选）
            reason: 解锁原因（可选）
        
        Returns:
            是否成功解锁
        """
        if video_id is None and not knowledge_point_ids:
            logger.warning("Either video_id or knowledge_point_ids must be provided")
            return False
        
        success = True
        
        # 解锁视频级别
        if video_id is not None:
            if video_id in self.video_locks:
                record = self.video_locks[video_id]
                if record.teacher_id == teacher_id:
                    record.status = LockStatus.UNLOCKED
                    record.unlocked_at = datetime.now()
                    
                    # 记录历史
                    history = LockHistory(
                        video_id=video_id,
                        knowledge_point_id=None,
                        teacher_id=teacher_id,
                        action="unlock",
                        timestamp=datetime.now(),
                        reason=reason
                    )
                    self.lock_history.append(history)
                    
                    logger.info(
                        f"Unlocked AI generation for video={video_id}, teacher={teacher_id}"
                    )
                else:
                    logger.warning(
                        f"Teacher {teacher_id} is not the owner of lock for video={video_id}"
                    )
                    success = False
            else:
                logger.warning(f"No lock found for video={video_id}")
                success = False
        
        # 解锁知识点级别
        if knowledge_point_ids:
            for kp_id in knowledge_point_ids:
                if kp_id in self.knowledge_point_locks:
                    record = self.knowledge_point_locks[kp_id]
                    if record.teacher_id == teacher_id:
                        record.status = LockStatus.UNLOCKED
                        record.unlocked_at = datetime.now()
                        
                        # 记录历史
                        history = LockHistory(
                            video_id=video_id,
                            knowledge_point_id=kp_id,
                            teacher_id=teacher_id,
                            action="unlock",
                            timestamp=datetime.now(),
                            reason=reason
                        )
                        self.lock_history.append(history)
                    else:
                        logger.warning(
                            f"Teacher {teacher_id} is not the owner of lock for kp={kp_id}"
                        )
                        success = False
                else:
                    logger.warning(f"No lock found for knowledge_point={kp_id}")
                    success = False
            
            logger.info(
                f"Unlocked AI generation for {len(knowledge_point_ids)} knowledge points, "
                f"teacher={teacher_id}"
            )
        
        return success
    
    def is_locked(
        self,
        video_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None
    ) -> bool:
        """检查是否已锁定
        
        Args:
            video_id: 视频ID（可选）
            knowledge_point_id: 知识点ID（可选）
        
        Returns:
            是否已锁定
        """
        # 检查视频级别锁定
        if video_id is not None:
            if video_id in self.video_locks:
                record = self.video_locks[video_id]
                if record.status == LockStatus.LOCKED:
                    return True
        
        # 检查知识点级别锁定
        if knowledge_point_id is not None:
            if knowledge_point_id in self.knowledge_point_locks:
                record = self.knowledge_point_locks[knowledge_point_id]
                if record.status == LockStatus.LOCKED:
                    return True
        
        return False
    
    def get_lock_status(
        self,
        video_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None
    ) -> Optional[LockStatus]:
        """获取锁定状态
        
        Args:
            video_id: 视频ID（可选）
            knowledge_point_id: 知识点ID（可选）
        
        Returns:
            锁定状态，如果未锁定则返回None
        """
        # 检查视频级别锁定
        if video_id is not None:
            if video_id in self.video_locks:
                record = self.video_locks[video_id]
                return record.status
        
        # 检查知识点级别锁定
        if knowledge_point_id is not None:
            if knowledge_point_id in self.knowledge_point_locks:
                record = self.knowledge_point_locks[knowledge_point_id]
                return record.status
        
        return None
    
    def get_lock_history(
        self,
        video_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[LockHistory]:
        """获取锁定历史
        
        Args:
            video_id: 视频ID（可选）
            knowledge_point_id: 知识点ID（可选）
            teacher_id: 教师ID（可选）
            limit: 限制返回数量（可选）
        
        Returns:
            锁定历史列表（按时间倒序）
        """
        history = self.lock_history.copy()
        
        # 过滤
        if video_id is not None:
            history = [h for h in history if h.video_id == video_id]
        
        if knowledge_point_id is not None:
            history = [h for h in history if h.knowledge_point_id == knowledge_point_id]
        
        if teacher_id is not None:
            history = [h for h in history if h.teacher_id == teacher_id]
        
        # 按时间倒序排序
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 限制数量
        if limit is not None:
            history = history[:limit]
        
        return history
    
    def enter_expert_mode(
        self,
        teacher_id: int,
        video_id: Optional[int] = None,
        knowledge_point_ids: Optional[List[int]] = None
    ) -> bool:
        """进入专家标注模式
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID（可选）
            knowledge_point_ids: 知识点ID列表（可选）
        
        Returns:
            是否成功进入专家模式
        """
        # 专家模式实际上就是锁定AI生成
        return self.lock_ai_generation(
            teacher_id, video_id, knowledge_point_ids,
            reason="进入专家标注模式"
        )
    
    def exit_expert_mode(
        self,
        teacher_id: int,
        video_id: Optional[int] = None,
        knowledge_point_ids: Optional[List[int]] = None
    ) -> bool:
        """退出专家标注模式
        
        Args:
            teacher_id: 教师ID
            video_id: 视频ID（可选）
            knowledge_point_ids: 知识点ID列表（可选）
        
        Returns:
            是否成功退出专家模式
        """
        return self.unlock_ai_generation(
            teacher_id, video_id, knowledge_point_ids,
            reason="退出专家标注模式"
        )
    
    def batch_lock(
        self,
        teacher_id: int,
        video_ids: Optional[List[int]] = None,
        knowledge_point_ids: Optional[List[int]] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """批量锁定
        
        Args:
            teacher_id: 教师ID
            video_ids: 视频ID列表（可选）
            knowledge_point_ids: 知识点ID列表（可选）
            reason: 锁定原因（可选）
        
        Returns:
            批量锁定结果字典
        """
        results = {
            "videos": {},
            "knowledge_points": {},
            "total_locked": 0
        }
        
        if video_ids:
            for video_id in video_ids:
                success = self.lock_ai_generation(
                    teacher_id, video_id=video_id, reason=reason
                )
                results["videos"][video_id] = success
                if success:
                    results["total_locked"] += 1
        
        if knowledge_point_ids:
            for kp_id in knowledge_point_ids:
                success = self.lock_ai_generation(
                    teacher_id, knowledge_point_ids=[kp_id], reason=reason
                )
                results["knowledge_points"][kp_id] = success
                if success:
                    results["total_locked"] += 1
        
        logger.info(
            f"Batch lock completed: teacher={teacher_id}, "
            f"total_locked={results['total_locked']}"
        )
        
        return results
    
    def batch_unlock(
        self,
        teacher_id: int,
        video_ids: Optional[List[int]] = None,
        knowledge_point_ids: Optional[List[int]] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """批量解锁
        
        Args:
            teacher_id: 教师ID
            video_ids: 视频ID列表（可选）
            knowledge_point_ids: 知识点ID列表（可选）
            reason: 解锁原因（可选）
        
        Returns:
            批量解锁结果字典
        """
        results = {
            "videos": {},
            "knowledge_points": {},
            "total_unlocked": 0
        }
        
        if video_ids:
            for video_id in video_ids:
                success = self.unlock_ai_generation(
                    teacher_id, video_id=video_id, reason=reason
                )
                results["videos"][video_id] = success
                if success:
                    results["total_unlocked"] += 1
        
        if knowledge_point_ids:
            for kp_id in knowledge_point_ids:
                success = self.unlock_ai_generation(
                    teacher_id, knowledge_point_ids=[kp_id], reason=reason
                )
                results["knowledge_points"][kp_id] = success
                if success:
                    results["total_unlocked"] += 1
        
        logger.info(
            f"Batch unlock completed: teacher={teacher_id}, "
            f"total_unlocked={results['total_unlocked']}"
        )
        
        return results
    
    def get_lock_statistics(
        self,
        teacher_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取锁定统计报告
        
        Args:
            teacher_id: 教师ID（可选）
        
        Returns:
            统计报告字典
        """
        video_locks = list(self.video_locks.values())
        kp_locks = list(self.knowledge_point_locks.values())
        
        if teacher_id is not None:
            video_locks = [l for l in video_locks if l.teacher_id == teacher_id]
            kp_locks = [l for l in kp_locks if l.teacher_id == teacher_id]
        
        locked_videos = sum(1 for l in video_locks if l.status == LockStatus.LOCKED)
        locked_kps = sum(1 for l in kp_locks if l.status == LockStatus.LOCKED)
        
        return {
            "total_video_locks": len(video_locks),
            "locked_videos": locked_videos,
            "total_knowledge_point_locks": len(kp_locks),
            "locked_knowledge_points": locked_kps,
            "total_locked": locked_videos + locked_kps
        }
