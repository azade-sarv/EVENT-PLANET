from rest_framework.routers import SimpleRouter

from .views import AttributeViewSet, EventTypeAttributeViewSet, EventAttributeValueViewSet

app_name = "attributes"

router = SimpleRouter()
router.register("organizer/attributes", AttributeViewSet, basename="attribute")
router.register("organizer/event-type-attributes", EventTypeAttributeViewSet, basename="event-type-attribute")
router.register("organizer/event-attributes", EventAttributeValueViewSet, basename="event-attribute")

urlpatterns = router.urls