"""
知识图谱关系计算

分析知识点之间的依赖关系，构建知识图谱。
包括前置依赖、相关关系、包含关系的识别。
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import networkx as nx

# 导入语义相似度计算模块
try:
    from semantic_similarity import SemanticSimilarityCalculator
    SEMANTIC_SIMILARITY_AVAILABLE = True
except ImportError:
    SEMANTIC_SIMILARITY_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgePointInfo:
    """知识点信息"""
    id: int
    name: str
    summary: str
    keywords: List[str]
    start_time: float
    end_time: float


@dataclass
class KnowledgeRelation:
    """知识点关系"""
    source_id: int
    target_id: int
    relation_type: str  # prerequisite, related, contains
    confidence: float


class KnowledgeGraphBuilder:
    """知识图谱构建器
    
    分析知识点之间的依赖关系，构建知识图谱。
    支持前置依赖、相关关系、包含关系的识别。
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.6,
        keyword_overlap_threshold: float = 0.3,
        prerequisite_confidence: float = 0.8,
        use_advanced_similarity: bool = False
    ):
        """初始化知识图谱构建器
        
        Args:
            similarity_threshold: 语义相似度阈值，高于此值认为相关
            keyword_overlap_threshold: 关键词重叠阈值
            prerequisite_confidence: 前置依赖关系的默认置信度
            use_advanced_similarity: 是否使用sentence-transformers（需要安装）
        """
        self.similarity_threshold = similarity_threshold
        self.keyword_overlap_threshold = keyword_overlap_threshold
        self.prerequisite_confidence = prerequisite_confidence
        
        # 初始化语义相似度计算器
        if SEMANTIC_SIMILARITY_AVAILABLE and use_advanced_similarity:
            self.similarity_calculator = SemanticSimilarityCalculator(use_advanced=True)
            logger.info("Using advanced similarity calculation (sentence-transformers)")
        else:
            self.similarity_calculator = None
            logger.info("Using simple similarity calculation")
        
        logger.info("KnowledgeGraphBuilder initialized")
    
    def build_graph(self, knowledge_points: List[KnowledgePointInfo]) -> nx.DiGraph:
        """构建知识图谱
        
        构建包含所有知识点和关系的有向图。
        
        Args:
            knowledge_points: 知识点列表
        
        Returns:
            知识图谱（NetworkX有向图）
        """
        try:
            logger.info(f"Building knowledge graph with {len(knowledge_points)} knowledge points")
            
            # 创建有向图
            graph = nx.DiGraph()
            
            # 添加节点
            for kp in knowledge_points:
                graph.add_node(
                    kp.id,
                    name=kp.name,
                    summary=kp.summary,
                    keywords=kp.keywords,
                    start_time=kp.start_time,
                    end_time=kp.end_time
                )
            
            # 检测各种关系
            prerequisites = self.detect_prerequisites(knowledge_points)
            related = self.detect_related(knowledge_points)
            contains = self.detect_contains(knowledge_points)
            
            # 添加边
            for rel in prerequisites + related + contains:
                graph.add_edge(
                    rel.source_id,
                    rel.target_id,
                    relation_type=rel.relation_type,
                    confidence=rel.confidence
                )
            
            # 检测并处理循环依赖
            cycles = self.detect_cycles(graph)
            if cycles:
                logger.warning(f"Detected {len(cycles)} cycles, resolving...")
                graph = self.resolve_cycles(graph)
            
            logger.info(f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error building graph: {e}", exc_info=True)
            raise
    
    def detect_prerequisites(
        self,
        knowledge_points: List[KnowledgePointInfo]
    ) -> List[KnowledgeRelation]:
        """检测前置依赖关系
        
        判断依据：
        1. 知识点B的文本中提到了知识点A的概念
        2. 知识点A在知识点B之前（时序）
        
        Args:
            knowledge_points: 知识点列表（已按时间排序）
        
        Returns:
            前置依赖关系列表
        """
        relations = []
        
        for i, kp_a in enumerate(knowledge_points):
            for j, kp_b in enumerate(knowledge_points[i+1:], start=i+1):
                # 检查B的文本中是否提到A的概念
                if self._mentions_concept(kp_b, kp_a):
                    # 检查时序：A应该在B之前
                    if kp_a.end_time <= kp_b.start_time:
                        confidence = self._calculate_prerequisite_confidence(kp_a, kp_b)
                        relations.append(KnowledgeRelation(
                            source_id=kp_a.id,
                            target_id=kp_b.id,
                            relation_type="prerequisite",
                            confidence=confidence
                        ))
                        logger.debug(f"Prerequisite: {kp_a.name} -> {kp_b.name}")
        
        logger.info(f"Detected {len(relations)} prerequisite relations")
        return relations
    
    def detect_related(
        self,
        knowledge_points: List[KnowledgePointInfo]
    ) -> List[KnowledgeRelation]:
        """检测相关关系
        
        判断依据：
        1. 关键词重叠度高
        2. 语义相似度高
        
        Args:
            knowledge_points: 知识点列表
        
        Returns:
            相关关系列表
        """
        relations = []
        
        for i, kp_a in enumerate(knowledge_points):
            for j, kp_b in enumerate(knowledge_points[i+1:], start=i+1):
                # 计算关键词重叠度
                keyword_overlap = self._calculate_keyword_overlap(kp_a.keywords, kp_b.keywords)
                
                # 计算语义相似度（基于摘要）
                semantic_similarity = self._calculate_semantic_similarity(kp_a.summary, kp_b.summary)
                
                # 如果重叠度或相似度超过阈值，认为是相关关系
                if keyword_overlap >= self.keyword_overlap_threshold or \
                   semantic_similarity >= self.similarity_threshold:
                    confidence = (keyword_overlap + semantic_similarity) / 2
                    relations.append(KnowledgeRelation(
                        source_id=kp_a.id,
                        target_id=kp_b.id,
                        relation_type="related",
                        confidence=confidence
                    ))
                    logger.debug(f"Related: {kp_a.name} <-> {kp_b.name}")
        
        logger.info(f"Detected {len(relations)} related relations")
        return relations
    
    def detect_contains(
        self,
        knowledge_points: List[KnowledgePointInfo]
    ) -> List[KnowledgeRelation]:
        """检测包含关系
        
        判断依据：
        1. 知识点A的关键词包含知识点B的关键词
        2. 知识点A的摘要中提到知识点B的概念
        
        Args:
            knowledge_points: 知识点列表
        
        Returns:
            包含关系列表
        """
        relations = []
        
        for i, kp_a in enumerate(knowledge_points):
            for j, kp_b in enumerate(knowledge_points):
                if i == j:
                    continue
                
                # 检查A是否包含B
                if self._contains_concept(kp_a, kp_b):
                    confidence = self._calculate_contains_confidence(kp_a, kp_b)
                    relations.append(KnowledgeRelation(
                        source_id=kp_a.id,
                        target_id=kp_b.id,
                        relation_type="contains",
                        confidence=confidence
                    ))
                    logger.debug(f"Contains: {kp_a.name} -> {kp_b.name}")
        
        logger.info(f"Detected {len(relations)} contains relations")
        return relations
    
    def detect_cycles(self, graph: nx.DiGraph) -> List[List[int]]:
        """检测循环依赖
        
        Args:
            graph: 知识图谱
        
        Returns:
            循环依赖列表，每个循环是一个节点ID列表
        """
        try:
            cycles = list(nx.simple_cycles(graph))
            return cycles
        except Exception as e:
            logger.warning(f"Error detecting cycles: {e}")
            return []
    
    def resolve_cycles(self, graph: nx.DiGraph) -> nx.DiGraph:
        """解决循环依赖
        
        策略：移除置信度最低的边来打破循环。
        
        Args:
            graph: 包含循环的图
        
        Returns:
            解决循环后的图
        """
        cycles = self.detect_cycles(graph)
        if not cycles:
            return graph
        
        # 创建图的副本
        resolved_graph = graph.copy()
        
        # 对每个循环，移除置信度最低的边
        for cycle in cycles:
            if len(cycle) < 2:
                continue
            
            # 找到循环中置信度最低的边
            min_confidence = float('inf')
            edge_to_remove = None
            
            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]
                
                if resolved_graph.has_edge(source, target):
                    confidence = resolved_graph[source][target].get('confidence', 1.0)
                    if confidence < min_confidence:
                        min_confidence = confidence
                        edge_to_remove = (source, target)
            
            # 移除置信度最低的边
            if edge_to_remove:
                resolved_graph.remove_edge(*edge_to_remove)
                logger.info(f"Removed edge {edge_to_remove} to break cycle")
        
        return resolved_graph
    
    def _mentions_concept(
        self,
        kp_b: KnowledgePointInfo,
        kp_a: KnowledgePointInfo
    ) -> bool:
        """检查知识点B是否提到知识点A的概念
        
        Args:
            kp_b: 目标知识点
            kp_a: 源知识点
        
        Returns:
            是否提到
        """
        # 检查B的摘要或名称中是否包含A的关键词
        text_b = kp_b.summary + " " + kp_b.name
        
        for keyword in kp_a.keywords[:3]:  # 只检查前3个关键词
            if keyword in text_b:
                return True
        
        # 检查A的名称是否在B的文本中
        if kp_a.name in text_b:
            return True
        
        return False
    
    def _contains_concept(
        self,
        kp_a: KnowledgePointInfo,
        kp_b: KnowledgePointInfo
    ) -> bool:
        """检查知识点A是否包含知识点B
        
        Args:
            kp_a: 父知识点
            kp_b: 子知识点
        
        Returns:
            是否包含
        """
        # 检查A的关键词是否包含B的关键词
        keywords_a = set(kp_a.keywords)
        keywords_b = set(kp_b.keywords)
        
        if len(keywords_b) == 0:
            return False
        
        overlap_ratio = len(keywords_a & keywords_b) / len(keywords_b)
        
        # 如果B的关键词大部分都在A中，认为A包含B
        return overlap_ratio >= 0.5
    
    def _calculate_keyword_overlap(
        self,
        keywords_a: List[str],
        keywords_b: List[str]
    ) -> float:
        """计算关键词重叠度
        
        Args:
            keywords_a: 知识点A的关键词
            keywords_b: 知识点B的关键词
        
        Returns:
            重叠度（0-1）
        """
        if not keywords_a or not keywords_b:
            return 0.0
        
        set_a = set(keywords_a)
        set_b = set(keywords_b)
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度
        
        优先使用sentence-transformers（如果可用），否则使用关键词重叠。
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        # 如果使用高级相似度计算器
        if self.similarity_calculator:
            return self.similarity_calculator.calculate(text1, text2)
        
        # 否则使用简单方法（词汇重叠）
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_prerequisite_confidence(
        self,
        kp_a: KnowledgePointInfo,
        kp_b: KnowledgePointInfo
    ) -> float:
        """计算前置依赖关系的置信度
        
        Args:
            kp_a: 前置知识点
            kp_b: 目标知识点
        
        Returns:
            置信度（0-1）
        """
        # 基于关键词重叠和文本提及
        keyword_overlap = self._calculate_keyword_overlap(kp_a.keywords, kp_b.keywords)
        mentions = 1.0 if self._mentions_concept(kp_b, kp_a) else 0.5
        
        confidence = (keyword_overlap * 0.5 + mentions * 0.5) * self.prerequisite_confidence
        return min(confidence, 1.0)
    
    def _calculate_contains_confidence(
        self,
        kp_a: KnowledgePointInfo,
        kp_b: KnowledgePointInfo
    ) -> float:
        """计算包含关系的置信度
        
        Args:
            kp_a: 父知识点
            kp_b: 子知识点
        
        Returns:
            置信度（0-1）
        """
        keyword_overlap = self._calculate_keyword_overlap(kp_a.keywords, kp_b.keywords)
        return keyword_overlap
    
    def get_relations(self, graph: nx.DiGraph) -> List[KnowledgeRelation]:
        """从图中提取关系列表
        
        Args:
            graph: 知识图谱
        
        Returns:
            关系列表
        """
        relations = []
        
        for source, target, data in graph.edges(data=True):
            relations.append(KnowledgeRelation(
                source_id=source,
                target_id=target,
                relation_type=data.get('relation_type', 'related'),
                confidence=data.get('confidence', 0.5)
            ))
        
        return relations


