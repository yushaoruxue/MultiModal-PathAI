"""
写锁租约机制

基于v10.0需求，解决教师专家标注时的并发冲突问题。
"""

import logging
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LockStatus(Enum):
    """锁状态枚举"""
    ACQUIRED = "acquired"  # 已获取
    EXPIRED = "expired"  # 已过期
    RELEASED = "released"  # 已释放
    ROLLED_BACK = "rolled_back"  # 已回滚


@dataclass
class WriteLock:
    """写锁"""
    lock_token: str  # 锁令牌
    resource_id: str  # 资源ID（视频ID或知识点ID）
    resource_type: str  # 资源类型（video/knowledge_point）
    teacher_id: int  # 教师ID
    acquired_at: datetime  # 获取时间
    expires_at: datetime  # 到期时间
    last_renewed_at: datetime  # 最后续约时间
    status: LockStatus = LockStatus.ACQUIRED  # 锁状态
    edited_data: Optional[Dict[str, Any]] = None  # 编辑的数据（未发布）
    original_data: Optional[Dict[str, Any]] = None  # 原始数据（用于回滚）


@dataclass
class LockAcquisitionResult:
    """锁获取结果"""
    success: bool  # 是否成功
    lock_token: Optional[str] = None  # 锁令牌
    expires_at: Optional[datetime] = None  # 到期时间
    message: str = ""  # 消息


