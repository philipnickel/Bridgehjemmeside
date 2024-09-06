from django import template

register = template.Library()

@register.filter
def translate_day(day_name, day_name_mapping):
    return day_name_mapping.get(day_name, day_name)

@register.filter
def split_reservationsnote(value):
    parts = value.split(',')
    if parts:
        return parts[0].split(':')[1].strip()
    return value