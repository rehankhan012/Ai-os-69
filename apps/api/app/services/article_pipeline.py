import json
import logging
from typing import Any
from app.prompts.prompt_loader import PromptLoader
from app.services.ai_service import get_ai_provider

logger = logging.getLogger(__name__)

class ArticlePipelineService:
    """10-Step AI Article Pipeline (V3.0)."""

    def __init__(self, provider=None):
        self.provider = provider or get_ai_provider()

    async def _safe_generate(self, prompt: str, require_json: bool = False, max_retries: int = 3) -> str | dict:
        """Helper to generate text with retries and optional JSON parsing."""
        system_prompt = PromptLoader.load("system")
        full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        for attempt in range(max_retries):
            try:
                # Add JSON hint if required
                if require_json and "json" not in full_prompt.lower():
                    # For safety, ensure we hint the provider
                    pass
                    
                response = await self.provider.generate_text(full_prompt)
                
                if require_json:
                    return self._parse_json(response)
                return response.strip()
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Pipeline step failed after {max_retries} attempts: {e}")

    def _parse_json(self, response_text: str) -> dict:
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        return json.loads(response_text)

    async def run_pipeline(
        self, topic: str, tone: str, affiliate_links: list[str],
        internal_links: list[dict], trusted_sources: list[str], additional_instructions: str
    ) -> dict:
        """Run the full 10-step pipeline and return the final structured JSON metadata."""
        
        # Step 1: Research
        research_prompt = PromptLoader.load_and_format("research", topic=topic)
        if additional_instructions:
            research_prompt += f"\n\nAdditional User Instructions to consider: {additional_instructions}"
        research_data = await self._safe_generate(research_prompt)
        
        # Step 2: Outline
        outline_prompt = PromptLoader.load_and_format("outline", topic=topic, research=research_data)
        outline_data = await self._safe_generate(outline_prompt)
        
        # Step 3: Draft
        draft_prompt = PromptLoader.load_and_format("draft", topic=topic, tone=tone, outline=outline_data, research=research_data)
        draft = await self._safe_generate(draft_prompt)
        
        max_quality_loops = 1
        loop_count = 0
        
        while loop_count <= max_quality_loops:
            # Step 4: Humanize
            humanize_prompt = PromptLoader.load_and_format("humanizer", draft=draft)
            draft = await self._safe_generate(humanize_prompt)
            
            # Step 5: SEO
            seo_prompt = PromptLoader.load_and_format("seo_enhancer", draft=draft)
            draft = await self._safe_generate(seo_prompt)
            
            # Step 6: Fact Check
            trusted_str = "\n".join(f"- {l}" for l in trusted_sources) if trusted_sources else "None explicitly provided, rely on general verifiable knowledge."
            fact_prompt = PromptLoader.load_and_format("fact_checker", draft=draft, trusted_sources=trusted_str)
            draft = await self._safe_generate(fact_prompt)
            
            # Step 7: Affiliate & Internal Links
            aff_str = "\n".join(f"- {l}" for l in affiliate_links) if affiliate_links else "None"
            int_str = "\n".join(f"- {l['title']}: {l['url']}" for l in internal_links) if internal_links else "None"
            links_prompt = PromptLoader.load_and_format("links_and_blocks", draft=draft, affiliate_links=aff_str, internal_links=int_str)
            draft = await self._safe_generate(links_prompt)
            
            # Step 8: HTML Rendering
            html_prompt = PromptLoader.load_and_format("html_renderer", draft=draft)
            html_content = await self._safe_generate(html_prompt)
            
            # Step 9 & 10: Metadata, Schema, and Quality Audit
            meta_prompt = PromptLoader.load_and_format("metadata_and_audit", topic=topic, html=html_content)
            final_data = await self._safe_generate(meta_prompt, require_json=True)
            
            # Add raw HTML to the final payload
            final_data["html"] = html_content
            
            # Quality Loop evaluation
            quality = final_data.get("quality_score", 0)
            if quality >= 95 or loop_count == max_quality_loops:
                break
                
            logger.info(f"Quality score {quality} is < 95. Initiating loop {loop_count + 1}...")
            # If we need to loop, we take the HTML output (or draft) and run it through Humanizer/SEO again.
            draft = html_content  # Feed the HTML back in as the draft to improve
            loop_count += 1
            
        return final_data