# 使用示例
if __name__ == "__main__":
    # 创建测试知识点
    knowledge_points = [
        KnowledgePointInfo(
            id=1,
            name="函数定义",
            summary="函数是一种映射关系，它将输入映射到输出。",
            keywords=["函数", "映射", "定义"],
            start_time=0.0,
            end_time=240.0
        ),
        KnowledgePointInfo(
            id=2,
            name="函数参数",
            summary="函数可以有位置参数、关键字参数和默认参数。",
            keywords=["函数", "参数", "位置参数"],
            start_time=240.0,
            end_time=480.0
        ),
        KnowledgePointInfo(
            id=3,
            name="函数返回值",
            summary="函数可以使用return语句返回结果。",
            keywords=["函数", "返回值", "return"],
            start_time=480.0,
            end_time=720.0
        ),
    ]
    
    # 构建知识图谱
    builder = KnowledgeGraphBuilder()
    graph = builder.build_graph(knowledge_points)
    
    # 输出结果
    print("=" * 60)
    print("知识图谱构建结果")
    print("=" * 60)
    print(f"节点数: {graph.number_of_nodes()}")
    print(f"边数: {graph.number_of_edges()}")
    print("\n关系列表:")
    
    relations = builder.get_relations(graph)
    for rel in relations:
        print(f"  {rel.source_id} -> {rel.target_id}: {rel.relation_type} (置信度: {rel.confidence:.2f})")
    
    # 检测循环
    cycles = builder.detect_cycles(graph)
    if cycles:
        print(f"\n检测到 {len(cycles)} 个循环:")
        for cycle in cycles:
            print(f"  {cycle}")
    else:
        print("\n未检测到循环依赖")
