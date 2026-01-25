"""
模块D整合示例：补偿资源生成完整流程

展示如何将四个模块组合使用，完成完整的补偿资源生成和推送流程。
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from knowledge_card_generator import KnowledgeCardGenerator, KnowledgePointInfo as KPInfo
from exercise_generator import ExerciseGenerator
from resource_pusher import ResourcePusher
from resource_quality_evaluator import ResourceQualityEvaluator
from tests.mock_data import MOCK_KNOWLEDGE_POINT


def main():
    """主流程：生成资源 -> 评估质量 -> 推送资源"""
    
    print("=" * 60)
    print("模块D：补偿资源生成 - 完整流程演示")
    print("=" * 60)
    
    # 步骤1：生成知识卡片
    print("\n【步骤1】生成知识卡片")
    print("-" * 60)
    
    card_generator = KnowledgeCardGenerator(use_ai=False)
    
    kp_info = KPInfo(
        id=MOCK_KNOWLEDGE_POINT["id"],
        name=MOCK_KNOWLEDGE_POINT["name"],
        summary=MOCK_KNOWLEDGE_POINT["summary"],
        keywords=MOCK_KNOWLEDGE_POINT["keywords"],
        difficulty=MOCK_KNOWLEDGE_POINT["difficulty"]
    )
    
    asr_text = "函数是一种映射关系，它将输入映射到输出。我们可以用def关键字来定义函数。"
    knowledge_card = card_generator.generate_card(kp_info, asr_text=asr_text)
    
    print(f"✓ 知识卡片生成完成（{len(knowledge_card)} 字符）")
    print(f"  预览：{knowledge_card[:100]}...")
    
    # 步骤2：生成练习题
    print("\n【步骤2】生成练习题")
    print("-" * 60)
    
    exercise_generator = ExerciseGenerator(use_ai=False)
    exercises = exercise_generator.generate_exercises(kp_info, count=5)
    
    print(f"✓ 练习题生成完成：{len(exercises)} 题")
    for i, ex in enumerate(exercises[:3], 1):  # 只显示前3题
        print(f"  题目 {i}: {ex.type} - {ex.question[:50]}...")
    
    # 步骤3：评估资源质量
    print("\n【步骤3】评估资源质量")
    print("-" * 60)
    
    quality_evaluator = ResourceQualityEvaluator()
    
    # 评估知识卡片质量
    card_quality = quality_evaluator.get_quality_score(
        resource_id="card_001",
        resource_content=knowledge_card,
        knowledge_point_info={
            "name": kp_info.name,
            "keywords": kp_info.keywords
        },
        student_feedback="mastered",
        exercise_score=0.9
    )
    
    print(f"✓ 知识卡片质量评估完成")
    print(f"  内容质量: {card_quality.content_quality:.2f}")
    print(f"  相关性: {card_quality.relevance:.2f}")
    print(f"  有效性: {card_quality.effectiveness:.2f}")
    print(f"  综合分数: {card_quality.overall_score:.2f}")
    
    # 评估练习题质量（使用第一题）
    if exercises:
        exercise_content = f"{exercises[0].question}\n{exercises[0].explanation}"
        exercise_quality = quality_evaluator.get_quality_score(
            resource_id="exercise_001",
            resource_content=exercise_content,
            knowledge_point_info={
                "name": kp_info.name,
                "keywords": kp_info.keywords
            },
            exercise_score=0.85
        )
        
        print(f"\n✓ 练习题质量评估完成")
        print(f"  综合分数: {exercise_quality.overall_score:.2f}")
    
    # 步骤4：推送资源
    print("\n【步骤4】推送资源")
    print("-" * 60)
    
    resource_pusher = ResourcePusher(push_method="database")
    
    # 推送知识卡片
    card_success = resource_pusher.push_resource(
        user_id=1,
        knowledge_point_id=kp_info.id,
        resource_type="knowledge_card",
        resource_content=knowledge_card
    )
    print(f"✓ 知识卡片推送: {'成功' if card_success else '失败'}")
    
    # 推送练习题（JSON格式）
    import json
    exercises_json = json.dumps([
        {
            "question": ex.question,
            "type": ex.type,
            "options": ex.options,
            "correct_answer": ex.correct_answer,
            "explanation": ex.explanation
        }
        for ex in exercises
    ], ensure_ascii=False)
    
    exercise_success = resource_pusher.push_resource(
        user_id=1,
        knowledge_point_id=kp_info.id,
        resource_type="exercise",
        resource_content=exercises_json
    )
    print(f"✓ 练习题推送: {'成功' if exercise_success else '失败'}")
    
    # 步骤5：查看待推送资源
    print("\n【步骤5】查看待推送资源")
    print("-" * 60)
    
    pending_resources = resource_pusher.get_pending_resources(1)
    print(f"✓ 待推送资源数: {len(pending_resources)}")
    for resource in pending_resources:
        print(f"  资源ID: {resource['resource_id']}")
        print(f"  类型: {resource['resource_type']}")
        print(f"  知识点ID: {resource['knowledge_point_id']}")
    
    # 步骤6：标记资源为已读
    print("\n【步骤6】标记资源为已读")
    print("-" * 60)
    
    if pending_resources:
        resource_id = pending_resources[0]["resource_id"]
        marked = resource_pusher.mark_as_read(1, resource_id)
        print(f"✓ 资源标记: {'成功' if marked else '失败'}")
    
    # 步骤7：生成质量报告
    print("\n【步骤7】生成质量报告")
    print("-" * 60)
    
    resource_ids = ["card_001", "exercise_001"]
    quality_report = quality_evaluator.generate_quality_report(resource_ids)
    
    print(f"✓ 质量报告生成完成")
    print(f"  总资源数: {quality_report['total_resources']}")
    print(f"  已评估数: {quality_report['evaluated_resources']}")
    print(f"  平均分数: {quality_report['average_score']:.2f}")
    print(f"  高质量资源: {quality_report['high_quality']}")
    print(f"  低质量资源: {quality_report['low_quality']}")
    print(f"  需要重新生成: {quality_report['regeneration_needed']}")
    
    print("\n" + "=" * 60)
    print("模块D完整流程演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("\n请确保所有依赖已安装")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
