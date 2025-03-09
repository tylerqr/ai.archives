# Shared Project - Architecture Archives

## System Architecture Overview

*Added on: 2023-08-10 11:25:30*

This document provides a high-level overview of the system architecture, covering both frontend and backend components and how they interact.

### Architecture Diagram

```
                                         +------------------+
                                         |                  |
                                         |  CDN / Vercel    |
                                         |                  |
                                         +--------+---------+
                                                  |
                                                  | HTTPS
                                                  |
+-----------------+                      +--------v---------+
|                 |                      |                  |
|  Content Team   +----+ Git/GitHub +----+  Frontend        |
|                 |                      |  Next.js         |
+-----------------+                      +--------+---------+
                                                  |
                                                  | REST API / GraphQL
                                                  |
+------------------+   +---------------+  +-------v----------+   +----------------+
|                  |   |               |  |                  |   |                |
|  Database Cluster+---+ Redis Cache   +--+  Backend API     +---+ File Storage   |
|  (PostgreSQL)    |   |               |  |  (Node.js/NestJS)|   | (S3/Cloudinary)|
|                  |   |               |  |                  |   |                |
+------------------+   +---------------+  +------------------+   +----------------+
```

### Component Overview

#### Frontend (Next.js)

- **Framework**: Next.js 14 with App Router
- **Rendering**: Hybrid (SSR + Client-side)
- **State Management**: React Context + SWR for data fetching
- **UI Library**: Custom components with Tailwind CSS
- **Authentication**: NextAuth.js with JWT

#### Backend (NestJS)

- **Framework**: NestJS with TypeScript
- **API Style**: REST with optional GraphQL endpoints
- **Database ORM**: TypeORM with PostgreSQL
- **Caching**: Redis for session and query caching
- **File Storage**: AWS S3 for user uploads
- **Authentication**: JWT-based with refresh tokens

#### Deployment Infrastructure

- **Frontend**: Vercel with preview deployments
- **Backend**: AWS ECS with Docker
- **Database**: AWS RDS with read replicas
- **Caching**: AWS ElastiCache (Redis)
- **CDN**: CloudFront for static assets
- **Monitoring**: Datadog and Sentry

### Data Flow

1. User requests arrive at the frontend (Next.js)
2. SSR renders initial page content
3. Frontend makes API calls to backend services
4. Backend validates requests and processes business logic
5. Backend fetches data from PostgreSQL database (with Redis cache)
6. Backend returns responses to frontend
7. Frontend renders updated UI with received data

### Authentication Flow

1. User logs in via the frontend login page
2. Credentials are sent to the backend auth service
3. Backend validates credentials against the database
4. Upon successful validation, JWT token is generated
5. Token is returned to frontend and stored in HTTP-only cookie
6. Frontend includes token in subsequent API requests
7. Backend validates token on each protected endpoint

---

## Cross-Project Conventions

*Added on: 2023-08-12 15:40:22*

To ensure consistency between frontend and backend development, we've established the following cross-project conventions.

### Naming Conventions

| Resource | Backend (API) | Frontend (Component/Page) |
|----------|---------------|---------------------------|
| User profiles | `/api/users/{id}` | `UserProfilePage` / `UserProfileCard` |
| Product listings | `/api/products` | `ProductsListPage` / `ProductCard` |
| Orders | `/api/orders/{id}` | `OrderDetailsPage` / `OrderSummary` |
| Authentication | `/api/auth/*` | `LoginForm` / `AuthProvider` |

### Data Models

We maintain consistent data models between frontend and backend:

1. **TypeScript Types**: Shared type definitions for common entities
2. **Validation**: Same validation rules applied on both ends
3. **Enums**: Identical enum values across both projects

Example of shared type definition:

```typescript
// Shared type (used in both projects)
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  PREMIUM = 'premium'
}
```

### Error Handling

Standardized error responses:

```typescript
// API error response format
export interface ErrorResponse {
  statusCode: number;
  message: string;
  error: string;
  details?: Record<string, string[]>;
}

// Frontend error handling
const handleApiError = (error: unknown) => {
  if (axios.isAxiosError(error) && error.response?.data) {
    const errorData = error.response.data as ErrorResponse;
    
    if (errorData.details) {
      // Handle validation errors
      return { 
        message: errorData.message,
        fieldErrors: errorData.details
      };
    }
    
    // Handle general errors
    return { message: errorData.message };
  }
  
  // Handle unexpected errors
  return { message: 'An unexpected error occurred' };
};
```

### API Response Envelope

All API responses follow a consistent structure:

```typescript
// Success response
{
  data: T, // The actual response data
  meta?: {
    pagination?: {
      total: number;
      page: number;
      limit: number;
      totalPages: number;
    }
  }
}

// Error response
{
  statusCode: number;
  message: string;
  error: string;
  details?: Record<string, string[]>;
}
```

### Development Workflow

1. **API-First Development**: Backend team creates and documents API endpoints first
2. **API Documentation**: Updated in Swagger before frontend integration
3. **Type Synchronization**: Frontend updates shared types based on API changes
4. **Feature Flags**: Used for coordinated deployment of interdependent features

---

## Lessons from Production Incidents

*Added on: 2023-08-20 09:10:15*

This section documents key lessons learned from production incidents affecting both frontend and backend systems.

### Connection Pool Exhaustion

**Incident Date**: 2023-08-15

**Description**: The backend experienced connection pool exhaustion to the PostgreSQL database during peak traffic, causing API timeouts that affected the frontend user experience.

**Root Cause**: Default connection pool size (10) was too small for concurrent requests during peak hours. Frontend was making excessive parallel requests without proper throttling.

**Solution**:
1. Increased PostgreSQL connection pool size to 50
2. Implemented request batching in frontend for certain operations
3. Added connection pool monitoring in Datadog
4. Implemented circuit breaker pattern to prevent cascading failures

**Cross-Project Impact**:
- Backend: Modified database configuration and implemented request throttling
- Frontend: Implemented request batching and added error handling for API timeouts

### Frontend Cache Inconsistency

**Incident Date**: 2023-08-18

**Description**: Users saw stale data in the frontend after making changes, causing confusion and support tickets.

**Root Cause**: Frontend cache (SWR) was not being properly invalidated after mutation operations. Backend was not sending appropriate cache headers.

**Solution**:
1. Implemented proper cache invalidation in SWR after mutations
2. Added cache-control headers in backend API responses
3. Introduced version-based cache keys for critical resources
4. Added "last updated" timestamps to user-visible data

**Cross-Project Impact**:
- Backend: Added proper cache headers and versioning for resources
- Frontend: Improved cache invalidation strategy and added refresh controls

### Authentication Token Handling

**Incident Date**: 2023-08-19

**Description**: Users were unexpectedly logged out during active sessions.

**Root Cause**: JWT tokens were expiring after 1 hour, but the frontend wasn't properly using refresh tokens to maintain sessions.

**Solution**:
1. Modified token expiration: Access tokens (1 hour), Refresh tokens (7 days)
2. Implemented automatic token refresh mechanism in frontend
3. Added sliding window expiration for refresh tokens in backend
4. Improved error handling for authentication failures

**Cross-Project Impact**:
- Backend: Modified token issuance and validation logic
- Frontend: Implemented transparent token refresh mechanism

--- 