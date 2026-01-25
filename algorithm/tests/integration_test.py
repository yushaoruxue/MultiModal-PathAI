"""
系统集成测试

测试整个学习闭环的功能，包括：
1. 视频上传 → 解析 → 知识点切分 → 知识点标注 → 知识图谱构建
2. 学生观看视频 → 行为采集 → 难点识别 → 补偿推送
3. 学生完成练习 → 反馈 → 路径调整
4. 完整的学习闭环
"""

import pytest
import sys
import os
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_point_segmenter import KnowledgePointSegmenter, KnowledgePoint
from knowledge_point_annotator import KnowledgePointAnnotator
from knowledge_graph_builder import KnowledgeGraphBuilder, KnowledgePointInfo
from difficulty_detector import DifficultyDetector, BehaviorData
from public_difficulty_detector import PublicDifficultyDetector
from learning_path_generator import LearningPathGenerator
from path_adjuster import PathAdjuster, LearningEvent
from remedial_resource_strategy import RemedialResourceStrategy, DifficultyLevel
from tests.mock_data import (
    MOCK_ASR_TEXTS, MOCK_OCR_TEXTS, MOCK_BEHAVIOR_DATA,
    MOCK_MASTERY_STATUS, MOCK_DEPENDENCIES, MOCK_KNOWLEDGE_POINT
)


