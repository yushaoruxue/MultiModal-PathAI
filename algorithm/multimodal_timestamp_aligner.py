"""
多模态时间戳对齐协议

基于v9.0需求，解决ASR、OCR、视频帧之间的时间戳不一致问题。
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
class ASRSegment:
    """ASR片段"""
    start_time: float  # 开始时间（秒）
    end_time: float  # 结束时间（秒）
    text: str  # 转录文本


@dataclass
class OCRSegment:
    """OCR片段"""
    start_time: float  # 开始时间（秒）
    end_time: float  # 结束时间（秒）
    text: str  # 识别文本
    slide_num: int  # 幻灯片编号


@dataclass
class VideoFrame:
    """视频帧"""
    timestamp: float  # 时间戳（秒）
    frame_data: Any  # 帧数据（简化处理）


@dataclass
class AlignedSegment:
    """对齐后的片段"""
    asr_segment: Optional[ASRSegment]
    ocr_segment: Optional[OCRSegment]
    video_frame: Optional[VideoFrame]
    aligned_timestamp: float  # 对齐后的时间戳
    alignment_score: float  # 对齐质量分数（0-1）
    semantic_coherence: float  # 语义连贯性（0-1）


@dataclass
class SemanticDissonance:
    """语义脱节"""
    timestamp: float
    asr_text: Optional[str]
    ocr_text: Optional[str]
    dissonance_score: float  # 脱节分数（0-1，越高越脱节）
    reason: str  # 脱节原因


class MultimodalTimestampAligner:
    """多模态时间戳对齐协议
    
    功能：
    1. 对齐窗口：±3秒软对齐窗口
    2. 对齐算法：基于语义相似度和时间戳距离
    3. 语义脱节检测：检测对齐后的语义是否一致
    4. 教师校验：语义脱节时通知教师手动校验
    """
    
    # 对齐窗口（秒）
    ALIGNMENT_WINDOW = 3.0  # ±3秒
    
    # 语义脱节阈值
    DISSONANCE_THRESHOLD = 0.5  # 脱节分数阈值
    
    def __init__(self, alignment_window: float = ALIGNMENT_WINDOW):
        """初始化多模态时间戳对齐器
        
        Args:
            alignment_window: 对齐窗口（秒，默认3.0）
        """
        self.alignment_window = alignment_window
        
        # 存储对齐历史
        self.alignment_history: List[AlignedSegment] = []
        
        # 存储语义脱节日志
        self.dissonance_log: List[SemanticDissonance] = []
        
        logger.info(
            f"MultimodalTimestampAligner initialized with "
            f"alignment_window=±{alignment_window}s"
        )
    
    def align_timestamps(
        self,
        asr_data: List[ASRSegment],
        ocr_data: List[OCRSegment],
        video_frames: List[VideoFrame]
    ) -> Dict[str, Any]:
        """对齐时间戳
        
        Args:
            asr_data: ASR时间戳列表
            ocr_data: OCR时间戳列表
            video_frames: 视频帧时间戳列表
        
        Returns:
            对齐结果字典
        """
        aligned_segments = []
        
        # 1. 对齐ASR和OCR
        for asr_seg in asr_data:
            # 找到时间窗口内的OCR片段
            matching_ocr = self._find_matching_segments(
                asr_seg.start_time, ocr_data, self.alignment_window
            )
            
            # 找到时间窗口内的视频帧
            matching_frames = self._find_matching_frames(
                asr_seg.start_time, video_frames, self.alignment_window
            )
            
            # 选择最佳匹配
            best_ocr = self._select_best_match(
                asr_seg, matching_ocr, "ocr"
            ) if matching_ocr else None
            
            best_frame = matching_frames[0] if matching_frames else None
            
            # 计算对齐质量分数
            alignment_score = self.calculate_alignment_score(
                asr_seg.start_time,
                best_ocr.start_time if best_ocr else None,
                best_frame.timestamp if best_frame else None,
                asr_seg.text,
                best_ocr.text if best_ocr else None
            )
            
            # 计算对齐后的时间戳（取平均值或加权平均）
            aligned_timestamp = self._calculate_aligned_timestamp(
                asr_seg.start_time,
                best_ocr.start_time if best_ocr else None,
                best_frame.timestamp if best_frame else None
            )
            
            # 计算语义连贯性
            semantic_coherence = self._calculate_semantic_coherence(
                asr_seg.text,
                best_ocr.text if best_ocr else None
            )
            
            aligned_seg = AlignedSegment(
                asr_segment=asr_seg,
                ocr_segment=best_ocr,
                video_frame=best_frame,
                aligned_timestamp=aligned_timestamp,
                alignment_score=alignment_score,
                semantic_coherence=semantic_coherence
            )
            
            aligned_segments.append(aligned_seg)
            self.alignment_history.append(aligned_seg)
        
        # 2. 检测语义脱节
        dissonances = self.detect_semantic_dissonance(aligned_segments)
        
        # 3. 计算平均对齐质量
        avg_alignment_score = (
            sum(seg.alignment_score for seg in aligned_segments) / len(aligned_segments)
            if aligned_segments else 0.0
        )
        
        result = {
            "aligned_segments": aligned_segments,
            "total_segments": len(aligned_segments),
            "average_alignment_score": avg_alignment_score,
            "dissonance_count": len(dissonances),
            "dissonances": dissonances
        }
        
        logger.info(
            f"Aligned timestamps: {len(aligned_segments)} segments, "
            f"avg_score={avg_alignment_score:.2f}, "
            f"dissonances={len(dissonances)}"
        )
        
        return result
    
    def _find_matching_segments(
        self,
        target_time: float,
        segments: List[OCRSegment],
        window: float
    ) -> List[OCRSegment]:
        """找到时间窗口内的匹配片段
        
        Args:
            target_time: 目标时间
            segments: 片段列表
            window: 时间窗口
        
        Returns:
            匹配的片段列表
        """
        matching = []
        for seg in segments:
            # 检查片段是否在时间窗口内
            if (seg.start_time <= target_time + window and
                seg.end_time >= target_time - window):
                matching.append(seg)
        
        return matching
    
    def _find_matching_frames(
        self,
        target_time: float,
        frames: List[VideoFrame],
        window: float
    ) -> List[VideoFrame]:
        """找到时间窗口内的匹配帧
        
        Args:
            target_time: 目标时间
            frames: 帧列表
            window: 时间窗口
        
        Returns:
            匹配的帧列表
        """
        matching = []
        for frame in frames:
            if abs(frame.timestamp - target_time) <= window:
                matching.append(frame)
        
        return matching
    
    def _select_best_match(
        self,
        asr_seg: ASRSegment,
        candidates: List[OCRSegment],
        match_type: str
    ) -> Optional[OCRSegment]:
        """选择最佳匹配
        
        Args:
            asr_seg: ASR片段
            candidates: 候选片段列表
            match_type: 匹配类型
        
        Returns:
            最佳匹配片段
        """
        if not candidates:
            return None
        
        best_score = 0.0
        best_match = None
        
        for candidate in candidates:
            # 计算时间戳距离分数
            time_score = 1.0 - abs(asr_seg.start_time - candidate.start_time) / self.alignment_window
            time_score = max(0.0, time_score)
            
            # 计算语义相似度（简化处理）
            semantic_score = self._calculate_text_similarity(asr_seg.text, candidate.text)
            
            # 综合分数
            score = time_score * 0.5 + semantic_score * 0.5
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match
    
    def calculate_alignment_score(
        self,
        timestamp1: float,
        timestamp2: Optional[float],
        timestamp3: Optional[float],
        text1: str,
        text2: Optional[str]
    ) -> float:
        """计算对齐质量分数
        
        Args:
            timestamp1: 时间戳1（ASR）
            timestamp2: 时间戳2（OCR，可选）
            timestamp3: 时间戳3（视频帧，可选）
            text1: 文本1（ASR）
            text2: 文本2（OCR，可选）
        
        Returns:
            对齐质量分数（0-1）
        """
        scores = []
        
        # 时间戳对齐分数
        if timestamp2 is not None:
            time_diff = abs(timestamp1 - timestamp2)
            time_score = 1.0 - min(1.0, time_diff / self.alignment_window)
            scores.append(time_score)
        
        if timestamp3 is not None:
            time_diff = abs(timestamp1 - timestamp3)
            time_score = 1.0 - min(1.0, time_diff / self.alignment_window)
            scores.append(time_score)
        
        # 语义相似度分数
        if text2 is not None:
            semantic_score = self._calculate_text_similarity(text1, text2)
            scores.append(semantic_score)
        
        # 如果没有匹配，返回较低分数
        if not scores:
            return 0.3
        
        # 返回平均分数
        return sum(scores) / len(scores)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化处理）
        
        Args:
            text1: 文本1
            text2: 文本2
        
        Returns:
            相似度分数（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        # 简单的字符重叠度计算
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        return jaccard_similarity
    
    def _calculate_aligned_timestamp(
        self,
        timestamp1: float,
        timestamp2: Optional[float],
        timestamp3: Optional[float]
    ) -> float:
        """计算对齐后的时间戳
        
        Args:
            timestamp1: 时间戳1
            timestamp2: 时间戳2（可选）
            timestamp3: 时间戳3（可选）
        
        Returns:
            对齐后的时间戳
        """
        timestamps = [timestamp1]
        if timestamp2 is not None:
            timestamps.append(timestamp2)
        if timestamp3 is not None:
            timestamps.append(timestamp3)
        
        # 返回平均值
        return sum(timestamps) / len(timestamps)
    
    def _calculate_semantic_coherence(
        self,
        text1: str,
        text2: Optional[str]
    ) -> float:
        """计算语义连贯性
        
        Args:
            text1: 文本1
            text2: 文本2（可选）
        
        Returns:
            语义连贯性分数（0-1）
        """
        if text2 is None:
            return 0.5  # 无OCR数据时给中等分数
        
        return self._calculate_text_similarity(text1, text2)
    
    def detect_semantic_dissonance(
        self,
        aligned_segments: List[AlignedSegment]
    ) -> List[SemanticDissonance]:
        """检测语义脱节
        
        Args:
            aligned_segments: 对齐后的片段列表
        
        Returns:
            语义脱节列表
        """
        dissonances = []
        
        for seg in aligned_segments:
            if seg.semantic_coherence < self.DISSONANCE_THRESHOLD:
                asr_text = seg.asr_segment.text if seg.asr_segment else None
                ocr_text = seg.ocr_segment.text if seg.ocr_segment else None
                
                dissonance = SemanticDissonance(
                    timestamp=seg.aligned_timestamp,
                    asr_text=asr_text,
                    ocr_text=ocr_text,
                    dissonance_score=1.0 - seg.semantic_coherence,
                    reason=f"ASR和OCR文本语义不一致（相似度：{seg.semantic_coherence:.2f}）"
                )
                
                dissonances.append(dissonance)
                self.dissonance_log.append(dissonance)
        
        if dissonances:
            logger.warning(
                f"Detected {len(dissonances)} semantic dissonances"
            )
        
        return dissonances
    
    def request_teacher_verification(
        self,
        dissonance_log: List[SemanticDissonance]
    ) -> bool:
        """请求教师校验
        
        Args:
            dissonance_log: 语义脱节日志
        
        Returns:
            是否成功请求
        """
        if not dissonance_log:
            return False
        
        # 这里应该调用通知服务，实际实现中需要对接通知系统
        verification_request = {
            "type": "semantic_dissonance_verification",
            "dissonance_count": len(dissonance_log),
            "dissonances": [
                {
                    "timestamp": d.timestamp,
                    "asr_text": d.asr_text,
                    "ocr_text": d.ocr_text,
                    "dissonance_score": d.dissonance_score,
                    "reason": d.reason
                }
                for d in dissonance_log
            ],
            "timestamp": datetime.now().isoformat(),
            "message": f"检测到{len(dissonance_log)}处语义脱节，需要教师手动校验"
        }
        
        logger.info(
            f"Requested teacher verification for {len(dissonance_log)} dissonances"
        )
        
        # 在实际实现中，这里应该：
        # 1. 调用通知服务API
        # 2. 发送邮件或站内消息
        # 3. 记录验证请求历史
        
        return True
    
    def get_alignment_statistics(
        self
    ) -> Dict[str, Any]:
        """获取对齐统计报告
        
        Returns:
            统计报告字典
        """
        if not self.alignment_history:
            return {
                "total_alignments": 0,
                "average_alignment_score": 0.0,
                "average_semantic_coherence": 0.0,
                "dissonance_count": 0
            }
        
        avg_alignment = sum(seg.alignment_score for seg in self.alignment_history) / len(self.alignment_history)
        avg_coherence = sum(seg.semantic_coherence for seg in self.alignment_history) / len(self.alignment_history)
        
        return {
            "total_alignments": len(self.alignment_history),
            "average_alignment_score": avg_alignment,
            "average_semantic_coherence": avg_coherence,
            "dissonance_count": len(self.dissonance_log),
            "dissonance_rate": len(self.dissonance_log) / len(self.alignment_history) if self.alignment_history else 0.0
        }
