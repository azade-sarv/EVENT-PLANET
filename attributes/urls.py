from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    AttributeViewSet,
    EventAttributeValueViewSet,
    EventCustomAttributeViewSet,
    EventTypeAttributeViewSet,
)

app_name = "attributes"

router = SimpleRouter()
router.register("organizer/attributes", AttributeViewSet, basename="attribute")
router.register(
    "organizer/event-type-attributes",
    EventTypeAttributeViewSet,
    basename="event-type-attribute",
)
router.register(
    "organizer/event-attributes",
    EventAttributeValueViewSet,
    basename="event-attribute",
)

urlpatterns = [
    path(
        "organizer/events/<int:event_id>/attributes/",
        EventCustomAttributeViewSet.as_view({"get": "list", "post": "create"}),
        name="event-custom-attributes",
    ),
    path(
        "organizer/events/<int:event_id>/attributes/<int:pk>/",
        EventCustomAttributeViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="event-custom-attribute-detail",
    ),
] + router.urls