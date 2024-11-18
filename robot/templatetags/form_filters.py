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


@register.filter
def make_range(value):
    """Tạo một danh sách từ 1 đến value."""
    return range(1, value)


@register.filter
def dict_key(d, key):
    """Truy xuất giá trị từ dictionary bằng key."""
    return d.get(key, None)


@register.filter(name='get_item')
def get_item2(dictionary, key):
    return dictionary.get(key)

