"""
弱网环境降级策略矩阵

基于v9.0需求，在弱网环境下自动降级监控功能。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """降级等级枚举"""
    FULL = "full"  # 全量监控
    LIGHT = "light"  # 精简监控（只监控关键行为）
    LOG_ONLY = "log_only"  # 仅日志模式（不实时分析）


class NetworkStatus(Enum):
    """网络状态枚举"""
    NORMAL = "normal"  # 正常
    WEAK = "weak"  # 弱网
    VERY_WEAK = "very_weak"  # 极弱网
    OFFLINE = "offline"  # 离线


@dataclass
class NetworkMetrics:
    """网络指标"""
    latency: float  # 延迟（毫秒）
    bandwidth: float  # 带宽（Mbps）
    packet_loss: float  # 丢包率（0-1）
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DegradationConfig:
    """降级配置"""
    level: DegradationLevel
    monitor_gaze: bool  # 是否监控视线追踪
    monitor_emotion: bool  # 是否监控微表情
    monitor_interaction: bool  # 是否监控交互行为
    real_time_analysis: bool  # 是否实时分析
    cache_locally: bool  # 是否本地缓存
    sync_on_recovery: bool  # 网络恢复后是否同步


@dataclass
class CachedBehaviorData:
    """缓存的行为数据"""
    user_id: int
    data: Dict[str, Any]
    cached_at: datetime = field(default_factory=datetime.now)
    synced: bool = False  # 是否已同步


class WeakNetworkDegradation:
    """弱网环境降级策略
    
    功能：
    1. 网络状态检测：检测网络延迟、带宽、丢包率
    2. 降级策略矩阵：根据网络状态，选择不同的降级等级
    3. 本地缓存：弱网时，行为数据本地缓存，网络恢复后同步
    4. 弱网区分：区分网络问题和真实学习困难
    """
    
    # 网络状态阈值
    NORMAL_LATENCY_THRESHOLD = 100.0  # 正常延迟阈值（毫秒）
    WEAK_LATENCY_THRESHOLD = 500.0  # 弱网延迟阈值（毫秒）
    
    NORMAL_BANDWIDTH_THRESHOLD = 5.0  # 正常带宽阈值（Mbps）
    WEAK_BANDWIDTH_THRESHOLD = 1.0  # 弱网带宽阈值（Mbps）
    
    NORMAL_PACKET_LOSS_THRESHOLD = 0.05  # 正常丢包率阈值（5%）
    WEAK_PACKET_LOSS_THRESHOLD = 0.2  # 弱网丢包率阈值（20%）
    
    def __init__(self):
        """初始化弱网降级策略"""
        # 存储网络状态历史
        self.network_history: List[NetworkMetrics] = []
        
        # 存储当前降级等级
        self.current_degradation_level: Dict[int, DegradationLevel] = {}  # key: user_id
        
        # 存储缓存的行为数据
        self.cached_data: Dict[int, List[CachedBehaviorData]] = {}  # key: user_id
        
        logger.info("WeakNetworkDegradation initialized")
    
    def detect_network_status(
        self,
        latency: float,
        bandwidth: float,
        packet_loss: float
    ) -> NetworkStatus:
        """检测网络状态
        
        Args:
            latency: 延迟（毫秒）
            bandwidth: 带宽（Mbps）
            packet_loss: 丢包率（0-1）
        
        Returns:
            网络状态
        """
        # 记录网络指标
        metrics = NetworkMetrics(
            latency=latency,
            bandwidth=bandwidth,
            packet_loss=packet_loss
        )
        self.network_history.append(metrics)
        
        # 只保留最近100条记录
        if len(self.network_history) > 100:
            self.network_history = self.network_history[-100:]
        
        # 判断网络状态
        if bandwidth == 0 or packet_loss >= 0.9:
            status = NetworkStatus.OFFLINE
        elif (latency >= self.WEAK_LATENCY_THRESHOLD or
              bandwidth <= self.WEAK_BANDWIDTH_THRESHOLD or
              packet_loss >= self.WEAK_PACKET_LOSS_THRESHOLD):
            status = NetworkStatus.VERY_WEAK
        elif (latency >= self.NORMAL_LATENCY_THRESHOLD or
              bandwidth <= self.NORMAL_BANDWIDTH_THRESHOLD or
              packet_loss >= self.NORMAL_PACKET_LOSS_THRESHOLD):
            status = NetworkStatus.WEAK
        else:
            status = NetworkStatus.NORMAL
        
        logger.debug(
            f"Network status detected: {status.value} "
            f"(latency={latency:.1f}ms, bandwidth={bandwidth:.2f}Mbps, "
            f"packet_loss={packet_loss:.1%})"
        )
        
        return status
    
    def determine_degradation_level(
        self,
        network_status: NetworkStatus,
        user_id: int
    ) -> DegradationLevel:
        """确定降级等级
        
        Args:
            network_status: 网络状态
            user_id: 用户ID
        
        Returns:
            降级等级
        """
        if network_status == NetworkStatus.NORMAL:
            level = DegradationLevel.FULL
        elif network_status == NetworkStatus.WEAK:
            level = DegradationLevel.LIGHT
        elif network_status == NetworkStatus.VERY_WEAK:
            level = DegradationLevel.LOG_ONLY
        else:  # OFFLINE
            level = DegradationLevel.LOG_ONLY
        
        # 更新当前降级等级
        self.current_degradation_level[user_id] = level
        
        logger.info(
            f"Degradation level for user={user_id}: {level.value} "
            f"(network_status={network_status.value})"
        )
        
        return level
    
    def apply_degradation_strategy(
        self,
        level: DegradationLevel
    ) -> DegradationConfig:
        """应用降级策略
        
        Args:
            level: 降级等级
        
        Returns:
            降级配置
        """
        if level == DegradationLevel.FULL:
            # 全量监控
            config = DegradationConfig(
                level=level,
                monitor_gaze=True,
                monitor_emotion=True,
                monitor_interaction=True,
                real_time_analysis=True,
                cache_locally=False,
                sync_on_recovery=False
            )
        elif level == DegradationLevel.LIGHT:
            # 精简监控（只监控关键行为）
            config = DegradationConfig(
                level=level,
                monitor_gaze=False,  # 不监控视线追踪（数据量大）
                monitor_emotion=False,  # 不监控微表情（数据量大）
                monitor_interaction=True,  # 监控交互行为（数据量小）
                real_time_analysis=True,  # 仍进行实时分析
                cache_locally=True,  # 本地缓存
                sync_on_recovery=True  # 网络恢复后同步
            )
        else:  # LOG_ONLY
            # 仅日志模式（不实时分析）
            config = DegradationConfig(
                level=level,
                monitor_gaze=False,
                monitor_emotion=False,
                monitor_interaction=True,  # 只记录交互行为
                real_time_analysis=False,  # 不实时分析
                cache_locally=True,  # 本地缓存
                sync_on_recovery=True  # 网络恢复后同步
            )
        
        logger.info(
            f"Applied degradation strategy: level={level.value}, "
            f"monitor_gaze={config.monitor_gaze}, "
            f"monitor_emotion={config.monitor_emotion}, "
            f"real_time_analysis={config.real_time_analysis}"
        )
        
        return config
    
    def cache_behavior_data(
        self,
        user_id: int,
        behavior_data: Dict[str, Any]
    ) -> bool:
        """缓存行为数据到本地
        
        Args:
            user_id: 用户ID
            behavior_data: 行为数据字典
        
        Returns:
            是否成功缓存
        """
        cached_item = CachedBehaviorData(
            user_id=user_id,
            data=behavior_data
        )
        
        if user_id not in self.cached_data:
            self.cached_data[user_id] = []
        
        self.cached_data[user_id].append(cached_item)
        
        logger.debug(
            f"Cached behavior data for user={user_id}, "
            f"total_cached={len(self.cached_data[user_id])}"
        )
        
        return True
    
    def sync_cached_data(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """同步缓存的数据到服务器
        
        Args:
            user_id: 用户ID
        
        Returns:
            同步结果字典
        """
        if user_id not in self.cached_data:
            return {
                "success": False,
                "message": "无缓存数据",
                "synced_count": 0
            }
        
        cached_items = self.cached_data[user_id]
        unsynced_items = [item for item in cached_items if not item.synced]
        
        if not unsynced_items:
            return {
                "success": True,
                "message": "所有数据已同步",
                "synced_count": 0
            }
        
        # 模拟同步过程（实际应该调用API）
        synced_count = 0
        for item in unsynced_items:
            # 这里应该调用后端API同步数据
            # 简化处理，直接标记为已同步
            item.synced = True
            synced_count += 1
        
        logger.info(
            f"Synced cached data for user={user_id}: "
            f"{synced_count}/{len(unsynced_items)} items"
        )
        
        return {
            "success": True,
            "message": f"成功同步{synced_count}条数据",
            "synced_count": synced_count,
            "total_cached": len(cached_items),
            "remaining": len([item for item in cached_items if not item.synced])
        }
    
    def get_degradation_level(self, user_id: int) -> DegradationLevel:
        """获取当前降级等级
        
        Args:
            user_id: 用户ID
        
        Returns:
            降级等级，如果不存在则返回FULL
        """
        return self.current_degradation_level.get(user_id, DegradationLevel.FULL)
    
    def is_network_issue(
        self,
        network_status: NetworkStatus,
        behavior_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """判断是否为网络问题（而非真实学习困难）
        
        Args:
            network_status: 网络状态
            behavior_data: 行为数据（可选）
        
        Returns:
            是否为网络问题
        """
        # 如果网络状态是弱网或离线，可能是网络问题
        if network_status in [NetworkStatus.WEAK, NetworkStatus.VERY_WEAK, NetworkStatus.OFFLINE]:
            return True
        
        # 如果行为数据显示观看时间很短但有很多暂停/回放，可能是网络卡顿
        if behavior_data:
            watch_percentage = behavior_data.get("watch_percentage", 1.0)
            pause_count = behavior_data.get("pause_count", 0)
            
            if watch_percentage < 0.3 and pause_count > 5:
                # 观看很少但暂停很多，可能是网络问题
                return True
        
        return False
    
    def get_network_statistics(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """获取网络统计报告
        
        Args:
            time_window_minutes: 时间窗口（分钟）
        
        Returns:
            统计报告字典
        """
        if not self.network_history:
            return {
                "total_samples": 0,
                "average_latency": 0.0,
                "average_bandwidth": 0.0,
                "average_packet_loss": 0.0,
                "network_status_distribution": {}
            }
        
        # 过滤时间窗口内的数据
        from datetime import timedelta
        now = datetime.now()
        time_window = timedelta(minutes=time_window_minutes)
        
        recent_metrics = [
            m for m in self.network_history
            if (now - m.timestamp) <= time_window
        ]
        
        if not recent_metrics:
            return {
                "total_samples": 0,
                "average_latency": 0.0,
                "average_bandwidth": 0.0,
                "average_packet_loss": 0.0,
                "network_status_distribution": {}
            }
        
        # 计算平均值
        avg_latency = sum(m.latency for m in recent_metrics) / len(recent_metrics)
        avg_bandwidth = sum(m.bandwidth for m in recent_metrics) / len(recent_metrics)
        avg_packet_loss = sum(m.packet_loss for m in recent_metrics) / len(recent_metrics)
        
        # 统计网络状态分布
        status_distribution = defaultdict(int)
        for m in recent_metrics:
            status = self.detect_network_status(m.latency, m.bandwidth, m.packet_loss)
            status_distribution[status.value] += 1
        
        return {
            "total_samples": len(recent_metrics),
            "average_latency": avg_latency,
            "average_bandwidth": avg_bandwidth,
            "average_packet_loss": avg_packet_loss,
            "network_status_distribution": dict(status_distribution)
        }
    
    def get_cached_data_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取缓存数据统计
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        if user_id is not None:
            if user_id not in self.cached_data:
                return {
                    "user_id": user_id,
                    "total_cached": 0,
                    "synced_count": 0,
                    "unsynced_count": 0
                }
            
            items = self.cached_data[user_id]
            synced_count = sum(1 for item in items if item.synced)
            
            return {
                "user_id": user_id,
                "total_cached": len(items),
                "synced_count": synced_count,
                "unsynced_count": len(items) - synced_count
            }
        
        # 统计所有用户
        total_cached = sum(len(items) for items in self.cached_data.values())
        total_synced = sum(
            sum(1 for item in items if item.synced)
            for items in self.cached_data.values()
        )
        
        return {
            "total_users": len(self.cached_data),
            "total_cached": total_cached,
            "total_synced": total_synced,
            "total_unsynced": total_cached - total_synced
        }
