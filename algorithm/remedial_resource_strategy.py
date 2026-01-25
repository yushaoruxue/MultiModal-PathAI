"""
补偿资源推送策略

设计智能的资源推送机制，使用状态机管理推送状态。
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """困难等级"""
    FIRST = "first"      # 首次卡顿
    SECOND = "second"    # 二次卡顿
    THIRD = "third"       # 三次卡顿


@dataclass
class PushStrategy:
    """推送策略"""
    level: DifficultyLevel
    resources: List[str]  # 资源类型列表：knowledge_card, exercise, example, tutor
    notify_teacher: bool = False


@dataclass
class PushRecord:
    """推送记录"""
    user_id: int
    knowledge_point_id: int
    timestamp: datetime
    strategy_level: DifficultyLevel
    feedback: Optional[str] = None  # "mastered", "still_difficult", None


class RemedialResourceStrategy:
    """补偿资源推送策略
    
    使用状态机管理推送状态，根据学生的困难程度推送不同级别的资源。
    """
    
    def __init__(
        self,
        push_timeout: int = 300,  # 5分钟（秒）
        max_push_per_day: int = 3,
        push_interval: int = 1800,  # 30分钟（秒）
        exercise_threshold: float = 0.8  # 练习正确率阈值
    ):
        """初始化补偿资源推送策略
        
        Args:
            push_timeout: 推送超时时间（秒），必须在此时限内推送
            max_push_per_day: 同一知识点每天最多推送次数
            push_interval: 推送间隔（秒）
            exercise_threshold: 练习正确率阈值（0-1）
        """
        self.push_timeout = push_timeout
        self.max_push_per_day = max_push_per_day
        self.push_interval = push_interval
        self.exercise_threshold = exercise_threshold
        
        # 推送历史记录
        self.push_history: List[PushRecord] = []
        
        # 推送状态：{user_id: {knowledge_point_id: DifficultyLevel}}
        self.push_states: Dict[int, Dict[int, DifficultyLevel]] = {}
        
        logger.info("RemedialResourceStrategy initialized")
    
    def should_push_resource(
        self,
        knowledge_point_id: int,
        user_id: int
    ) -> bool:
        """判断是否应该推送资源
        
        检查条件：
        1. 是否在超时时间内
        2. 是否超过每日推送限制
        3. 是否满足推送间隔
        
        Args:
            knowledge_point_id: 知识点ID
            user_id: 用户ID
        
        Returns:
            是否应该推送
        """
        # 检查干预疲劳
        if self.check_intervention_fatigue(user_id, knowledge_point_id):
            logger.debug(f"Intervention fatigue detected for user {user_id}, kp {knowledge_point_id}")
            return False
        
        # 检查推送间隔
        if not self._check_push_interval(user_id, knowledge_point_id):
            logger.debug(f"Push interval not met for user {user_id}, kp {knowledge_point_id}")
            return False
        
        return True
    
    def get_push_strategy(
        self,
        difficulty_level: DifficultyLevel,
        attempt_count: int
    ) -> PushStrategy:
        """获取推送策略
        
        根据困难等级和尝试次数确定推送策略。
        
        Args:
            difficulty_level: 困难等级
            attempt_count: 尝试次数
        
        Returns:
            推送策略
        """
        if difficulty_level == DifficultyLevel.FIRST or attempt_count == 1:
            return PushStrategy(
                level=DifficultyLevel.FIRST,
                resources=["knowledge_card", "exercise"],
                notify_teacher=False
            )
        
        elif difficulty_level == DifficultyLevel.SECOND or attempt_count == 2:
            return PushStrategy(
                level=DifficultyLevel.SECOND,
                resources=["knowledge_card", "exercise", "example"],
                notify_teacher=False
            )
        
        else:  # THIRD or attempt_count >= 3
            return PushStrategy(
                level=DifficultyLevel.THIRD,
                resources=["knowledge_card", "exercise", "example", "tutor"],
                notify_teacher=True
            )
    
    def push_resource(
        self,
        user_id: int,
        knowledge_point_id: int,
        strategy: PushStrategy
    ) -> bool:
        """推送资源
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            strategy: 推送策略
        
        Returns:
            是否推送成功
        """
        try:
            if not self.should_push_resource(knowledge_point_id, user_id):
                return False
            
            # 记录推送
            record = PushRecord(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                timestamp=datetime.now(),
                strategy_level=strategy.level
            )
            self.push_history.append(record)
            
            # 更新推送状态
            if user_id not in self.push_states:
                self.push_states[user_id] = {}
            self.push_states[user_id][knowledge_point_id] = strategy.level
            
            logger.info(f"Resource pushed: user={user_id}, kp={knowledge_point_id}, level={strategy.level.value}")
            logger.info(f"Resources: {', '.join(strategy.resources)}")
            
            if strategy.notify_teacher:
                logger.info(f"Teacher notified for user {user_id}, kp {knowledge_point_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error pushing resource: {e}", exc_info=True)
            return False
    
    def handle_feedback(
        self,
        user_id: int,
        resource_id: int,
        feedback_type: str,
        exercise_score: Optional[float] = None
    ) -> Dict:
        """处理反馈
        
        根据学生反馈决定下一步行动。
        
        Args:
            user_id: 用户ID
            resource_id: 资源ID（这里简化为知识点ID）
            feedback_type: 反馈类型（"mastered", "still_difficult"）
            exercise_score: 练习得分（0-1），如果提供则用于判断
        
        Returns:
            处理结果字典，包含：
            - action: 下一步行动（"continue", "upgrade", "notify_teacher"）
            - next_strategy: 下一个推送策略（如果需要）
        """
        knowledge_point_id = resource_id  # 简化处理
        
        # 更新推送记录
        recent_record = self._get_recent_push_record(user_id, knowledge_point_id)
        if recent_record:
            recent_record.feedback = feedback_type
        
        # 判断下一步行动
        if feedback_type == "mastered" or (exercise_score and exercise_score >= self.exercise_threshold):
            # 已掌握，继续学习路径
            action = "continue"
            # 清除推送状态
            if user_id in self.push_states and knowledge_point_id in self.push_states[user_id]:
                del self.push_states[user_id][knowledge_point_id]
            
            return {
                "action": action,
                "message": "已掌握，继续学习路径"
            }
        
        elif feedback_type == "still_difficult" or (exercise_score and exercise_score < self.exercise_threshold):
            # 仍不懂，升级干预
            current_level = self.push_states.get(user_id, {}).get(knowledge_point_id, DifficultyLevel.FIRST)
            
            if current_level == DifficultyLevel.FIRST:
                next_level = DifficultyLevel.SECOND
            elif current_level == DifficultyLevel.SECOND:
                next_level = DifficultyLevel.THIRD
            else:
                next_level = DifficultyLevel.THIRD
            
            next_strategy = self.get_push_strategy(next_level, 0)
            
            return {
                "action": "upgrade",
                "next_strategy": {
                    "level": next_strategy.level.value,
                    "resources": next_strategy.resources
                },
                "message": f"升级干预到 {next_level.value} 级别"
            }
        
        else:
            return {
                "action": "wait",
                "message": "等待更多反馈"
            }
    
    def check_intervention_fatigue(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> bool:
        """检查干预疲劳
        
        同一知识点24小时内最多推送3次。
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            是否达到干预疲劳（True表示应该停止推送）
        """
        # 获取24小时内的推送记录
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        recent_pushes = [
            record for record in self.push_history
            if record.user_id == user_id
            and record.knowledge_point_id == knowledge_point_id
            and record.timestamp >= cutoff_time
        ]
        
        if len(recent_pushes) >= self.max_push_per_day:
            logger.warning(f"Intervention fatigue: {len(recent_pushes)} pushes in 24h for user {user_id}, kp {knowledge_point_id}")
            return True
        
        return False
    
    def get_priority(
        self,
        knowledge_point_ids: List[int],
        dependencies: Optional[List[Tuple[int, int, str]]] = None
    ) -> List[int]:
        """获取知识点优先级
        
        如果学生连续标记多个知识点为疑难，优先推送最重要的（依赖关系最多的）。
        
        Args:
            knowledge_point_ids: 疑难点ID列表
            dependencies: 依赖关系列表（可选）
        
        Returns:
            按优先级排序的知识点ID列表
        """
        if not dependencies:
            # 如果没有依赖关系，保持原顺序
            return knowledge_point_ids
        
        # 计算每个知识点的依赖数量（有多少知识点依赖它）
        dependency_count = {}
        for kp_id in knowledge_point_ids:
            count = sum(1 for dep in dependencies if dep[1] == kp_id and dep[2] == "prerequisite")
            dependency_count[kp_id] = count
        
        # 按依赖数量降序排序
        sorted_ids = sorted(knowledge_point_ids, key=lambda x: dependency_count.get(x, 0), reverse=True)
        
        return sorted_ids
    
    def _check_push_interval(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> bool:
        """检查推送间隔
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            是否满足推送间隔要求
        """
        # 获取最近的推送记录
        recent_record = self._get_recent_push_record(user_id, knowledge_point_id)
        
        if not recent_record:
            return True  # 没有历史记录，可以推送
        
        # 检查时间间隔
        time_since_last_push = (datetime.now() - recent_record.timestamp).total_seconds()
        
        return time_since_last_push >= self.push_interval
    
    def _get_recent_push_record(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> Optional[PushRecord]:
        """获取最近的推送记录
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
        
        Returns:
            最近的推送记录，如果没有则返回None
        """
        records = [
            record for record in self.push_history
            if record.user_id == user_id and record.knowledge_point_id == knowledge_point_id
        ]
        
        if not records:
            return None
        
        # 返回最近的记录
        return max(records, key=lambda r: r.timestamp)
    
    def get_push_history(
        self,
        user_id: Optional[int] = None,
        knowledge_point_id: Optional[int] = None
    ) -> List[PushRecord]:
        """获取推送历史
        
        Args:
            user_id: 用户ID（可选，用于筛选）
            knowledge_point_id: 知识点ID（可选，用于筛选）
        
        Returns:
            推送记录列表
        """
        records = self.push_history
        
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        
        if knowledge_point_id is not None:
            records = [r for r in records if r.knowledge_point_id == knowledge_point_id]
        
        return records


# 状态机图（Mermaid格式）
STATEMACHINE_DIAGRAM = """
```mermaid
stateDiagram-v2
    [*] --> FirstAttempt: 知识点标记为疑难
    
    FirstAttempt --> PushLevel1: 首次卡顿
    PushLevel1 --> WaitFeedback1: 推送知识卡片+练习
    
    WaitFeedback1 --> Continue: 练习正确率>=80%或反馈"已掌握"
    WaitFeedback1 --> SecondAttempt: 练习正确率<80%或反馈"仍不懂"
    
    SecondAttempt --> PushLevel2: 二次卡顿
    PushLevel2 --> WaitFeedback2: 推送知识卡片+练习+例题
    
    WaitFeedback2 --> Continue: 练习正确率>=80%或反馈"已掌握"
    WaitFeedback2 --> ThirdAttempt: 练习正确率<80%或反馈"仍不懂"
    
    ThirdAttempt --> PushLevel3: 三次卡顿
    PushLevel3 --> WaitFeedback3: 推送知识卡片+练习+例题+答疑
    PushLevel3 --> NotifyTeacher: 通知教师
    
    WaitFeedback3 --> Continue: 练习正确率>=80%或反馈"已掌握"
    WaitFeedback3 --> [*]: 练习正确率<80%或反馈"仍不懂"
    
    Continue --> [*]: 继续学习路径
    NotifyTeacher --> [*]
```
"""


# 使用示例
if __name__ == "__main__":
    from datetime import datetime
    
    # 创建推送策略
    strategy = RemedialResourceStrategy()
    
    # 模拟：学生标记知识点为疑难
    user_id = 1
    kp_id = 10
    
    # 检查是否应该推送
    if strategy.should_push_resource(kp_id, user_id):
        # 获取推送策略（首次卡顿）
        push_strategy = strategy.get_push_strategy(DifficultyLevel.FIRST, attempt_count=1)
        
        # 推送资源
        success = strategy.push_resource(user_id, kp_id, push_strategy)
        
        if success:
            print("=" * 60)
            print("补偿资源推送")
            print("=" * 60)
            print(f"用户ID: {user_id}")
            print(f"知识点ID: {kp_id}")
            print(f"推送级别: {push_strategy.level.value}")
            print(f"推送资源: {', '.join(push_strategy.resources)}")
            
            # 模拟反馈：练习得分60%
            feedback_result = strategy.handle_feedback(
                user_id=user_id,
                resource_id=kp_id,
                feedback_type="still_difficult",
                exercise_score=0.6
            )
            
            print(f"\n反馈处理结果:")
            print(f"  行动: {feedback_result['action']}")
            print(f"  消息: {feedback_result.get('message', '')}")
            
            if feedback_result['action'] == 'upgrade':
                print(f"  下一级别: {feedback_result['next_strategy']['level']}")
                print(f"  下一资源: {', '.join(feedback_result['next_strategy']['resources'])}")
