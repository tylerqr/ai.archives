# Project-Specific Rules

This file contains project-specific rules for the AI agent to follow when working with our projects.

## Frontend Project Rules

- Always use TypeScript for new components
- Follow the component structure: /components/[feature]/[Component].tsx
- Use CSS modules for styling with naming convention: [Component].module.css
- UI components should be placed in /components/ui/ directory
- Always write tests for new components in /components/[feature]/__tests__/[Component].test.tsx

## Backend Project Rules

- Follow RESTful API design principles
- Use the repository pattern for database operations
- All API endpoints should include comprehensive error handling
- Include validation for all input data
- Document all API endpoints with OpenAPI/Swagger
- Follow the controller-service-repository architecture

## Cross-Project Collaboration

- Frontend and backend teams should coordinate API changes
- Backend must update API documentation before frontend implementation
- Use feature flags for coordinated deployments
- Maintain consistent data models between frontend and backend

## Best Practices

- Write comprehensive tests for critical functionality
- Document complex business logic
- Use meaningful variable and function names
- Follow consistent code formatting
- Include helpful comments, but avoid obvious ones
- Optimize performance-critical code paths

## Error Handling

- Never swallow exceptions without logging
- Use appropriate error codes and messages
- Implement retry mechanisms for transient failures
- Provide user-friendly error messages 