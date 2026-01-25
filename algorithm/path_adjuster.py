"""
学习路径动态调整逻辑

根据学生的学习进度实时调整路径，支持增量调整。
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from learning_path_generator import LearningPathGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LearningEvent:
    """学习事件"""
    event_type: str  # "completed", "mastered", "difficult", "remedial_completed"
    knowledge_point_id: int
    timestamp: datetime
    metadata: Optional[Dict] = None


@dataclass
class AdjustmentResult:
    """调整结果"""
    adjusted_path: List[Dict]
    adjustment_reason: str
    next_action: str


class PathAdjuster:
    """路径调整器
    
    根据学生的学习进度实时调整路径，支持增量调整。
    """
    
    def __init__(
        self,
        path_generator: Optional[LearningPathGenerator] = None
    ):
        """初始化路径调整器
        
        Args:
            path_generator: 路径生成器实例，如果为None则创建新实例
        """
        self.path_generator = path_generator or LearningPathGenerator()
        self.adjustment_history: List[Dict] = []
        
        logger.info("PathAdjuster initialized")
    
    def adjust_path(
        self,
        current_path: List[Dict],
        learning_event: LearningEvent,
        progress: Optional[Dict] = None
    ) -> AdjustmentResult:
        """调整学习路径
        
        根据学习事件类型调用相应的处理方法。
        
        Args:
            current_path: 当前学习路径
            learning_event: 学习事件
            progress: 学习进度信息（可选）
        
        Returns:
            调整结果
        """
        try:
            logger.info(f"Adjusting path for event: {learning_event.event_type}, kp_id: {learning_event.knowledge_point_id}")
            
            # 根据事件类型处理
            if learning_event.event_type == "mastered":
                adjusted_path = self.handle_mastery_event(current_path, learning_event.knowledge_point_id)
                reason = self.get_adjustment_reason("mastered", learning_event.knowledge_point_id)
                next_action = "继续学习下一个知识点"
                
            elif learning_event.event_type == "difficult":
                adjusted_path = self.handle_difficulty_event(current_path, learning_event.knowledge_point_id)
                reason = self.get_adjustment_reason("difficult", learning_event.knowledge_point_id)
                next_action = "学习补偿资源，然后重新尝试"
                
            elif learning_event.event_type == "completed":
                adjusted_path = self.handle_completion_event(current_path, learning_event.knowledge_point_id)
                reason = self.get_adjustment_reason("completed", learning_event.knowledge_point_id)
                next_action = "评估掌握情况，决定下一步"
                
            elif learning_event.event_type == "remedial_completed":
                adjusted_path = self.handle_remedial_completion(current_path, learning_event.knowledge_point_id)
                reason = self.get_adjustment_reason("remedial_completed", learning_event.knowledge_point_id)
                next_action = "重新尝试学习该知识点"
                
            else:
                logger.warning(f"Unknown event type: {learning_event.event_type}")
                adjusted_path = current_path
                reason = "未知事件类型，路径未调整"
                next_action = "继续当前学习"
            
            # 根据学习速度优化（如果提供了进度信息）
            if progress and progress.get("learning_speed"):
                adjusted_path = self.optimize_for_speed(adjusted_path, progress["learning_speed"])
            
            # 记录调整历史
            self._record_adjustment(learning_event, reason, len(current_path), len(adjusted_path))
            
            result = AdjustmentResult(
                adjusted_path=adjusted_path,
                adjustment_reason=reason,
                next_action=next_action
            )
            
            logger.info(f"Path adjusted: {len(current_path)} -> {len(adjusted_path)} nodes")
            return result
            
        except Exception as e:
            logger.error(f"Error adjusting path: {e}", exc_info=True)
            raise
    
    def handle_mastery_event(
        self,
        path: List[Dict],
        kp_id: int
    ) -> List[Dict]:
        """处理掌握事件
        
        如果学生快速掌握了某个知识点，可以跳过相关的基础知识点。
        
        Args:
            path: 当前路径
            kp_id: 已掌握的知识点ID
        
        Returns:
            调整后的路径
        """
        # 从路径中移除已掌握的知识点
        adjusted_path = [
            node for node in path
            if node.get("knowledge_point_id") != kp_id or node.get("node_type") == "remedial_resource"
        ]
        
        # 移除对应的补偿资源节点（如果存在）
        adjusted_path = [
            node for node in adjusted_path
            if not (node.get("node_type") == "remedial_resource" and 
                   node.get("knowledge_point_id") == kp_id)
        ]
        
        # 重新编号
        for i, node in enumerate(adjusted_path, 1):
            node["order"] = i
        
        logger.debug(f"Removed mastered knowledge point {kp_id} from path")
        return adjusted_path
    
    def handle_difficulty_event(
        self,
        path: List[Dict],
        kp_id: int
    ) -> List[Dict]:
        """处理疑难事件
        
        如果学生遇到困难，插入更多的基础知识点或补偿资源。
        
        Args:
            path: 当前路径
            kp_id: 疑难知识点ID
        
        Returns:
            调整后的路径
        """
        adjusted_path = []
        
        for node in path:
            adjusted_path.append(node)
            
            # 如果遇到疑难点，在它之前插入补偿资源节点
            if node.get("knowledge_point_id") == kp_id and node.get("node_type") == "knowledge_point":
                # 检查是否已有补偿资源节点
                has_remedial = any(
                    n.get("knowledge_point_id") == kp_id and n.get("node_type") == "remedial_resource"
                    for n in adjusted_path
                )
                
                if not has_remedial:
                    # 插入补偿资源节点
                    remedial_node = {
                        "knowledge_point_id": kp_id,
                        "order": node["order"],
                        "reason": "疑难点，需要先学习补偿资源",
                        "node_type": "remedial_resource"
                    }
                    # 插入到当前节点之前
                    adjusted_path.insert(-1, remedial_node)
                    # 调整后续节点的顺序
                    for i, n in enumerate(adjusted_path[adjusted_path.index(remedial_node)+1:], 
                                       start=remedial_node["order"]+1):
                        n["order"] = i
        
        # 重新编号
        for i, node in enumerate(adjusted_path, 1):
            node["order"] = i
        
        logger.debug(f"Inserted remedial resource for difficult knowledge point {kp_id}")
        return adjusted_path
    
    def handle_completion_event(
        self,
        path: List[Dict],
        kp_id: int
    ) -> List[Dict]:
        """处理完成事件
        
        学生完成了一个知识点学习，标记为"学习中"状态。
        路径通常不需要大幅调整，但可以优化后续顺序。
        
        Args:
            path: 当前路径
            kp_id: 完成的知识点ID
        
        Returns:
            调整后的路径
        """
        # 完成事件通常不需要调整路径，只是标记进度
        # 但可以优化后续节点的顺序
        adjusted_path = path.copy()
        
        logger.debug(f"Knowledge point {kp_id} completed, path remains mostly unchanged")
        return adjusted_path
    
    def handle_remedial_completion(
        self,
        path: List[Dict],
        kp_id: int
    ) -> List[Dict]:
        """处理补偿资源完成事件
        
        学生完成了补偿资源学习，重新评估是否掌握。
        
        Args:
            path: 当前路径
            kp_id: 完成补偿资源的知识点ID
        
        Returns:
            调整后的路径
        """
        adjusted_path = []
        
        for node in path:
            # 移除已完成的补偿资源节点
            if node.get("knowledge_point_id") == kp_id and node.get("node_type") == "remedial_resource":
                continue
            
            adjusted_path.append(node)
        
        # 重新编号
        for i, node in enumerate(adjusted_path, 1):
            node["order"] = i
        
        logger.debug(f"Removed completed remedial resource for knowledge point {kp_id}")
        return adjusted_path
    
    def optimize_for_speed(
        self,
        path: List[Dict],
        learning_speed: str
    ) -> List[Dict]:
        """根据学习速度优化路径
        
        Args:
            path: 当前路径
            learning_speed: 学习速度（"fast", "normal", "slow"）
        
        Returns:
            优化后的路径
        """
        if learning_speed == "fast":
            # 快速学习者：可以跳过一些基础知识点，直接学习高级内容
            # 这里简化处理：保持原路径，但可以标记为"可跳过"
            logger.debug("Fast learner detected, keeping current path")
            return path
            
        elif learning_speed == "slow":
            # 慢速学习者：可能需要插入更多基础知识点
            # 这里简化处理：保持原路径，但可以标记为"需要更多时间"
            logger.debug("Slow learner detected, keeping current path")
            return path
            
        else:
            # 正常速度：保持原路径
            return path
    
    def get_adjustment_reason(
        self,
        event_type: str,
        kp_id: int
    ) -> str:
        """获取调整原因说明
        
        Args:
            event_type: 事件类型
            kp_id: 知识点ID
        
        Returns:
            调整原因文本
        """
        reasons = {
            "mastered": f"知识点 {kp_id} 已掌握，从路径中移除",
            "difficult": f"知识点 {kp_id} 标记为疑难，插入补偿资源",
            "completed": f"知识点 {kp_id} 学习完成，继续下一步",
            "remedial_completed": f"知识点 {kp_id} 的补偿资源学习完成，可以重新尝试"
        }
        
        return reasons.get(event_type, f"未知事件类型: {event_type}")
    
    def _record_adjustment(
        self,
        event: LearningEvent,
        reason: str,
        old_path_length: int,
        new_path_length: int
    ) -> None:
        """记录调整历史
        
        Args:
            event: 学习事件
            reason: 调整原因
            old_path_length: 调整前路径长度
            new_path_length: 调整后路径长度
        """
        record = {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "knowledge_point_id": event.knowledge_point_id,
            "reason": reason,
            "old_path_length": old_path_length,
            "new_path_length": new_path_length
        }
        
        self.adjustment_history.append(record)
        logger.debug(f"Adjustment recorded: {record}")
    
    def get_adjustment_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """获取调整历史
        
        Args:
            limit: 返回记录数量限制
        
        Returns:
            调整历史记录列表
        """
        if limit:
            return self.adjustment_history[-limit:]
        return self.adjustment_history


# 使用示例
if __name__ == "__main__":
    from datetime import datetime
    
    # 创建路径调整器
    adjuster = PathAdjuster()
    
    # 模拟当前路径
    current_path = [
        {"knowledge_point_id": 1, "order": 1, "reason": "基础知识点", "node_type": "knowledge_point"},
        {"knowledge_point_id": 2, "order": 2, "reason": "进阶知识点", "node_type": "knowledge_point"},
        {"knowledge_point_id": 3, "order": 3, "reason": "高级知识点", "node_type": "knowledge_point"},
    ]
    
    # 模拟学习事件：学生标记知识点2为疑难
    event = LearningEvent(
        event_type="difficult",
        knowledge_point_id=2,
        timestamp=datetime.now()
    )
    
    # 执行调整
    result = adjuster.adjust_path(current_path, event)
    
    # 输出结果
    print("=" * 60)
    print("路径调整结果")
    print("=" * 60)
    print(f"调整原因: {result.adjustment_reason}")
    print(f"下一步行动: {result.next_action}")
    print(f"\n调整后的路径:")
    for node in result.adjusted_path:
        print(f"  顺序 {node['order']}: 知识点 {node['knowledge_point_id']} ({node['node_type']})")
    
    # 查看调整历史
    history = adjuster.get_adjustment_history()
    print(f"\n调整历史记录数: {len(history)}")
