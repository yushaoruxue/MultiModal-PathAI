"""
模块A整合示例：知识点切分 + 自动标注 + 知识图谱构建

展示如何将三个模块组合使用，完成完整的视频多模态解析流程。
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from knowledge_point_segmenter import KnowledgePointSegmenter, KnowledgePoint
from knowledge_point_annotator import KnowledgePointAnnotator
from knowledge_graph_builder import KnowledgeGraphBuilder, KnowledgePointInfo
from mock_data import MOCK_ASR_TEXTS, MOCK_OCR_TEXTS


def main():
    """主流程：切分 -> 标注 -> 构建图谱"""
    
    print("=" * 60)
    print("模块A：视频多模态解析核心算法 - 完整流程演示")
    print("=" * 60)
    
    # 步骤1：知识点切分
    print("\n【步骤1】知识点切分")
    print("-" * 60)
    segmenter = KnowledgePointSegmenter(
        similarity_threshold=0.7,
        min_duration=120.0,
        max_duration=600.0
    )
    
    knowledge_points = segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    print(f"✓ 切分完成，生成了 {len(knowledge_points)} 个知识点")
    
    # 步骤2：知识点自动标注
    print("\n【步骤2】知识点自动标注")
    print("-" * 60)
    annotator = KnowledgePointAnnotator()
    
    annotated_knowledge_points = []
    for i, kp in enumerate(knowledge_points, 1):
        # 获取该知识点的ASR和OCR文本
        kp_asr = [
            item for item in MOCK_ASR_TEXTS
            if item["start_time"] >= kp.start_time and item["end_time"] <= kp.end_time
        ]
        kp_ocr = [
            item for item in MOCK_OCR_TEXTS
            if item["start_time"] >= kp.start_time and item["end_time"] <= kp.end_time
        ]
        
        # 合并文本用于标注
        kp_text = " ".join([item.get("text", "") for item in kp_asr])
        
        # 执行标注
        annotation = annotator.annotate(
            knowledge_point_text=kp_text,
            asr_texts=kp_asr,
            ocr_texts=kp_ocr,
            start_time=kp.start_time,
            end_time=kp.end_time
        )
        
        # 更新知识点信息
        kp.name = annotation["name"]
        kp.summary = annotation["summary"]
        kp.keywords = annotation["keywords"]
        kp.difficulty = annotation["difficulty"]
        
        annotated_knowledge_points.append(kp)
        print(f"✓ 知识点 {i}: {kp.name} ({kp.difficulty})")
    
    # 步骤3：构建知识图谱
    print("\n【步骤3】构建知识图谱")
    print("-" * 60)
    
    # 转换为KnowledgePointInfo格式
    kp_infos = [
        KnowledgePointInfo(
            id=i+1,
            name=kp.name,
            summary=kp.summary,
            keywords=kp.keywords,
            start_time=kp.start_time,
            end_time=kp.end_time
        )
        for i, kp in enumerate(annotated_knowledge_points)
    ]
    
    # 构建图谱
    graph_builder = KnowledgeGraphBuilder()
    graph = graph_builder.build_graph(kp_infos)
    
    print(f"✓ 图谱构建完成：{graph.number_of_nodes()} 个节点，{graph.number_of_edges()} 条边")
    
    # 输出关系
    relations = graph_builder.get_relations(graph)
    if relations:
        print("\n检测到的关系：")
        for rel in relations:
            source_name = next(kp.name for kp in kp_infos if kp.id == rel.source_id)
            target_name = next(kp.name for kp in kp_infos if kp.id == rel.target_id)
            print(f"  {source_name} -> {target_name}: {rel.relation_type} (置信度: {rel.confidence:.2f})")
    
    # 检测循环
    cycles = graph_builder.detect_cycles(graph)
    if cycles:
        print(f"\n⚠️  检测到 {len(cycles)} 个循环依赖（已自动解决）")
    else:
        print("\n✓ 未检测到循环依赖")
    
    # 输出最终结果
    print("\n" + "=" * 60)
    print("最终结果：知识点列表")
    print("=" * 60)
    for i, kp in enumerate(annotated_knowledge_points, 1):
        print(f"\n知识点 {i}: {kp.name}")
        print(f"  时间: {kp.start_time:.1f}s - {kp.end_time:.1f}s")
        print(f"  关键词: {', '.join(kp.keywords[:5])}")
        print(f"  摘要: {kp.summary[:80]}...")
        print(f"  难度: {kp.difficulty}")
    
    print("\n" + "=" * 60)
    print("模块A完整流程演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n请先安装依赖：")
        print("  pip install jieba numpy networkx")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
