from django import forms as dj_forms
from django import template

register = template.Library()


@register.filter
def field_widget_type(field):
    """Classify a BoundField's widget so form.html can render checkbox
    groups (Groups, Permissions) differently from a single boolean checkbox
    or a plain input/select."""
    widget = field.field.widget
    if isinstance(widget, dj_forms.CheckboxSelectMultiple):
        return 'multi_checkbox'
    if isinstance(widget, dj_forms.RadioSelect):
        return 'radio'
    if isinstance(widget, dj_forms.CheckboxInput):
        return 'checkbox'
    return 'other'


@register.filter
def get_attr(obj, field_name):
    """Return getattr(obj, field_name), calling it if it's a method (no args)."""
    if obj is None:
        return ''
    value = getattr(obj, field_name, '')
    if callable(value):
        try:
            value = value()
        except TypeError:
            return ''
    if value is None:
        return ''
    return value


@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)
