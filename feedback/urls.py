from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    EventFeedbackViewSet,
    MyFeedbackViewSet,
    PublicEventFeedbackViewSet,
)

app_name = "feedback"

router = SimpleRouter()
router.register(
    "participant/feedback",
    MyFeedbackViewSet,
    basename="my-feedback",
)

urlpatterns = [
    path(
        "organizer/events/<int:event_id>/feedback/",
        EventFeedbackViewSet.as_view({"get": "list"}),
        name="event-feedback",
    ),
    path(
        "public/events/<int:event_id>/feedback/",
        PublicEventFeedbackViewSet.as_view({"get": "list"}),
        name="public-event-feedback",
    ),
] + router.urls