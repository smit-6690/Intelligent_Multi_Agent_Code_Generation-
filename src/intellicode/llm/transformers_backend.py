from __future__ import annotations

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from .base import LLMBackend


class TransformersBackend(LLMBackend):
    def __init__(
        self,
        model_id: str,
        adapter_path: str | None = None,
        load_in_4bit: bool = True,
        temperature: float = 0.0,
    ):
        self.temperature = temperature
        quantization_config = None
        if load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            quantization_config=quantization_config,
            trust_remote_code=True,
        )
        if adapter_path:
            adapter = Path(adapter_path)
            if not adapter.exists():
                raise FileNotFoundError(f"Adapter path does not exist: {adapter}")
            self.model = PeftModel.from_pretrained(self.model, str(adapter))
        self.model.eval()

    def generate(self, system: str, user: str, max_new_tokens: int = 1024) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        sample = self.temperature > 0
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=sample,
                temperature=self.temperature if sample else None,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = output[0, inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()
