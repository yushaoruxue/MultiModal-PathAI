"""
补偿资源推送机制

将生成的资源推送给学生，支持多种推送方式。
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Resource:
    """资源对象"""
    resource_id: str
    user_id: int
    knowledge_point_id: int
    resource_type: str  # knowledge_card, exercise, video
    content: str  # Markdown或JSON格式的内容
    created_at: datetime
    status: str = "pending"  # pending, sent, read


class ResourcePusher:
    """资源推送器
    
    将生成的补偿资源推送给学生，支持多种推送方式。
    """
    
    def __init__(
        self,
        push_method: str = "database",  # websocket, message_queue, database
        max_retries: int = 3
    ):
        """初始化资源推送器
        
        Args:
            push_method: 推送方式（websocket, message_queue, database）
            max_retries: 最大重试次数
        """
        self.push_method = push_method
        self.max_retries = max_retries
        
        # 推送历史（模拟数据库）
        self.push_history: List[Resource] = []
        
        # 待推送资源（模拟数据库）
        self.pending_resources: Dict[int, List[Resource]] = {}
        
        logger.info(f"ResourcePusher initialized with method: {push_method}")
    
    def push_resource(
        self,
        user_id: int,
        knowledge_point_id: int,
        resource_type: str,
        resource_content: str
    ) -> bool:
        """推送资源
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            resource_type: 资源类型（knowledge_card, exercise, video）
            resource_content: 资源内容（Markdown或JSON格式）
        
        Returns:
            是否推送成功
        """
        try:
            logger.info(f"Pushing resource: user={user_id}, kp={knowledge_point_id}, type={resource_type}")
            
            # 创建资源对象
            resource_id = f"{user_id}_{knowledge_point_id}_{resource_type}_{datetime.now().timestamp()}"
            resource = Resource(
                resource_id=resource_id,
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                resource_type=resource_type,
                content=resource_content,
                created_at=datetime.now(),
                status="pending"
            )
            
            # 根据推送方式推送
            success = False
            if self.push_method == "websocket":
                success = self.push_via_websocket(user_id, resource)
            elif self.push_method == "message_queue":
                success = self.push_via_message_queue(user_id, resource)
            else:  # database
                success = self.push_via_database(user_id, resource)
            
            if success:
                resource.status = "sent"
                logger.info(f"Resource pushed successfully: {resource_id}")
            else:
                logger.warning(f"Failed to push resource: {resource_id}")
            
            # 记录推送历史
            self.push_history.append(resource)
            
            return success
            
        except Exception as e:
            logger.error(f"Error pushing resource: {e}", exc_info=True)
            return False
    
    def push_via_websocket(self, user_id: int, resource: Resource) -> bool:
        """通过WebSocket推送资源
        
        Args:
            user_id: 用户ID
            resource: 资源对象
        
        Returns:
            是否推送成功
        """
        try:
            # 模拟WebSocket推送
            logger.debug(f"Pushing via WebSocket to user {user_id}")
            # 实际实现中，这里会连接到WebSocket服务器并发送消息
            # websocket.send(user_id, json.dumps(resource.__dict__))
            return True
        except Exception as e:
            logger.error(f"Error pushing via WebSocket: {e}")
            return False
    
    def push_via_message_queue(self, user_id: int, resource: Resource) -> bool:
        """通过消息队列推送资源
        
        Args:
            user_id: 用户ID
            resource: 资源对象
        
        Returns:
            是否推送成功
        """
        try:
            # 模拟消息队列推送
            logger.debug(f"Pushing via message queue to user {user_id}")
            # 实际实现中，这里会发送消息到RabbitMQ/Kafka
            # queue.publish("resource_push", json.dumps(resource.__dict__))
            return True
        except Exception as e:
            logger.error(f"Error pushing via message queue: {e}")
            return False
    
    def push_via_database(self, user_id: int, resource: Resource) -> bool:
        """通过数据库推送资源（学生登录时查询）
        
        Args:
            user_id: 用户ID
            resource: 资源对象
        
        Returns:
            是否推送成功
        """
        try:
            # 将资源添加到待推送列表
            if user_id not in self.pending_resources:
                self.pending_resources[user_id] = []
            
            self.pending_resources[user_id].append(resource)
            
            logger.debug(f"Resource added to database for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error pushing via database: {e}")
            return False
    
    def get_pending_resources(self, user_id: int) -> List[Dict]:
        """获取待推送资源列表
        
        Args:
            user_id: 用户ID
        
        Returns:
            待推送资源列表
        """
        if user_id not in self.pending_resources:
            return []
        
        resources = self.pending_resources[user_id]
        
        # 转换为字典格式
        result = []
        for resource in resources:
            if resource.status == "pending":
                result.append({
                    "resource_id": resource.resource_id,
                    "knowledge_point_id": resource.knowledge_point_id,
                    "resource_type": resource.resource_type,
                    "content": resource.content,
                    "created_at": resource.created_at.isoformat()
                })
        
        return result
    
    def mark_as_read(
        self,
        user_id: int,
        resource_id: str
    ) -> bool:
        """标记资源为已读
        
        Args:
            user_id: 用户ID
            resource_id: 资源ID
        
        Returns:
            是否标记成功
        """
        try:
            if user_id not in self.pending_resources:
                return False
            
            # 查找资源
            for resource in self.pending_resources[user_id]:
                if resource.resource_id == resource_id:
                    resource.status = "read"
                    logger.info(f"Resource marked as read: {resource_id}")
                    return True
            
            # 也在历史记录中查找
            for resource in self.push_history:
                if resource.resource_id == resource_id and resource.user_id == user_id:
                    resource.status = "read"
                    return True
            
            logger.warning(f"Resource not found: {resource_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error marking resource as read: {e}")
            return False
    
    def batch_push(
        self,
        resources: List[Dict]
    ) -> Dict[str, int]:
        """批量推送资源
        
        Args:
            resources: 资源列表，每个资源包含 user_id, knowledge_point_id, resource_type, content
        
        Returns:
            推送结果统计：{"success": count, "failed": count}
        """
        success_count = 0
        failed_count = 0
        
        for resource_data in resources:
            success = self.push_resource(
                user_id=resource_data["user_id"],
                knowledge_point_id=resource_data["knowledge_point_id"],
                resource_type=resource_data["resource_type"],
                resource_content=resource_data["content"]
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Batch push completed: {success_count} success, {failed_count} failed")
        
        return {
            "success": success_count,
            "failed": failed_count
        }


# 使用示例
if __name__ == "__main__":
    # 创建推送器
    pusher = ResourcePusher(push_method="database")
    
    # 推送知识卡片
    knowledge_card_content = """# 函数定义

## 核心概念
函数是一种映射关系，它将输入映射到输出。
"""
    
    success = pusher.push_resource(
        user_id=1,
        knowledge_point_id=10,
        resource_type="knowledge_card",
        resource_content=knowledge_card_content
    )
    
    print(f"推送结果: {'成功' if success else '失败'}")
    
    # 获取待推送资源
    pending = pusher.get_pending_resources(1)
    print(f"待推送资源数: {len(pending)}")
    
    # 标记为已读
    if pending:
        pusher.mark_as_read(1, pending[0]["resource_id"])
        print("资源已标记为已读")
