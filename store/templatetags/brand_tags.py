from django import template
from store.models import Brand

register = template.Library()


@register.filter
def brand_slug(brand_name):
    """Look up the Brand slug for a given brand name."""
    try:
        brand = Brand.objects.get(name=brand_name)
        return brand.slug
    except Brand.DoesNotExist:
        return None
