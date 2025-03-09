# Project Conventions

This rule file defines project-specific conventions that all AI agents should follow when working with our codebase.

## Code Style

- Use 2 spaces for indentation in all files
- Use single quotes for JavaScript/TypeScript strings
- Place opening braces on the same line as the statement
- Add semicolons at the end of statements
- Maximum line length: 100 characters
- Use camelCase for variables and functions
- Use PascalCase for classes and components
- Use UPPER_SNAKE_CASE for constants

## Git Workflow

- Create feature branches from `develop`
- Branch naming: `feature/short-description` or `bugfix/issue-reference`
- Write descriptive commit messages in present tense
- Use semantic prefixes: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- Include issue references in commits when applicable
- Squash commits before merging to develop

## Directory Structure

### Frontend

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   │   ├── common/      # Generic UI components
│   │   └── features/    # Feature-specific components
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── services/        # API service layer
│   ├── utils/           # Helper functions
│   ├── contexts/        # React context providers
│   ├── types/           # TypeScript types and interfaces
│   └── styles/          # Global styles and themes
├── public/              # Static assets
└── tests/               # Test files
```

### Backend

```
backend/
├── src/
│   ├── controllers/     # Route handlers
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   ├── repositories/    # Database operations
│   ├── middlewares/     # Express middlewares
│   ├── utils/           # Helper functions
│   ├── config/          # Configuration files
│   └── types/           # TypeScript types and interfaces
├── scripts/             # Utility scripts
└── tests/               # Test files
```

## Testing Standards

- Write unit tests for all components and functions
- Maintain at least 80% test coverage
- Name test files with `.test.ts` or `.test.tsx` extensions
- Use Jest and React Testing Library for frontend tests
- Use Jest for backend tests
- Run tests before pushing code

## Documentation

- Add JSDoc comments to all functions and components
- Include parameter types and return types
- Document complex algorithms and business logic
- Update README files when functionality changes
- Include examples for API endpoints

## Deployment

- Frontend deploys automatically from `main` branch
- Backend deploys after successful CI/CD pipeline
- Staging environment pulls from `develop` branch
- Production environment pulls from `main` branch
- Use feature flags for incomplete features 