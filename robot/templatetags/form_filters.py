from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def split(value, delimiter=','):
    return value.split(delimiter) if value else []


@register.filter
def trim(value):
    """Loại bỏ khoảng trắng ở đầu và cuối của mỗi phần tử trong danh sách."""
    return [item.strip() for item in value.split(',')] if value else []


@register.filter
def format_vnd(value):
    return intcomma(value).replace(",", ".")


@register.filter
def get_item(value, index):
    try:
        return value[int(index)]
    except (IndexError, ValueError):
        return None  # Nếu không tìm thấy hoặc có lỗi, trả về None
