"""
测试跨课原型匹配冷启动算法
"""

import pytest
from datetime import datetime
from algorithm.cross_course_prototype_matcher import (
    CrossCoursePrototypeMatcher,
    Course,
    PrototypeMatch
)


class TestCrossCoursePrototypeMatcher:
    """测试跨课原型匹配器"""
    
    def test_init(self):
        """测试初始化"""
        matcher = CrossCoursePrototypeMatcher(similarity_threshold=0.8)
        
        assert matcher.similarity_threshold == 0.8
        assert len(matcher.course_library) == 0
    
    def test_add_course_to_library(self):
        """测试添加课程到库"""
        matcher = CrossCoursePrototypeMatcher()
        
        course = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询和数据库设计",
            knowledge_points=[
                {"id": 1, "name": "SELECT查询", "keywords": ["SELECT", "查询"]},
                {"id": 2, "name": "JOIN连接", "keywords": ["JOIN", "连接"]}
            ]
        )
        
        result = matcher.add_course_to_library(course)
        
        assert result is True
        assert 1 in matcher.course_library
        assert matcher.course_library[1].title == "数据库基础"
    
    def test_calculate_similarity(self):
        """测试计算相似度"""
        matcher = CrossCoursePrototypeMatcher()
        
        course1 = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询和数据库设计",
            knowledge_points=[
                {"id": 1, "name": "SELECT查询", "keywords": ["SELECT"]}
            ]
        )
        
        course2 = Course(
            course_id=2,
            title="数据库进阶",
            description="深入学习SQL查询和数据库优化",
            knowledge_points=[
                {"id": 1, "name": "SELECT查询", "keywords": ["SELECT"]}
            ]
        )
        
        similarity, breakdown = matcher.calculate_similarity(course1, course2)
        
        assert 0.0 <= similarity <= 1.0
        assert "semantic" in breakdown
        assert "structural" in breakdown
        assert "combined" in breakdown
    
    def test_find_prototype_high_similarity(self):
        """测试查找原型（高相似度）"""
        matcher = CrossCoursePrototypeMatcher(similarity_threshold=0.5)
        
        # 添加原型课程
        prototype = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询和数据库设计",
            knowledge_points=[
                {"id": 1, "name": "SELECT查询", "keywords": ["SELECT"]}
            ],
            baseline_config={"difficulty_threshold": 6.0}
        )
        matcher.add_course_to_library(prototype)
        
        # 新课程（相似）
        new_course = Course(
            course_id=2,
            title="数据库入门",
            description="学习SQL查询和数据库基础",
            knowledge_points=[
                {"id": 1, "name": "SELECT查询", "keywords": ["SELECT"]}
            ]
        )
        
        match = matcher.find_prototype(new_course)
        
        assert match is not None
        assert match.prototype_course_id == 1
        assert match.similarity_score >= 0.5
    
    def test_find_prototype_low_similarity(self):
        """测试查找原型（低相似度）"""
        matcher = CrossCoursePrototypeMatcher(similarity_threshold=0.9)
        
        # 添加原型课程
        prototype = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询",
            knowledge_points=[{"id": 1, "name": "SELECT查询"}]
        )
        matcher.add_course_to_library(prototype)
        
        # 新课程（不相似）
        new_course = Course(
            course_id=2,
            title="Python编程",
            description="学习Python语法和编程",
            knowledge_points=[{"id": 1, "name": "变量定义"}]
        )
        
        match = matcher.find_prototype(new_course)
        
        # 相似度应该低于阈值，返回None
        assert match is None or match.similarity_score < 0.9
    
    def test_apply_prototype_baseline(self):
        """测试应用原型基准线"""
        matcher = CrossCoursePrototypeMatcher()
        
        # 原型课程
        prototype = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL",
            knowledge_points=[],
            baseline_config={"difficulty_threshold": 6.0, "intervention_level": "L2"}
        )
        matcher.add_course_to_library(prototype)
        
        # 新课程
        new_course = Course(
            course_id=2,
            title="数据库进阶",
            description="深入学习SQL",
            knowledge_points=[]
        )
        matcher.add_course_to_library(new_course)
        
        # 应用基准线
        result = matcher.apply_prototype_baseline(2, 1)
        
        assert result is True
        assert new_course.baseline_config is not None
        assert new_course.baseline_config["difficulty_threshold"] == 6.0
    
    def test_get_matching_recommendations(self):
        """测试获取匹配推荐"""
        matcher = CrossCoursePrototypeMatcher()
        
        # 添加多个课程
        course1 = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询",
            knowledge_points=[{"id": 1, "name": "SELECT查询"}]
        )
        course2 = Course(
            course_id=2,
            title="Python编程",
            description="学习Python语法",
            knowledge_points=[{"id": 1, "name": "变量定义"}]
        )
        
        matcher.add_course_to_library(course1)
        matcher.add_course_to_library(course2)
        
        # 新课程
        new_course = Course(
            course_id=3,
            title="数据库入门",
            description="学习SQL基础",
            knowledge_points=[{"id": 1, "name": "SELECT查询"}]
        )
        
        recommendations = matcher.get_matching_recommendations(new_course, top_k=2)
        
        assert len(recommendations) <= 2
        assert all(r.similarity_score >= 0.0 for r in recommendations)
        # 应该按相似度降序排列
        if len(recommendations) > 1:
            assert recommendations[0].similarity_score >= recommendations[1].similarity_score
    
    def test_auto_match_and_apply(self):
        """测试自动匹配并应用"""
        matcher = CrossCoursePrototypeMatcher(similarity_threshold=0.5)
        
        # 原型课程
        prototype = Course(
            course_id=1,
            title="数据库基础",
            description="学习SQL查询",
            knowledge_points=[{"id": 1, "name": "SELECT查询"}],
            baseline_config={"difficulty_threshold": 6.0}
        )
        matcher.add_course_to_library(prototype)
        
        # 新课程
        new_course = Course(
            course_id=2,
            title="数据库入门",
            description="学习SQL基础",
            knowledge_points=[{"id": 1, "name": "SELECT查询"}]
        )
        
        match = matcher.auto_match_and_apply(new_course)
        
        # 如果相似度足够高，应该匹配成功
        if match:
            assert match.prototype_course_id == 1
            assert new_course.baseline_config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
