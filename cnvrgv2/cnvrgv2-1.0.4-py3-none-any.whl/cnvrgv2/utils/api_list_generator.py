import json

from cnvrgv2.proxy import Proxy, HTTP


def api_list_generator(
    context,
    route,
    object,
    filter=None,
    sort="-id",
    page_size=20,
    identifier="slug",
    pagination_type="cursor",
    data=None
):
    """
    General api list generator for smart resource paginating
    @param context: Proxy object to communicate with the API
    @param route: The relevant API route
    @param object: The object to cast the response into
    @param sort: sort key (-key -> DESC | key -> ASC)
    @param page_size: Number of items returned each API call
    @param identifier: Name of the object's identifier, in case it's not slug
    @param pagination_type: Cursor or Offset pagination
    @param data: Additional data to add to the list call
    @return: Generator object
    """

    proxy = Proxy(context)
    next_page = ""

    while True:
        data = data or {}

        payload = {"sort": sort, "page[size]": page_size, **data}

        # Using dumps on None creates the string "null" which is unexpected at server
        if filter:
            payload["filter"] = json.dumps(filter)

        if pagination_type == "cursor":
            payload["page[after]"] = next_page
        else:
            if next_page == "":
                next_page = 1
            payload["page[offset]"] = next_page

        response = proxy.call_api(
            route=route,
            http_method=HTTP.GET,
            payload=payload
        )
        items = response.items

        for item in items:
            object_slug = item.attributes[identifier]
            object_instance = object(context=context, slug=object_slug, attributes=item.attributes)
            yield object_instance

        if len(items) < page_size:
            break

        next_page = response.next if pagination_type == "cursor" else next_page + 1
