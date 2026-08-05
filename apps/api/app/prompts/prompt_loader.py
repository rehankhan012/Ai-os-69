import os

PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))

class PromptLoader:
    @staticmethod
    def load(prompt_name: str) -> str:
        filepath = os.path.join(PROMPTS_DIR, f"{prompt_name}.md")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    @staticmethod
    def load_and_format(prompt_name: str, **kwargs) -> str:
        template = PromptLoader.load(prompt_name)
        # Using string format, but only replacing provided kwargs to avoid KeyError on missing ones like {draft} if not provided
        # Actually it's safer to just return template.format(**kwargs) 
        # But some templates have JSON schema brackets {{ }}, which format() handles correctly if escaped.
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # If there's a missing key, fallback to raw template (or we could just let it fail so we know)
            raise ValueError(f"Missing variable {e} for prompt {prompt_name}")
