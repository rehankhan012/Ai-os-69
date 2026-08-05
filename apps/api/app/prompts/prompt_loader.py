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
    def build_article_prompt(topic: str, tone: str, affiliate_links: list[str], internal_links: list[dict], trusted_sources: list[str], additional_instructions: str) -> str:
        system = PromptLoader.load("system")
        writer = PromptLoader.load("article_writer").format(
            topic=topic,
            tone=tone,
            additional_instructions=additional_instructions if additional_instructions else "None"
        )
        seo = PromptLoader.load("seo_rules")
        
        affiliate = ""
        if affiliate_links:
            affiliate = PromptLoader.load("affiliate_rules")
            affiliate += "\n\nAffiliate Links:\n" + "\n".join(f"- {l}" for l in affiliate_links)
            
        internal = ""
        if internal_links:
            internal = "\n\nInternal Links:\n" + "\n".join(f"- {l['title']} : {l['url']}" for l in internal_links)
            
        trusted = ""
        if trusted_sources:
            trusted = "\n\nTrusted Sources:\n" + "\n".join(f"- {l}" for l in trusted_sources)
            
        html = PromptLoader.load("html_rules")
        
        parts = [
            system,
            writer,
            seo,
            internal,
            trusted,
            affiliate,
            html
        ]
        
        return "\n\n---\n\n".join(filter(None, parts))