class WriteLockLeaseManager:
    """写锁租约管理器
    
    功能：
    1. 写锁获取：教师编辑前必须获取写锁
    2. 租约时间：30分钟，超时自动释放
    3. 续约机制：心跳续约，延长租约时间
    4. 原子化发布：编辑完成后原子化发布，交还AI托管
    5. 超时回滚：超时未发布，自动回滚到稳定版本
    """
    
    # 默认租约时间（30分钟）
    DEFAULT_LEASE_DURATION = timedelta(minutes=30)
    
    # 续约时间（延长30分钟）
    RENEW_DURATION = timedelta(minutes=30)
    
    def __init__(self, lease_duration: timedelta = DEFAULT_LEASE_DURATION):
        """初始化写锁租约管理器
        
        Args:
            lease_duration: 租约持续时间（默认30分钟）
        """
        self.lease_duration = lease_duration
        
        # 存储锁（key: lock_token）
        self.locks: Dict[str, WriteLock] = {}
        
        # 资源到锁的映射（key: (resource_type, resource_id)）
        self.resource_locks: Dict[tuple, str] = {}
        
        # 线程锁（保护并发访问）
        self._lock = threading.Lock()
        
        # 锁令牌计数器
        self._token_counter = 0
        
        logger.info(
            f"WriteLockLeaseManager initialized with lease_duration={lease_duration}"
        )
    
    def acquire_lock(
        self,
        resource_id: str,
        resource_type: str,
        teacher_id: int,
        original_data: Optional[Dict[str, Any]] = None
    ) -> LockAcquisitionResult:
        """获取写锁
        
        Args:
            resource_id: 资源ID（视频ID或知识点ID）
            resource_type: 资源类型（video/knowledge_point）
            teacher_id: 教师ID
            original_data: 原始数据（用于回滚，可选）
        
        Returns:
            锁获取结果
        """
        with self._lock:
            resource_key = (resource_type, resource_id)
            
            # 检查资源是否已被锁定
            if resource_key in self.resource_locks:
                existing_token = self.resource_locks[resource_key]
                existing_lock = self.locks.get(existing_token)
                
                if existing_lock and existing_lock.status == LockStatus.ACQUIRED:
                    # 检查是否过期
                    if datetime.now() < existing_lock.expires_at:
                        # 如果同一个教师，允许续约
                        if existing_lock.teacher_id == teacher_id:
                            return self.renew_lock(existing_token, teacher_id)
                        else:
                            return LockAcquisitionResult(
                                success=False,
                                message=f"资源已被教师{existing_lock.teacher_id}锁定，到期时间：{existing_lock.expires_at}"
                            )
                    else:
                        # 已过期，清理
                        self._cleanup_expired_lock(existing_token)
            
            # 生成锁令牌
            self._token_counter += 1
            lock_token = f"lock_{resource_type}_{resource_id}_{self._token_counter}_{int(datetime.now().timestamp())}"
            
            # 创建锁
            now = datetime.now()
            lock = WriteLock(
                lock_token=lock_token,
                resource_id=resource_id,
                resource_type=resource_type,
                teacher_id=teacher_id,
                acquired_at=now,
                expires_at=now + self.lease_duration,
                last_renewed_at=now,
                status=LockStatus.ACQUIRED,
                original_data=original_data
            )
            
            # 存储锁
            self.locks[lock_token] = lock
            self.resource_locks[resource_key] = lock_token
            
            logger.info(
                f"Lock acquired: token={lock_token}, resource={resource_type}:{resource_id}, "
                f"teacher={teacher_id}, expires_at={lock.expires_at}"
            )
            
            return LockAcquisitionResult(
                success=True,
                lock_token=lock_token,
                expires_at=lock.expires_at,
                message="锁获取成功"
            )
    
    def renew_lock(
        self,
        lock_token: str,
        teacher_id: int
    ) -> LockAcquisitionResult:
        """续约锁
        
        Args:
            lock_token: 锁令牌
            teacher_id: 教师ID
        
        Returns:
            续约结果
        """
        with self._lock:
            if lock_token not in self.locks:
                return LockAcquisitionResult(
                    success=False,
                    message="锁不存在"
                )
            
            lock = self.locks[lock_token]
            
            # 验证教师ID
            if lock.teacher_id != teacher_id:
                return LockAcquisitionResult(
                    success=False,
                    message="无权续约此锁"
                )
            
            # 检查锁状态
            if lock.status != LockStatus.ACQUIRED:
                return LockAcquisitionResult(
                    success=False,
                    message=f"锁状态为{lock.status.value}，无法续约"
                )
            
            # 检查是否已过期
            if datetime.now() >= lock.expires_at:
                return LockAcquisitionResult(
                    success=False,
                    message="锁已过期，无法续约"
                )
            
            # 续约（延长租约时间）
            now = datetime.now()
            lock.expires_at = now + self.RENEW_DURATION
            lock.last_renewed_at = now
            
            logger.info(
                f"Lock renewed: token={lock_token}, new_expires_at={lock.expires_at}"
            )
            
            return LockAcquisitionResult(
                success=True,
                lock_token=lock_token,
                expires_at=lock.expires_at,
                message="锁续约成功"
            )
    
    def release_lock(
        self,
        lock_token: str,
        rollback: bool = True
    ) -> bool:
        """释放锁
        
        Args:
            lock_token: 锁令牌
            rollback: 是否回滚到原始数据（默认True）
        
        Returns:
            是否成功释放
        """
        with self._lock:
            if lock_token not in self.locks:
                logger.warning(f"Lock not found: {lock_token}")
                return False
            
            lock = self.locks[lock_token]
            
            # 如果回滚，恢复原始数据
            if rollback and lock.edited_data and lock.original_data:
                logger.info(f"Rolling back changes for lock: {lock_token}")
                # 这里应该调用实际的数据回滚逻辑
                # 简化处理，只记录日志
            
            # 更新锁状态
            lock.status = LockStatus.RELEASED if not rollback else LockStatus.ROLLED_BACK
            
            # 清理资源映射
            resource_key = (lock.resource_type, lock.resource_id)
            if resource_key in self.resource_locks:
                del self.resource_locks[resource_key]
            
            logger.info(
                f"Lock released: token={lock_token}, rollback={rollback}"
            )
            
            return True
    
    def atomic_publish(
        self,
        lock_token: str,
        edited_data: Dict[str, Any]
    ) -> bool:
        """原子化发布编辑数据
        
        Args:
            lock_token: 锁令牌
            edited_data: 编辑后的数据
        
        Returns:
            是否成功发布
        """
        with self._lock:
            if lock_token not in self.locks:
                logger.error(f"Lock not found: {lock_token}")
                return False
            
            lock = self.locks[lock_token]
            
            # 检查锁状态
            if lock.status != LockStatus.ACQUIRED:
                logger.error(f"Lock status is {lock.status.value}, cannot publish")
                return False
            
            # 检查是否已过期
            if datetime.now() >= lock.expires_at:
                logger.error(f"Lock expired, cannot publish")
                self._cleanup_expired_lock(lock_token)
                return False
            
            # 保存编辑数据
            lock.edited_data = edited_data
            
            # 原子化发布（这里应该调用实际的数据发布逻辑）
            # 简化处理，只记录日志
            logger.info(
                f"Atomic publish: token={lock_token}, resource={lock.resource_type}:{lock.resource_id}"
            )
            
            # 发布成功后释放锁
            self.release_lock(lock_token, rollback=False)
            
            return True
    
    def check_lock_timeout(self) -> List[Dict[str, Any]]:
        """检查锁超时（定时任务调用）
        
        Returns:
            超时的锁列表
        """
        with self._lock:
            now = datetime.now()
            expired_locks = []
            
            for lock_token, lock in list(self.locks.items()):
                if lock.status == LockStatus.ACQUIRED and now >= lock.expires_at:
                    # 锁已过期
                    expired_locks.append({
                        "lock_token": lock_token,
                        "resource_id": lock.resource_id,
                        "resource_type": lock.resource_type,
                        "teacher_id": lock.teacher_id,
                        "expires_at": lock.expires_at.isoformat(),
                        "acquired_at": lock.acquired_at.isoformat()
                    })
                    
                    # 清理过期锁
                    self._cleanup_expired_lock(lock_token)
            
            if expired_locks:
                logger.warning(f"Found {len(expired_locks)} expired locks")
            
            return expired_locks
    
    def _cleanup_expired_lock(self, lock_token: str) -> None:
        """清理过期锁
        
        Args:
            lock_token: 锁令牌
        """
        if lock_token not in self.locks:
            return
        
        lock = self.locks[lock_token]
        
        # 更新状态
        lock.status = LockStatus.EXPIRED
        
        # 回滚数据
        if lock.edited_data and lock.original_data:
            logger.info(f"Auto-rolling back expired lock: {lock_token}")
            # 这里应该调用实际的数据回滚逻辑
        
        # 清理资源映射
        resource_key = (lock.resource_type, lock.resource_id)
        if resource_key in self.resource_locks:
            del self.resource_locks[resource_key]
        
        logger.info(f"Cleaned up expired lock: {lock_token}")
    
    def get_lock_status(
        self,
        lock_token: str
    ) -> Optional[Dict[str, Any]]:
        """获取锁状态
        
        Args:
            lock_token: 锁令牌
        
        Returns:
            锁状态字典，如果不存在则返回None
        """
        with self._lock:
            if lock_token not in self.locks:
                return None
            
            lock = self.locks[lock_token]
            now = datetime.now()
            
            return {
                "lock_token": lock_token,
                "resource_id": lock.resource_id,
                "resource_type": lock.resource_type,
                "teacher_id": lock.teacher_id,
                "status": lock.status.value,
                "acquired_at": lock.acquired_at.isoformat(),
                "expires_at": lock.expires_at.isoformat(),
                "last_renewed_at": lock.last_renewed_at.isoformat(),
                "is_expired": now >= lock.expires_at,
                "remaining_seconds": max(0, int((lock.expires_at - now).total_seconds())),
                "has_edited_data": lock.edited_data is not None
            }
    
    def get_resource_lock_status(
        self,
        resource_id: str,
        resource_type: str
    ) -> Optional[Dict[str, Any]]:
        """获取资源的锁状态
        
        Args:
            resource_id: 资源ID
            resource_type: 资源类型
        
        Returns:
            锁状态字典，如果资源未被锁定则返回None
        """
        resource_key = (resource_type, resource_id)
        
        with self._lock:
            if resource_key not in self.resource_locks:
                return None
            
            lock_token = self.resource_locks[resource_key]
            return self.get_lock_status(lock_token)
    
    def get_all_locks(
        self,
        teacher_id: Optional[int] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有锁
        
        Args:
            teacher_id: 教师ID（可选，用于过滤）
            resource_type: 资源类型（可选，用于过滤）
        
        Returns:
            锁列表
        """
        with self._lock:
            locks = []
            
            for lock_token, lock in self.locks.items():
                # 过滤
                if teacher_id is not None and lock.teacher_id != teacher_id:
                    continue
                if resource_type is not None and lock.resource_type != resource_type:
                    continue
                
                status = self.get_lock_status(lock_token)
                if status:
                    locks.append(status)
            
            return locks
    
    def get_lock_statistics(self) -> Dict[str, Any]:
        """获取锁统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            total = len(self.locks)
            by_status = {}
            by_type = {}
            
            for lock in self.locks.values():
                # 按状态统计
                status_key = lock.status.value
                by_status[status_key] = by_status.get(status_key, 0) + 1
                
                # 按类型统计
                type_key = lock.resource_type
                by_type[type_key] = by_type.get(type_key, 0) + 1
            
            # 统计过期锁
            now = datetime.now()
            expired_count = sum(
                1 for lock in self.locks.values()
                if lock.status == LockStatus.ACQUIRED and now >= lock.expires_at
            )
            
            return {
                "total_locks": total,
                "by_status": by_status,
                "by_type": by_type,
                "expired_count": expired_count,
                "active_locks": by_status.get(LockStatus.ACQUIRED.value, 0)
            }
