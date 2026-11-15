from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import EventFeedbackViewSet, MyFeedbackViewSet

app_name = "feedback"

router = SimpleRouter()
router.register(
    "participant/feedback",
    MyFeedbackViewSet,
    basename="my-feedback",
)

urlpatterns = [
    path(
        "public/events/<int:event_id>/feedback/",
        EventFeedbackViewSet.as_view({"get": "list"}),
        name="event-feedback",
    ),
] + router.urls