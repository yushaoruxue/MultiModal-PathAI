"""
监控信号丢失处理机制

基于v8.0需求，检测摄像头黑屏/遮挡等情况。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalSource(Enum):
    """信号源枚举"""
    CAMERA = "camera"  # 摄像头
    GAZE_TRACKER = "gaze_tracker"  # 视线追踪
    EMOTION_DETECTOR = "emotion_detector"  # 微表情检测
    AUDIO = "audio"  # 音频


class SignalLossReason(Enum):
    """信号丢失原因枚举"""
    NETWORK_ISSUE = "network_issue"  # 网络问题
    DEVICE_OFFLINE = "device_offline"  # 设备离线
    CAMERA_BLOCKED = "camera_blocked"  # 摄像头被遮挡
    CAMERA_BLACK_SCREEN = "camera_black_screen"  # 摄像头黑屏
    UNKNOWN = "unknown"  # 未知原因


class ActionType(Enum):
    """处理动作枚举"""
    PAUSE = "pause"  # 暂停学习
    RESUME = "resume"  # 恢复学习
    IGNORE = "ignore"  # 忽略（可能是网络问题）


@dataclass
class SignalData:
    """监控信号数据"""
    source: SignalSource
    timestamp: datetime
    is_valid: bool  # 信号是否有效
    quality_score: float = 0.0  # 信号质量分数（0-1）
    data: Optional[Dict] = None  # 信号数据


@dataclass
class NetworkStatus:
    """网络状态数据"""
    is_online: bool
    latency: float  # 延迟（毫秒）
    bandwidth: float  # 带宽（Mbps）
    packet_loss: float  # 丢包率（0-1）
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SignalLossInfo:
    """信号丢失信息"""
    source: SignalSource
    is_lost: bool
    reason: SignalLossReason
    duration: float  # 丢失时长（秒）
    first_lost_time: Optional[datetime] = None
    last_check_time: datetime = field(default_factory=datetime.now)


@dataclass
class SignalLossRecord:
    """信号丢失记录"""
    user_id: int
    video_id: int
    source: SignalSource
    reason: SignalLossReason
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    action_taken: ActionType = ActionType.PAUSE


class SignalLossHandler:
    """监控信号丢失处理机制
    
    功能：
    1. 心跳检测：定期检测监控信号是否正常
    2. 信号丢失处理：如果检测到信号丢失，强制暂停学习
    3. 弱网区分：区分网络问题导致的信号丢失和真实遮挡
    4. 恢复机制：信号恢复后，自动恢复学习状态
    """
    
    # 默认心跳间隔（秒）
    DEFAULT_HEARTBEAT_INTERVAL = 5.0
    
    # 信号丢失判定阈值（连续丢失多少次判定为丢失）
    LOSS_THRESHOLD = 3
    
    # 网络问题判定阈值
    NETWORK_LATENCY_THRESHOLD = 1000.0  # 延迟阈值（毫秒）
    NETWORK_PACKET_LOSS_THRESHOLD = 0.3  # 丢包率阈值
    
    def __init__(
        self,
        heartbeat_interval: float = DEFAULT_HEARTBEAT_INTERVAL,
        loss_threshold: int = LOSS_THRESHOLD
    ):
        """初始化信号丢失处理器
        
        Args:
            heartbeat_interval: 心跳检测间隔（秒）
            loss_threshold: 信号丢失判定阈值（连续丢失次数）
        """
        self.heartbeat_interval = heartbeat_interval
        self.loss_threshold = loss_threshold
        
        # 存储每个信号源的最近状态
        self.signal_states: Dict[SignalSource, List[bool]] = {}  # 最近N次检测结果
        
        # 存储信号丢失记录
        self.loss_records: Dict[tuple, SignalLossRecord] = {}  # key: (user_id, video_id, source)
        
        # 存储每个用户的学习状态
        self.user_learning_states: Dict[tuple, bool] = {}  # key: (user_id, video_id), value: is_paused
        
        logger.info(
            f"SignalLossHandler initialized with "
            f"heartbeat_interval={heartbeat_interval}s, "
            f"loss_threshold={loss_threshold}"
        )
    
    def detect_signal_loss(
        self,
        signal_data: SignalData,
        network_status: Optional[NetworkStatus] = None
    ) -> SignalLossInfo:
        """检测信号丢失
        
        Args:
            signal_data: 监控信号数据
            network_status: 网络状态数据（可选）
        
        Returns:
            信号丢失检测结果
        """
        source = signal_data.source
        
        # 更新信号状态历史
        if source not in self.signal_states:
            self.signal_states[source] = []
        
        # 记录当前检测结果
        is_valid = signal_data.is_valid and signal_data.quality_score > 0.3
        self.signal_states[source].append(is_valid)
        
        # 只保留最近N次检测结果
        if len(self.signal_states[source]) > self.loss_threshold * 2:
            self.signal_states[source] = self.signal_states[source][-self.loss_threshold * 2:]
        
        # 检查是否连续丢失
        recent_states = self.signal_states[source][-self.loss_threshold:]
        is_lost = len(recent_states) >= self.loss_threshold and not any(recent_states)
        
        # 判断丢失原因
        reason = self._determine_loss_reason(signal_data, network_status, is_lost)
        
        # 计算丢失时长
        duration = 0.0
        first_lost_time = None
        
        if is_lost:
            # 查找第一次丢失的时间
            for i in range(len(self.signal_states[source]) - 1, -1, -1):
                if not self.signal_states[source][i]:
                    if i == len(self.signal_states[source]) - 1:
                        first_lost_time = signal_data.timestamp
                    duration = (signal_data.timestamp - first_lost_time).total_seconds() if first_lost_time else 0.0
                else:
                    break
        
        info = SignalLossInfo(
            source=source,
            is_lost=is_lost,
            reason=reason,
            duration=duration,
            first_lost_time=first_lost_time,
            last_check_time=signal_data.timestamp
        )
        
        if is_lost:
            logger.warning(
                f"Signal loss detected: source={source.value}, "
                f"reason={reason.value}, duration={duration:.1f}s"
            )
        
        return info
    
    def _determine_loss_reason(
        self,
        signal_data: SignalData,
        network_status: Optional[NetworkStatus],
        is_lost: bool
    ) -> SignalLossReason:
        """判断信号丢失原因
        
        Args:
            signal_data: 信号数据
            network_status: 网络状态
            is_lost: 是否丢失
        
        Returns:
            丢失原因
        """
        if not is_lost:
            return SignalLossReason.UNKNOWN
        
        # 检查网络状态
        if network_status:
            if not network_status.is_online:
                return SignalLossReason.NETWORK_ISSUE
            
            if (network_status.latency > self.NETWORK_LATENCY_THRESHOLD or
                network_status.packet_loss > self.NETWORK_PACKET_LOSS_THRESHOLD):
                return SignalLossReason.NETWORK_ISSUE
        
        # 检查信号质量
        if signal_data.quality_score == 0.0:
            if signal_data.source == SignalSource.CAMERA:
                return SignalLossReason.CAMERA_BLACK_SCREEN
            return SignalLossReason.DEVICE_OFFLINE
        
        if signal_data.quality_score < 0.1:
            if signal_data.source == SignalSource.CAMERA:
                return SignalLossReason.CAMERA_BLOCKED
        
        return SignalLossReason.UNKNOWN
    
    def handle_signal_loss(
        self,
        user_id: int,
        video_id: int,
        loss_info: SignalLossInfo
    ) -> ActionType:
        """处理信号丢失
        
        Args:
            user_id: 用户ID
            video_id: 视频ID
            loss_info: 信号丢失信息
        
        Returns:
            处理动作
        """
        key = (user_id, video_id, loss_info.source)
        
        if not loss_info.is_lost:
            # 信号正常，检查是否需要恢复
            if key in self.loss_records:
                # 之前有丢失记录，现在恢复了
                record = self.loss_records[key]
                record.end_time = datetime.now()
                record.duration = (record.end_time - record.start_time).total_seconds()
                
                # 删除记录
                del self.loss_records[key]
                
                # 恢复学习状态
                learning_key = (user_id, video_id)
                if learning_key in self.user_learning_states:
                    self.user_learning_states[learning_key] = False  # 恢复学习
                
                logger.info(
                    f"Signal recovered for user={user_id}, video={video_id}, "
                    f"source={loss_info.source.value}, duration={record.duration:.1f}s"
                )
                
                return ActionType.RESUME
            
            return ActionType.IGNORE
        
        # 信号丢失
        # 判断是否需要暂停学习
        if loss_info.reason == SignalLossReason.NETWORK_ISSUE:
            # 网络问题，可能只是暂时性的，不立即暂停
            if loss_info.duration < 10.0:  # 10秒内不暂停
                return ActionType.IGNORE
        
        # 创建或更新丢失记录
        if key not in self.loss_records:
            record = SignalLossRecord(
                user_id=user_id,
                video_id=video_id,
                source=loss_info.source,
                reason=loss_info.reason,
                start_time=loss_info.first_lost_time or datetime.now(),
                action_taken=ActionType.PAUSE
            )
            self.loss_records[key] = record
            
            # 暂停学习
            learning_key = (user_id, video_id)
            self.user_learning_states[learning_key] = True  # 暂停学习
            
            logger.warning(
                f"Signal loss handled: user={user_id}, video={video_id}, "
                f"source={loss_info.source.value}, reason={loss_info.reason.value}, "
                f"action=PAUSE"
            )
            
            return ActionType.PAUSE
        
        return ActionType.IGNORE
    
    def check_heartbeat(self, signal_source: SignalSource) -> bool:
        """检查心跳（信号是否正常）
        
        Args:
            signal_source: 信号源
        
        Returns:
            心跳是否正常
        """
        if signal_source not in self.signal_states:
            return False
        
        states = self.signal_states[signal_source]
        
        if not states:
            return False
        
        # 检查最近一次检测结果
        return states[-1] if states else False
    
    def resume_after_recovery(
        self,
        user_id: int,
        video_id: int
    ) -> bool:
        """信号恢复后恢复学习状态
        
        Args:
            user_id: 用户ID
            video_id: 视频ID
        
        Returns:
            是否成功恢复
        """
        learning_key = (user_id, video_id)
        
        if learning_key not in self.user_learning_states:
            return False
        
        if not self.user_learning_states[learning_key]:
            # 本来就没有暂停
            return False
        
        # 检查所有信号源是否都恢复
        all_recovered = True
        for (uid, vid, source), record in self.loss_records.items():
            if uid == user_id and vid == video_id:
                all_recovered = False
                break
        
        if all_recovered:
            self.user_learning_states[learning_key] = False
            logger.info(
                f"Resumed learning for user={user_id}, video={video_id}"
            )
            return True
        
        return False
    
    def get_signal_quality(
        self,
        signal_source: SignalSource
    ) -> Dict[str, Any]:
        """获取信号质量统计
        
        Args:
            signal_source: 信号源
        
        Returns:
            信号质量统计字典
        """
        if signal_source not in self.signal_states:
            return {
                "source": signal_source.value,
                "is_online": False,
                "recent_valid_rate": 0.0,
                "total_checks": 0
            }
        
        states = self.signal_states[signal_source]
        
        if not states:
            return {
                "source": signal_source.value,
                "is_online": False,
                "recent_valid_rate": 0.0,
                "total_checks": 0
            }
        
        recent_states = states[-10:]  # 最近10次
        valid_count = sum(1 for s in recent_states if s)
        valid_rate = valid_count / len(recent_states) if recent_states else 0.0
        
        return {
            "source": signal_source.value,
            "is_online": states[-1] if states else False,
            "recent_valid_rate": valid_rate,
            "total_checks": len(states),
            "consecutive_losses": self._count_consecutive_losses(states)
        }
    
    def _count_consecutive_losses(self, states: List[bool]) -> int:
        """计算连续丢失次数
        
        Args:
            states: 状态列表
        
        Returns:
            连续丢失次数
        """
        if not states:
            return 0
        
        count = 0
        for state in reversed(states):
            if not state:
                count += 1
            else:
                break
        
        return count
    
    def get_loss_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取信号丢失统计
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        records = list(self.loss_records.values())
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if not records:
            return {
                "total_loss_events": 0,
                "active_losses": 0,
                "total_duration": 0.0,
                "average_duration": 0.0,
                "by_reason": {}
            }
        
        active_losses = sum(1 for r in records if r.end_time is None)
        total_duration = sum(r.duration for r in records)
        avg_duration = total_duration / len(records) if records else 0.0
        
        # 按原因统计
        by_reason = {}
        for record in records:
            reason = record.reason.value
            if reason not in by_reason:
                by_reason[reason] = {"count": 0, "total_duration": 0.0}
            by_reason[reason]["count"] += 1
            by_reason[reason]["total_duration"] += record.duration
        
        return {
            "total_loss_events": len(records),
            "active_losses": active_losses,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "by_reason": by_reason
        }
