HTML RULES:
Return the article as clean semantic HTML (using <h1>, <h2>, <h3>, <p>, <ul>, <li>, <table>, <a>, etc.).

OUTPUT FORMAT:
You MUST return your entire response as a structured JSON object with the following schema exactly:
{
  "title": "String. The H1 title of the article.",
  "slug": "String. A URL-friendly slug based on the title.",
  "excerpt": "String. A 1-2 sentence compelling summary.",
  "meta_title": "String. SEO optimized meta title (50-60 characters).",
  "meta_description": "String. SEO optimized meta description (150-160 characters).",
  "focus_keyword": "String. The primary keyword targeted.",
  "tags": ["Array of strings", "relevant tags"],
  "reading_time": "Integer. Estimated reading time in minutes.",
  "word_count": "Integer. Total word count of the HTML content.",
  "html": "String. The FULL generated article in semantic HTML. Do not wrap in markdown backticks inside this JSON field.",
  "faq": [
    {"question": "String", "answer": "String"}
  ],
  "affiliate_links_used": ["Array of strings", "The exact affiliate URLs you actually included in the HTML"],
  "internal_links_used": ["Array of strings", "The exact internal URLs you actually included in the HTML"]
}
Return ONLY valid JSON. Do not include markdown formatting or backticks around the JSON block.
