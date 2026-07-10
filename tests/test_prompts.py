from intellicode.prompts import PromptRegistry


def test_all_agent_prompts_load() -> None:
    registry = PromptRegistry("configs/agent_prompts.yaml")
    for name in ["spec_analyzer", "developer", "test_designer", "reviewer", "repair", "judge"]:
        template = registry.get(name)
        assert template.system
        assert template.user
