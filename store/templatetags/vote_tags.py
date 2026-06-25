from django import template

register = template.Library()


@register.filter
def pretty_label(value, prefix=''):
    """
    Strip a prefix from a vote label and convert underscores to spaces.
    Usage: {{ v.vote_label|pretty_label:"longevity_" }}
    Result: 'longevity_long_lasting' → 'Long Lasting'
    """
    s = str(value)
    if prefix and s.startswith(prefix):
        s = s[len(prefix):]
    return s.replace('_', ' ').title()


@register.filter
def accord_image(name):
    """
    Map an accord name to a curated, high-quality, premium Unsplash image URL.
    """
    name = str(name).lower().strip()
    mapping = {
        'amber': 'https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?w=150&auto=format&fit=crop&q=80',
        'animalic': 'https://images.unsplash.com/photo-1574068468668-a05a11f871da?w=150&auto=format&fit=crop&q=80',
        'aromatic': 'https://images.unsplash.com/photo-1515002246390-7bf7e8f87b54?w=150&auto=format&fit=crop&q=80',
        'balsamic': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=150&auto=format&fit=crop&q=80',
        'cacao': 'https://images.unsplash.com/photo-1587132137056-bfbf0166836e?w=150&auto=format&fit=crop&q=80',
        'caramel': 'https://images.unsplash.com/photo-1590080875515-8a3a8dc573b5?w=150&auto=format&fit=crop&q=80',
        'chocolate': 'https://images.unsplash.com/photo-1548907040-4d42b52115ca?w=150&auto=format&fit=crop&q=80',
        'cinnamon': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=150&auto=format&fit=crop&q=80',
        'citrus': 'https://images.unsplash.com/photo-1557800636-894a64c1696f?w=150&auto=format&fit=crop&q=80',
        'earthy': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=150&auto=format&fit=crop&q=80',
        'floral': 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=150&auto=format&fit=crop&q=80',
        'fresh': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=150&auto=format&fit=crop&q=80',
        'fresh spicy': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=150&auto=format&fit=crop&q=80',
        'fruity': 'https://images.unsplash.com/photo-1481349518771-20055b2a7b24?w=150&auto=format&fit=crop&q=80',
        'green': 'https://images.unsplash.com/photo-1533038590840-1cde6b66b7c6?w=150&auto=format&fit=crop&q=80',
        'honey': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=150&auto=format&fit=crop&q=80',
        'lavender': 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?w=150&auto=format&fit=crop&q=80',
        'leather': 'https://images.unsplash.com/photo-1524295981977-628f41e3d36b?w=150&auto=format&fit=crop&q=80',
        'metallic': 'https://images.unsplash.com/photo-1535813547-99c456a41d4a?w=150&auto=format&fit=crop&q=80',
        'musky': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=150&auto=format&fit=crop&q=80',
        'nutty': 'https://images.unsplash.com/photo-1536628838512-eb7e30e1628d?w=150&auto=format&fit=crop&q=80',
        'patchouli': 'https://images.unsplash.com/photo-1546842931-886c185b4c8c?w=150&auto=format&fit=crop&q=80',
        'powdery': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=150&auto=format&fit=crop&q=80',
        'rose': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=150&auto=format&fit=crop&q=80',
        'soft spicy': 'https://images.unsplash.com/photo-1509358271058-acd22cc93898?w=150&auto=format&fit=crop&q=80',
        'sweet': 'https://images.unsplash.com/photo-1534080564583-6be75777b70a?w=150&auto=format&fit=crop&q=80',
        'tobacco': 'https://images.unsplash.com/photo-1527018601619-a508a2be00cd?w=150&auto=format&fit=crop&q=80',
        'vanilla': 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=150&auto=format&fit=crop&q=80',
        'violet': 'https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=150&auto=format&fit=crop&q=80',
        'warm spicy': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=150&auto=format&fit=crop&q=80',
        'white floral': 'https://images.unsplash.com/photo-1560717789-0ac7c58ac90a?w=150&auto=format&fit=crop&q=80',
        'woody': 'https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=150&auto=format&fit=crop&q=80',
    }
    return mapping.get(name, 'https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?w=150&auto=format&fit=crop&q=80')

