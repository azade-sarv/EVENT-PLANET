from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import EventParticipantsViewSet, MyRegistrationsViewSet

app_name = "registrations"

router = SimpleRouter()
router.register(
    "participant/registrations",
    MyRegistrationsViewSet,
    basename="my-registration",
)

urlpatterns = [
    path(
        "organizer/events/<int:event_id>/participants/",
        EventParticipantsViewSet.as_view({"get": "list"}),
        name="event-participants",
    ),
] + router.urls