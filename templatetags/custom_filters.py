from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """คูณค่า value ด้วย arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """บวกค่า value กับ arg"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0