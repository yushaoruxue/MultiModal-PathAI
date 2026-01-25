"""
知识点自动标注逻辑

对切分好的知识点进行自动标注，包括：
- 知识点名称生成
- 知识点摘要生成
- 关键词提取
- 难度自动标注
- 知识点类型标注
"""

import logging
from typing import List, Dict, Optional
import jieba
import jieba.analyse
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgePointAnnotator:
    """知识点自动标注器
    
    对切分好的知识点进行自动标注，生成名称、摘要、关键词、难度等信息。
    """
    
    def __init__(
        self,
        name_max_length: int = 15,
        summary_min_length: int = 50,
        summary_max_length: int = 200,
        keyword_count: int = 10
    ):
        """初始化知识点标注器
        
        Args:
            name_max_length: 知识点名称最大长度（字符数）
            summary_min_length: 摘要最小长度（字符数）
            summary_max_length: 摘要最大长度（字符数）
            keyword_count: 关键词数量
        """
        self.name_max_length = name_max_length
        self.summary_min_length = summary_min_length
        self.summary_max_length = summary_max_length
        self.keyword_count = keyword_count
        
        # 初始化jieba
        jieba.initialize()
        
        # 知识点类型关键词（用于类型分类）
        self.type_keywords = {
            "concept": ["定义", "概念", "是什么", "含义", "理解"],
            "example": ["例子", "示例", "例题", "实例", "演示"],
            "practice": ["练习", "操作", "实践", "动手", "实验"],
            "summary": ["总结", "回顾", "归纳", "要点"],
        }
        
        logger.info("KnowledgePointAnnotator initialized")
    
    def annotate(
        self,
        knowledge_point_text: str,
        asr_texts: Optional[List[Dict]] = None,
        ocr_texts: Optional[List[Dict]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict:
        """对知识点进行自动标注
        
        生成知识点的所有标注信息，包括名称、摘要、关键词、难度、类型等。
        
        Args:
            knowledge_point_text: 知识点的文本内容
            asr_texts: ASR转写文本列表（可选，用于补充信息）
            ocr_texts: OCR识别文本列表（可选，用于补充信息）
            start_time: 知识点开始时间（可选）
            end_time: 知识点结束时间（可选）
        
        Returns:
            标注结果字典，包含：
            - name: 知识点名称
            - summary: 摘要
            - keywords: 关键词列表
            - difficulty: 难度等级（easy/medium/hard）
            - type: 知识点类型（concept/example/practice/summary）
            - metadata: 其他元数据
        """
        try:
            logger.info(f"Annotating knowledge point, text length: {len(knowledge_point_text)}")
            
            # 合并所有文本
            full_text = self._merge_texts(knowledge_point_text, asr_texts, ocr_texts)
            
            # 生成各项标注
            name = self.generate_name(full_text)
            summary = self.generate_summary(full_text)
            keywords = self.extract_keywords(full_text, top_k=self.keyword_count)
            difficulty = self.estimate_difficulty(full_text, keywords)
            kp_type = self.classify_type(full_text)
            
            result = {
                "name": name,
                "summary": summary,
                "keywords": keywords,
                "difficulty": difficulty,
                "type": kp_type,
                "metadata": {
                    "text_length": len(full_text),
                    "keyword_count": len(keywords),
                    "start_time": start_time,
                    "end_time": end_time,
                }
            }
            
            logger.info(f"Annotation completed: {name}")
            return result
            
        except Exception as e:
            logger.error(f"Error in annotation: {e}", exc_info=True)
            raise
    
    def generate_name(self, text: str) -> str:
        """生成知识点名称
        
        从文本中提取核心概念，使用关键词组合生成名称。
        名称要简洁（5-15字）。
        
        Args:
            text: 输入文本
        
        Returns:
            知识点名称
        """
        try:
            if not text:
                return "未命名知识点"
            
            # 提取关键词
            keywords = self.extract_keywords(text, top_k=5)
            
            if keywords:
                # 使用前2-3个关键词组合
                name = "".join(keywords[:2])
                if len(name) < 5:
                    name = "".join(keywords[:3])
                
                # 限制长度
                if len(name) > self.name_max_length:
                    name = name[:self.name_max_length]
                
                return name
            
            # 如果没有关键词，使用文本的前几个字
            sentences = text.split('。')
            if sentences:
                first_sentence = sentences[0].strip()
                if len(first_sentence) > self.name_max_length:
                    return first_sentence[:self.name_max_length]
                return first_sentence
            
            return text[:self.name_max_length] if len(text) > self.name_max_length else text
            
        except Exception as e:
            logger.warning(f"Error generating name: {e}")
            return "未命名知识点"
    
    def generate_summary(self, text: str) -> str:
        """生成知识点摘要
        
        使用简单的方法生成摘要：提取关键句子。
        后续可以替换为TextRank或AI模型生成。
        
        Args:
            text: 输入文本
        
        Returns:
            摘要文本（50-200字）
        """
        try:
            if not text:
                return ""
            
            # 简单实现：提取前几个句子
            sentences = [s.strip() for s in text.split('。') if s.strip()]
            
            if not sentences:
                return text[:self.summary_max_length] if len(text) > self.summary_max_length else text
            
            summary = ""
            for sentence in sentences:
                if len(summary) + len(sentence) <= self.summary_max_length:
                    summary += sentence + "。"
                else:
                    break
            
            # 确保摘要长度在要求范围内
            if len(summary) < self.summary_min_length:
                # 如果太短，至少包含前几个句子
                summary = "。".join(sentences[:3]) + "。"
                if len(summary) > self.summary_max_length:
                    summary = summary[:self.summary_max_length]
            
            return summary.strip()
            
        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return text[:self.summary_max_length] if text else ""
    
    def extract_keywords(self, text: str, top_k: Optional[int] = None) -> List[str]:
        """提取关键词
        
        使用jieba的TF-IDF算法提取关键词。
        过滤停用词。
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词，如果为None则使用self.keyword_count
        
        Returns:
            关键词列表
        """
        try:
            if not text:
                return []
            
            if top_k is None:
                top_k = self.keyword_count
            
            # 使用jieba提取关键词（TF-IDF）
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
            
            # 过滤停用词和单字符
            filtered_keywords = [
                kw for kw in keywords
                if len(kw) > 1 and not self._is_stopword(kw)
            ]
            
            return filtered_keywords[:top_k]
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def estimate_difficulty(self, text: str, keywords: Optional[List[str]] = None) -> str:
        """估算知识点难度
        
        基于文本特征（长度、复杂度、专业术语数量）估算难度。
        
        规则：
        - 文本长度 > 500字 且 关键词 > 8个 -> hard
        - 文本长度 < 200字 且 关键词 < 5个 -> easy
        - 其他 -> medium
        
        Args:
            text: 输入文本
            keywords: 关键词列表（可选，如果不提供会自动提取）
        
        Returns:
            难度等级：easy/medium/hard
        """
        try:
            if not text:
                return "medium"
            
            if keywords is None:
                keywords = self.extract_keywords(text, top_k=10)
            
            text_length = len(text)
            keyword_count = len(keywords)
            
            # 计算专业术语比例（简单规则：关键词占比）
            keyword_ratio = keyword_count / max(len(text.split()), 1)
            
            # 判断难度
            if text_length > 500 and keyword_count > 8 and keyword_ratio > 0.1:
                return "hard"
            elif text_length < 200 and keyword_count < 5:
                return "easy"
            else:
                return "medium"
                
        except Exception as e:
            logger.warning(f"Error estimating difficulty: {e}")
            return "medium"
    
    def classify_type(self, text: str) -> str:
        """分类知识点类型
        
        根据文本内容判断知识点类型：
        - concept: 概念定义
        - example: 例题讲解
        - practice: 实践操作
        - summary: 总结归纳
        
        Args:
            text: 输入文本
        
        Returns:
            知识点类型
        """
        try:
            if not text:
                return "concept"
            
            # 统计各类型关键词出现次数
            type_scores = {}
            for kp_type, keywords in self.type_keywords.items():
                score = sum(1 for kw in keywords if kw in text)
                type_scores[kp_type] = score
            
            # 返回得分最高的类型
            if type_scores:
                max_type = max(type_scores, key=type_scores.get)
                if type_scores[max_type] > 0:
                    return max_type
            
            # 默认返回concept
            return "concept"
            
        except Exception as e:
            logger.warning(f"Error classifying type: {e}")
            return "concept"
    
    def _merge_texts(
        self,
        knowledge_point_text: str,
        asr_texts: Optional[List[Dict]],
        ocr_texts: Optional[List[Dict]]
    ) -> str:
        """合并所有文本
        
        Args:
            knowledge_point_text: 知识点文本
            asr_texts: ASR文本列表
            ocr_texts: OCR文本列表
        
        Returns:
            合并后的文本
        """
        texts = [knowledge_point_text]
        
        if asr_texts:
            for item in asr_texts:
                text = item.get("text", "")
                if text:
                    texts.append(text)
        
        if ocr_texts:
            for item in ocr_texts:
                text = item.get("text", "")
                if text:
                    texts.append(text)
        
        return " ".join(texts)
    
    def _is_stopword(self, word: str) -> bool:
        """判断是否为停用词
        
        Args:
            word: 词语
        
        Returns:
            是否为停用词
        """
        # 简单的停用词列表（可以扩展）
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
            "自己", "这", "那", "个", "中", "为", "来", "能", "可以", "对", "等", "与"
        }
        
        return word in stopwords or len(word) == 1


# 使用示例
if __name__ == "__main__":
    from tests.mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS
    
    # 创建标注器
    annotator = KnowledgePointAnnotator()
    
    # 测试文本
    test_text = """
    函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。
    函数的定义包括函数名、参数列表和函数体。让我们看一个简单的例子。
    def add(a, b): return a + b。这就是一个简单的加法函数。
    """
    
    # 执行标注
    result = annotator.annotate(
        knowledge_point_text=test_text,
        asr_texts=MOCK_ASR_TEXTS[:3],
        ocr_texts=MOCK_OCR_TEXTS[:2]
    )
    
    # 输出结果
    print("=" * 60)
    print("知识点自动标注结果")
    print("=" * 60)
    print(f"名称: {result['name']}")
    print(f"摘要: {result['summary']}")
    print(f"关键词: {', '.join(result['keywords'])}")
    print(f"难度: {result['difficulty']}")
    print(f"类型: {result['type']}")
    print(f"元数据: {result['metadata']}")
