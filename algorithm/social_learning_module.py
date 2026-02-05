"""
社会学习模块（知识锦囊）

基于v6.0需求，为疑难知识点生成"知识锦囊"（同伴经验音频）。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    """学习风格枚举"""
    VISUAL = "visual"  # 视觉型
    AUDITORY = "auditory"  # 听觉型
    KINESTHETIC = "kinesthetic"  # 动觉型
    READING = "reading"  # 阅读型


@dataclass
class KnowledgeTip:
    """知识锦囊"""
    tip_id: int
    knowledge_point_id: int
    contributor_id: int  # 贡献者ID（已掌握该知识点的学生）
    audio_url: str  # 音频链接
    transcript: str  # 文字转录
    learning_style: LearningStyle  # 学习风格
    quality_score: float = 0.0  # 质量分数（0-1）
    relevance_score: float = 0.0  # 相关性分数（0-1）
    usage_count: int = 0  # 使用次数
    helpful_count: int = 0  # 有帮助次数
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TipEvaluation:
    """锦囊评估结果"""
    tip_id: int
    quality_score: float  # 质量分数（0-1）
    relevance_score: float  # 相关性分数（0-1）
    helpful_rate: float  # 有帮助率（0-1）
    overall_score: float  # 综合分数（0-1）
    evaluation_details: Dict[str, Any]  # 评估详情


class SocialLearningModule:
    """社会学习模块（知识锦囊）
    
    功能：
    1. 知识锦囊：收集已掌握该知识点的学生的经验分享（音频形式）
    2. 同伴经验：学生可以录制音频分享学习经验
    3. 智能匹配：根据知识点和学习风格匹配最相关的锦囊
    4. 质量评估：评估锦囊的质量和相关性
    """
    
    def __init__(self):
        """初始化社会学习模块"""
        # 存储知识锦囊
        self.knowledge_tips: Dict[int, KnowledgeTip] = {}  # key: tip_id
        
        # 存储知识点到锦囊的映射
        self.kp_tips: Dict[int, List[int]] = {}  # key: knowledge_point_id, value: tip_id列表
        
        # 存储用户反馈
        self.tip_feedback: Dict[int, List[Dict[str, Any]]] = {}  # key: tip_id
        
        logger.info("SocialLearningModule initialized")
    
    def collect_student_tip(
        self,
        user_id: int,
        knowledge_point_id: int,
        audio_url: str,
        transcript: str,
        learning_style: LearningStyle
    ) -> int:
        """收集学生分享的知识锦囊
        
        Args:
            user_id: 用户ID（贡献者）
            knowledge_point_id: 知识点ID
            audio_url: 音频链接
            transcript: 文字转录
            learning_style: 学习风格
        
        Returns:
            锦囊ID
        """
        # 生成锦囊ID
        tip_id = len(self.knowledge_tips) + 1
        
        tip = KnowledgeTip(
            tip_id=tip_id,
            knowledge_point_id=knowledge_point_id,
            contributor_id=user_id,
            audio_url=audio_url,
            transcript=transcript,
            learning_style=learning_style
        )
        
        self.knowledge_tips[tip_id] = tip
        
        # 更新知识点到锦囊的映射
        if knowledge_point_id not in self.kp_tips:
            self.kp_tips[knowledge_point_id] = []
        
        self.kp_tips[knowledge_point_id].append(tip_id)
        
        logger.info(
            f"Collected knowledge tip: tip_id={tip_id}, "
            f"kp_id={knowledge_point_id}, contributor={user_id}, "
            f"style={learning_style.value}"
        )
        
        return tip_id
    
    def match_knowledge_tips(
        self,
        knowledge_point_id: int,
        learning_style: Optional[LearningStyle] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """匹配知识锦囊
        
        Args:
            knowledge_point_id: 知识点ID
            learning_style: 学习风格（可选）
            limit: 返回数量限制
        
        Returns:
            匹配的锦囊列表（按相关性排序）
        """
        if knowledge_point_id not in self.kp_tips:
            return []
        
        tip_ids = self.kp_tips[knowledge_point_id]
        tips = [self.knowledge_tips[tid] for tid in tip_ids if tid in self.knowledge_tips]
        
        # 如果指定了学习风格，优先匹配相同风格的锦囊
        if learning_style is not None:
            # 计算相关性分数
            for tip in tips:
                tip.relevance_score = self._calculate_relevance_score(tip, learning_style)
            
            # 按相关性分数排序
            tips.sort(key=lambda t: t.relevance_score, reverse=True)
        else:
            # 按质量分数排序
            tips.sort(key=lambda t: t.quality_score, reverse=True)
        
        # 限制返回数量
        tips = tips[:limit]
        
        # 转换为字典格式
        result = []
        for tip in tips:
            result.append({
                "tip_id": tip.tip_id,
                "knowledge_point_id": tip.knowledge_point_id,
                "contributor_id": tip.contributor_id,
                "audio_url": tip.audio_url,
                "transcript": tip.transcript,
                "learning_style": tip.learning_style.value,
                "quality_score": tip.quality_score,
                "relevance_score": tip.relevance_score,
                "usage_count": tip.usage_count,
                "helpful_count": tip.helpful_count
            })
        
        logger.info(
            f"Matched {len(result)} knowledge tips for kp={knowledge_point_id}, "
            f"learning_style={learning_style.value if learning_style else None}"
        )
        
        return result
    
    def _calculate_relevance_score(
        self,
        tip: KnowledgeTip,
        target_learning_style: LearningStyle
    ) -> float:
        """计算相关性分数
        
        Args:
            tip: 知识锦囊
            target_learning_style: 目标学习风格
        
        Returns:
            相关性分数（0-1）
        """
        # 基础分数（质量分数）
        base_score = tip.quality_score
        
        # 学习风格匹配度
        if tip.learning_style == target_learning_style:
            style_match = 1.0
        else:
            # 部分匹配（例如视觉型和阅读型有一定相似性）
            style_match = 0.5
        
        # 使用率权重（使用次数越多，可能越有用）
        usage_weight = min(1.0, tip.usage_count / 10.0)
        
        # 有帮助率权重
        helpful_rate = (
            tip.helpful_count / tip.usage_count
            if tip.usage_count > 0 else 0.5
        )
        
        # 综合相关性分数
        relevance = (
            base_score * 0.4 +
            style_match * 0.3 +
            usage_weight * 0.15 +
            helpful_rate * 0.15
        )
        
        return max(0.0, min(1.0, relevance))
    
    def evaluate_tip_quality(self, tip_id: int) -> TipEvaluation:
        """评估锦囊质量
        
        Args:
            tip_id: 锦囊ID
        
        Returns:
            评估结果
        """
        if tip_id not in self.knowledge_tips:
            return TipEvaluation(
                tip_id=tip_id,
                quality_score=0.0,
                relevance_score=0.0,
                helpful_rate=0.0,
                overall_score=0.0,
                evaluation_details={"error": "锦囊不存在"}
            )
        
        tip = self.knowledge_tips[tip_id]
        
        # 1. 内容质量评估（基于转录文本）
        content_quality = self._evaluate_content_quality(tip.transcript)
        
        # 2. 有帮助率
        helpful_rate = (
            tip.helpful_count / tip.usage_count
            if tip.usage_count > 0 else 0.5
        )
        
        # 3. 使用率（使用次数越多，可能质量越好）
        usage_score = min(1.0, tip.usage_count / 20.0)
        
        # 综合质量分数
        quality_score = (content_quality * 0.5 + helpful_rate * 0.3 + usage_score * 0.2)
        
        # 更新锦囊的质量分数
        tip.quality_score = quality_score
        
        evaluation = TipEvaluation(
            tip_id=tip_id,
            quality_score=quality_score,
            relevance_score=tip.relevance_score,
            helpful_rate=helpful_rate,
            overall_score=(quality_score + tip.relevance_score) / 2.0,
            evaluation_details={
                "content_quality": content_quality,
                "helpful_rate": helpful_rate,
                "usage_score": usage_score,
                "usage_count": tip.usage_count,
                "helpful_count": tip.helpful_count
            }
        )
        
        logger.info(
            f"Evaluated tip quality: tip_id={tip_id}, "
            f"quality_score={quality_score:.2f}, "
            f"overall_score={evaluation.overall_score:.2f}"
        )
        
        return evaluation
    
    def _evaluate_content_quality(self, transcript: str) -> float:
        """评估内容质量（基于转录文本）
        
        Args:
            transcript: 文字转录
        
        Returns:
            质量分数（0-1）
        """
        if not transcript:
            return 0.0
        
        # 简单的质量评估指标
        score = 0.5  # 基础分数
        
        # 长度检查（太短可能质量不高）
        if len(transcript) < 20:
            score -= 0.2
        elif len(transcript) > 100:
            score += 0.1
        
        # 关键词检查（包含学习方法相关词汇）
        learning_keywords = ["理解", "掌握", "方法", "技巧", "注意", "重点", "关键"]
        keyword_count = sum(1 for keyword in learning_keywords if keyword in transcript)
        score += min(0.2, keyword_count * 0.05)
        
        return max(0.0, min(1.0, score))
    
    def rank_tips_by_relevance(
        self,
        tips: List[KnowledgeTip],
        learning_style: LearningStyle
    ) -> List[KnowledgeTip]:
        """按相关性排序锦囊
        
        Args:
            tips: 锦囊列表
            learning_style: 学习风格
        
        Returns:
            排序后的锦囊列表
        """
        # 计算每个锦囊的相关性分数
        for tip in tips:
            tip.relevance_score = self._calculate_relevance_score(tip, learning_style)
        
        # 按相关性分数排序
        sorted_tips = sorted(tips, key=lambda t: t.relevance_score, reverse=True)
        
        return sorted_tips
    
    def record_tip_usage(
        self,
        tip_id: int,
        user_id: int,
        was_helpful: bool = False
    ) -> bool:
        """记录锦囊使用情况
        
        Args:
            tip_id: 锦囊ID
            user_id: 用户ID
            was_helpful: 是否有帮助
        
        Returns:
            是否成功记录
        """
        if tip_id not in self.knowledge_tips:
            logger.warning(f"Tip {tip_id} not found")
            return False
        
        tip = self.knowledge_tips[tip_id]
        tip.usage_count += 1
        
        if was_helpful:
            tip.helpful_count += 1
        
        # 记录反馈
        if tip_id not in self.tip_feedback:
            self.tip_feedback[tip_id] = []
        
        self.tip_feedback[tip_id].append({
            "user_id": user_id,
            "was_helpful": was_helpful,
            "timestamp": datetime.now()
        })
        
        logger.debug(
            f"Recorded tip usage: tip_id={tip_id}, user={user_id}, "
            f"helpful={was_helpful}, total_usage={tip.usage_count}"
        )
        
        return True
    
    def get_tip_statistics(
        self,
        knowledge_point_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取锦囊统计报告
        
        Args:
            knowledge_point_id: 知识点ID（可选）
        
        Returns:
            统计报告字典
        """
        if knowledge_point_id is not None:
            if knowledge_point_id not in self.kp_tips:
                return {
                    "knowledge_point_id": knowledge_point_id,
                    "total_tips": 0,
                    "average_quality": 0.0,
                    "average_helpful_rate": 0.0
                }
            
            tip_ids = self.kp_tips[knowledge_point_id]
            tips = [self.knowledge_tips[tid] for tid in tip_ids if tid in self.knowledge_tips]
        else:
            tips = list(self.knowledge_tips.values())
        
        if not tips:
            return {
                "total_tips": 0,
                "average_quality": 0.0,
                "average_helpful_rate": 0.0
            }
        
        avg_quality = sum(t.quality_score for t in tips) / len(tips)
        avg_helpful_rate = sum(
            t.helpful_count / t.usage_count if t.usage_count > 0 else 0.0
            for t in tips
        ) / len(tips)
        total_usage = sum(t.usage_count for t in tips)
        
        return {
            "total_tips": len(tips),
            "average_quality": avg_quality,
            "average_helpful_rate": avg_helpful_rate,
            "total_usage": total_usage,
            "average_usage_per_tip": total_usage / len(tips) if tips else 0.0
        }
