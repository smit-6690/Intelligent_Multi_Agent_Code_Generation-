from intellicode.training import format_record


def test_format_record() -> None:
    text = format_record({"instruction": "Add numbers", "response": "def add(a,b): return a+b"})
    assert "### Instruction" in text
    assert "### Response" in text
