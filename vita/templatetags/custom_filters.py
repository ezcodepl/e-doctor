# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_by_time')
def get_by_time(schedule, time):
    for item in schedule:
        if item['time'] == time:
            return item
    return None

@register.filter
def dictkey(value, key):
    try:
        return value[key]
    except KeyError:
        return None