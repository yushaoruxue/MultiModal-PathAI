"""
资源质量评估功能

评估生成的补偿资源的质量，包括内容质量、相关性、有效性等维度。
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """质量分数"""
    content_quality: float  # 内容质量（0-1）
    relevance: float  # 相关性（0-1）
    effectiveness: float  # 有效性（0-1）
    overall_score: float  # 综合分数（0-1）


class ResourceQualityEvaluator:
    """资源质量评估器
    
    评估生成的补偿资源的质量，包括内容质量、相关性、有效性等维度。
    """
    
    def __init__(
        self,
        content_weight: float = 0.4,
        relevance_weight: float = 0.3,
        effectiveness_weight: float = 0.3,
        quality_threshold: float = 0.6
    ):
        """初始化资源质量评估器
        
        Args:
            content_weight: 内容质量权重
            relevance_weight: 相关性权重
            effectiveness_weight: 有效性权重
            quality_threshold: 质量阈值，低于此值需要重新生成
        """
        self.content_weight = content_weight
        self.relevance_weight = relevance_weight
        self.effectiveness_weight = effectiveness_weight
        self.quality_threshold = quality_threshold
        
        # 验证权重总和为1
        total_weight = content_weight + relevance_weight + effectiveness_weight
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            self.content_weight /= total_weight
            self.relevance_weight /= total_weight
            self.effectiveness_weight /= total_weight
        
        # 评估历史记录
        self.evaluation_history: Dict[str, QualityScore] = {}
        
        logger.info("ResourceQualityEvaluator initialized")
    
    def evaluate_content_quality(self, resource_content: str) -> Dict:
        """评估内容质量
        
        评估维度：
        - 准确性（内容是否正确）
        - 完整性（是否包含必要信息）
        - 清晰度（是否容易理解）
        
        Args:
            resource_content: 资源内容（Markdown或JSON格式）
        
        Returns:
            内容质量评估结果字典
        """
        try:
            # 简单实现：基于内容长度、结构等评估
            # 实际应用中可以使用AI模型进行更准确的评估
            
            # 评估完整性
            completeness = self._evaluate_completeness(resource_content)
            
            # 评估清晰度
            clarity = self._evaluate_clarity(resource_content)
            
            # 评估准确性（简化处理，实际需要AI模型）
            accuracy = 0.8  # 默认值，实际需要验证内容正确性
            
            # 综合内容质量分数
            content_quality = (completeness + clarity + accuracy) / 3
            
            result = {
                "accuracy": accuracy,
                "completeness": completeness,
                "clarity": clarity,
                "overall": content_quality
            }
            
            logger.debug(f"Content quality evaluated: {content_quality:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating content quality: {e}", exc_info=True)
            return {
                "accuracy": 0.5,
                "completeness": 0.5,
                "clarity": 0.5,
                "overall": 0.5
            }
    
    def evaluate_relevance(
        self,
        resource_content: str,
        knowledge_point_info: Dict
    ) -> float:
        """评估相关性
        
        评估资源与知识点的相关度，是否针对学生的疑难点。
        
        Args:
            resource_content: 资源内容
            knowledge_point_info: 知识点信息字典
        
        Returns:
            相关性分数（0-1）
        """
        try:
            # 检查资源内容中是否包含知识点的关键词
            kp_name = knowledge_point_info.get("name", "")
            kp_keywords = knowledge_point_info.get("keywords", [])
            
            # 计算关键词匹配度
            keyword_matches = 0
            for keyword in kp_keywords:
                if keyword in resource_content:
                    keyword_matches += 1
            
            keyword_score = keyword_matches / len(kp_keywords) if kp_keywords else 0.5
            
            # 检查是否包含知识点名称
            name_score = 1.0 if kp_name in resource_content else 0.5
            
            # 综合相关性分数
            relevance = (keyword_score * 0.7 + name_score * 0.3)
            
            logger.debug(f"Relevance evaluated: {relevance:.2f}")
            return relevance
            
        except Exception as e:
            logger.error(f"Error evaluating relevance: {e}", exc_info=True)
            return 0.5
    
    def evaluate_effectiveness(
        self,
        resource_id: str,
        student_feedback: Optional[str] = None,
        exercise_score: Optional[float] = None
    ) -> Dict:
        """评估有效性
        
        基于学生反馈和练习正确率评估资源有效性。
        
        Args:
            resource_id: 资源ID
            student_feedback: 学生反馈（"mastered", "still_difficult", None）
            exercise_score: 练习正确率（0-1）
        
        Returns:
            有效性评估结果字典
        """
        try:
            # 基于学生反馈
            feedback_score = 0.5
            if student_feedback == "mastered":
                feedback_score = 1.0
            elif student_feedback == "still_difficult":
                feedback_score = 0.3
            
            # 基于练习正确率
            exercise_score_value = exercise_score if exercise_score is not None else 0.5
            
            # 综合有效性分数
            effectiveness = (feedback_score * 0.6 + exercise_score_value * 0.4)
            
            result = {
                "feedback_score": feedback_score,
                "exercise_score": exercise_score_value,
                "overall": effectiveness
            }
            
            logger.debug(f"Effectiveness evaluated: {effectiveness:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating effectiveness: {e}", exc_info=True)
            return {
                "feedback_score": 0.5,
                "exercise_score": 0.5,
                "overall": 0.5
            }
    
    def get_quality_score(
        self,
        resource_id: str,
        resource_content: str,
        knowledge_point_info: Dict,
        student_feedback: Optional[str] = None,
        exercise_score: Optional[float] = None
    ) -> QualityScore:
        """获取综合质量分数
        
        Args:
            resource_id: 资源ID
            resource_content: 资源内容
            knowledge_point_info: 知识点信息
            student_feedback: 学生反馈（可选）
            exercise_score: 练习正确率（可选）
        
        Returns:
            质量分数对象
        """
        try:
            # 评估内容质量
            content_result = self.evaluate_content_quality(resource_content)
            content_quality = content_result["overall"]
            
            # 评估相关性
            relevance = self.evaluate_relevance(resource_content, knowledge_point_info)
            
            # 评估有效性
            effectiveness_result = self.evaluate_effectiveness(
                resource_id, student_feedback, exercise_score
            )
            effectiveness = effectiveness_result["overall"]
            
            # 计算综合分数
            overall_score = (
                content_quality * self.content_weight +
                relevance * self.relevance_weight +
                effectiveness * self.effectiveness_weight
            )
            
            quality_score = QualityScore(
                content_quality=content_quality,
                relevance=relevance,
                effectiveness=effectiveness,
                overall_score=overall_score
            )
            
            # 记录评估历史
            self.evaluation_history[resource_id] = quality_score
            
            logger.info(f"Quality score for {resource_id}: {overall_score:.2f}")
            return quality_score
            
        except Exception as e:
            logger.error(f"Error getting quality score: {e}", exc_info=True)
            raise
    
    def should_regenerate(
        self,
        resource_id: str,
        quality_score: Optional[QualityScore] = None
    ) -> bool:
        """判断是否应该重新生成资源
        
        Args:
            resource_id: 资源ID
            quality_score: 质量分数（如果为None则从历史记录获取）
        
        Returns:
            是否应该重新生成
        """
        if quality_score is None:
            quality_score = self.evaluation_history.get(resource_id)
            if quality_score is None:
                return False
        
        should_regenerate = quality_score.overall_score < self.quality_threshold
        
        if should_regenerate:
            logger.info(f"Resource {resource_id} should be regenerated (score: {quality_score.overall_score:.2f})")
        
        return should_regenerate
    
    def _evaluate_completeness(self, content: str) -> float:
        """评估完整性
        
        Args:
            content: 资源内容
        
        Returns:
            完整性分数（0-1）
        """
        # 简单实现：检查是否包含必要的部分
        required_sections = ["概念", "例题", "建议"]
        found_sections = sum(1 for section in required_sections if section in content)
        
        completeness = found_sections / len(required_sections)
        return completeness
    
    def _evaluate_clarity(self, content: str) -> float:
        """评估清晰度
        
        Args:
            content: 资源内容
        
        Returns:
            清晰度分数（0-1）
        """
        # 简单实现：基于内容长度和结构
        # 内容不应该太短或太长
        length_score = 1.0
        if len(content) < 100:
            length_score = 0.5
        elif len(content) > 5000:
            length_score = 0.7
        
        # 检查是否有结构（标题、列表等）
        has_structure = any(marker in content for marker in ["#", "-", "*", "1.", "2."])
        structure_score = 1.0 if has_structure else 0.5
        
        clarity = (length_score + structure_score) / 2
        return clarity
    
    def generate_quality_report(
        self,
        resource_ids: List[str]
    ) -> Dict:
        """生成质量报告
        
        Args:
            resource_ids: 资源ID列表
        
        Returns:
            质量报告字典
        """
        if not resource_ids:
            return {
                "total_resources": 0,
                "average_score": 0.0,
                "high_quality": 0,
                "low_quality": 0
            }
        
        scores = []
        high_quality = 0
        low_quality = 0
        
        for resource_id in resource_ids:
            quality_score = self.evaluation_history.get(resource_id)
            if quality_score:
                scores.append(quality_score.overall_score)
                if quality_score.overall_score >= 0.8:
                    high_quality += 1
                elif quality_score.overall_score < self.quality_threshold:
                    low_quality += 1
        
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        report = {
            "total_resources": len(resource_ids),
            "evaluated_resources": len(scores),
            "average_score": average_score,
            "high_quality": high_quality,
            "low_quality": low_quality,
            "regeneration_needed": low_quality
        }
        
        return report


# 使用示例
if __name__ == "__main__":
    # 创建评估器
    evaluator = ResourceQualityEvaluator()
    
    # 模拟资源内容
    resource_content = """# 函数定义

## 核心概念
函数是一种映射关系，它将输入映射到输出。

## 典型例题
1. 定义一个函数 add(a, b)，计算两个数的和。
"""
    
    knowledge_point_info = {
        "name": "函数定义",
        "keywords": ["函数", "映射", "定义"]
    }
    
    # 评估质量
    quality_score = evaluator.get_quality_score(
        resource_id="test_001",
        resource_content=resource_content,
        knowledge_point_info=knowledge_point_info,
        student_feedback="mastered",
        exercise_score=0.9
    )
    
    print("=" * 60)
    print("资源质量评估结果")
    print("=" * 60)
    print(f"内容质量: {quality_score.content_quality:.2f}")
    print(f"相关性: {quality_score.relevance:.2f}")
    print(f"有效性: {quality_score.effectiveness:.2f}")
    print(f"综合分数: {quality_score.overall_score:.2f}")
    
    # 判断是否需要重新生成
    should_regenerate = evaluator.should_regenerate("test_001", quality_score)
    print(f"是否需要重新生成: {'是' if should_regenerate else '否'}")
