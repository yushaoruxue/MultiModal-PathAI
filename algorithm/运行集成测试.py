"""
运行系统集成测试

使用方法：
    python 运行集成测试.py

或者使用pytest：
    pytest tests/integration_test.py -v -s
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

def main():
    """运行集成测试"""
    print("=" * 60)
    print("系统集成测试")
    print("=" * 60)
    print("\n开始运行测试...\n")
    
    try:
        # 尝试使用pytest运行
        import pytest
        exit_code = pytest.main([
            "tests/integration_test.py",
            "-v",  # 详细输出
            "-s",  # 显示print输出
            "--tb=short"  # 简短的错误追踪
        ])
        
        if exit_code == 0:
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 部分测试失败")
            print("=" * 60)
        
        return exit_code
        
    except ImportError:
        print("❌ pytest未安装，请先安装：pip install pytest")
        print("\n或者直接运行测试文件：")
        print("  python tests/integration_test.py")
        
        # 尝试直接运行测试
        try:
            from tests.integration_test import TestCompleteLearningLoop
            test = TestCompleteLearningLoop()
            test.setup_method()
            
            print("\n运行场景1：视频解析到知识图谱构建")
            test.test_scenario1_video_parsing_to_knowledge_graph()
            
            print("\n运行场景2：行为采集到难点识别")
            test.test_scenario2_behavior_to_difficulty_detection()
            
            print("\n运行场景3：学习路径生成和调整")
            test.test_scenario3_learning_path_generation_and_adjustment()
            
            print("\n运行场景4：完整学习闭环")
            test.test_scenario4_complete_learning_loop()
            
            print("\n运行集成测试：所有模块协同工作")
            test.test_integration_all_modules()
            
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
            
            return 0
            
        except Exception as e:
            print(f"\n❌ 运行测试时出错：{e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
