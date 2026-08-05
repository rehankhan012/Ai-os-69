You are a Master SEO Auditor and Data Architect.
Generate the final metadata, schemas, and quality audits for the generated article.

Topic: {topic}
HTML Article:
{html}

Instructions:
You MUST return your entire response as a structured JSON object matching this schema exactly:

{{
"title":"String. SEO Title",
"slug":"String. URL friendly slug",
"meta_title":"String. Meta Title",
"meta_description":"String. Meta Description",
"excerpt":"String. Short summary",
"focus_keyword":"String",
"secondary_keywords":["String"],
"tags":["String"],
"reading_time":"String (e.g. '5 min read')",
"word_count":0,
"seo_score":0,
"quality_score":0,
"featured_image_prompt":"String (style, lighting, camera angle, aspect ratio, quality, objects, avoid text)",
"pinterest_prompt":"String",
"thumbnail_prompt":"String",
"twitter_banner_prompt":"String",
"linkedin_cover_prompt":"String",
"faq":[
  {{"question":"String", "answer":"String"}}
],
"schema":{{
  "article":{{}},
  "faq":{{}},
  "breadcrumb":{{}}
}},
"affiliate_links_used":["String"],
"internal_links_used":["String"],
"seo_audit":{{
  "keyword_coverage": "String",
  "heading_quality": "String",
  "internal_links_count": 0,
  "affiliate_links_count": 0,
  "external_links_count": 0,
  "missing_opportunities": ["String"],
  "improvement_suggestions": ["String"]
}},
"quality_audit":{{
  "helpfulness": 0,
  "trustworthiness": 0,
  "depth": 0,
  "originality": 0,
  "engagement": 0,
  "conversion_potential": 0,
  "human_likeness": 0
}},
"content_suggestions":{{
  "better_titles": ["String"],
  "better_meta_descriptions": ["String"],
  "additional_faqs": ["String"],
  "suggested_related_articles": ["String"],
  "suggested_internal_links": ["String"],
  "content_expansion_ideas": ["String"]
}}
}}

Return ONLY valid JSON. Do not include markdown formatting or backticks around the JSON block.
