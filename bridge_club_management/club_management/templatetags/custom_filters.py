from django import template

register = template.Library()

@register.filter
def translate_day(day_name, day_name_mapping):
    return day_name_mapping.get(day_name, day_name)