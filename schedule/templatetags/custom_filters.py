from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[int(i)]


@register.filter
def split(value, arg):
    return value.split(arg)
