"""
Shared small utilities.
"""

import re
import uuid


def slugify(text: str, max_length: int = 80) -> str:
    """Convert a title into a URL-safe slug: 'Best Coffee!' -> 'best-coffee'."""
    if not text:
        return uuid.uuid4().hex
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or uuid.uuid4().hex


def unique_slugify(text: str, existing: set[str], max_length: int = 80) -> str:
    """Slugify and guarantee uniqueness against a set of existing slugs."""
    base = slugify(text, max_length)
    candidate, i = base, 1
    while candidate in existing:
        suffix = f"-{i}"
        candidate = f"{base[: max_length - len(suffix)]}{suffix}"
        i += 1
    existing.add(candidate)
    return candidate
