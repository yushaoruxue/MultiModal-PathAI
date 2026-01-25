"""
知识点切分算法使用示例

运行前请先安装依赖：
pip install jieba numpy
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from knowledge_point_segmenter import KnowledgePointSegmenter
from mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS


def main():
    """主函数"""
    print("=" * 60)
    print("知识点切分算法 - 使用示例")
    print("=" * 60)
    
    # 创建切分器
    print("\n1. 创建知识点切分器...")
    segmenter = KnowledgePointSegmenter(
        similarity_threshold=0.7,  # 相似度阈值
        min_duration=120.0,         # 最小时长2分钟
        max_duration=600.0          # 最大时长10分钟
    )
    print("✓ 切分器创建成功")
    
    # 执行切分
    print("\n2. 执行知识点切分...")
    print(f"   ASR文本段数: {len(MOCK_ASR_TEXTS)}")
    print(f"   OCR文本段数: {len(MOCK_OCR_TEXTS)}")
    
    knowledge_points = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    print(f"✓ 切分完成，生成了 {len(knowledge_points)} 个知识点")
    
    # 输出结果
    print("\n3. 切分结果：")
    print("=" * 60)
    for i, kp in enumerate(knowledge_points, 1):
        duration = kp.end_time - kp.start_time
        print(f"\n知识点 {i}: {kp.name}")
        print(f"  时间范围: {kp.start_time:.1f}s - {kp.end_time:.1f}s (时长: {duration:.1f}秒)")
        print(f"  关键词: {', '.join(kp.keywords[:5])}")
        print(f"  摘要: {kp.summary[:100]}...")
        print(f"  难度: {kp.difficulty}")
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("\n提示：")
    print("- 安装依赖: pip install jieba numpy")
    print("- 运行测试: pytest tests/test_segmenter.py -v")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n请先安装依赖：")
        print("  pip install jieba numpy")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
