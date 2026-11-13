from rest_framework.routers import SimpleRouter

from .views import StageRoleViewSet, StageViewSet

app_name = "stages"

router = SimpleRouter()
router.register(
    "organizer/stages",
    StageViewSet,
    basename="stage",
)
router.register(
    "organizer/stage-roles",
    StageRoleViewSet,
    basename="stage-role",
)

urlpatterns = router.urls