# 🌐 Turjuman Frontend v2

A modern, responsive frontend for the Turjuman book translation system built with Next.js.

## 🚀 Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/abdallah-ali-abdallah/turjuman-book-translator.git
cd turjuman-book-translator/frontend-v2
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env.local` file based on `.env.example`:
```bash
cp .env.example .env.local
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🎯 Goals

- Create a modern, responsive UI using Next.js and React
- Improve user experience with better navigation and layout
- Enhance visual design while maintaining the existing functionality
- Ensure compatibility with the current backend API
- Implement proper state management
- Add new features like dark mode, responsive design, and better error handling
- Containerize the application for easy deployment

## 🏗️ Architecture

### Tech Stack

- **Frontend Framework**: Next.js 14+ (App Router)
- **UI Library**: Tailwind CSS with shadcn/ui components
- **State Management**: React Context API + React Query for API calls
- **Styling**: Tailwind CSS with custom theme variables
- **Icons**: Lucide React
- **Containerization**: Docker with multi-stage builds

### Directory Structure

```
frontend-v2/
├── app/                      # Next.js app directory
│   ├── api/                  # API route handlers (if needed)
│   ├── (auth)/               # Auth-related routes (future)
│   ├── dashboard/            # Dashboard pages
│   │   ├── page.tsx          # Main dashboard
│   │   ├── new-translation/  # New translation form
│   │   ├── history/          # Translation history
│   │   ├── glossary/         # Glossary management
│   │   └── settings/         # Settings pages
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Landing page
├── components/               # Reusable React components
│   ├── ui/                   # UI components (buttons, inputs, etc.)
│   ├── layout/               # Layout components (header, sidebar, etc.)
│   ├── translation/          # Translation-specific components
│   ├── glossary/             # Glossary-specific components
│   └── settings/             # Settings-specific components
├── lib/                      # Utility functions and helpers
│   ├── api.ts                # API client
│   ├── types.ts              # TypeScript types
│   └── utils.ts              # Utility functions
├── hooks/                    # Custom React hooks
│   ├── use-translation.ts    # Translation-related hooks
│   ├── use-glossary.ts       # Glossary-related hooks
│   └── use-settings.ts       # Settings-related hooks
├── providers/                # Context providers
│   ├── theme-provider.tsx    # Theme provider
│   └── api-provider.tsx      # API provider
├── styles/                   # Global styles
│   └── globals.css           # Global CSS
├── public/                   # Static assets
├── .env.example              # Example environment variables
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Project dependencies
```

## 📱 Pages and Features

### 1. Landing Page
- Brief introduction to Turjuman
- Quick start guide
- Features overview
- Call-to-action to start translating

### 2. Dashboard
- Overview of translation statistics
- Quick access to recent translations
- Status of ongoing translations
- Quick links to create new translations

### 3. New Translation
- Form to upload files or paste text
- Language selection (source and target)
- Translation mode selection (Deep or Quick)
- Chunking algorithm selection
- Accent and style options
- Provider and model selection

### 4. Translation Progress
- Real-time progress tracking
- Detailed logs
- Chunk-by-chunk view
- Cancel translation option
- Download translated content

### 5. Translation History
- List of all translations
- Filter by status, language, date
- Search functionality
- View, download, or delete translations

### 6. Glossary Management
- Create and edit glossaries
- Import/export glossaries
- Set default glossary
- View glossary terms

### 7. Settings
- LLM configuration profiles
- Environment variables management
- Theme selection
- API URL configuration

## 🎨 UI/UX Design

### Theme System
- Light and dark mode support
- Multiple color themes (similar to current implementation)
- Consistent color palette across the application
- Responsive design for all screen sizes

### Components
- Modern, clean UI components
- Consistent spacing and typography
- Accessible design (WCAG compliance)
- Loading states and error handling
- Animations for transitions

## 🔄 API Integration

### Backend API Endpoints
- `/jobs` - Create and list translation jobs
- `/jobs/{job_id}` - Get job details
- `/jobs/{job_id}/stream` - Stream job updates
- `/jobs/statistics` - Get job statistics
- `/providers` - Get available providers
- `/glossaries` - Manage glossaries
- `/llm-config` - Manage LLM configurations
- `/env-variables` - Manage environment variables

### State Management
- Use React Query for API data fetching and caching
- Context API for global state (theme, user preferences)
- Local state for form inputs and UI state

## 🐳 Docker Setup

### Multi-Stage Build
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=build /app/next.config.js ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json

# Run the app
CMD ["npm", "start"]
```

### Docker Compose Integration
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8051:8051"
    volumes:
      - ./data:/app/data
    env_file:
      - .env

  frontend:
    build:
      context: ./frontend-v2
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8051
    depends_on:
      - backend
```

## 📋 Implementation Plan

### Phase 1: Setup and Basic Structure
1. Initialize Next.js project with TypeScript
2. Set up Tailwind CSS and shadcn/ui
3. Create basic layout components (header, sidebar, footer)
4. Implement theme system with light/dark mode
5. Set up API client and basic hooks

### Phase 2: Core Features
1. Implement dashboard page with statistics
2. Create new translation form
3. Implement translation progress tracking
4. Build translation history page
5. Implement basic settings page

