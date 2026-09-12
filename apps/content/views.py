from django.shortcuts import render

from .showcase import COLLECTION, FLOWER_FILTERS


def home(request):
    selected = [value for value in request.GET.getlist("flower") if value in dict(FLOWER_FILTERS)]
    query = request.GET.get("q", "").strip()[:100]
    sort = request.GET.get("sort", "featured")
    if sort not in {"featured", "price", "-price"}:
        sort = "featured"

    def price_bound(name):
        value = request.GET.get(name, "")
        try:
            return max(0, min(int(value), 1000000))
        except (ValueError, TypeError):
            return None

    minimum, maximum = price_bound("min"), price_bound("max")
    products = [
        product
        for product in COLLECTION
        if (not selected or product["flowers"] in selected)
        and (
            not query
            or query.casefold() in (product["name"] + " " + product["composition"]).casefold()
        )
        and (minimum is None or product["price"] >= minimum)
        and (maximum is None or product["price"] <= maximum)
    ]
    if sort != "featured":
        products.sort(key=lambda product: product["price"], reverse=sort == "-price")
    return render(
        request,
        "content/home.html",
        {
            "products": products,
            "flower_filters": FLOWER_FILTERS,
            "selected": selected,
            "query": query,
            "sort": sort,
            "minimum": minimum,
            "maximum": maximum,
            "filtered": bool(selected or query or minimum is not None or maximum is not None),
        },
    )
