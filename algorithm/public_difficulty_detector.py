"""
公共难点识别逻辑

识别多个学生都感到困难的知识点，为教师提供教学建议。
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from difficulty_detector import DifficultyDetector, BehaviorData, DifficultyResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PublicDifficultyResult:
    """公共难点识别结果"""
    knowledge_point_id: int
    is_public_difficulty: bool
    difficulty_ratio: float  # 困难学生比例（0-1）
    average_difficulty_score: float  # 平均困难度分数
    affected_students: List[int]  # 受影响的学生ID列表
    recommendation: str  # 教学建议


class PublicDifficultyDetector:
    """公共难点识别器
    
    识别多个学生都感到困难的知识点，统计困难学生比例，
    为教师提供教学建议。
    """
    
    def __init__(
        self,
        difficulty_ratio_threshold: float = 0.3,
        difficulty_detector: Optional[DifficultyDetector] = None
    ):
        """初始化公共难点识别器
        
        Args:
            difficulty_ratio_threshold: 困难学生比例阈值（默认0.3，即30%）
            difficulty_detector: 难点识别器实例，如果为None则创建新实例
        """
        self.difficulty_ratio_threshold = difficulty_ratio_threshold
        self.difficulty_detector = difficulty_detector or DifficultyDetector()
        
        logger.info(f"PublicDifficultyDetector initialized with threshold={difficulty_ratio_threshold}")
    
    def detect_public_difficulty(
        self,
        knowledge_point_id: int,
        all_students_behavior: List[BehaviorData]
    ) -> PublicDifficultyResult:
        """检测公共难点
        
        Args:
            knowledge_point_id: 知识点ID
            all_students_behavior: 所有学生对该知识点的行为数据列表
        
        Returns:
            公共难点识别结果
        """
        try:
            logger.info(f"Detecting public difficulty for knowledge point {knowledge_point_id}")
            logger.info(f"Total students: {len(all_students_behavior)}")
            
            if not all_students_behavior:
                return PublicDifficultyResult(
                    knowledge_point_id=knowledge_point_id,
                    is_public_difficulty=False,
                    difficulty_ratio=0.0,
                    average_difficulty_score=0.0,
                    affected_students=[],
                    recommendation="暂无数据"
                )
            
            # 对每个学生进行难点检测
            difficulty_results = []
            difficult_students = []
            
            for behavior_data in all_students_behavior:
                result = self.difficulty_detector.detect(behavior_data)
                difficulty_results.append(result)
                
                if result.is_difficult:
                    difficult_students.append(behavior_data.user_id)
            
            # 计算困难学生比例
            difficulty_ratio = len(difficult_students) / len(all_students_behavior)
            
            # 计算平均困难度分数
            average_difficulty_score = sum(r.difficulty_score for r in difficulty_results) / len(difficulty_results)
            
            # 判断是否为公共难点
            is_public_difficulty = difficulty_ratio >= self.difficulty_ratio_threshold
            
            # 生成教学建议
            recommendation = self.get_recommendation(difficulty_ratio, average_difficulty_score)
            
            result = PublicDifficultyResult(
                knowledge_point_id=knowledge_point_id,
                is_public_difficulty=is_public_difficulty,
                difficulty_ratio=difficulty_ratio,
                average_difficulty_score=average_difficulty_score,
                affected_students=difficult_students,
                recommendation=recommendation
            )
            
            logger.info(f"Public difficulty detection completed: is_public={is_public_difficulty}, ratio={difficulty_ratio:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in public difficulty detection: {e}", exc_info=True)
            raise
    
    def calculate_difficulty_ratio(
        self,
        knowledge_point_id: int,
        behavior_data: List[BehaviorData]
    ) -> float:
        """计算困难学生比例
        
        Args:
            knowledge_point_id: 知识点ID
            behavior_data: 行为数据列表
        
        Returns:
            困难学生比例（0-1）
        """
        if not behavior_data:
            return 0.0
        
        difficult_count = 0
        for behavior in behavior_data:
            result = self.difficulty_detector.detect(behavior)
            if result.is_difficult:
                difficult_count += 1
        
        return difficult_count / len(behavior_data)
    
    def get_recommendation(
        self,
        difficulty_ratio: float,
        average_score: float
    ) -> str:
        """生成教学建议
        
        根据困难学生比例和平均困难度分数生成教学建议。
        
        Args:
            difficulty_ratio: 困难学生比例（0-1）
            average_score: 平均困难度分数（0-10）
        
        Returns:
            教学建议文本
        """
        if difficulty_ratio >= 0.5 and average_score >= 7.0:
            return "严重难点：超过50%的学生感到困难，平均困难度分数较高。建议：1) 重点讲解 2) 补充详细资源 3) 考虑调整教学方式"
        elif difficulty_ratio >= 0.3 and average_score >= 5.0:
            return "公共难点：约30%的学生感到困难。建议：1) 增加讲解时间 2) 提供补偿资源 3) 组织答疑"
        elif difficulty_ratio >= 0.2:
            return "轻微难点：部分学生感到困难。建议：1) 关注困难学生 2) 提供额外练习 3) 个别辅导"
        else:
            return "正常：大多数学生掌握良好，无需特殊处理"
    
    def batch_detect(
        self,
        video_id: int,
        knowledge_point_behaviors: Dict[int, List[BehaviorData]]
    ) -> List[PublicDifficultyResult]:
        """批量检测视频的所有知识点
        
        Args:
            video_id: 视频ID
            knowledge_point_behaviors: 字典，key为知识点ID，value为该知识点的所有学生行为数据
        
        Returns:
            公共难点识别结果列表
        """
        results = []
        
        for kp_id, behavior_list in knowledge_point_behaviors.items():
            result = self.detect_public_difficulty(kp_id, behavior_list)
            results.append(result)
        
        logger.info(f"Batch detection completed for video {video_id}: {len(results)} knowledge points")
        return results
    
    def generate_statistics_report(
        self,
        results: List[PublicDifficultyResult]
    ) -> Dict:
        """生成统计报告
        
        Args:
            results: 公共难点识别结果列表
        
        Returns:
            统计报告字典
        """
        if not results:
            return {
                "total_knowledge_points": 0,
                "public_difficulties": 0,
                "average_difficulty_ratio": 0.0,
                "most_difficult_kp": None
            }
        
        public_difficulties = [r for r in results if r.is_public_difficulty]
        average_ratio = sum(r.difficulty_ratio for r in results) / len(results)
        
        # 找出最困难的知识点
        most_difficult = max(results, key=lambda r: r.difficulty_ratio) if results else None
        
        report = {
            "total_knowledge_points": len(results),
            "public_difficulties": len(public_difficulties),
            "public_difficulty_ratio": len(public_difficulties) / len(results) if results else 0.0,
            "average_difficulty_ratio": average_ratio,
            "most_difficult_kp": {
                "id": most_difficult.knowledge_point_id,
                "difficulty_ratio": most_difficult.difficulty_ratio,
                "recommendation": most_difficult.recommendation
            } if most_difficult else None
        }
        
        return report


# 使用示例
if __name__ == "__main__":
    from difficulty_detector import BehaviorData
    
    # 创建公共难点识别器
    detector = PublicDifficultyDetector(difficulty_ratio_threshold=0.3)
    
    # 模拟多个学生的行为数据
    all_students_behavior = [
        BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                    total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
        BehaviorData(user_id=2, knowledge_point_id=10, replay_count=2, pause_count=4,
                    total_watch_time=500.0, knowledge_point_duration=200.0, seek_count=1),
        BehaviorData(user_id=3, knowledge_point_id=10, replay_count=0, pause_count=1,
                    total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
        BehaviorData(user_id=4, knowledge_point_id=10, replay_count=4, pause_count=6,
                    total_watch_time=700.0, knowledge_point_duration=200.0, seek_count=3),
    ]
    
    # 执行检测
    result = detector.detect_public_difficulty(10, all_students_behavior)
    
    # 输出结果
    print("=" * 60)
    print("公共难点识别结果")
    print("=" * 60)
    print(f"知识点ID: {result.knowledge_point_id}")
    print(f"是否为公共难点: {result.is_public_difficulty}")
    print(f"困难学生比例: {result.difficulty_ratio:.1%}")
    print(f"平均困难度分数: {result.average_difficulty_score:.2f}/10")
    print(f"受影响学生: {result.affected_students}")
    print(f"教学建议: {result.recommendation}")