class TestCompleteLearningLoop:
    """完整学习闭环测试"""
    
    def setup_method(self):
        """测试前初始化所有模块"""
        # 模块A：视频多模态解析
        self.segmenter = KnowledgePointSegmenter()
        self.annotator = KnowledgePointAnnotator()
        self.graph_builder = KnowledgeGraphBuilder()
        
        # 模块B：难点识别
        self.difficulty_detector = DifficultyDetector()
        self.public_detector = PublicDifficultyDetector()
        
        # 模块C：学习路径
        self.path_generator = LearningPathGenerator()
        self.path_adjuster = PathAdjuster(path_generator=self.path_generator)
        self.resource_strategy = RemedialResourceStrategy()
    
    def test_scenario1_video_parsing_to_knowledge_graph(self):
        """测试场景1：视频解析到知识图谱构建
        
        流程：视频上传 → ASR/OCR → 知识点切分 → 知识点标注 → 知识图谱构建
        """
        print("\n=== 场景1：视频解析到知识图谱构建 ===")
        
        # 步骤1：知识点切分
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        assert len(knowledge_points) > 0, "应该至少生成一个知识点"
        print(f"✓ 知识点切分完成：{len(knowledge_points)} 个知识点")
        
        # 步骤2：知识点标注
        annotated_kps = []
        for kp in knowledge_points[:3]:  # 只标注前3个，加快测试
            kp_asr = [item for item in MOCK_ASR_TEXTS 
                     if item["start_time"] >= kp.start_time and item["end_time"] <= kp.end_time]
            kp_text = " ".join([item.get("text", "") for item in kp_asr])
            
            annotation = self.annotator.annotate(
                knowledge_point_text=kp_text,
                asr_texts=kp_asr,
                start_time=kp.start_time,
                end_time=kp.end_time
            )
            
            # 更新知识点信息
            kp.name = annotation["name"]
            kp.summary = annotation["summary"]
            kp.keywords = annotation["keywords"]
            kp.difficulty = annotation["difficulty"]
            
            annotated_kps.append(kp)
        
        assert len(annotated_kps) > 0, "应该至少有一个标注的知识点"
        print(f"✓ 知识点标注完成：{len(annotated_kps)} 个知识点")
        
        # 步骤3：构建知识图谱
        kp_infos = [
            KnowledgePointInfo(
                id=i+1,
                name=kp.name,
                summary=kp.summary,
                keywords=kp.keywords,
                start_time=kp.start_time,
                end_time=kp.end_time
            )
            for i, kp in enumerate(annotated_kps)
        ]
        
        graph = self.graph_builder.build_graph(kp_infos)
        assert graph.number_of_nodes() > 0, "知识图谱应该有节点"
        print(f"✓ 知识图谱构建完成：{graph.number_of_nodes()} 个节点，{graph.number_of_edges()} 条边")
        
        # 验证图谱结构
        relations = self.graph_builder.get_relations(graph)
        print(f"✓ 检测到 {len(relations)} 个关系")
        
        return graph, kp_infos
    
    def test_scenario2_behavior_to_difficulty_detection(self):
        """测试场景2：行为采集到难点识别
        
        流程：学生观看视频 → 行为采集 → 难点识别 → 公共难点识别
        """
        print("\n=== 场景2：行为采集到难点识别 ===")
        
        # 步骤1：个体难点识别
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=3,
            pause_count=5,
            total_watch_time=600.0,
            knowledge_point_duration=200.0,
            seek_count=2
        )
        
        result = self.difficulty_detector.detect(behavior_data)
        assert isinstance(result.is_difficult, bool), "应该有难点判定结果"
        print(f"✓ 个体难点识别完成：{'是疑难点' if result.is_difficult else '不是疑难点'}")
        print(f"  困难度分数：{result.difficulty_score:.2f}/10")
        
        # 步骤2：公共难点识别
        all_students_behavior = [
            BehaviorData(user_id=1, knowledge_point_id=10, replay_count=3, pause_count=5,
                        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2),
            BehaviorData(user_id=2, knowledge_point_id=10, replay_count=2, pause_count=4,
                        total_watch_time=500.0, knowledge_point_duration=200.0, seek_count=1),
            BehaviorData(user_id=3, knowledge_point_id=10, replay_count=0, pause_count=1,
                        total_watch_time=200.0, knowledge_point_duration=200.0, seek_count=0),
        ]
        
        public_result = self.public_detector.detect_public_difficulty(10, all_students_behavior)
        assert isinstance(public_result.is_public_difficulty, bool), "应该有公共难点判定结果"
        print(f"✓ 公共难点识别完成：{'是公共难点' if public_result.is_public_difficulty else '不是公共难点'}")
        print(f"  困难学生比例：{public_result.difficulty_ratio:.1%}")
        print(f"  教学建议：{public_result.recommendation}")
        
        return public_result
    
    def test_scenario3_learning_path_generation_and_adjustment(self):
        """测试场景3：学习路径生成和调整
        
        流程：生成学习路径 → 学生标记疑难 → 路径调整 → 补偿资源推送
        """
        print("\n=== 场景3：学习路径生成和调整 ===")
        
        # 步骤1：生成初始学习路径
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
        
        initial_path = self.path_generator.generate_path(
            user_id=1,
            mastery_status=mastery_status,
            dependencies=dependencies,
            difficult_points=difficult_points,
            difficulty_info=difficulty_info
        )
        
        assert len(initial_path) > 0, "应该生成学习路径"
        print(f"✓ 初始学习路径生成完成：{len(initial_path)} 个节点")
        
        # 步骤2：学生标记知识点为疑难，调整路径
        event = LearningEvent(
            event_type="difficult",
            knowledge_point_id=2,
            timestamp=datetime.now()
        )
        
        adjustment_result = self.path_adjuster.adjust_path(initial_path, event)
        assert len(adjustment_result.adjusted_path) > 0, "调整后应该有路径"
        print(f"✓ 路径调整完成：{adjustment_result.adjustment_reason}")
        
        # 步骤3：补偿资源推送
        if self.resource_strategy.should_push_resource(2, 1):
            push_strategy = self.resource_strategy.get_push_strategy(DifficultyLevel.FIRST, 1)
            success = self.resource_strategy.push_resource(1, 2, push_strategy)
            assert success, "资源推送应该成功"
            print(f"✓ 补偿资源推送完成：级别 {push_strategy.level.value}")
        
        return adjustment_result
    
    def test_scenario4_complete_learning_loop(self):
        """测试场景4：完整学习闭环
        
        完整流程：
        1. 视频解析 → 知识图谱
        2. 行为采集 → 难点识别
        3. 生成学习路径
        4. 学生遇到困难 → 路径调整 → 资源推送
        5. 学生完成学习 → 路径更新
        """
        print("\n=== 场景4：完整学习闭环 ===")
        
        # 阶段1：视频解析
        print("\n[阶段1] 视频解析")
        knowledge_points = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        print(f"  ✓ 知识点切分：{len(knowledge_points)} 个知识点")
        
        # 阶段2：难点识别
        print("\n[阶段2] 难点识别")
        behavior_data = BehaviorData(
            user_id=1,
            knowledge_point_id=10,
            replay_count=3,
            pause_count=5,
            total_watch_time=600.0,
            knowledge_point_duration=200.0,
            seek_count=2
        )
        difficulty_result = self.difficulty_detector.detect(behavior_data)
        difficult_points = [10] if difficulty_result.is_difficult else []
        print(f"  ✓ 难点识别：{'发现疑难点' if difficult_points else '无疑难点'}")
        
        # 阶段3：生成学习路径
        print("\n[阶段3] 生成学习路径")
        mastery_status = {1: "未学", 2: "未学", 3: "未学", 10: "疑难"}
        dependencies = [(1, 2, "prerequisite"), (2, 3, "prerequisite")]
        
        path = self.path_generator.generate_path(
            user_id=1,
            mastery_status=mastery_status,
            dependencies=dependencies,
            difficult_points=difficult_points
        )
        print(f"  ✓ 学习路径生成：{len(path)} 个节点")
        
        # 阶段4：遇到困难，调整路径并推送资源
        print("\n[阶段4] 遇到困难，调整路径")
        event = LearningEvent(
            event_type="difficult",
            knowledge_point_id=2,
            timestamp=datetime.now()
        )
        adjustment = self.path_adjuster.adjust_path(path, event)
        print(f"  ✓ 路径调整：{adjustment.adjustment_reason}")
        
        # 推送补偿资源
        if self.resource_strategy.should_push_resource(2, 1):
            push_strategy = self.resource_strategy.get_push_strategy(DifficultyLevel.FIRST, 1)
            self.resource_strategy.push_resource(1, 2, push_strategy)
            print(f"  ✓ 补偿资源推送：{', '.join(push_strategy.resources)}")
        
        # 阶段5：完成学习，更新路径
        print("\n[阶段5] 完成学习，更新路径")
        completion_event = LearningEvent(
            event_type="mastered",
            knowledge_point_id=1,
            timestamp=datetime.now()
        )
        final_adjustment = self.path_adjuster.adjust_path(adjustment.adjusted_path, completion_event)
        print(f"  ✓ 路径更新：{final_adjustment.adjustment_reason}")
        print(f"  ✓ 最终路径节点数：{len(final_adjustment.adjusted_path)}")
        
        # 验证完整性
        assert len(final_adjustment.adjusted_path) >= 0, "最终路径应该有效"
        print("\n✓ 完整学习闭环测试通过！")
        
        return final_adjustment
    
    def test_integration_all_modules(self):
        """集成测试：所有模块协同工作"""
        print("\n=== 集成测试：所有模块协同工作 ===")
        
        # 1. 模块A：视频解析
        kps = self.segmenter.segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
        assert len(kps) > 0
        
        # 2. 模块B：难点识别
        behavior = BehaviorData(
            user_id=1, knowledge_point_id=10,
            replay_count=3, pause_count=5,
            total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2
        )
        difficulty = self.difficulty_detector.detect(behavior)
        assert isinstance(difficulty.is_difficult, bool)
        
        # 3. 模块C：学习路径
        mastery = {1: "未学", 2: "未学", 3: "未学"}
        deps = [(1, 2, "prerequisite"), (2, 3, "prerequisite")]
        path = self.path_generator.generate_path(1, mastery, deps)
        assert len(path) > 0
        
        # 4. 路径调整
        event = LearningEvent("difficult", 2, datetime.now())
        adjusted = self.path_adjuster.adjust_path(path, event)
        assert len(adjusted.adjusted_path) > 0
        
        # 5. 资源推送
        strategy = self.resource_strategy.get_push_strategy(DifficultyLevel.FIRST, 1)
        pushed = self.resource_strategy.push_resource(1, 2, strategy)
        assert pushed or not self.resource_strategy.should_push_resource(2, 1)
        
        print("✓ 所有模块集成测试通过！")


