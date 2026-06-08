from django import template

register = template.Library()


@register.filter
def currency(value, currency_config):
    """Convert USD price to local currency and format with symbol."""
    try:
        rate = currency_config.get('rate', 1.0)
        symbol = currency_config.get('symbol', '$')
        converted = float(value) * rate
        return f"{symbol}{converted:.2f}"
    except (TypeError, ValueError, AttributeError):
        return f"${value}"
