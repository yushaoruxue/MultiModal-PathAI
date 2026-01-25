"""
模块B整合示例：难点识别 + 公共难点识别

展示如何将两个模块组合使用，完成完整的难点识别流程。
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from difficulty_detector import DifficultyDetector, BehaviorData
from public_difficulty_detector import PublicDifficultyDetector


def main():
    """主流程：个体难点识别 -> 公共难点识别"""
    
    print("=" * 60)
    print("模块B：难点识别算法 - 完整流程演示")
    print("=" * 60)
    
    # 步骤1：个体难点识别
    print("\n【步骤1】个体难点识别")
    print("-" * 60)
    
    detector = DifficultyDetector()
    
    # 模拟多个学生的行为数据
    students_behavior = [
        BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                    total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
        BehaviorData(user_id=2, knowledge_point_id=10, replay_count=2, pause_count=4,
                    total_watch_time=500.0, knowledge_point_duration=200.0, seek_count=1),
        BehaviorData(user_id=3, knowledge_point_id=10, replay_count=0, pause_count=1,
                    total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
        BehaviorData(user_id=4, knowledge_point_id=10, replay_count=4, pause_count=6,
                    total_watch_time=700.0, knowledge_point_duration=200.0, seek_count=3),
    ]
    
    print(f"检测 {len(students_behavior)} 个学生的学习行为...")
    individual_results = []
    
    for behavior in students_behavior:
        result = detector.detect(behavior)
        individual_results.append((behavior.user_id, result))
        
        status = "⚠️ 疑难点" if result.is_difficult else "✓ 正常"
        print(f"  学生 {behavior.user_id}: {status} (分数: {result.difficulty_score:.2f}/10)")
        if result.trigger_reasons:
            for reason in result.trigger_reasons:
                print(f"    - {reason}")
    
    # 步骤2：公共难点识别
    print("\n【步骤2】公共难点识别")
    print("-" * 60)
    
    public_detector = PublicDifficultyDetector(difficulty_ratio_threshold=0.3)
    public_result = public_detector.detect_public_difficulty(10, students_behavior)
    
    print(f"知识点ID: {public_result.knowledge_point_id}")
    print(f"是否为公共难点: {'是' if public_result.is_public_difficulty else '否'}")
    print(f"困难学生比例: {public_result.difficulty_ratio:.1%}")
    print(f"平均困难度分数: {public_result.average_difficulty_score:.2f}/10")
    print(f"受影响学生: {public_result.affected_students}")
    print(f"\n教学建议:")
    print(f"  {public_result.recommendation}")
    
    # 步骤3：统计报告
    print("\n【步骤3】统计报告")
    print("-" * 60)
    
    # 模拟多个知识点的结果
    all_results = [public_result]
    report = public_detector.generate_statistics_report(all_results)
    
    print(f"总知识点数: {report['total_knowledge_points']}")
    print(f"公共难点数: {report['public_difficulties']}")
    print(f"公共难点比例: {report.get('public_difficulty_ratio', 0):.1%}")
    print(f"平均困难比例: {report['average_difficulty_ratio']:.1%}")
    
    if report['most_difficult_kp']:
        print(f"\n最困难的知识点:")
        print(f"  ID: {report['most_difficult_kp']['id']}")
        print(f"  困难比例: {report['most_difficult_kp']['difficulty_ratio']:.1%}")
        print(f"  建议: {report['most_difficult_kp']['recommendation']}")
    
    print("\n" + "=" * 60)
    print("模块B完整流程演示完成！")
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
