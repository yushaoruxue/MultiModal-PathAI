"""
练习题自动生成功能

为疑难知识点生成诊断练习题，支持选择题、填空题、判断题、简答题。
"""

import logging
from typing import List, Dict, Optional
import random
from dataclasses import dataclass

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
    difficulty: str = "medium"
    kp_type: str = "concept"  # concept, example, practice


@dataclass
class Exercise:
    """练习题"""
    question: str
    type: str  # choice, fill_blank, true_false, short_answer
    options: Optional[List[str]] = None  # 选择题选项
    correct_answer: str = ""
    explanation: str = ""
    difficulty: str = "medium"


class ExerciseGenerator:
    """练习题生成器
    
    为疑难知识点生成诊断练习题，支持多种题型。
    """
    
    def __init__(
        self,
        use_ai: bool = False,
        ai_api_key: Optional[str] = None
    ):
        """初始化练习题生成器
        
        Args:
            use_ai: 是否使用AI模型生成题目（需要配置API密钥）
            ai_api_key: AI API密钥（可选）
        """
        self.use_ai = use_ai
        self.ai_api_key = ai_api_key
        
        # 题目类型权重（用于随机选择）
        self.question_type_weights = {
            "choice": 0.4,      # 40% 选择题
            "fill_blank": 0.3,  # 30% 填空题
            "true_false": 0.2,  # 20% 判断题
            "short_answer": 0.1  # 10% 简答题
        }
        
        logger.info(f"ExerciseGenerator initialized (use_ai={use_ai})")
    
    def generate_exercises(
        self,
        knowledge_point_info: KnowledgePointInfo,
        count: int = 5,
        difficulty: Optional[str] = None
    ) -> List[Exercise]:
        """生成练习题列表
        
        Args:
            knowledge_point_info: 知识点信息
            count: 题目数量（默认5题）
            difficulty: 题目难度（如果为None则使用知识点的难度）
        
        Returns:
            练习题列表
        """
        try:
            if difficulty is None:
                difficulty = knowledge_point_info.difficulty
            
            logger.info(f"Generating {count} exercises for: {knowledge_point_info.name}")
            
            exercises = []
            question_types = self._select_question_types(count)
            
            for i, q_type in enumerate(question_types):
                if q_type == "choice":
                    exercise = self.generate_choice_question(knowledge_point_info, difficulty)
                elif q_type == "fill_blank":
                    exercise = self.generate_fill_blank_question(knowledge_point_info, difficulty)
                elif q_type == "true_false":
                    exercise = self.generate_true_false_question(knowledge_point_info, difficulty)
                else:  # short_answer
                    exercise = self.generate_short_answer_question(knowledge_point_info, difficulty)
                
                # 验证题目质量
                if self.validate_question(exercise):
                    exercises.append(exercise)
                else:
                    logger.warning(f"Generated invalid question, regenerating...")
                    # 重新生成
                    if q_type == "choice":
                        exercise = self.generate_choice_question(knowledge_point_info, difficulty)
                    else:
                        exercise = self.generate_fill_blank_question(knowledge_point_info, difficulty)
                    if self.validate_question(exercise):
                        exercises.append(exercise)
            
            logger.info(f"Generated {len(exercises)} valid exercises")
            return exercises
            
        except Exception as e:
            logger.error(f"Error generating exercises: {e}", exc_info=True)
            raise
    
    def generate_choice_question(
        self,
        knowledge_point_info: KnowledgePointInfo,
        difficulty: str = "medium"
    ) -> Exercise:
        """生成选择题
        
        生成4个选项，包含正确答案和干扰项。
        
        Args:
            knowledge_point_info: 知识点信息
            difficulty: 题目难度
        
        Returns:
            选择题对象
        """
        # 根据知识点类型生成题目
        if "函数" in knowledge_point_info.name:
            question = "Python中定义函数的关键字是什么？"
            correct_answer = "def"
            options = ["def", "function", "define", "func"]
            explanation = "在Python中，使用def关键字来定义函数。"
        elif "参数" in knowledge_point_info.name:
            question = "函数参数中，位置参数和关键字参数的区别是什么？"
            correct_answer = "位置参数按顺序传递，关键字参数可以指定参数名"
            options = [
                "位置参数按顺序传递，关键字参数可以指定参数名",
                "位置参数必须指定参数名，关键字参数按顺序传递",
                "两者没有区别",
                "位置参数是必需的，关键字参数是可选的"
            ]
            explanation = "位置参数按照定义时的顺序传递，而关键字参数可以通过参数名指定，顺序可以改变。"
        else:
            # 通用题目
            question = f"关于{knowledge_point_info.name}，以下哪个说法是正确的？"
            correct_answer = f"{knowledge_point_info.name}是重要的概念"
            options = [
                correct_answer,
                f"{knowledge_point_info.name}不重要",
                f"{knowledge_point_info.name}很难理解",
                f"{knowledge_point_info.name}不需要掌握"
            ]
            explanation = f"这是关于{knowledge_point_info.name}的基础知识。"
        
        # 打乱选项顺序
        correct_index = options.index(correct_answer)
        random.shuffle(options)
        # 确保正确答案在选项中
        if correct_answer not in options:
            options[0] = correct_answer
            correct_index = 0
        else:
            correct_index = options.index(correct_answer)
        
        return Exercise(
            question=question,
            type="choice",
            options=options,
            correct_answer=chr(65 + correct_index),  # A, B, C, D
            explanation=explanation,
            difficulty=difficulty
        )
    
    def generate_fill_blank_question(
        self,
        knowledge_point_info: KnowledgePointInfo,
        difficulty: str = "medium"
    ) -> Exercise:
        """生成填空题
        
        Args:
            knowledge_point_info: 知识点信息
            difficulty: 题目难度
        
        Returns:
            填空题对象
        """
        if "函数" in knowledge_point_info.name:
            question = "在Python中，使用______关键字来定义函数。"
            correct_answer = "def"
            explanation = "def是Python中定义函数的关键字。"
        elif "参数" in knowledge_point_info.name:
            question = "函数参数中，______参数按照定义时的顺序传递。"
            correct_answer = "位置"
            explanation = "位置参数按照定义时的顺序传递，不需要指定参数名。"
        else:
            question = f"关于{knowledge_point_info.name}，核心概念是______。"
            correct_answer = knowledge_point_info.summary[:20] if knowledge_point_info.summary else "重要概念"
            explanation = f"这是{knowledge_point_info.name}的核心概念。"
        
        return Exercise(
            question=question,
            type="fill_blank",
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty
        )
    
    def generate_true_false_question(
        self,
        knowledge_point_info: KnowledgePointInfo,
        difficulty: str = "medium"
    ) -> Exercise:
        """生成判断题
        
        Args:
            knowledge_point_info: 知识点信息
            difficulty: 题目难度
        
        Returns:
            判断题对象
        """
        if "函数" in knowledge_point_info.name:
            question = "在Python中，函数必须使用return语句返回值。"
            correct_answer = "错误"
            explanation = "函数可以不使用return语句，默认返回None。"
        elif "参数" in knowledge_point_info.name:
            question = "位置参数和关键字参数可以混合使用。"
            correct_answer = "正确"
            explanation = "位置参数和关键字参数可以混合使用，但位置参数必须在关键字参数之前。"
        else:
            question = f"{knowledge_point_info.name}是一个基础概念。"
            correct_answer = "正确"
            explanation = f"{knowledge_point_info.name}确实是需要掌握的基础概念。"
        
        return Exercise(
            question=question,
            type="true_false",
            options=["正确", "错误"],
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty
        )
    
    def generate_short_answer_question(
        self,
        knowledge_point_info: KnowledgePointInfo,
        difficulty: str = "medium"
    ) -> Exercise:
        """生成简答题
        
        Args:
            knowledge_point_info: 知识点信息
            difficulty: 题目难度
        
        Returns:
            简答题对象
        """
        question = f"请简要说明{knowledge_point_info.name}的概念和应用。"
        correct_answer = knowledge_point_info.summary if knowledge_point_info.summary else f"{knowledge_point_info.name}是一个重要的概念。"
        explanation = f"这是关于{knowledge_point_info.name}的简要说明，需要理解其核心概念和应用场景。"
        
        return Exercise(
            question=question,
            type="short_answer",
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty
        )
    
    def validate_question(self, exercise: Exercise) -> bool:
        """验证题目质量
        
        检查题目是否合理、完整。
        
        Args:
            exercise: 练习题对象
        
        Returns:
            是否有效
        """
        # 检查基本字段
        if not exercise.question or len(exercise.question.strip()) < 5:
            return False
        
        if not exercise.correct_answer:
            return False
        
        if not exercise.explanation:
            return False
        
        # 检查选择题选项
        if exercise.type == "choice":
            if not exercise.options or len(exercise.options) < 2:
                return False
            if exercise.correct_answer not in ["A", "B", "C", "D"]:
                return False
        
        # 检查判断题选项
        if exercise.type == "true_false":
            if not exercise.options or len(exercise.options) < 2:
                return False
        
        return True
    
    def _select_question_types(self, count: int) -> List[str]:
        """选择题目类型
        
        根据权重随机选择题目类型。
        
        Args:
            count: 题目数量
        
        Returns:
            题目类型列表
        """
        types = []
        available_types = list(self.question_type_weights.keys())
        weights = list(self.question_type_weights.values())
        
        for _ in range(count):
            # 根据权重随机选择
            selected_type = random.choices(available_types, weights=weights)[0]
            types.append(selected_type)
        
        return types


# 使用示例
if __name__ == "__main__":
    from knowledge_card_generator import KnowledgePointInfo as KPInfo
    
    # 创建生成器
    generator = ExerciseGenerator(use_ai=False)
    
    # 创建知识点信息
    kp_info = KPInfo(
        id=10,
        name="函数定义",
        summary="函数是一种映射关系，它将输入映射到输出。",
        keywords=["函数", "映射", "定义"],
        difficulty="medium"
    )
    
    # 生成练习题
    exercises = generator.generate_exercises(kp_info, count=5)
    
    # 输出结果
    print("=" * 60)
    print("练习题生成结果")
    print("=" * 60)
    for i, exercise in enumerate(exercises, 1):
        print(f"\n题目 {i}: {exercise.type}")
        print(f"问题: {exercise.question}")
        if exercise.options:
            print(f"选项: {', '.join(exercise.options)}")
        print(f"正确答案: {exercise.correct_answer}")
        print(f"解析: {exercise.explanation}")
