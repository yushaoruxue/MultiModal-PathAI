"""
难点识别算法

基于学生的观看行为数据识别疑难点。
包括难点判定规则引擎和困难度分数计算。
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BehaviorData:
    """观看行为数据"""
    user_id: int
    knowledge_point_id: int
    replay_count: int = 0
    pause_count: int = 0
    total_watch_time: float = 0.0
    knowledge_point_duration: float = 0.0
    seek_count: int = 0
    last_watch_time: Optional[datetime] = None


@dataclass
class KnowledgePointInfo:
    """知识点基本信息"""
    id: int
    difficulty: str = "medium"  # easy/medium/hard
    duration: float = 0.0


@dataclass
class DifficultyResult:
    """难点识别结果"""
    is_difficult: bool
    difficulty_score: float  # 0-10
    trigger_reasons: List[str]
    confidence: float  # 0-1


class DifficultyDetector:
    """难点识别器
    
    基于学生的观看行为数据识别疑难点。
    使用规则引擎进行判定，支持可配置的阈值和权重。
    """
    
    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """初始化难点识别器
        
        Args:
            thresholds: 判定阈值字典，包含：
                - replay: 回放次数阈值（默认2）
                - pause: 暂停次数阈值（默认3）
                - watch_ratio: 停留时长比阈值（默认3.0）
                - seek: 快进/快退次数阈值（默认5）
            weights: 权重字典，包含：
                - replay: 回放权重（默认0.3）
                - pause: 暂停权重（默认0.3）
                - watch_ratio: 停留时长比权重（默认0.2）
                - seek: 快进/快退权重（默认0.2）
        """
        # 默认阈值
        self.thresholds = thresholds or {
            "replay": 2.0,
            "pause": 3.0,
            "watch_ratio": 3.0,
            "seek": 5.0
        }
        
        # 默认权重
        self.weights = weights or {
            "replay": 0.3,
            "pause": 0.3,
            "watch_ratio": 0.2,
            "seek": 0.2
        }
        
        # 验证权重总和为1
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
        logger.info(f"DifficultyDetector initialized with thresholds={self.thresholds}, weights={self.weights}")
    
    def detect(
        self,
        behavior_data: BehaviorData,
        knowledge_point_info: Optional[KnowledgePointInfo] = None
    ) -> DifficultyResult:
        """检测是否为疑难点
        
        Args:
            behavior_data: 观看行为数据
            knowledge_point_info: 知识点基本信息（可选）
        
        Returns:
            难点识别结果
        """
        try:
            logger.debug(f"Detecting difficulty for user {behavior_data.user_id}, kp {behavior_data.knowledge_point_id}")
            
            # 计算困难度分数
            difficulty_score = self.calculate_difficulty_score(behavior_data)
            
            # 获取触发原因
            trigger_reasons = self.get_trigger_reasons(behavior_data)
            
            # 判断是否为疑难点
            is_difficult = len(trigger_reasons) > 0 or difficulty_score >= 1.0
            
            # 计算置信度
            confidence = self._calculate_confidence(behavior_data, trigger_reasons, difficulty_score)
            
            result = DifficultyResult(
                is_difficult=is_difficult,
                difficulty_score=min(difficulty_score, 10.0),  # 限制在0-10
                trigger_reasons=trigger_reasons,
                confidence=confidence
            )
            
            logger.info(f"Detection result: is_difficult={is_difficult}, score={difficulty_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in detection: {e}", exc_info=True)
            raise
    
    def calculate_difficulty_score(self, behavior_data: BehaviorData) -> float:
        """计算困难度分数
        
        公式：
        Di = w1 × (replay_count/T1) + w2 × (pause_count/T2) + 
             w3 × (停留时长比/T3) + w4 × (seek_count/T4)
        
        Args:
            behavior_data: 观看行为数据
        
        Returns:
            困难度分数（0-10）
        """
        try:
            # 计算停留时长比
            watch_ratio = 0.0
            if behavior_data.knowledge_point_duration > 0:
                watch_ratio = behavior_data.total_watch_time / behavior_data.knowledge_point_duration
            
            # 计算各项指标
            replay_score = (behavior_data.replay_count / self.thresholds["replay"]) * self.weights["replay"]
            pause_score = (behavior_data.pause_count / self.thresholds["pause"]) * self.weights["pause"]
            watch_ratio_score = (watch_ratio / self.thresholds["watch_ratio"]) * self.weights["watch_ratio"]
            seek_score = (behavior_data.seek_count / self.thresholds["seek"]) * self.weights["seek"]
            
            # 计算总分
            total_score = (replay_score + pause_score + watch_ratio_score + seek_score) * 10
            
            return max(0.0, total_score)
            
        except Exception as e:
            logger.warning(f"Error calculating difficulty score: {e}")
            return 0.0
    
    def get_trigger_reasons(self, behavior_data: BehaviorData) -> List[str]:
        """获取触发疑难点判定的原因
        
        Args:
            behavior_data: 观看行为数据
        
        Returns:
            触发原因列表
        """
        reasons = []
        
        # 计算停留时长比
        watch_ratio = 0.0
        if behavior_data.knowledge_point_duration > 0:
            watch_ratio = behavior_data.total_watch_time / behavior_data.knowledge_point_duration
        
        # 检查各项指标
        if behavior_data.replay_count >= self.thresholds["replay"]:
            reasons.append(f"回放次数过多（{behavior_data.replay_count}次 >= {self.thresholds['replay']}次）")
        
        if behavior_data.pause_count >= self.thresholds["pause"]:
            reasons.append(f"暂停次数过多（{behavior_data.pause_count}次 >= {self.thresholds['pause']}次）")
        
        if watch_ratio >= self.thresholds["watch_ratio"]:
            reasons.append(f"停留时长过长（{watch_ratio:.1f}倍 >= {self.thresholds['watch_ratio']}倍）")
        
        if behavior_data.seek_count >= self.thresholds["seek"]:
            reasons.append(f"快进/快退次数过多（{behavior_data.seek_count}次 >= {self.thresholds['seek']}次）")
        
        return reasons
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """更新判定阈值
        
        Args:
            new_thresholds: 新的阈值字典
        """
        self.thresholds.update(new_thresholds)
        logger.info(f"Thresholds updated: {self.thresholds}")
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """更新权重
        
        Args:
            new_weights: 新的权重字典
        """
        # 归一化权重
        total_weight = sum(new_weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in new_weights.items()}
        else:
            self.weights = new_weights
        
        logger.info(f"Weights updated: {self.weights}")
    
    def batch_detect(
        self,
        behavior_data_list: List[BehaviorData],
        knowledge_point_info: Optional[KnowledgePointInfo] = None
    ) -> List[Tuple[BehaviorData, DifficultyResult]]:
        """批量检测
        
        Args:
            behavior_data_list: 行为数据列表
            knowledge_point_info: 知识点基本信息（可选）
        
        Returns:
            (行为数据, 检测结果) 元组列表
        """
        results = []
        
        for behavior_data in behavior_data_list:
            result = self.detect(behavior_data, knowledge_point_info)
            results.append((behavior_data, result))
        
        logger.info(f"Batch detection completed: {len(results)} results")
        return results
    
    def _calculate_confidence(
        self,
        behavior_data: BehaviorData,
        trigger_reasons: List[str],
        difficulty_score: float
    ) -> float:
        """计算判定置信度
        
        基于触发原因数量和困难度分数计算置信度。
        
        Args:
            behavior_data: 观看行为数据
            trigger_reasons: 触发原因列表
            difficulty_score: 困难度分数
        
        Returns:
            置信度（0-1）
        """
        # 基础置信度：基于触发原因数量
        reason_count = len(trigger_reasons)
        base_confidence = min(reason_count * 0.3, 0.9)
        
        # 分数置信度：基于困难度分数
        score_confidence = min(difficulty_score / 10.0, 1.0) * 0.5
        
        # 综合置信度
        confidence = min(base_confidence + score_confidence, 1.0)
        
        return confidence


# 使用示例
if __name__ == "__main__":
    from tests.mock_data import MOCK_BEHAVIOR_DATA
    
    # 创建难点识别器
    detector = DifficultyDetector()
    
    # 创建行为数据
    behavior_data = BehaviorData(
        user_id=1,
        knowledge_point_id=10,
        replay_count=3,
        pause_count=5,
        total_watch_time=600.0,
        knowledge_point_duration=200.0,
        seek_count=2
    )
    
    # 执行检测
    result = detector.detect(behavior_data)
    
    # 输出结果
    print("=" * 60)
    print("难点识别结果")
    print("=" * 60)
    print(f"是否为疑难点: {result.is_difficult}")
    print(f"困难度分数: {result.difficulty_score:.2f}/10")
    print(f"置信度: {result.confidence:.2f}")
    print(f"触发原因:")
    for reason in result.trigger_reasons:
        print(f"  - {reason}")