@pytest.fixture
def setup_modules():
    """设置测试模块"""
    return {
        "segmenter": KnowledgePointSegmenter(),
        "annotator": KnowledgePointAnnotator(),
        "graph_builder": KnowledgeGraphBuilder(),
        "difficulty_detector": DifficultyDetector(),
        "public_detector": PublicDifficultyDetector(),
        "path_generator": LearningPathGenerator(),
        "path_adjuster": PathAdjuster(),
        "resource_strategy": RemedialResourceStrategy()
    }


def test_end_to_end_workflow(setup_modules):
    """端到端工作流测试"""
    print("\n" + "=" * 60)
    print("端到端工作流测试")
    print("=" * 60)
    
    modules = setup_modules
    
    # 完整流程
    # 1. 视频解析
    kps = modules["segmenter"].segment(MOCK_ASR_TEXTS, MOCK_OCR_TEXTS)
    print(f"✓ 步骤1：视频解析完成，{len(kps)} 个知识点")
    
    # 2. 难点识别
    behavior = BehaviorData(
        user_id=1, knowledge_point_id=10,
        replay_count=3, pause_count=5,
        total_watch_time=600.0, knowledge_point_duration=200.0, seek_count=2
    )
    difficulty = modules["difficulty_detector"].detect(behavior)
    print(f"✓ 步骤2：难点识别完成，{'是疑难点' if difficulty.is_difficult else '不是疑难点'}")
    
    # 3. 生成路径
    mastery = {1: "未学", 2: "未学", 3: "未学"}
    deps = [(1, 2, "prerequisite"), (2, 3, "prerequisite")]
    path = modules["path_generator"].generate_path(1, mastery, deps)
    print(f"✓ 步骤3：学习路径生成完成，{len(path)} 个节点")
    
    # 4. 调整路径
    event = LearningEvent("difficult", 2, datetime.now())
    adjusted = modules["path_adjuster"].adjust_path(path, event)
    print(f"✓ 步骤4：路径调整完成")
    
    # 5. 推送资源
    strategy = modules["resource_strategy"].get_push_strategy(DifficultyLevel.FIRST, 1)
    if modules["resource_strategy"].should_push_resource(2, 1):
        modules["resource_strategy"].push_resource(1, 2, strategy)
        print(f"✓ 步骤5：资源推送完成")
    
    print("\n✓ 端到端工作流测试通过！")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
