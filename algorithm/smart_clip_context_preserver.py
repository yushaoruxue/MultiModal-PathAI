"""
智能剪辑上下文保留协议

基于v7.0需求，剪辑补偿视频时保留前后上下文。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContextConfig:
    """上下文保留配置"""
    before_seconds: float = 5.0  # 前5秒
    after_seconds: float = 3.0  # 后3秒
    min_clip_duration: float = 3.0  # 最小剪辑时长（秒）
    max_clip_duration: float = 300.0  # 最大剪辑时长（秒）


@dataclass
class ClipRange:
    """剪辑时间范围"""
    start_time: float  # 开始时间（秒）
    end_time: float  # 结束时间（秒）
    original_start: float  # 原始知识点开始时间
    original_end: float  # 原始知识点结束时间
    context_before: float  # 前文保留时长
    context_after: float  # 后文保留时长


@dataclass
class ClipQuality:
    """剪辑质量评估"""
    video_id: str
    quality_score: float  # 质量分数（0-1）
    semantic_coherence: float  # 语义连贯性（0-1）
    boundary_quality: float  # 边界质量（0-1）
    context_preservation: float  # 上下文保留度（0-1）
    issues: List[str]  # 问题列表


class SmartClipContextPreserver:
    """智能剪辑上下文保留协议
    
    功能：
    1. 上下文保留：剪辑知识点视频时，保留前5秒+后3秒的上下文
    2. 语义连贯性：确保剪辑后的视频语义连贯
    3. 智能边界检测：自动检测知识点边界，避免截断关键内容
    4. 质量评估：评估剪辑后视频的质量
    """
    
    # 默认上下文配置
    DEFAULT_CONTEXT_BEFORE = 5.0  # 前5秒
    DEFAULT_CONTEXT_AFTER = 3.0  # 后3秒
    
    def __init__(self, context_config: Optional[ContextConfig] = None):
        """初始化智能剪辑上下文保留器
        
        Args:
            context_config: 上下文配置（可选）
        """
        self.context_config = context_config or ContextConfig()
        
        # 存储剪辑历史
        self.clip_history: Dict[str, ClipRange] = {}  # key: video_id
        
        logger.info(
            f"SmartClipContextPreserver initialized with "
            f"context_before={self.context_config.before_seconds}s, "
            f"context_after={self.context_config.after_seconds}s"
        )
    
    def clip_with_context(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        context_config: Optional[ContextConfig] = None
    ) -> Tuple[str, ClipRange]:
        """剪辑视频并保留上下文
        
        Args:
            video_path: 原视频路径
            start_time: 知识点开始时间（秒）
            end_time: 知识点结束时间（秒）
            context_config: 上下文配置（可选）
        
        Returns:
            (剪辑后的视频路径, 剪辑时间范围)
        """
        config = context_config or self.context_config
        
        # 计算实际剪辑时间范围（含上下文）
        clip_start = max(0.0, start_time - config.before_seconds)
        clip_end = end_time + config.after_seconds
        
        # 检测语义边界（智能调整）
        adjusted_start = self.detect_semantic_boundary(
            video_path, clip_start, "before"
        )
        adjusted_end = self.detect_semantic_boundary(
            video_path, clip_end, "after"
        )
        
        # 确保剪辑时长在合理范围内
        clip_duration = adjusted_end - adjusted_start
        if clip_duration < config.min_clip_duration:
            # 如果太短，扩展上下文
            center = (adjusted_start + adjusted_end) / 2.0
            adjusted_start = max(0.0, center - config.min_clip_duration / 2.0)
            adjusted_end = adjusted_start + config.min_clip_duration
        
        if clip_duration > config.max_clip_duration:
            # 如果太长，限制上下文
            adjusted_start = start_time - config.before_seconds
            adjusted_end = end_time + config.after_seconds
            if adjusted_end - adjusted_start > config.max_clip_duration:
                # 优先保留后文
                adjusted_start = adjusted_end - config.max_clip_duration
        
        clip_range = ClipRange(
            start_time=adjusted_start,
            end_time=adjusted_end,
            original_start=start_time,
            original_end=end_time,
            context_before=adjusted_start - start_time if adjusted_start < start_time else 0.0,
            context_after=adjusted_end - end_time if adjusted_end > end_time else 0.0
        )
        
        # 生成输出路径
        output_path = self._generate_output_path(video_path, clip_range)
        
        # 执行剪辑（这里应该调用ffmpeg，简化处理）
        # 实际实现中应该调用：ffmpeg -i input.mp4 -ss start -t duration output.mp4
        logger.info(
            f"Cliping video: {video_path} -> {output_path}, "
            f"range=[{adjusted_start:.1f}s, {adjusted_end:.1f}s], "
            f"context=[{clip_range.context_before:.1f}s before, "
            f"{clip_range.context_after:.1f}s after]"
        )
        
        # 存储剪辑历史
        self.clip_history[output_path] = clip_range
        
        return output_path, clip_range
    
    def detect_semantic_boundary(
        self,
        video_path: str,
        target_time: float,
        direction: str  # "before" or "after"
    ) -> float:
        """检测语义边界
        
        自动检测知识点边界，避免截断关键内容
        
        Args:
            video_path: 视频路径
            target_time: 目标时间（秒）
            direction: 方向（"before"向前检测，"after"向后检测）
        
        Returns:
            调整后的时间（秒）
        """
        # 这里应该使用语义分析（如语音识别、场景检测等）
        # 简化处理：在目标时间附近寻找合适的边界
        
        # 假设每5秒有一个语义边界
        boundary_interval = 5.0
        
        if direction == "before":
            # 向前寻找最近的边界
            adjusted_time = (target_time // boundary_interval) * boundary_interval
            # 确保不超过目标时间
            if adjusted_time > target_time:
                adjusted_time -= boundary_interval
        else:  # after
            # 向后寻找最近的边界
            adjusted_time = ((target_time // boundary_interval) + 1) * boundary_interval
            # 确保不小于目标时间
            if adjusted_time < target_time:
                adjusted_time += boundary_interval
        
        logger.debug(
            f"Detected semantic boundary: target={target_time:.1f}s, "
            f"direction={direction}, adjusted={adjusted_time:.1f}s"
        )
        
        return adjusted_time
    
    def evaluate_clip_quality(
        self,
        clipped_video_path: str,
        original_range: Optional[ClipRange] = None
    ) -> ClipQuality:
        """评估剪辑质量
        
        Args:
            clipped_video_path: 剪辑后的视频路径
            original_range: 原始剪辑范围（可选）
        
        Returns:
            质量评估结果
        """
        if clipped_video_path not in self.clip_history:
            if original_range is None:
                return ClipQuality(
                    video_id=clipped_video_path,
                    quality_score=0.0,
                    semantic_coherence=0.0,
                    boundary_quality=0.0,
                    context_preservation=0.0,
                    issues=["剪辑范围信息缺失"]
                )
            clip_range = original_range
        else:
            clip_range = self.clip_history[clipped_video_path]
        
        issues = []
        scores = {}
        
        # 1. 上下文保留度评估
        expected_before = self.context_config.before_seconds
        expected_after = self.context_config.after_seconds
        
        before_preservation = min(1.0, clip_range.context_before / expected_before) if expected_before > 0 else 1.0
        after_preservation = min(1.0, clip_range.context_after / expected_after) if expected_after > 0 else 1.0
        context_preservation = (before_preservation + after_preservation) / 2.0
        
        scores["context_preservation"] = context_preservation
        
        if context_preservation < 0.8:
            issues.append(f"上下文保留不足（前文：{clip_range.context_before:.1f}s，后文：{clip_range.context_after:.1f}s）")
        
        # 2. 语义连贯性评估（简化处理）
        # 实际应该分析视频内容，检查是否有明显的截断
        clip_duration = clip_range.end_time - clip_range.start_time
        original_duration = clip_range.original_end - clip_range.original_start
        
        # 如果剪辑时长合理，认为语义连贯
        if clip_duration >= original_duration * 1.1:  # 至少保留110%的原始内容
            semantic_coherence = 1.0
        elif clip_duration >= original_duration:
            semantic_coherence = 0.8
        else:
            semantic_coherence = 0.5
            issues.append("剪辑时长过短，可能影响语义连贯性")
        
        scores["semantic_coherence"] = semantic_coherence
        
        # 3. 边界质量评估
        # 检查边界是否在合理位置（是否在语义边界上）
        boundary_quality = 0.8  # 简化处理，假设边界质量良好
        scores["boundary_quality"] = boundary_quality
        
        # 4. 综合质量分数
        quality_score = (
            context_preservation * 0.4 +
            semantic_coherence * 0.4 +
            boundary_quality * 0.2
        )
        
        quality = ClipQuality(
            video_id=clipped_video_path,
            quality_score=quality_score,
            semantic_coherence=semantic_coherence,
            boundary_quality=boundary_quality,
            context_preservation=context_preservation,
            issues=issues
        )
        
        logger.info(
            f"Evaluated clip quality: video={clipped_video_path}, "
            f"score={quality_score:.2f}, issues={len(issues)}"
        )
        
        return quality
    
    def preserve_context_seamlessly(
        self,
        original_video_path: str,
        clipped_video_path: str
    ) -> str:
        """无缝保留上下文
        
        确保剪辑后的视频与原始视频在上下文处无缝衔接
        
        Args:
            original_video_path: 原始视频路径
            clipped_video_path: 剪辑后的视频路径
        
        Returns:
            处理后的视频路径
        """
        # 这里应该进行视频处理，确保无缝衔接
        # 实际实现中可能需要：
        # 1. 检查剪辑边界处的帧
        # 2. 添加淡入淡出效果
        # 3. 调整音频过渡
        
        output_path = clipped_video_path.replace(".mp4", "_seamless.mp4")
        
        logger.info(
            f"Preserving context seamlessly: {original_video_path} -> {output_path}"
        )
        
        return output_path
    
    def _generate_output_path(
        self,
        input_path: str,
        clip_range: ClipRange
    ) -> str:
        """生成输出路径
        
        Args:
            input_path: 输入视频路径
            clip_range: 剪辑范围
        
        Returns:
            输出视频路径
        """
        import os
        
        base_name = os.path.splitext(input_path)[0]
        extension = os.path.splitext(input_path)[1]
        
        output_path = f"{base_name}_clip_{clip_range.start_time:.1f}_{clip_range.end_time:.1f}{extension}"
        
        return output_path
    
    def batch_clip(
        self,
        video_path: str,
        clip_ranges: List[Tuple[float, float]],
        context_config: Optional[ContextConfig] = None
    ) -> List[Tuple[str, ClipRange]]:
        """批量剪辑
        
        Args:
            video_path: 原视频路径
            clip_ranges: 剪辑范围列表（(start, end)元组列表）
            context_config: 上下文配置（可选）
        
        Returns:
            剪辑结果列表（(输出路径, 剪辑范围)元组列表）
        """
        results = []
        
        for start_time, end_time in clip_ranges:
            output_path, clip_range = self.clip_with_context(
                video_path, start_time, end_time, context_config
            )
            results.append((output_path, clip_range))
        
        logger.info(
            f"Batch clipped {len(results)} segments from {video_path}"
        )
        
        return results
    
    def get_clip_statistics(
        self
    ) -> Dict[str, Any]:
        """获取剪辑统计报告
        
        Returns:
            统计报告字典
        """
        if not self.clip_history:
            return {
                "total_clips": 0,
                "average_context_before": 0.0,
                "average_context_after": 0.0
            }
        
        avg_before = sum(r.context_before for r in self.clip_history.values()) / len(self.clip_history)
        avg_after = sum(r.context_after for r in self.clip_history.values()) / len(self.clip_history)
        
        return {
            "total_clips": len(self.clip_history),
            "average_context_before": avg_before,
            "average_context_after": avg_after,
            "average_clip_duration": sum(
                r.end_time - r.start_time for r in self.clip_history.values()
            ) / len(self.clip_history)
        }
