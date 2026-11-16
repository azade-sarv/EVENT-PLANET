# EVENT-PLANET

EVENT-PLANET is an API-first platform for managing and planning events. The system provides a comprehensive backend for event organizers to create, manage, and publish events, while allowing participants to register, attend, and provide feedback.

**Key characteristics:**
- API-first architecture (user interface is optional)
- Built with Django REST Framework
- PostgreSQL database
- Token-based authentication
- Role-based access control (Participant and Organizer)

---

## 1. Roles and Authentication

### User Roles

The system defines two primary roles:

**Participant:**
- Can browse published events
- Can register for events
- Can submit feedback for finished events they attended
- Can view their own registrations and feedback

**Organizer:**
- Can create and manage events
- Can define event stages and assign roles (speaker, judge, coach)
- Can set dynamic attributes for events
- Can view registrations and feedback for their own events
- Can publish results for finished events

### Authentication

The system uses Django REST Framework's token authentication.

**Registration:**
```http
POST /api/auth/register/
{
  "username": "string",
  "password": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "PARTICIPANT" | "ORGANIZER"
}