class OwnedEventQuerysetMixin:
    event_owner_lookup = "event__organizer"

    def get_queryset(self):
        return super().get_queryset().filter(
            **{self.event_owner_lookup: self.request.user}
        )