# Turjuman Frontend v2 Implementation Plan

## Overview

This document outlines the detailed implementation plan for the Turjuman Frontend v2 project. The goal is to create a modern, responsive, and feature-rich frontend for the Turjuman book translation system using Next.js, replacing the current single-page application.

## Phase 1: Setup and Basic Structure (Completed)

- [x] Initialize Next.js project with TypeScript
- [x] Set up Tailwind CSS and shadcn/ui components
- [x] Create basic layout components (header, sidebar, footer)
- [x] Implement theme system with light/dark mode and additional themes
- [x] Set up API client and basic hooks
- [x] Create Docker configuration

## Phase 2: Core Features (In Progress)

- [x] Implement dashboard page with statistics
- [ ] Create new translation form
  - [ ] File upload component
  - [ ] Text input component
  - [ ] Language selection
  - [ ] Translation mode selection
  - [ ] Provider and model selection
  - [ ] Form validation
- [ ] Implement translation progress tracking
  - [ ] Progress bar component
  - [ ] Real-time updates using SSE
  - [ ] Log display
  - [ ] Chunk display
- [ ] Build translation history page
  - [ ] List view of all translations
  - [ ] Filtering and sorting options
  - [ ] Detailed view of individual translations
- [ ] Implement basic settings page
  - [ ] API URL configuration
  - [ ] Theme selection

## Phase 3: Advanced Features (Planned)

- [ ] Add glossary management
  - [ ] Create and edit glossaries
  - [ ] Import/export glossaries
  - [ ] Set default glossary
- [ ] Implement LLM configuration profiles
  - [ ] Create and edit profiles
  - [ ] Set default profile
- [ ] Add environment variables management
  - [ ] Secure storage of API keys
  - [ ] Edit and delete variables
- [ ] Enhance translation view with chunk-by-chunk display
  - [ ] Side-by-side view of original and translated text
  - [ ] Highlighting of current chunk
- [ ] Implement file upload/download functionality
  - [ ] Support for various file formats
  - [ ] Progress indication during upload/download

## Phase 4: Polish and Optimization (Planned)

- [ ] Add animations and transitions
  - [ ] Page transitions
  - [ ] Component animations
- [ ] Optimize for performance
  - [ ] Lazy loading of components
  - [ ] Optimized API calls
  - [ ] Caching strategies
- [ ] Implement error handling and fallbacks
  - [ ] Error boundaries
  - [ ] Retry mechanisms
  - [ ] User-friendly error messages
- [ ] Add responsive design for mobile devices
  - [ ] Mobile-friendly navigation
  - [ ] Responsive layouts
  - [ ] Touch-friendly interactions
- [ ] Conduct accessibility audit and fixes
  - [ ] Keyboard navigation
  - [ ] Screen reader support
  - [ ] Color contrast

## Phase 5: Deployment and Integration (Planned)

- [x] Set up Docker configuration
- [x] Create Docker Compose setup for full-stack deployment
- [ ] Write documentation
  - [ ] User guide
  - [ ] Developer documentation
  - [ ] API documentation
- [ ] Test integration with backend
  - [ ] End-to-end testing
  - [ ] API integration testing
- [ ] Deploy and verify functionality
  - [ ] Production deployment
  - [ ] Monitoring setup
  - [ ] Performance verification

## Detailed Task Breakdown

### New Translation Form

1. Create form layout with tabs for file upload and text input
2. Implement file upload with drag-and-drop functionality
3. Add text input with character count and validation
4. Create language selection dropdowns with search functionality
5. Add translation mode selection (Deep/Quick) with explanations
6. Implement provider and model selection based on available providers
7. Add form validation and error handling
8. Implement form submission and redirect to progress page

### Translation Progress Tracking

1. Create progress page layout with tabs for different views
2. Implement SSE connection for real-time updates
3. Create progress bar component with step indication
4. Add log display with filtering options
5. Implement chunk display with original and translated text
6. Add download functionality for completed translations
7. Create cancel translation functionality

### Translation History

1. Create history page layout with filtering options
2. Implement pagination for large result sets
3. Add sorting functionality by date, status, language, etc.
4. Create detailed view for individual translations
5. Implement delete functionality with confirmation
6. Add download functionality for completed translations
7. Create search functionality for finding specific translations

### Glossary Management

1. Create glossary page layout with list and edit views
2. Implement glossary creation and editing
3. Add import/export functionality
4. Create default glossary selection
5. Implement glossary term management
6. Add search and filtering for glossary terms
7. Create glossary deletion with confirmation

### LLM Configuration

1. Create configuration page layout with list and edit views
2. Implement configuration profile creation and editing
3. Add default profile selection
4. Create provider and model selection
5. Implement configuration deletion with confirmation
6. Add duplication functionality for easy modification

## Timeline

- Phase 1: 1 week (Completed)
- Phase 2: 2 weeks
- Phase 3: 2 weeks
- Phase 4: 1 week
- Phase 5: 1 week

Total estimated time: 7 weeks

## Next Steps

1. Complete the new translation form implementation
2. Implement the translation progress tracking functionality
3. Build the translation history page
4. Begin work on the glossary management features

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [React Query Documentation](https://tanstack.com/query/latest/docs/react/overview)
- [Turjuman Backend API Documentation](http://localhost:8051/docs)
