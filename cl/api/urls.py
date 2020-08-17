from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from cl.api import views
from cl.audio import api_views as audio_views
from cl.favorites import api_views as favorite_views
from cl.people_db import api_views as people_views
from cl.recap import views as recap_views
from cl.search import api_views as search_views
from cl.visualizations import api_views as viz_views

router = DefaultRouter()
# Search & Audio
router.register(r"dockets", search_views.DocketViewSet, base_name="docket")
router.register(
    r"originating-court-information",
    search_views.OriginatingCourtInformationViewSet,
    base_name="originatingcourtinformation",
)
router.register(
    r"docket-entries", search_views.DocketEntryViewSet, base_name="docketentry"
)
router.register(
    r"recap-documents",
    search_views.RECAPDocumentViewSet,
    base_name="recapdocument",
)
router.register(r"courts", search_views.CourtViewSet, base_name="court")
router.register(r"audio", audio_views.AudioViewSet, base_name="audio")
router.register(
    r"clusters", search_views.OpinionClusterViewSet, base_name="opinioncluster"
)
router.register(r"opinions", search_views.OpinionViewSet, base_name="opinion")
router.register(
    r"opinions-cited",
    search_views.OpinionsCitedViewSet,
    base_name="opinionscited",
)
router.register(r"search", search_views.SearchViewSet, base_name="search")
router.register(r"tag", search_views.TagViewSet, base_name="tag")

# People & Entities
router.register(r"people", people_views.PersonViewSet)
router.register(r"positions", people_views.PositionViewSet)
router.register(r"retention-events", people_views.RetentionEventViewSet)
router.register(r"educations", people_views.EducationViewSet)
router.register(r"schools", people_views.SchoolViewSet)
router.register(
    r"political-affiliations", people_views.PoliticalAffiliationViewSet
)
router.register(r"sources", people_views.SourceViewSet)
router.register(r"aba-ratings", people_views.ABARatingViewSet)
router.register(r"parties", people_views.PartyViewSet, base_name="party")
router.register(
    r"attorneys", people_views.AttorneyViewSet, base_name="attorney"
)

# RECAP
router.register(r"recap", recap_views.PacerProcessingQueueViewSet)
router.register(r"recap-fetch", recap_views.PacerFetchRequestViewSet)
router.register(
    r"recap-query",
    recap_views.PacerDocIdLookupViewSet,
    base_name="fast-recapdocument",
)
router.register(
    r"fjc-integrated-database", recap_views.FjcIntegratedDatabaseViewSet
)

# Tags
router.register(
    r"tags", favorite_views.UserTagViewSet, base_name="UserTag",
)
router.register(
    r"docket-tags", favorite_views.DocketTagViewSet, base_name="DocketTag",
)

# Visualizations
router.register(
    r"visualizations/json", viz_views.JSONViewSet, base_name="jsonversion",
)
router.register(
    r"visualizations", viz_views.VisualizationViewSet, base_name="scotusmap",
)

API_TITLE = "CourtListener Legal Data API"
core_api_schema_view = get_schema_view(title=API_TITLE)
swagger_schema_view = get_schema_view(
    title=API_TITLE, renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer],
)


urlpatterns = [
    url(
        r"^api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    url(r"^api/rest/(?P<version>[v3]+)/", include(router.urls)),
    # Schemas
    url("^api/schema/$", core_api_schema_view, name="core_api_schema"),
    url("^api/swagger/$", swagger_schema_view, name="swagger_schema"),
    # Documentation
    url(r"^api/$", views.api_index, name="api_index"),
    url(r"^api/jurisdictions/$", views.court_index, name="court_index"),
    url(
        r"^api/rest-info/(?P<version>v[123])?/?$",
        views.rest_docs,
        name="rest_docs",
    ),
    url(
        r"^api/tutorial/(?P<version>v[123])?/?$",
        views.rest_tutorial,
        name="rest_tutorial",
    ),
    url(r"^api/bulk-info/$", views.bulk_data_index, name="bulk_data_index"),
    url(
        r"^api/replication/$", views.replication_docs, name="replication_docs"
    ),
    url(
        r"^api/replication/status/$",
        views.replication_status,
        name="replication_status",
    ),
    url(
        r"^api/rest/v(?P<version>[123])/coverage/(?P<court>.+)/$",
        views.coverage_data,
        name="coverage_data",
    ),
    url(
        r"^api/rest/v(?P<version>[123])/alert-frequency/(?P<day_count>\d+)/$",
        views.get_result_count,
        name="alert_frequency",
    ),
    # Deprecation Dates:
    # v1: 2016-04-01
    # v2: 2016-04-01
    url(
        r"^api/rest/v(?P<v>[12])/.*",
        views.deprecated_api,
        name="deprecated_api",
    ),
]
