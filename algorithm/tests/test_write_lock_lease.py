"""
测试写锁租约机制
"""

import pytest
from datetime import datetime, timedelta
from algorithm.write_lock_lease_manager import (
    WriteLockLeaseManager,
    LockStatus
)


class TestWriteLockLeaseManager:
    """测试写锁租约管理器"""
    
    def test_init(self):
        """测试初始化"""
        manager = WriteLockLeaseManager()
        
        assert manager.lease_duration == timedelta(minutes=30)
        assert len(manager.locks) == 0
        assert len(manager.resource_locks) == 0
    
    def test_acquire_lock(self):
        """测试获取锁"""
        manager = WriteLockLeaseManager()
        
        result = manager.acquire_lock(
            resource_id="video_123",
            resource_type="video",
            teacher_id=100
        )
        
        assert result.success is True
        assert result.lock_token is not None
        assert result.expires_at is not None
        assert result.lock_token in manager.locks
    
    def test_acquire_lock_duplicate(self):
        """测试重复获取锁（同一资源）"""
        manager = WriteLockLeaseManager()
        
        # 第一次获取
        result1 = manager.acquire_lock("video_123", "video", 100)
        assert result1.success is True
        
        # 第二次获取（不同教师）
        result2 = manager.acquire_lock("video_123", "video", 200)
        assert result2.success is False
        assert "已被锁定" in result2.message
    
    def test_renew_lock(self):
        """测试续约锁"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 获取原始到期时间
        original_expires = manager.locks[lock_token].expires_at
        
        # 续约
        renew_result = manager.renew_lock(lock_token, 100)
        
        assert renew_result.success is True
        assert manager.locks[lock_token].expires_at > original_expires
    
    def test_renew_lock_wrong_teacher(self):
        """测试错误教师续约"""
        manager = WriteLockLeaseManager()
        
        # 教师100获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 教师200尝试续约
        renew_result = manager.renew_lock(lock_token, 200)
        
        assert renew_result.success is False
        assert "无权续约" in renew_result.message
    
    def test_release_lock(self):
        """测试释放锁"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 释放锁
        released = manager.release_lock(lock_token, rollback=False)
        
        assert released is True
        assert manager.locks[lock_token].status == LockStatus.RELEASED
        assert ("video", "video_123") not in manager.resource_locks
    
    def test_release_lock_with_rollback(self):
        """测试释放锁并回滚"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 释放锁并回滚
        released = manager.release_lock(lock_token, rollback=True)
        
        assert released is True
        assert manager.locks[lock_token].status == LockStatus.ROLLED_BACK
    
    def test_atomic_publish(self):
        """测试原子化发布"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 原子化发布
        edited_data = {"title": "新标题", "content": "新内容"}
        published = manager.atomic_publish(lock_token, edited_data)
        
        assert published is True
        assert manager.locks[lock_token].edited_data == edited_data
        assert manager.locks[lock_token].status == LockStatus.RELEASED
    
    def test_check_lock_timeout(self):
        """测试检查锁超时"""
        manager = WriteLockLeaseManager(lease_duration=timedelta(seconds=1))
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 等待超时（模拟）
        import time
        time.sleep(1.1)
        
        # 检查超时
        expired = manager.check_lock_timeout()
        
        assert len(expired) == 1
        assert expired[0]["lock_token"] == lock_token
        assert manager.locks[lock_token].status == LockStatus.EXPIRED
    
    def test_get_lock_status(self):
        """测试获取锁状态"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        lock_token = result.lock_token
        
        # 获取状态
        status = manager.get_lock_status(lock_token)
        
        assert status is not None
        assert status["lock_token"] == lock_token
        assert status["resource_id"] == "video_123"
        assert status["teacher_id"] == 100
        assert status["status"] == LockStatus.ACQUIRED.value
        assert "remaining_seconds" in status
    
    def test_get_resource_lock_status(self):
        """测试获取资源的锁状态"""
        manager = WriteLockLeaseManager()
        
        # 获取锁
        result = manager.acquire_lock("video_123", "video", 100)
        
        # 获取资源锁状态
        status = manager.get_resource_lock_status("video_123", "video")
        
        assert status is not None
        assert status["resource_id"] == "video_123"
        assert status["resource_type"] == "video"
    
    def test_get_resource_lock_status_not_locked(self):
        """测试获取未锁定资源的状态"""
        manager = WriteLockLeaseManager()
        
        # 获取未锁定资源的状态
        status = manager.get_resource_lock_status("video_123", "video")
        
        assert status is None
    
    def test_get_all_locks(self):
        """测试获取所有锁"""
        manager = WriteLockLeaseManager()
        
        # 获取多个锁
        manager.acquire_lock("video_123", "video", 100)
        manager.acquire_lock("video_456", "video", 100)
        manager.acquire_lock("kp_789", "knowledge_point", 200)
        
        # 获取所有锁
        all_locks = manager.get_all_locks()
        
        assert len(all_locks) == 3
        
        # 按教师过滤
        teacher_100_locks = manager.get_all_locks(teacher_id=100)
        assert len(teacher_100_locks) == 2
        
        # 按类型过滤
        video_locks = manager.get_all_locks(resource_type="video")
        assert len(video_locks) == 2
    
    def test_get_lock_statistics(self):
        """测试获取锁统计信息"""
        manager = WriteLockLeaseManager()
        
        # 获取多个锁
        manager.acquire_lock("video_123", "video", 100)
        manager.acquire_lock("video_456", "video", 100)
        manager.acquire_lock("kp_789", "knowledge_point", 200)
        
        # 获取统计
        stats = manager.get_lock_statistics()
        
        assert stats["total_locks"] == 3
        assert stats["active_locks"] == 3
        assert stats["by_type"]["video"] == 2
        assert stats["by_type"]["knowledge_point"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
