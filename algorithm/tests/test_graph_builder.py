"""
知识图谱构建单元测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph_builder import (
    KnowledgeGraphBuilder,
    KnowledgePointInfo,
    KnowledgeRelation
)
import networkx as nx


class TestKnowledgeGraphBuilder:
    """知识图谱构建器测试类"""
    
    def setup_method(self):
        """测试前初始化"""
        self.builder = KnowledgeGraphBuilder()
        
        # 创建测试知识点
        self.knowledge_points = [
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
    
    def test_build_graph(self):
        """测试构建知识图谱"""
        graph = self.builder.build_graph(self.knowledge_points)
        
        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() == len(self.knowledge_points)
        assert graph.number_of_nodes() >= 0
    
    def test_detect_prerequisites(self):
        """测试前置依赖检测"""
        relations = self.builder.detect_prerequisites(self.knowledge_points)
        
        assert isinstance(relations, list)
        assert all(isinstance(r, KnowledgeRelation) for r in relations)
        assert all(r.relation_type == "prerequisite" for r in relations)
    
    def test_detect_related(self):
        """测试相关关系检测"""
        relations = self.builder.detect_related(self.knowledge_points)
        
        assert isinstance(relations, list)
        assert all(isinstance(r, KnowledgeRelation) for r in relations)
        assert all(r.relation_type == "related" for r in relations)
    
    def test_detect_contains(self):
        """测试包含关系检测"""
        relations = self.builder.detect_contains(self.knowledge_points)
        
        assert isinstance(relations, list)
        assert all(isinstance(r, KnowledgeRelation) for r in relations)
        assert all(r.relation_type == "contains" for r in relations)
    
    def test_detect_cycles(self):
        """测试循环依赖检测"""
        graph = self.builder.build_graph(self.knowledge_points)
        cycles = self.builder.detect_cycles(graph)
        
        assert isinstance(cycles, list)
    
    def test_resolve_cycles(self):
        """测试循环依赖解决"""
        # 创建一个包含循环的图
        graph = nx.DiGraph()
        graph.add_edge(1, 2, relation_type="prerequisite", confidence=0.8)
        graph.add_edge(2, 3, relation_type="prerequisite", confidence=0.7)
        graph.add_edge(3, 1, relation_type="prerequisite", confidence=0.6)  # 形成循环
        
        resolved_graph = self.builder.resolve_cycles(graph)
        
        assert isinstance(resolved_graph, nx.DiGraph)
        cycles = self.builder.detect_cycles(resolved_graph)
        assert len(cycles) == 0, "解决后应该没有循环"
    
    def test_calculate_keyword_overlap(self):
        """测试关键词重叠度计算"""
        keywords_a = ["函数", "映射", "定义"]
        keywords_b = ["函数", "参数"]
        
        overlap = self.builder._calculate_keyword_overlap(keywords_a, keywords_b)
        
        assert 0 <= overlap <= 1
        assert overlap > 0  # 有重叠
    
    def test_calculate_semantic_similarity(self):
        """测试语义相似度计算"""
        text1 = "函数是一种映射关系"
        text2 = "函数是一种映射关系"
        similarity = self.builder._calculate_semantic_similarity(text1, text2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # 相同文本应该相似度高
    
    def test_get_relations(self):
        """测试从图中提取关系"""
        graph = self.builder.build_graph(self.knowledge_points)
        relations = self.builder.get_relations(graph)
        
        assert isinstance(relations, list)
        assert all(isinstance(r, KnowledgeRelation) for r in relations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
