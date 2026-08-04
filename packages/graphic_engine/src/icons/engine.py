"""
Icon Engine — scalable SVG icons organized by category.

Categories: technology, finance, food, travel, fitness, education,
fashion, marketing, business, ai, programming, health
"""

from typing import Optional


class IconEngine:
    """Provides SVG icon markup for any category."""

    ICONS = {
        # Technology
        "technology": '<path d="M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7z"/><polyline points="8 13 10 15 14 11"/>',
        "tech": '<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
        "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
        "ai": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
        "robot": '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="9" cy="9" r="2"/><circle cx="15" cy="9" r="2"/><path d="M9 3L12 6l3-3"/>',

        # Finance
        "finance": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="6" x2="12" y2="18"/><path d="M8 12h8"/>',
        "money": '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        "growth": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',

        # Food
        "food": '<path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/>',
        "recipe": '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>',
        "coffee": '<path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>',

        # Travel
        "travel": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        "plane": '<path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',

        # Fitness
        "fitness": '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>',
        "gym": '<path d="M6.5 6.5L17.5 17.5"/><path d="M17.5 6.5L6.5 17.5"/>',

        # Education
        "education": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
        "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        "graduation": '<path d="M22 10l-10-5L2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',

        # Fashion
        "fashion": '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
        "style": '<circle cx="12" cy="8" r="5"/><path d="M3 21v-2a7 7 0 0 1 7-7h4a7 7 0 0 1 7 7v2"/>',

        # Marketing
        "marketing": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
        "megaphone": '<path d="M3 11l3-9h3l-3 9H3z"/><path d="M21.5 12.5L16 15V9l5.5 3.5z"/><path d="M6 11v8a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-8"/>',
        "seo": '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>',

        # Business
        "business": '<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
        "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>',
        "chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',

        # Health
        "health": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
        "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
        "brain": '<path d="M12 2a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4 4 4 0 0 1-4-4V6a4 4 0 0 1 4-4z"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h4"/>',

        # Programming
        "programming": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
        "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/>',
    }

    @staticmethod
    def get_icon(name: str, size: int = 80, color: str = "#E94560") -> str:
        """Get an SVG icon by name, rendered at the specified size."""
        path_data = IconEngine.ICONS.get(name.lower())
        if not path_data:
            # Try to find a related icon
            for category, data in IconEngine.ICONS.items():
                if name.lower() in category:
                    path_data = data
                    break
        if not path_data:
            # Default fallback icon (star)
            path_data = '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'

        view_box = "0 0 24 24"
        return (
            f'<svg width="{size}" height="{size}" viewBox="{view_box}" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'{path_data}</svg>'
        )

    @staticmethod
    def get_category_icon(category: str, size: int = 80, color: str = "#E94560") -> str:
        """Get the best icon for a category."""
        category_map = {
            "technology": "tech", "finance": "finance", "food": "food",
            "travel": "travel", "fitness": "fitness", "education": "education",
            "fashion": "fashion", "marketing": "marketing", "business": "business",
            "ai": "ai", "programming": "code", "health": "health",
            "lifestyle": "heart", "motivation": "brain", "recipes": "recipe",
        }
        icon_name = category_map.get(category.lower(), "star")
        return IconEngine.get_icon(icon_name, size, color)