"""
硬件画像驱动三级降级算法

基于v10.0需求，根据设备性能自动降级。
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
    FULL = "full"  # 全量模式
    LIGHT = "light"  # 精简模式
    LOG_ONLY = "log_only"  # 仅日志模式


@dataclass
class HardwareProfile:
    """硬件画像"""
    cpu_usage: float  # CPU使用率（0-100%）
    memory_usage: float  # 内存使用率（0-100%）
    gpu_available: bool  # GPU是否可用
    fps: float  # 帧率（FPS）
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DegradationDecision:
    """降级决策结果"""
    level: DegradationLevel
    previous_level: Optional[DegradationLevel]
    weight_compensation: float  # 权重补偿系数
    performance_alert: Optional[str]  # 性能告警（如果有）
    reason: str  # 决策原因


@dataclass
class PerformanceAlert:
    """性能告警"""
    alert_type: str  # 告警类型
    severity: str  # 严重程度：low/medium/high/critical
    message: str  # 告警消息
    timestamp: datetime = field(default_factory=datetime.now)


class HardwareDegradation:
    """硬件画像驱动三级降级算法
    
    功能：
    1. 硬件画像：周期性采集CPU、内存、GPU、FPS等性能指标
    2. 三级降级：
       - 全量模式：CPU<50%, FPS>30
       - 精简模式：50%≤CPU<80%, 20≤FPS<30
       - 仅日志模式：CPU≥80%, FPS<20
    3. 权重补偿：降级模式下，自动调整算法权重（0.4→0.8），保证准确率
    4. 性能监控：实时监控设备性能，防止页面卡死
    """
    
    # 降级阈值
    FULL_CPU_THRESHOLD = 50.0  # 全量模式CPU阈值（%）
    LIGHT_CPU_THRESHOLD = 80.0  # 精简模式CPU阈值（%）
    
    FULL_FPS_THRESHOLD = 30.0  # 全量模式FPS阈值
    LIGHT_FPS_THRESHOLD = 20.0  # 精简模式FPS阈值
    
    # 权重补偿系数
    FULL_WEIGHT = 1.0  # 全量模式权重
    LIGHT_WEIGHT = 0.8  # 精简模式权重（从0.4提升到0.8）
    LOG_ONLY_WEIGHT = 0.6  # 仅日志模式权重
    
    # 性能告警阈值
    CRITICAL_CPU_THRESHOLD = 95.0  # 严重CPU阈值
    CRITICAL_FPS_THRESHOLD = 10.0  # 严重FPS阈值
    CRITICAL_MEMORY_THRESHOLD = 95.0  # 严重内存阈值
    
    def __init__(self):
        """初始化硬件降级算法"""
        # 存储硬件画像历史
        self.hardware_history: Dict[int, List[HardwareProfile]] = {}  # key: user_id
        
        # 存储当前降级等级
        self.current_level: Dict[int, DegradationLevel] = {}  # key: user_id
        
        # 存储性能告警
        self.performance_alerts: List[PerformanceAlert] = []
        
        logger.info("HardwareDegradation initialized")
    
    def collect_hardware_profile(
        self,
        user_id: int,
        cpu_usage: float,
        memory_usage: float,
        gpu_available: bool,
        fps: float
    ) -> HardwareProfile:
        """采集硬件画像
        
        Args:
            user_id: 用户ID
            cpu_usage: CPU使用率（0-100%）
            memory_usage: 内存使用率（0-100%）
            gpu_available: GPU是否可用
            fps: 帧率（FPS）
        
        Returns:
            硬件画像
        """
        profile = HardwareProfile(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_available=gpu_available,
            fps=fps
        )
        
        if user_id not in self.hardware_history:
            self.hardware_history[user_id] = []
        
        self.hardware_history[user_id].append(profile)
        
        # 只保留最近100条记录
        if len(self.hardware_history[user_id]) > 100:
            self.hardware_history[user_id] = self.hardware_history[user_id][-100:]
        
        logger.debug(
            f"Collected hardware profile for user={user_id}: "
            f"CPU={cpu_usage:.1f}%, Memory={memory_usage:.1f}%, "
            f"GPU={'available' if gpu_available else 'unavailable'}, FPS={fps:.1f}"
        )
        
        return profile
    
    def determine_degradation_level(
        self,
        hardware_profile: HardwareProfile,
        user_id: int
    ) -> DegradationDecision:
        """确定降级等级
        
        Args:
            hardware_profile: 硬件画像
            user_id: 用户ID
        
        Returns:
            降级决策结果
        """
        previous_level = self.current_level.get(user_id, DegradationLevel.FULL)
        
        cpu = hardware_profile.cpu_usage
        fps = hardware_profile.fps
        
        # 判断降级等级
        if cpu < self.FULL_CPU_THRESHOLD and fps >= self.FULL_FPS_THRESHOLD:
            level = DegradationLevel.FULL
            reason = f"CPU使用率{cpu:.1f}%<{self.FULL_CPU_THRESHOLD}%且FPS{fps:.1f}>={self.FULL_FPS_THRESHOLD}，全量模式"
        elif cpu < self.LIGHT_CPU_THRESHOLD and fps >= self.LIGHT_FPS_THRESHOLD:
            level = DegradationLevel.LIGHT
            reason = (
                f"CPU使用率{self.FULL_CPU_THRESHOLD}%≤{cpu:.1f}%<{self.LIGHT_CPU_THRESHOLD}% "
                f"且{self.LIGHT_FPS_THRESHOLD}≤FPS{fps:.1f}<{self.FULL_FPS_THRESHOLD}，精简模式"
            )
        else:
            level = DegradationLevel.LOG_ONLY
            reason = (
                f"CPU使用率{cpu:.1f}%≥{self.LIGHT_CPU_THRESHOLD}%或FPS{fps:.1f}<{self.LIGHT_FPS_THRESHOLD}，仅日志模式"
            )
        
        # 更新当前等级
        self.current_level[user_id] = level
        
        # 计算权重补偿
        weight_compensation = self.calculate_weight_compensation(level)
        
        # 检查性能告警
        performance_alert = self._check_performance_alert(hardware_profile)
        
        decision = DegradationDecision(
            level=level,
            previous_level=previous_level,
            weight_compensation=weight_compensation,
            performance_alert=performance_alert,
            reason=reason
        )
        
        if level != previous_level:
            logger.info(
                f"Degradation level changed for user={user_id}: "
                f"{previous_level.value} -> {level.value}, reason: {reason}"
            )
        
        return decision
    
    def calculate_weight_compensation(self, level: DegradationLevel) -> float:
        """计算权重补偿系数
        
        降级模式下，自动调整算法权重（0.4→0.8），保证准确率
        
        Args:
            level: 降级等级
        
        Returns:
            权重补偿系数
        """
        if level == DegradationLevel.FULL:
            return self.FULL_WEIGHT
        elif level == DegradationLevel.LIGHT:
            return self.LIGHT_WEIGHT  # 从0.4提升到0.8
        else:  # LOG_ONLY
            return self.LOG_ONLY_WEIGHT
    
    def apply_weight_compensation(
        self,
        algorithm_weights: Dict[str, float],
        compensation: float
    ) -> Dict[str, float]:
        """应用权重补偿到算法权重
        
        Args:
            algorithm_weights: 算法权重字典
            compensation: 权重补偿系数
        
        Returns:
            调整后的权重字典
        """
        adjusted_weights = {
            key: weight * compensation
            for key, weight in algorithm_weights.items()
        }
        
        logger.debug(
            f"Applied weight compensation {compensation:.2f}: "
            f"original={algorithm_weights}, adjusted={adjusted_weights}"
        )
        
        return adjusted_weights
    
    def monitor_performance(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """监控性能
        
        Args:
            user_id: 用户ID
        
        Returns:
            性能监控结果字典
        """
        if user_id not in self.hardware_history:
            return {
                "user_id": user_id,
                "has_data": False,
                "current_level": DegradationLevel.FULL.value,
                "alerts": []
            }
        
        profiles = self.hardware_history[user_id]
        
        if not profiles:
            return {
                "user_id": user_id,
                "has_data": False,
                "current_level": DegradationLevel.FULL.value,
                "alerts": []
            }
        
        # 获取最新的硬件画像
        latest_profile = profiles[-1]
        
        # 获取当前降级等级
        current_level = self.current_level.get(user_id, DegradationLevel.FULL)
        
        # 检查告警
        alerts = []
        if latest_profile.cpu_usage >= self.CRITICAL_CPU_THRESHOLD:
            alerts.append({
                "type": "high_cpu",
                "severity": "critical",
                "message": f"CPU使用率过高：{latest_profile.cpu_usage:.1f}%"
            })
        
        if latest_profile.fps < self.CRITICAL_FPS_THRESHOLD:
            alerts.append({
                "type": "low_fps",
                "severity": "critical",
                "message": f"帧率过低：{latest_profile.fps:.1f} FPS"
            })
        
        if latest_profile.memory_usage >= self.CRITICAL_MEMORY_THRESHOLD:
            alerts.append({
                "type": "high_memory",
                "severity": "high",
                "message": f"内存使用率过高：{latest_profile.memory_usage:.1f}%"
            })
        
        # 计算平均性能指标
        if len(profiles) > 1:
            avg_cpu = sum(p.cpu_usage for p in profiles) / len(profiles)
            avg_fps = sum(p.fps for p in profiles) / len(profiles)
            avg_memory = sum(p.memory_usage for p in profiles) / len(profiles)
        else:
            avg_cpu = latest_profile.cpu_usage
            avg_fps = latest_profile.fps
            avg_memory = latest_profile.memory_usage
        
        return {
            "user_id": user_id,
            "has_data": True,
            "current_level": current_level.value,
            "current_cpu": latest_profile.cpu_usage,
            "current_fps": latest_profile.fps,
            "current_memory": latest_profile.memory_usage,
            "average_cpu": avg_cpu,
            "average_fps": avg_fps,
            "average_memory": avg_memory,
            "alerts": alerts,
            "weight_compensation": self.calculate_weight_compensation(current_level)
        }
    
    def _check_performance_alert(
        self,
        hardware_profile: HardwareProfile
    ) -> Optional[str]:
        """检查性能告警
        
        Args:
            hardware_profile: 硬件画像
        
        Returns:
            告警消息，如果没有告警则返回None
        """
        alerts = []
        
        if hardware_profile.cpu_usage >= self.CRITICAL_CPU_THRESHOLD:
            alerts.append(f"CPU使用率严重过高：{hardware_profile.cpu_usage:.1f}%")
        
        if hardware_profile.fps < self.CRITICAL_FPS_THRESHOLD:
            alerts.append(f"帧率严重过低：{hardware_profile.fps:.1f} FPS")
        
        if hardware_profile.memory_usage >= self.CRITICAL_MEMORY_THRESHOLD:
            alerts.append(f"内存使用率严重过高：{hardware_profile.memory_usage:.1f}%")
        
        if alerts:
            alert_message = "；".join(alerts)
            
            # 记录告警
            alert = PerformanceAlert(
                alert_type="performance_critical",
                severity="critical",
                message=alert_message
            )
            self.performance_alerts.append(alert)
            
            # 只保留最近100条告警
            if len(self.performance_alerts) > 100:
                self.performance_alerts = self.performance_alerts[-100:]
            
            logger.warning(f"Performance alert: {alert_message}")
            
            return alert_message
        
        return None
    
    def get_hardware_statistics(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取硬件统计报告
        
        Args:
            user_id: 用户ID（可选）
        
        Returns:
            统计报告字典
        """
        if user_id is not None:
            if user_id not in self.hardware_history:
                return {
                    "user_id": user_id,
                    "total_samples": 0,
                    "current_level": DegradationLevel.FULL.value
                }
            
            profiles = self.hardware_history[user_id]
            current_level = self.current_level.get(user_id, DegradationLevel.FULL)
            
            if not profiles:
                return {
                    "user_id": user_id,
                    "total_samples": 0,
                    "current_level": current_level.value
                }
            
            avg_cpu = sum(p.cpu_usage for p in profiles) / len(profiles)
            avg_fps = sum(p.fps for p in profiles) / len(profiles)
            avg_memory = sum(p.memory_usage for p in profiles) / len(profiles)
            
            return {
                "user_id": user_id,
                "total_samples": len(profiles),
                "current_level": current_level.value,
                "average_cpu": avg_cpu,
                "average_fps": avg_fps,
                "average_memory": avg_memory,
                "min_cpu": min(p.cpu_usage for p in profiles),
                "max_cpu": max(p.cpu_usage for p in profiles),
                "min_fps": min(p.fps for p in profiles),
                "max_fps": max(p.fps for p in profiles)
            }
        
        # 统计所有用户
        all_profiles = []
        for profiles in self.hardware_history.values():
            all_profiles.extend(profiles)
        
        if not all_profiles:
            return {
                "total_users": 0,
                "total_samples": 0,
                "level_distribution": {}
            }
        
        # 统计降级等级分布
        level_distribution = defaultdict(int)
        for level in self.current_level.values():
            level_distribution[level.value] += 1
        
        return {
            "total_users": len(self.hardware_history),
            "total_samples": len(all_profiles),
            "average_cpu": sum(p.cpu_usage for p in all_profiles) / len(all_profiles),
            "average_fps": sum(p.fps for p in all_profiles) / len(all_profiles),
            "average_memory": sum(p.memory_usage for p in all_profiles) / len(all_profiles),
            "level_distribution": dict(level_distribution)
        }
    
    def get_performance_alerts(
        self,
        severity: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[PerformanceAlert]:
        """获取性能告警列表
        
        Args:
            severity: 严重程度过滤（可选）
            limit: 限制返回数量（可选）
        
        Returns:
            性能告警列表（按时间倒序）
        """
        alerts = self.performance_alerts.copy()
        
        if severity is not None:
            alerts = [a for a in alerts if a.severity == severity]
        
        # 按时间倒序排序
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit is not None:
            alerts = alerts[:limit]
        
        return alerts
