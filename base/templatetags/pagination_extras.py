import dataclasses

from django import template


register = template.Library()


@dataclasses.dataclass
class Page:
    page_number: int
    active: bool


@register.simple_tag(takes_context=True)
def register_pages_list(context: template.Context, pages_count: int = 3):
    current_page = context["page_obj"].number
    first = current_page - pages_count
    last = current_page + pages_count

    if first <= 0:
        last += -first + 1

    if last > context["paginator"].num_pages:
        first -= last - context["paginator"].num_pages

    context["page_list"] = [
        Page(
            page_number,
            active=page_number == current_page,
        )
        for page_number in context["page_obj"].paginator.page_range
        if first <= page_number <= last
    ]

    return ""
