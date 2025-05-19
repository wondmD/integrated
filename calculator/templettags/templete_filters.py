from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replace all occurrences of old with new in value. Expects arg as 'old,new'."""
    old, new = arg.split(',')
    return value.replace(old, new)