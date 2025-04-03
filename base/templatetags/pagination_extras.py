import dataclasses

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def build_previous_query_params(context):
    if context["page_obj"].has_previous():
        return f"page={context["page_obj"].previous_page_number()}"

    return ""


@register.simple_tag(takes_context=True)
def build_next_query_params(context):
    if context["page_obj"].has_next():
        return f"page={context["page_obj"].next_page_number()}"

    return ""


@dataclasses.dataclass
class Page:
    page_number: int
    query_params: str
    active: bool


@register.simple_tag(takes_context=True)
def register_pages_list(context, pages_count=3):
    current_page = context["page_obj"].number
    first = current_page - pages_count
    last = current_page + pages_count

    context["page_list"] = [
        Page(
            page_number,
            query_params=f"page={page_number}",
            active=page_number == current_page
        )
        for page_number in context["page_obj"].paginator.page_range
        if first <= page_number <= last
    ]

    return ""
