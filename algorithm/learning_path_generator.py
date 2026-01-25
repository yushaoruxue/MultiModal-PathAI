"""
个性化学习路径生成算法

为每个学生生成定制化的学习顺序，考虑知识点依赖关系、掌握状态、疑难点等。
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import networkx as nx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PathNode:
    """路径节点"""
    knowledge_point_id: int
    order: int
    reason: str
    node_type: str = "knowledge_point"  # knowledge_point, remedial_resource


@dataclass
class NextSuggestion:
    """下一步学习建议"""
    next_knowledge_point_id: int
    reason: str
    estimated_time: float  # 预计学习时间（分钟）


class LearningPathGenerator:
    """学习路径生成器
    
    为每个学生生成个性化学习路径，考虑：
    - 知识点依赖关系（拓扑排序）
    - 掌握状态（跳过已掌握）
    - 疑难点（优先推送补偿资源）
    - 难度梯度（先易后难）
    """
    
    def __init__(
        self,
        difficulty_weights: Optional[Dict[str, int]] = None
    ):
        """初始化学习路径生成器
        
        Args:
            difficulty_weights: 难度权重，用于排序（easy=1, medium=2, hard=3）
        """
        self.difficulty_weights = difficulty_weights or {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
        
        logger.info("LearningPathGenerator initialized")
    
    def generate_path(
        self,
        user_id: int,
        mastery_status: Dict[int, str],
        dependencies: List[Tuple[int, int, str]],
        difficult_points: Optional[List[int]] = None,
        difficulty_info: Optional[Dict[int, str]] = None
    ) -> List[Dict]:
        """生成个性化学习路径
        
        算法步骤：
        1. 构建知识图谱（有向无环图DAG）
        2. 使用拓扑排序生成基础路径
        3. 根据掌握状态过滤已掌握的知识点
        4. 对疑难点进行特殊处理（插入补偿资源学习节点）
        5. 优化路径顺序（考虑难度梯度）
        
        Args:
            user_id: 用户ID
            mastery_status: 掌握状态字典 {knowledge_point_id: status}
                status: "未学" | "学习中" | "疑难" | "已掌握"
            dependencies: 依赖关系列表 [(source_id, target_id, relation_type), ...]
                relation_type: "prerequisite" | "related" | "contains"
            difficult_points: 疑难点列表（可选）
            difficulty_info: 难度信息字典 {knowledge_point_id: difficulty}（可选）
                difficulty: "easy" | "medium" | "hard"
        
        Returns:
            学习路径序列，每个元素包含：
            - knowledge_point_id: 知识点ID
            - order: 顺序（从1开始）
            - reason: 推荐原因
            - node_type: 节点类型（knowledge_point 或 remedial_resource）
        """
        try:
            logger.info(f"Generating learning path for user {user_id}")
            
            # 1. 构建知识图谱
            graph = self._build_dependency_graph(dependencies)
            
            # 2. 获取所有知识点ID
            all_kp_ids = set(mastery_status.keys())
            if dependencies:
                all_kp_ids.update([dep[0] for dep in dependencies])
                all_kp_ids.update([dep[1] for dep in dependencies])
            
            # 3. 过滤已掌握的知识点
            unmastered_kp_ids = self.filter_mastered(list(all_kp_ids), mastery_status)
            
            if not unmastered_kp_ids:
                logger.info("All knowledge points are mastered")
                return []
            
            # 4. 拓扑排序生成基础路径
            base_path = self.topological_sort(graph, mastery_status, unmastered_kp_ids)
            
            # 5. 对疑难点进行特殊处理
            if difficult_points:
                path_with_remedial = self.insert_remedial_resources(
                    base_path, difficult_points, mastery_status
                )
            else:
                path_with_remedial = base_path
            
            # 6. 优化路径顺序（考虑难度梯度）
            if difficulty_info:
                optimized_path = self.optimize_path_order(path_with_remedial, difficulty_info)
            else:
                optimized_path = path_with_remedial
            
            # 7. 添加推荐原因
            final_path = self._add_recommendation_reasons(optimized_path, mastery_status, difficulty_info)
            
            logger.info(f"Path generated: {len(final_path)} nodes")
            return final_path
            
        except Exception as e:
            logger.error(f"Error generating path: {e}", exc_info=True)
            raise
    
    def topological_sort(
        self,
        graph: nx.DiGraph,
        mastery_status: Dict[int, str],
        unmastered_kp_ids: List[int]
    ) -> List[int]:
        """拓扑排序生成基础路径
        
        只考虑前置依赖关系（prerequisite），确保前置知识先学。
        
        Args:
            graph: 知识图谱
            mastery_status: 掌握状态
            unmastered_kp_ids: 未掌握的知识点ID列表
        
        Returns:
            排序后的知识点ID列表
        """
        try:
            # 创建子图（只包含未掌握的知识点和前置依赖边）
            subgraph = graph.subgraph(unmastered_kp_ids).copy()
            
            # 只保留前置依赖边
            edges_to_remove = []
            for u, v, data in subgraph.edges(data=True):
                if data.get('relation_type') != 'prerequisite':
                    edges_to_remove.append((u, v))
            subgraph.remove_edges_from(edges_to_remove)
            
            # 拓扑排序
            try:
                sorted_nodes = list(nx.topological_sort(subgraph))
            except nx.NetworkXError:
                # 如果有循环，使用其他排序方法
                logger.warning("Cycle detected in graph, using alternative sorting")
                sorted_nodes = self._alternative_sort(subgraph, unmastered_kp_ids)
            
            # 确保所有未掌握的知识点都在路径中
            for kp_id in unmastered_kp_ids:
                if kp_id not in sorted_nodes:
                    sorted_nodes.append(kp_id)
            
            return sorted_nodes
            
        except Exception as e:
            logger.warning(f"Error in topological sort: {e}")
            # 如果排序失败，返回原始顺序
            return unmastered_kp_ids
    
    def filter_mastered(
        self,
        knowledge_points: List[int],
        mastery_status: Dict[int, str]
    ) -> List[int]:
        """过滤已掌握的知识点
        
        Args:
            knowledge_points: 知识点ID列表
            mastery_status: 掌握状态字典
        
        Returns:
            未掌握的知识点ID列表
        """
        unmastered = [
            kp_id for kp_id in knowledge_points
            if mastery_status.get(kp_id, "未学") != "已掌握"
        ]
        
        logger.debug(f"Filtered: {len(knowledge_points)} -> {len(unmastered)} unmastered")
        return unmastered
    
    def insert_remedial_resources(
        self,
        path: List[int],
        difficult_points: List[int],
        mastery_status: Dict[int, str]
    ) -> List[Dict]:
        """插入补偿资源学习节点
        
        对疑难点，在知识点之前插入补偿资源学习节点。
        
        Args:
            path: 基础路径（知识点ID列表）
            difficult_points: 疑难点列表
            mastery_status: 掌握状态
        
        Returns:
            包含补偿资源节点的路径
        """
        result = []
        order = 1
        
        for kp_id in path:
            # 如果是疑难点，先插入补偿资源节点
            if kp_id in difficult_points and mastery_status.get(kp_id) == "疑难":
                result.append({
                    "knowledge_point_id": kp_id,
                    "order": order,
                    "reason": "疑难点，需要先学习补偿资源",
                    "node_type": "remedial_resource"
                })
                order += 1
            
            # 添加知识点节点
            result.append({
                "knowledge_point_id": kp_id,
                "order": order,
                "reason": "按依赖关系学习",
                "node_type": "knowledge_point"
            })
            order += 1
        
        return result
    
    def optimize_path_order(
        self,
        path: List[Dict],
        difficulty_info: Dict[int, str]
    ) -> List[Dict]:
        """优化路径顺序（考虑难度梯度）
        
        在满足依赖关系的前提下，尽量先易后难。
        
        Args:
            path: 当前路径
            difficulty_info: 难度信息字典
        
        Returns:
            优化后的路径
        """
        # 将路径按节点类型分组
        knowledge_point_nodes = [node for node in path if node.get("node_type") == "knowledge_point"]
        other_nodes = [node for node in path if node.get("node_type") != "knowledge_point"]
        
        # 对知识点节点按难度排序
        def get_difficulty_weight(node):
            kp_id = node["knowledge_point_id"]
            difficulty = difficulty_info.get(kp_id, "medium")
            return self.difficulty_weights.get(difficulty, 2)
        
        # 保持原有顺序，但在同级别内按难度排序
        # 这里简化处理：只对相邻的相同难度节点进行微调
        sorted_kp_nodes = sorted(knowledge_point_nodes, key=get_difficulty_weight)
        
        # 重新组合路径（保持补偿资源节点在对应知识点之前）
        result = []
        used_kp_ids = set()
        
        # 先添加补偿资源节点和对应的知识点
        for node in path:
            if node.get("node_type") == "remedial_resource":
                result.append(node)
                # 找到对应的知识点节点
                kp_id = node["knowledge_point_id"]
                kp_node = next(
                    (n for n in knowledge_point_nodes if n["knowledge_point_id"] == kp_id),
                    None
                )
                if kp_node:
                    result.append(kp_node)
                    used_kp_ids.add(kp_id)
        
        # 添加剩余的知识点节点
        for node in sorted_kp_nodes:
            if node["knowledge_point_id"] not in used_kp_ids:
                result.append(node)
        
        # 重新编号
        for i, node in enumerate(result, 1):
            node["order"] = i
        
        return result
    
    def get_next_suggestion(
        self,
        path: List[Dict],
        current_position: int = 0
    ) -> Optional[NextSuggestion]:
        """获取下一步学习建议
        
        Args:
            path: 学习路径
            current_position: 当前位置（路径索引，从0开始）
        
        Returns:
            下一步学习建议，如果已到路径末尾则返回None
        """
        if current_position >= len(path):
            return None
        
        next_node = path[current_position]
        kp_id = next_node["knowledge_point_id"]
        reason = next_node.get("reason", "继续学习路径")
        
        # 估算学习时间（简单规则）
        estimated_time = self._estimate_learning_time(next_node)
        
        return NextSuggestion(
            next_knowledge_point_id=kp_id,
            reason=reason,
            estimated_time=estimated_time
        )
    
    def _build_dependency_graph(
        self,
        dependencies: List[Tuple[int, int, str]]
    ) -> nx.DiGraph:
        """构建依赖关系图
        
        Args:
            dependencies: 依赖关系列表
        
        Returns:
            有向图
        """
        graph = nx.DiGraph()
        
        for source_id, target_id, relation_type in dependencies:
            graph.add_edge(source_id, target_id, relation_type=relation_type)
        
        return graph
    
    def _alternative_sort(
        self,
        graph: nx.DiGraph,
        kp_ids: List[int]
    ) -> List[int]:
        """替代排序方法（当存在循环时）
        
        Args:
            graph: 知识图谱
            kp_ids: 知识点ID列表
        
        Returns:
            排序后的列表
        """
        # 简单实现：按入度排序（入度小的先学）
        in_degrees = dict(graph.in_degree(kp_ids))
        sorted_ids = sorted(kp_ids, key=lambda x: in_degrees.get(x, 0))
        return sorted_ids
    
    def _add_recommendation_reasons(
        self,
        path: List[Dict],
        mastery_status: Dict[int, str],
        difficulty_info: Optional[Dict[int, str]]
    ) -> List[Dict]:
        """添加推荐原因
        
        Args:
            path: 路径列表
            mastery_status: 掌握状态
            difficulty_info: 难度信息
        
        Returns:
            添加了推荐原因的路径
        """
        for node in path:
            kp_id = node["knowledge_point_id"]
            
            # 如果还没有推荐原因，生成一个
            if not node.get("reason") or node["reason"] == "按依赖关系学习":
                status = mastery_status.get(kp_id, "未学")
                difficulty = difficulty_info.get(kp_id, "medium") if difficulty_info else "medium"
                
                if status == "疑难":
                    node["reason"] = f"疑难点，需要重点学习（难度：{difficulty}）"
                elif status == "学习中":
                    node["reason"] = f"继续学习（难度：{difficulty}）"
                else:
                    node["reason"] = f"新知识点（难度：{difficulty}）"
        
        return path
    
    def _estimate_learning_time(self, node: Dict) -> float:
        """估算学习时间（分钟）
        
        Args:
            node: 路径节点
        
        Returns:
            预计学习时间（分钟）
        """
        # 简单规则：
        # - 补偿资源：10-15分钟
        # - 知识点：根据难度估算
        if node.get("node_type") == "remedial_resource":
            return 12.0  # 平均12分钟
        
        # 知识点时间根据难度估算（这里简化处理）
        return 15.0  # 默认15分钟


# 使用示例
if __name__ == "__main__":
    from tests.mock_data import MOCK_MASTERY_STATUS, MOCK_DEPENDENCIES
    
    # 创建路径生成器
    generator = LearningPathGenerator()
    
    # 模拟数据
    mastery_status = MOCK_MASTERY_STATUS
    dependencies = MOCK_DEPENDENCIES
    difficult_points = [3, 6]  # 疑难点
    difficulty_info = {
        1: "easy",
        2: "medium",
        3: "hard",
        4: "medium",
        5: "easy",
        6: "hard"
    }
    
    # 生成路径
    path = generator.generate_path(
        user_id=1,
        mastery_status=mastery_status,
        dependencies=dependencies,
        difficult_points=difficult_points,
        difficulty_info=difficulty_info
    )
    
    # 输出结果
    print("=" * 60)
    print("个性化学习路径")
    print("=" * 60)
    for node in path:
        print(f"\n顺序 {node['order']}: 知识点 {node['knowledge_point_id']}")
        print(f"  类型: {node['node_type']}")
        print(f"  原因: {node['reason']}")
    
    # 获取下一步建议
    suggestion = generator.get_next_suggestion(path, current_position=0)
    if suggestion:
        print("\n" + "=" * 60)
        print("下一步学习建议")
        print("=" * 60)
        print(f"知识点ID: {suggestion.next_knowledge_point_id}")
        print(f"原因: {suggestion.reason}")
        print(f"预计时间: {suggestion.estimated_time:.1f} 分钟")
