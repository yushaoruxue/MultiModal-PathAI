"""
知识卡片生成功能

为疑难知识点生成补偿学习资源，使用模板和AI模型生成知识卡片。
"""

import logging
from typing import List, Dict, Optional
import re
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
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class KnowledgeCardGenerator:
    """知识卡片生成器
    
    为疑难知识点生成补偿学习资源，包括核心概念、公式、例题、常见误区、学习建议等。
    """
    
    def __init__(
        self,
        use_ai: bool = False,
        ai_api_key: Optional[str] = None
    ):
        """初始化知识卡片生成器
        
        Args:
            use_ai: 是否使用AI模型生成内容（需要配置API密钥）
            ai_api_key: AI API密钥（可选）
        """
        self.use_ai = use_ai
        self.ai_api_key = ai_api_key
        
        # 缓存已生成的卡片
        self.card_cache: Dict[int, str] = {}
        
        logger.info(f"KnowledgeCardGenerator initialized (use_ai={use_ai})")
    
    def generate_card(
        self,
        knowledge_point_info: KnowledgePointInfo,
        asr_text: Optional[str] = None,
        ocr_text: Optional[str] = None
    ) -> str:
        """生成知识卡片
        
        Args:
            knowledge_point_info: 知识点信息
            asr_text: ASR转写文本（可选）
            ocr_text: OCR识别文本（可选）
        
        Returns:
            知识卡片内容（Markdown格式）
        """
        try:
            # 检查缓存
            if knowledge_point_info.id in self.card_cache:
                logger.debug(f"Using cached card for knowledge point {knowledge_point_info.id}")
                return self.card_cache[knowledge_point_info.id]
            
            logger.info(f"Generating knowledge card for: {knowledge_point_info.name}")
            
            # 合并文本
            full_text = self._merge_texts(asr_text, ocr_text, knowledge_point_info.summary)
            
            # 提取各部分内容
            core_concept = self.extract_core_concept(full_text, knowledge_point_info)
            formulas = self.extract_formulas(full_text)
            examples = self.generate_examples(knowledge_point_info, full_text)
            common_mistakes = self.generate_common_mistakes(knowledge_point_info, full_text)
            learning_tips = self.generate_learning_tips(knowledge_point_info, full_text)
            
            # 格式化为Markdown
            card_content = self.format_as_markdown(
                knowledge_point_info=knowledge_point_info,
                core_concept=core_concept,
                formulas=formulas,
                examples=examples,
                common_mistakes=common_mistakes,
                learning_tips=learning_tips
            )
            
            # 缓存结果
            self.card_cache[knowledge_point_info.id] = card_content
            
            logger.info(f"Knowledge card generated successfully")
            return card_content
            
        except Exception as e:
            logger.error(f"Error generating knowledge card: {e}", exc_info=True)
            raise
    
    def extract_core_concept(
        self,
        text: str,
        knowledge_point_info: KnowledgePointInfo
    ) -> str:
        """提取核心概念
        
        从文本中提取简洁的概念定义（50-100字）。
        
        Args:
            text: 输入文本
            knowledge_point_info: 知识点信息
        
        Returns:
            核心概念文本
        """
        # 优先使用知识点的摘要
        if knowledge_point_info.summary:
            summary = knowledge_point_info.summary
            if 50 <= len(summary) <= 100:
                return summary
            elif len(summary) < 50:
                # 如果太短，从文本中补充
                return self._extend_summary(summary, text, target_length=80)
            else:
                # 如果太长，截取
                return summary[:100] + "..."
        
        # 如果没有摘要，从文本中提取
        sentences = text.split('。')
        concept = ""
        for sentence in sentences:
            if len(concept) + len(sentence) <= 100:
                concept += sentence + "。"
            else:
                break
        
        return concept[:100] if concept else text[:100]
    
    def extract_formulas(self, text: str) -> List[str]:
        """提取公式/定理
        
        从文本中提取数学公式、定理等。
        
        Args:
            text: 输入文本
        
        Returns:
            公式列表
        """
        formulas = []
        
        # 简单的公式匹配模式（可以扩展）
        patterns = [
            r'[a-zA-Z]\s*=\s*[^。，]+',  # 变量 = 表达式
            r'[a-zA-Z]\([^)]+\)\s*=\s*[^。，]+',  # 函数表达式
            r'[a-zA-Z]\s*→\s*[^。，]+',  # 映射关系
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            formulas.extend(matches)
        
        # 去重
        formulas = list(set(formulas))
        
        return formulas[:5]  # 最多返回5个公式
    
    def generate_examples(
        self,
        knowledge_point_info: KnowledgePointInfo,
        text: str
    ) -> List[Dict]:
        """生成典型例题
        
        生成1-2个简单例题。
        
        Args:
            knowledge_point_info: 知识点信息
            text: 输入文本
        
        Returns:
            例题列表，每个例题包含：question, answer, explanation
        """
        examples = []
        
        # 简单实现：从文本中提取示例，或使用模板生成
        # 这里使用模板生成
        if "函数" in knowledge_point_info.name or "函数" in knowledge_point_info.keywords:
            examples.append({
                "question": "定义一个函数 add(a, b)，计算两个数的和。",
                "answer": "def add(a, b):\n    return a + b",
                "explanation": "这是一个简单的函数定义示例，展示了如何使用def关键字定义函数。"
            })
        
        if "参数" in knowledge_point_info.name or "参数" in knowledge_point_info.keywords:
            examples.append({
                "question": "调用函数 add(3, 5)，结果是多少？",
                "answer": "8",
                "explanation": "函数add接收两个参数3和5，返回它们的和8。"
            })
        
        # 如果没有匹配的模板，生成通用示例
        if not examples:
            examples.append({
                "question": f"请给出一个关于{knowledge_point_info.name}的简单例子。",
                "answer": "示例答案",
                "explanation": f"这是关于{knowledge_point_info.name}的一个简单示例。"
            })
        
        return examples[:2]  # 最多返回2个例题
    
    def generate_common_mistakes(
        self,
        knowledge_point_info: KnowledgePointInfo,
        text: str
    ) -> List[str]:
        """生成常见误区
        
        列出学生容易出错的地方。
        
        Args:
            knowledge_point_info: 知识点信息
            text: 输入文本
        
        Returns:
            常见误区列表
        """
        mistakes = []
        
        # 根据知识点类型生成常见误区
        if "函数" in knowledge_point_info.name:
            mistakes.append("忘记使用return语句返回值")
            mistakes.append("函数参数类型不匹配")
            mistakes.append("函数作用域理解错误")
        
        if "参数" in knowledge_point_info.name:
            mistakes.append("位置参数和关键字参数混淆")
            mistakes.append("默认参数的位置错误")
        
        # 通用误区
        if not mistakes:
            mistakes.append(f"对{knowledge_point_info.name}的概念理解不准确")
            mistakes.append(f"在应用{knowledge_point_info.name}时容易忽略细节")
        
        return mistakes[:3]  # 最多返回3个常见误区
    
    def generate_learning_tips(
        self,
        knowledge_point_info: KnowledgePointInfo,
        text: str
    ) -> List[str]:
        """生成学习建议
        
        提供如何掌握这个知识点的建议。
        
        Args:
            knowledge_point_info: 知识点信息
            text: 输入文本
        
        Returns:
            学习建议列表
        """
        tips = []
        
        # 根据难度生成学习建议
        if knowledge_point_info.difficulty == "easy":
            tips.append("这是一个基础概念，建议多练习相关题目")
            tips.append("理解基本定义后，尝试自己举例说明")
        elif knowledge_point_info.difficulty == "hard":
            tips.append("这是一个难点，建议先理解前置知识")
            tips.append("多看几遍视频，理解核心概念")
            tips.append("完成相关练习，巩固理解")
        else:
            tips.append("理解概念后，通过练习加深印象")
            tips.append("注意区分相关概念的区别")
        
        # 通用建议
        tips.append(f"掌握{knowledge_point_info.name}的关键是理解其本质")
        tips.append("建议结合实际例子来理解")
        
        return tips[:4]  # 最多返回4个学习建议
    
    def format_as_markdown(
        self,
        knowledge_point_info: KnowledgePointInfo,
        core_concept: str,
        formulas: List[str],
        examples: List[Dict],
        common_mistakes: List[str],
        learning_tips: List[str]
    ) -> str:
        """格式化为Markdown格式
        
        Args:
            knowledge_point_info: 知识点信息
            core_concept: 核心概念
            formulas: 公式列表
            examples: 例题列表
            common_mistakes: 常见误区列表
            learning_tips: 学习建议列表
        
        Returns:
            Markdown格式的知识卡片
        """
        markdown = f"""# {knowledge_point_info.name}

## 📚 核心概念

{core_concept}

"""
        
        # 添加公式
        if formulas:
            markdown += "## 📐 关键公式/定理\n\n"
            for i, formula in enumerate(formulas, 1):
                markdown += f"{i}. `{formula}`\n"
            markdown += "\n"
        
        # 添加例题
        if examples:
            markdown += "## 💡 典型例题\n\n"
            for i, example in enumerate(examples, 1):
                markdown += f"### 例题 {i}\n\n"
                markdown += f"**题目**：{example['question']}\n\n"
                markdown += f"**答案**：\n```\n{example['answer']}\n```\n\n"
                markdown += f"**解析**：{example['explanation']}\n\n"
        
        # 添加常见误区
        if common_mistakes:
            markdown += "## ⚠️ 常见误区\n\n"
            for i, mistake in enumerate(common_mistakes, 1):
                markdown += f"{i}. {mistake}\n"
            markdown += "\n"
        
        # 添加学习建议
        if learning_tips:
            markdown += "## 💪 学习建议\n\n"
            for i, tip in enumerate(learning_tips, 1):
                markdown += f"{i}. {tip}\n"
            markdown += "\n"
        
        # 添加关键词标签
        if knowledge_point_info.keywords:
            markdown += "## 🏷️ 关键词\n\n"
            markdown += ", ".join([f"`{kw}`" for kw in knowledge_point_info.keywords[:5]])
            markdown += "\n"
        
        return markdown
    
    def _merge_texts(
        self,
        asr_text: Optional[str],
        ocr_text: Optional[str],
        summary: str
    ) -> str:
        """合并文本
        
        Args:
            asr_text: ASR文本
            ocr_text: OCR文本
            summary: 摘要
        
        Returns:
            合并后的文本
        """
        texts = [summary]
        if asr_text:
            texts.append(asr_text)
        if ocr_text:
            texts.append(ocr_text)
        return " ".join(texts)
    
    def _extend_summary(
        self,
        summary: str,
        text: str,
        target_length: int = 80
    ) -> str:
        """扩展摘要
        
        Args:
            summary: 原始摘要
            text: 完整文本
            target_length: 目标长度
        
        Returns:
            扩展后的摘要
        """
        if len(summary) >= target_length:
            return summary
        
        # 从完整文本中补充
        remaining = target_length - len(summary)
        sentences = text.split('。')
        
        for sentence in sentences:
            if len(summary) + len(sentence) <= target_length:
                summary += sentence + "。"
            else:
                break
        
        return summary[:target_length]


# 使用示例
if __name__ == "__main__":
    from tests.mock_data import MOCK_KNOWLEDGE_POINT
    
    # 创建生成器
    generator = KnowledgeCardGenerator(use_ai=False)
    
    # 创建知识点信息
    kp_info = KnowledgePointInfo(
        id=MOCK_KNOWLEDGE_POINT["id"],
        name=MOCK_KNOWLEDGE_POINT["name"],
        summary=MOCK_KNOWLEDGE_POINT["summary"],
        keywords=MOCK_KNOWLEDGE_POINT["keywords"],
        difficulty=MOCK_KNOWLEDGE_POINT["difficulty"]
    )
    
    # 生成知识卡片
    asr_text = "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"
    card = generator.generate_card(kp_info, asr_text=asr_text)
    
    # 输出结果
    print("=" * 60)
    print("知识卡片生成结果")
    print("=" * 60)
    print(card)
