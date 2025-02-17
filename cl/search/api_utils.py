from django.conf import settings
from rest_framework.exceptions import ParseError

from cl.lib import search_utils
from cl.lib.scorched_utils import ExtraSolrInterface
from cl.lib.search_utils import map_to_docket_entry_sorting
from cl.search.models import SEARCH_TYPES


def get_object_list(request, cd, paginator):
    """Perform the Solr work"""
    # Set the offset value
    try:
        page_number = int(request.GET.get(paginator.page_query_param, 1))
    except ValueError:
        raise ParseError(
            f"Invalid page number: {request.GET.get(paginator.page_query_param)}"
        )
    page_size = paginator.get_page_size(request)
    # Assume page_size = 20, then: 1 --> 0, 2 --> 20, 3 --> 40
    offset = max(0, (page_number - 1) * page_size)
    group = False
    if cd["type"] == SEARCH_TYPES.DOCKETS:
        group = True
    main_query = search_utils.build_main_query(
        cd, highlight="text", facet=False, group=group
    )
    main_query["caller"] = "api_search"
    if cd["type"] == SEARCH_TYPES.RECAP:
        main_query["sort"] = map_to_docket_entry_sorting(main_query["sort"])
    sl = SolrList(main_query=main_query, offset=offset, type=cd["type"])
    return sl


class SolrList(object):
    """This implements a yielding list object that fetches items as they are
    queried.
    """

    def __init__(self, main_query, offset, type, length=None):
        super(SolrList, self).__init__()
        self.main_query = main_query
        self.offset = offset
        self.type = type
        self._item_cache = []
        if self.type == SEARCH_TYPES.OPINION:
            self.conn = ExtraSolrInterface(settings.SOLR_OPINION_URL, mode="r")
        elif self.type == SEARCH_TYPES.ORAL_ARGUMENT:
            self.conn = ExtraSolrInterface(settings.SOLR_AUDIO_URL, mode="r")
        elif self.type in [SEARCH_TYPES.RECAP, SEARCH_TYPES.DOCKETS]:
            self.conn = ExtraSolrInterface(settings.SOLR_RECAP_URL, mode="r")
        elif self.type == SEARCH_TYPES.PEOPLE:
            self.conn = ExtraSolrInterface(settings.SOLR_PEOPLE_URL, mode="r")
        self._length = length

    def __len__(self):
        if self._length is None:
            mq = self.main_query.copy()  # local copy for manipulation
            mq["caller"] = "api_search_count"
            count = self.conn.query().add_extra(**mq).count()
            self._length = count
        return self._length

    def __iter__(self):
        for item in range(0, len(self)):
            try:
                yield self._item_cache[item]
            except IndexError:
                yield self.__getitem__(item)

    def __getitem__(self, item):
        self.main_query["start"] = self.offset
        r = self.conn.query().add_extra(**self.main_query).execute()
        self.conn.conn.http_connection.close()
        if r.group_field is None:
            # Pull the text snippet up a level
            for result in r.result.docs:
                result["snippet"] = "&hellip;".join(
                    result["solr_highlights"]["text"]
                )
                self._item_cache.append(SolrObject(initial=result))
        else:
            # Flatten group results, and pull up the text snippet as above.
            for group in getattr(r.groups, r.group_field)["groups"]:
                for doc in group["doclist"]["docs"]:
                    doc["snippet"] = "&hellip;".join(
                        doc["solr_highlights"]["text"]
                    )
                    self._item_cache.append(SolrObject(initial=doc))

        # Now, assuming our _item_cache is all set, we just get the item.
        if isinstance(item, slice):
            s = slice(
                item.start - int(self.offset),
                item.stop - int(self.offset),
                item.step,
            )
            return self._item_cache[s]
        else:
            # Not slicing.
            try:
                return self._item_cache[item]
            except IndexError:
                # No results!
                return []

    def append(self, p_object):
        """Lightly override the append method so we get items duplicated in
        our cache.
        """
        self._item_cache.append(p_object)


class SolrObject(object):
    def __init__(self, initial=None):
        self.__dict__["_data"] = initial or {}

    def __getattr__(self, key):
        return self._data.get(key, None)

    def to_dict(self):
        return self._data