### Phase 3: Advanced Features
1. Add glossary management
2. Implement LLM configuration profiles
3. Add environment variables management
4. Enhance translation view with chunk-by-chunk display
5. Implement file upload/download functionality

### Phase 4: Polish and Optimization
1. Add animations and transitions
2. Optimize for performance
3. Implement error handling and fallbacks
4. Add responsive design for mobile devices
5. Conduct accessibility audit and fixes

### Phase 5: Deployment and Integration
1. Set up Docker configuration
2. Create Docker Compose setup for full-stack deployment
3. Write documentation
4. Test integration with backend
5. Deploy and verify functionality

## 🧪 Testing Strategy

1. **Unit Tests**: Test individual components and hooks
2. **Integration Tests**: Test API integration and data flow
3. **E2E Tests**: Test complete user flows
4. **Accessibility Tests**: Ensure WCAG compliance
5. **Performance Tests**: Ensure fast loading and rendering

## 🚀 Future Enhancements

1. User authentication and profiles
2. Collaborative translation features
3. Advanced analytics dashboard
4. PDF/DOCX preview and editing
5. Integration with translation memory systems
6. Offline support with PWA features
7. Mobile app using React Native

## 📚 Dependencies

### Core Dependencies
- next
- react
- react-dom
- typescript
- tailwindcss
- postcss
- autoprefixer

### UI Dependencies
- @radix-ui/react-*
- class-variance-authority
- clsx
- lucide-react
- tailwind-merge
- tailwindcss-animate

### Data Fetching
- @tanstack/react-query
- axios

### Form Handling
- react-hook-form
- zod

### Utilities
- date-fns
- lodash
- nanoid

## 🔄 API Client Implementation

```typescript
// lib/api.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8051';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const translationApi = {
  // Jobs
  createJob: (data) => api.post('/jobs', data),
  getJobs: () => api.get('/jobs'),
  getJob: (id) => api.get(`/jobs/${id}`),
  deleteJob: (id) => api.delete(`/jobs/${id}`),

  // Statistics
  getStatistics: () => api.get('/jobs/statistics'),

  // Providers
  getProviders: () => api.get('/providers'),

  // Glossaries
  getGlossaries: () => api.get('/glossaries'),
  createGlossary: (data) => api.post('/glossaries', data),
  updateGlossary: (id, data) => api.put(`/glossaries/${id}`, data),
  deleteGlossary: (id) => api.delete(`/glossaries/${id}`),

  // LLM Config
  getLLMConfigs: () => api.get('/llm-config'),
  createLLMConfig: (data) => api.post('/llm-config', data),
  updateLLMConfig: (id, data) => api.put(`/llm-config/${id}`, data),
  deleteLLMConfig: (id) => api.delete(`/llm-config/${id}`),

  // Environment Variables
  getEnvVariables: () => api.get('/env-variables'),
  setEnvVariable: (data) => api.post('/env-variables', data),
  deleteEnvVariable: (key) => api.delete(`/env-variables/${key}`),
};

export default api;
```

## 🔐 Environment Variables

```
# .env.example
NEXT_PUBLIC_API_URL=http://localhost:8051
```

## 🎭 Theme Implementation

```typescript
// providers/theme-provider.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'yellow' | 'grey' | 'purple' | 'green' | 'cyberpunk-cyan';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      // Default to system preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(isDark ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    }
  }, []);

  const value = {
    theme,
    setTheme: (newTheme: Theme) => {
      localStorage.setItem('theme', newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
      setTheme(newTheme);
    },
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
```

## 📊 Dashboard Implementation

The dashboard will feature:

1. **Statistics Cards**
   - Total jobs
   - Total words translated
   - Success rate
   - Average translation time

2. **Recent Translations**
   - List of recent translations with status
   - Quick actions (view, download, delete)

3. **Top Models and Languages**
   - Charts showing most used models
   - Charts showing most translated languages

4. **Quick Actions**
   - Start new translation
   - Manage glossaries
   - Configure settings

## 🔄 Translation Progress Implementation

For real-time updates, we'll use Server-Sent Events (SSE) to stream progress:

```typescript
// hooks/use-translation-progress.ts
import { useState, useEffect } from 'react';

export function useTranslationProgress(jobId: string) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');
  const [currentStep, setCurrentStep] = useState('');
  const [logs, setLogs] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8051';
    const eventSource = new EventSource(`${apiUrl}/jobs/${jobId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress_percent || 0);
      setStatus(data.status);
      setCurrentStep(data.current_step);
      setLogs(data.logs || []);
      setChunks(data.chunks || []);
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      setError('Connection error. Please refresh the page.');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  return { progress, status, currentStep, logs, chunks, error };
}
```

## 🐳 Docker Deployment

### Build and run with Docker

```bash
docker build -t turjuman-frontend-v2 .
docker run -p 3000:3000 turjuman-frontend-v2
```

### Using Docker Compose

From the root directory of the project:

```bash
docker-compose up
```

This will start both the frontend and backend services.

## 🌐 Environment Variables

- `NEXT_PUBLIC_API_URL` - URL of the Turjuman backend API (default: http://localhost:8051)

## 📚 Documentation

For more detailed information, see the following documents:

- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Detailed implementation plan and timeline
- [API Integration](./lib/api.ts) - API client implementation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
