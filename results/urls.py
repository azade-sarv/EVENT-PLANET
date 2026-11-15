from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    OrganizerEventResultViewSet,
    PublicEventResultViewSet,
    ResultEntryViewSet,
)

app_name = "results"

router = SimpleRouter()
router.register(
    "organizer/results",
    OrganizerEventResultViewSet,
    basename="organizer-result",
)
router.register(
    "organizer/result-entries",
    ResultEntryViewSet,
    basename="result-entry",
)

urlpatterns = [
    path(
        "public/events/<int:event_id>/results/",
        PublicEventResultViewSet.as_view({"get": "list"}),
        name="public-event-results",
    ),
] + router.urls