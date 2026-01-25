"""
模块C整合示例：学习路径生成 + 动态调整 + 补偿资源推送

展示如何将三个模块组合使用，完成完整的学习路径管理流程。
"""

import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from learning_path_generator import LearningPathGenerator
from path_adjuster import PathAdjuster, LearningEvent
from remedial_resource_strategy import RemedialResourceStrategy, DifficultyLevel
from tests.mock_data import MOCK_MASTERY_STATUS, MOCK_DEPENDENCIES


def main():
    """主流程：生成路径 -> 调整路径 -> 推送资源"""
    
    print("=" * 60)
    print("模块C：学习路径生成算法 - 完整流程演示")
    print("=" * 60)
    
    # 步骤1：生成初始学习路径
    print("\n【步骤1】生成初始学习路径")
    print("-" * 60)
    
    generator = LearningPathGenerator()
    
    mastery_status = MOCK_MASTERY_STATUS
    dependencies = MOCK_DEPENDENCIES
    difficult_points = [3, 6]
    difficulty_info = {
        1: "easy",
        2: "medium",
        3: "hard",
        4: "medium",
        5: "easy",
        6: "hard"
    }
    
    initial_path = generator.generate_path(
        user_id=1,
        mastery_status=mastery_status,
        dependencies=dependencies,
        difficult_points=difficult_points,
        difficulty_info=difficulty_info
    )
    
    print(f"✓ 生成了 {len(initial_path)} 个路径节点")
    for node in initial_path[:5]:  # 只显示前5个
        print(f"  顺序 {node['order']}: 知识点 {node['knowledge_point_id']} ({node['node_type']})")
    
    # 步骤2：动态调整路径
    print("\n【步骤2】动态调整路径")
    print("-" * 60)
    
    adjuster = PathAdjuster(path_generator=generator)
    
    # 模拟：学生标记知识点2为疑难
    event = LearningEvent(
        event_type="difficult",
        knowledge_point_id=2,
        timestamp=datetime.now()
    )
    
    adjustment_result = adjuster.adjust_path(initial_path, event)
    
    print(f"调整原因: {adjustment_result.adjustment_reason}")
    print(f"下一步行动: {adjustment_result.next_action}")
    print(f"调整后路径节点数: {len(adjustment_result.adjusted_path)}")
    
    # 步骤3：补偿资源推送
    print("\n【步骤3】补偿资源推送")
    print("-" * 60)
    
    strategy = RemedialResourceStrategy()
    
    # 检查是否应该推送
    if strategy.should_push_resource(2, 1):
        # 获取推送策略（首次卡顿）
        push_strategy = strategy.get_push_strategy(DifficultyLevel.FIRST, attempt_count=1)
        
        # 推送资源
        success = strategy.push_resource(1, 2, push_strategy)
        
        if success:
            print(f"✓ 资源推送成功")
            print(f"  推送级别: {push_strategy.level.value}")
            print(f"  推送资源: {', '.join(push_strategy.resources)}")
            
            # 模拟反馈：练习得分60%
            print(f"\n模拟反馈：练习得分 60%")
            feedback_result = strategy.handle_feedback(
                user_id=1,
                resource_id=2,
                feedback_type="still_difficult",
                exercise_score=0.6
            )
            
            print(f"反馈处理:")
            print(f"  行动: {feedback_result['action']}")
            print(f"  消息: {feedback_result.get('message', '')}")
            
            if feedback_result['action'] == 'upgrade':
                print(f"  下一级别: {feedback_result['next_strategy']['level']}")
                print(f"  下一资源: {', '.join(feedback_result['next_strategy']['resources'])}")
    
    # 步骤4：获取下一步学习建议
    print("\n【步骤4】获取下一步学习建议")
    print("-" * 60)
    
    suggestion = generator.get_next_suggestion(adjustment_result.adjusted_path, current_position=0)
    if suggestion:
        print(f"下一步学习:")
        print(f"  知识点ID: {suggestion.next_knowledge_point_id}")
        print(f"  原因: {suggestion.reason}")
        print(f"  预计时间: {suggestion.estimated_time:.1f} 分钟")
    
    # 步骤5：查看调整历史
    print("\n【步骤5】查看调整历史")
    print("-" * 60)
    
    history = adjuster.get_adjustment_history()
    print(f"调整历史记录数: {len(history)}")
    if history:
        latest = history[-1]
        print(f"最新调整:")
        print(f"  时间: {latest['timestamp']}")
        print(f"  事件: {latest['event_type']}")
        print(f"  知识点: {latest['knowledge_point_id']}")
        print(f"  原因: {latest['reason']}")
    
    print("\n" + "=" * 60)
    print("模块C完整流程演示完成！")
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
