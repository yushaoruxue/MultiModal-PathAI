"""
跨课原型匹配冷启动算法

基于v10.0需求，对于新课程，自动匹配相似课程的基准线。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Course:
    """课程信息"""
    course_id: int
    title: str
    description: str
    knowledge_points: List[Dict[str, Any]]  # 知识点列表
    baseline_config: Optional[Dict[str, Any]] = None  # 基准线配置
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PrototypeMatch:
    """原型匹配结果"""
    prototype_course_id: int
    similarity_score: float
    match_type: str  # "semantic" / "structural" / "combined"
    baseline_config: Dict[str, Any]
    matched_knowledge_points: List[int]  # 匹配的知识点ID列表


@dataclass
class MatchingRecommendation:
    """匹配推荐"""
    course_id: int
    course_title: str
    similarity_score: float
    match_reason: str
    baseline_config: Optional[Dict[str, Any]] = None


class CrossCoursePrototypeMatcher:
    """跨课原型匹配冷启动算法
    
    功能：
    1. 相似度计算：计算新课程与已有课程的相似度（基于课程描述、知识点结构）
    2. 原型匹配：如果相似度>0.8，自动复用相似课程的基准线
    3. 冷启动优化：新课程无需教师手动设置基准线
    """
    
    # 相似度阈值（默认0.8）
    DEFAULT_SIMILARITY_THRESHOLD = 0.8
    
    # 语义相似度权重
    SEMANTIC_WEIGHT = 0.6
    
    # 结构相似度权重
    STRUCTURAL_WEIGHT = 0.4
    
    def __init__(self, similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD):
        """初始化跨课原型匹配器
        
        Args:
            similarity_threshold: 相似度阈值（默认0.8）
        """
        self.similarity_threshold = similarity_threshold
        
        # 存储课程库
        self.course_library: Dict[int, Course] = {}
        
        logger.info(
            f"CrossCoursePrototypeMatcher initialized with "
            f"similarity_threshold={similarity_threshold}"
        )
    
    def add_course_to_library(self, course: Course) -> bool:
        """添加课程到课程库
        
        Args:
            course: 课程信息
        
        Returns:
            是否成功添加
        """
        self.course_library[course.course_id] = course
        
        logger.info(
            f"Added course to library: {course.course_id} - {course.title}"
        )
        
        return True
    
    def calculate_similarity(
        self,
        new_course: Course,
        existing_course: Course
    ) -> Tuple[float, Dict[str, float]]:
        """计算课程相似度
        
        Args:
            new_course: 新课程
            existing_course: 已有课程
        
        Returns:
            (综合相似度, 各维度相似度字典)
        """
        # 1. 计算语义相似度（基于课程描述和标题）
        semantic_sim = self._calculate_semantic_similarity(
            new_course, existing_course
        )
        
        # 2. 计算结构相似度（基于知识点结构）
        structural_sim = self._calculate_structural_similarity(
            new_course, existing_course
        )
        
        # 3. 综合相似度（加权平均）
        combined_sim = (
            semantic_sim * self.SEMANTIC_WEIGHT +
            structural_sim * self.STRUCTURAL_WEIGHT
        )
        
        similarity_breakdown = {
            "semantic": semantic_sim,
            "structural": structural_sim,
            "combined": combined_sim
        }
        
        logger.debug(
            f"Similarity between {new_course.course_id} and {existing_course.course_id}: "
            f"semantic={semantic_sim:.3f}, structural={structural_sim:.3f}, "
            f"combined={combined_sim:.3f}"
        )
        
        return combined_sim, similarity_breakdown
    
    def _calculate_semantic_similarity(
        self,
        course1: Course,
        course2: Course
    ) -> float:
        """计算语义相似度
        
        基于课程标题和描述的文本相似度
        
        Args:
            course1: 课程1
            course2: 课程2
        
        Returns:
            语义相似度（0-1）
        """
        # 简化实现：基于标题和描述的词汇重叠度
        # 实际应该使用词向量或BERT等模型计算语义相似度
        
        # 提取关键词（简化：分词）
        title1_words = set(course1.title.lower().split())
        title2_words = set(course2.title.lower().split())
        
        desc1_words = set(course1.description.lower().split())
        desc2_words = set(course2.description.lower().split())
        
        # 计算标题相似度（Jaccard相似度）
        title_intersection = len(title1_words & title2_words)
        title_union = len(title1_words | title2_words)
        title_sim = title_intersection / title_union if title_union > 0 else 0.0
        
        # 计算描述相似度（Jaccard相似度）
        desc_intersection = len(desc1_words & desc2_words)
        desc_union = len(desc1_words | desc2_words)
        desc_sim = desc_intersection / desc_union if desc_union > 0 else 0.0
        
        # 综合语义相似度（标题权重0.4，描述权重0.6）
        semantic_sim = title_sim * 0.4 + desc_sim * 0.6
        
        return min(1.0, max(0.0, semantic_sim))
    
    def _calculate_structural_similarity(
        self,
        course1: Course,
        course2: Course
    ) -> float:
        """计算结构相似度
        
        基于知识点结构的相似度
        
        Args:
            course1: 课程1
            course2: 课程2
        
        Returns:
            结构相似度（0-1）
        """
        kp1 = course1.knowledge_points
        kp2 = course2.knowledge_points
        
        if not kp1 or not kp2:
            return 0.0
        
        # 1. 知识点数量相似度
        count_sim = 1.0 - abs(len(kp1) - len(kp2)) / max(len(kp1), len(kp2))
        
        # 2. 知识点层级结构相似度（如果有层级）
        level_sim = self._calculate_level_similarity(kp1, kp2)
        
        # 3. 知识点关键词相似度
        keyword_sim = self._calculate_keyword_similarity(kp1, kp2)
        
        # 综合结构相似度
        structural_sim = (
            count_sim * 0.3 +
            level_sim * 0.3 +
            keyword_sim * 0.4
        )
        
        return min(1.0, max(0.0, structural_sim))
    
    def _calculate_level_similarity(
        self,
        kp1: List[Dict[str, Any]],
        kp2: List[Dict[str, Any]]
    ) -> float:
        """计算知识点层级相似度
        
        Args:
            kp1: 知识点列表1
            kp2: 知识点列表2
        
        Returns:
            层级相似度（0-1）
        """
        # 提取层级信息（如果有）
        levels1 = [kp.get("level", 1) for kp in kp1]
        levels2 = [kp.get("level", 1) for kp in kp2]
        
        if not levels1 or not levels2:
            return 0.5  # 默认相似度
        
        # 计算层级分布相似度
        from collections import Counter
        dist1 = Counter(levels1)
        dist2 = Counter(levels2)
        
        all_levels = set(dist1.keys()) | set(dist2.keys())
        if not all_levels:
            return 0.5
        
        # 计算分布差异
        total_diff = 0.0
        for level in all_levels:
            count1 = dist1.get(level, 0) / len(levels1)
            count2 = dist2.get(level, 0) / len(levels2)
            total_diff += abs(count1 - count2)
        
        # 相似度 = 1 - 差异
        similarity = 1.0 - (total_diff / len(all_levels))
        
        return max(0.0, similarity)
    
    def _calculate_keyword_similarity(
        self,
        kp1: List[Dict[str, Any]],
        kp2: List[Dict[str, Any]]
    ) -> float:
        """计算知识点关键词相似度
        
        Args:
            kp1: 知识点列表1
            kp2: 知识点列表2
        
        Returns:
            关键词相似度（0-1）
        """
        # 提取所有关键词
        keywords1 = set()
        for kp in kp1:
            kp_keywords = kp.get("keywords", [])
            if isinstance(kp_keywords, list):
                keywords1.update(kp_keywords)
            elif isinstance(kp_keywords, str):
                keywords1.update(kp_keywords.split())
        
        keywords2 = set()
        for kp in kp2:
            kp_keywords = kp.get("keywords", [])
            if isinstance(kp_keywords, list):
                keywords2.update(kp_keywords)
            elif isinstance(kp_keywords, str):
                keywords2.update(kp_keywords.split())
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def find_prototype(
        self,
        new_course: Course,
        course_library: Optional[Dict[int, Course]] = None
    ) -> Optional[PrototypeMatch]:
        """查找原型课程
        
        Args:
            new_course: 新课程
            course_library: 课程库（可选，如果不提供则使用内部库）
        
        Returns:
            原型匹配结果，如果没有找到则返回None
        """
        if course_library is None:
            course_library = self.course_library
        
        if not course_library:
            logger.warning("Course library is empty")
            return None
        
        best_match = None
        best_similarity = 0.0
        
        # 遍历所有课程，找到最相似的
        for course_id, existing_course in course_library.items():
            similarity, breakdown = self.calculate_similarity(
                new_course, existing_course
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing_course
        
        # 检查是否达到阈值
        if best_match is None or best_similarity < self.similarity_threshold:
            logger.info(
                f"No prototype found for course {new_course.course_id}, "
                f"best similarity: {best_similarity:.3f} < {self.similarity_threshold}"
            )
            return None
        
        # 找出匹配的知识点
        matched_kps = self._find_matched_knowledge_points(
            new_course, best_match
        )
        
        match = PrototypeMatch(
            prototype_course_id=best_match.course_id,
            similarity_score=best_similarity,
            match_type="combined",
            baseline_config=best_match.baseline_config or {},
            matched_knowledge_points=matched_kps
        )
        
        logger.info(
            f"Found prototype for course {new_course.course_id}: "
            f"prototype={best_match.course_id}, similarity={best_similarity:.3f}"
        )
        
        return match
    
    def _find_matched_knowledge_points(
        self,
        new_course: Course,
        prototype_course: Course
    ) -> List[int]:
        """找出匹配的知识点
        
        Args:
            new_course: 新课程
            prototype_course: 原型课程
        
        Returns:
            匹配的知识点ID列表
        """
        matched = []
        
        # 简化实现：基于知识点名称相似度匹配
        for new_kp in new_course.knowledge_points:
            new_kp_id = new_kp.get("id")
            new_kp_name = new_kp.get("name", "").lower()
            
            for proto_kp in prototype_course.knowledge_points:
                proto_kp_name = proto_kp.get("name", "").lower()
                
                # 计算名称相似度（简化：词汇重叠）
                new_words = set(new_kp_name.split())
                proto_words = set(proto_kp_name.split())
                
                if new_words and proto_words:
                    overlap = len(new_words & proto_words) / len(new_words | proto_words)
                    if overlap > 0.5:  # 相似度>0.5认为匹配
                        matched.append(new_kp_id)
                        break
        
        return matched
    
    def apply_prototype_baseline(
        self,
        new_course_id: int,
        prototype_course_id: int
    ) -> bool:
        """应用原型基准线到新课程
        
        Args:
            new_course_id: 新课程ID
            prototype_course_id: 原型课程ID
        
        Returns:
            是否成功应用
        """
        if prototype_course_id not in self.course_library:
            logger.error(f"Prototype course {prototype_course_id} not found")
            return False
        
        if new_course_id not in self.course_library:
            logger.error(f"New course {new_course_id} not found")
            return False
        
        prototype_course = self.course_library[prototype_course_id]
        new_course = self.course_library[new_course_id]
        
        if not prototype_course.baseline_config:
            logger.warning(f"Prototype course {prototype_course_id} has no baseline config")
            return False
        
        # 应用基准线配置
        new_course.baseline_config = prototype_course.baseline_config.copy()
        
        logger.info(
            f"Applied prototype baseline from {prototype_course_id} to {new_course_id}"
        )
        
        return True
    
    def get_matching_recommendations(
        self,
        new_course: Course,
        top_k: int = 5
    ) -> List[MatchingRecommendation]:
        """获取匹配推荐列表
        
        Args:
            new_course: 新课程
            top_k: 返回前k个推荐
        
        Returns:
            匹配推荐列表
        """
        recommendations = []
        
        for course_id, existing_course in self.course_library.items():
            similarity, breakdown = self.calculate_similarity(
                new_course, existing_course
            )
            
            # 生成推荐原因
            if breakdown["semantic"] > breakdown["structural"]:
                reason = f"语义相似度高（{breakdown['semantic']:.2%}）"
            else:
                reason = f"结构相似度高（{breakdown['structural']:.2%}）"
            
            recommendation = MatchingRecommendation(
                course_id=course_id,
                course_title=existing_course.title,
                similarity_score=similarity,
                match_reason=reason,
                baseline_config=existing_course.baseline_config
            )
            
            recommendations.append(recommendation)
        
        # 按相似度排序
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # 返回前k个
        return recommendations[:top_k]
    
    def auto_match_and_apply(
        self,
        new_course: Course
    ) -> Optional[PrototypeMatch]:
        """自动匹配并应用原型基准线
        
        Args:
            new_course: 新课程
        
        Returns:
            匹配结果，如果没有找到则返回None
        """
        # 添加到课程库
        self.add_course_to_library(new_course)
        
        # 查找原型
        match = self.find_prototype(new_course)
        
        if match:
            # 应用基准线
            self.apply_prototype_baseline(
                new_course.course_id,
                match.prototype_course_id
            )
            
            logger.info(
                f"Auto-matched and applied prototype baseline for course {new_course.course_id}"
            )
        
        return match
