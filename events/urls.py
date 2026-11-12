from rest_framework.routers import SimpleRouter

from .views import OrganizerEventViewSet, PublicEventViewSet

app_name = "events"

router = SimpleRouter()
router.register(
    "organizer/events",
    OrganizerEventViewSet,
    basename="organizer-event",
)
router.register(
    "public/events",
    PublicEventViewSet,
    basename="public-event",
)

urlpatterns = router.urls