# API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Interview Endpoints](#interview-endpoints)
  - [Profile Endpoints](#profile-endpoints)
  - [Category Endpoints](#category-endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)

---

## Overview

**Base URL:** `http://localhost:8000`

**API Version:** 1.0

**Content Type:** `application/json`

**Authentication:** JWT Bearer Token

---

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Getting a Token

1. Register a new user via `/register`
2. Login via `/login`
3. Use the returned `access_token` in subsequent requests

### Token Expiration

Tokens expire after 30 minutes by default. Implement token refresh or re-login.

---

## Endpoints

### Authentication Endpoints

#### Register User

Create a new user account.

**Endpoint:** `POST /register`

**Authentication:** None required

**Request Body:**
```json
{
  "username": "string (required, unique)",
  "email": "string (required, unique, valid email)",
  "password": "string (required, min 6 characters)",
  "name": "string (required)",
  "bio": "string (optional)",
  "experience_level": "string (optional, default: 'Beginner')"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe",
    "bio": "Software Engineer",
    "experience_level": "Intermediate"
  }
}
```

**Errors:**
- `400 Bad Request`: Invalid input or user already exists
- `422 Unprocessable Entity`: Validation error

---

#### Login

Authenticate and receive a JWT token.

**Endpoint:** `POST /login`

**Authentication:** None required

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation error

---

### Interview Endpoints

#### Get Categories

Get list of available interview categories.

**Endpoint:** `GET /categories`

**Authentication:** Required

**Response:** `200 OK`
```json
[
  "Python",
  "JavaScript",
  "Java",
  "Data Structures",
  "Algorithms",
  "System Design",
  "Databases"
]
```

**Errors:**
- `401 Unauthorized`: Invalid or missing token

---

#### Start Interview

Start a new interview session with random questions.

**Endpoint:** `POST /interview/start`

**Authentication:** Required

**Request Body:**
```json
{
  "category": "string (required)",
  "num_questions": "integer (required, 1-20)",
  "user_id": "integer (required)"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "id": 1,
      "question": "What is a list comprehension in Python?",
      "category": "Python",
      "difficulty": "Medium",
      "expected_answer": "A list comprehension is a concise way..."
    }
  ],
  "total_questions": 5,
  "started_at": "2026-01-20T10:30:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid category or number of questions
- `404 Not Found`: No questions found for category
- `401 Unauthorized`: Invalid token

---

#### Submit Answer

Submit an answer for evaluation.

**Endpoint:** `POST /interview/answer`

**Authentication:** Required

**Request Body:**
```json
{
  "session_id": "string (required)",
  "question_id": "integer (required)",
  "user_answer": "string (required)",
  "user_id": "integer (required)",
  "time_taken": "integer (optional, seconds)"
}
```

**Response:** `200 OK`
```json
{
  "score": 85.5,
  "feedback": "Excellent explanation! You covered the key concepts.",
  "is_correct": true,
  "expected_answer": "A list comprehension is...",
  "similarity": 0.855,
  "evaluation_details": {
    "semantic_match": "high",
    "key_concepts_covered": ["concise syntax", "iteration", "filtering"]
  }
}
```

**Errors:**
- `400 Bad Request`: Invalid session or question ID
- `404 Not Found`: Session not found
- `401 Unauthorized`: Invalid token

---

#### End Interview

Complete an interview session and get final results.

**Endpoint:** `POST /interview/end`

**Authentication:** Required

**Request Body:**
```json
{
  "session_id": "string (required)",
  "user_id": "integer (required)"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_score": 82.3,
  "average_score": 82.3,
  "passed": true,
  "questions_answered": 5,
  "time_spent": 450,
  "achievements": [
    {
      "title": "First Interview",
      "description": "Completed your first interview",
      "icon": "trophy",
      "unlocked_at": "2026-01-20T10:35:00Z"
    }
  ],
  "new_streak": 7,
  "stats_updated": {
    "total_interviews": 15,
    "current_streak": 7
  }
}
```

**Errors:**
- `400 Bad Request`: Invalid session ID
- `404 Not Found`: Session not found
- `401 Unauthorized`: Invalid token

---

### Profile Endpoints

#### Get User Profile

Get detailed user profile information.

**Endpoint:** `GET /profile/{user_id}`

**Authentication:** Required

**Path Parameters:**
- `user_id` (integer): User ID

**Response:** `200 OK`
```json
{
  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "name": "John Doe",
  "bio": "Software Engineer with 5 years experience",
  "experience_level": "Advanced",
  "interests": ["Python", "JavaScript", "System Design"],
  "created_at": "2025-12-01T00:00:00Z",
  "stats": {
    "interview_count": 25,
    "total_score": 2075.5,
    "average_score": 83.02,
    "current_streak": 7,
    "longest_streak": 14,
    "pass_rate": 88.0
  },
  "achievements": [
    {
      "id": 1,
      "title": "First Interview",
      "description": "Completed your first interview",
      "icon": "trophy",
      "unlocked_at": "2025-12-02T10:30:00Z"
    }
  ],
  "last_interview_date": "2026-01-20"
}
```

**Errors:**
- `404 Not Found`: User not found
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Cannot access other user's profile

---

#### Update Profile

Update user profile information.

**Endpoint:** `PUT /profile/{user_id}`

**Authentication:** Required

**Path Parameters:**
- `user_id` (integer): User ID

**Request Body:**
```json
{
  "name": "string (optional)",
  "bio": "string (optional)",
  "experience_level": "string (optional)",
  "interests": "array (optional)"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": 1,
    "username": "johndoe",
    "name": "John Smith",
    "bio": "Senior Software Engineer",
    "experience_level": "Expert",
    "interests": ["Python", "Machine Learning"]
  }
}
```

**Errors:**
- `404 Not Found`: User not found
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Cannot update other user's profile

---

#### Get Interview History

Get user's interview history with pagination.

**Endpoint:** `GET /profile/{user_id}/history`

**Authentication:** Required

**Path Parameters:**
- `user_id` (integer): User ID

**Query Parameters:**
- `limit` (integer, optional): Number of records (default: 50, max: 100)
- `offset` (integer, optional): Number of records to skip (default: 0)
- `category` (string, optional): Filter by category
- `passed` (boolean, optional): Filter by pass/fail status

**Response:** `200 OK`
```json
{
  "total": 25,
  "limit": 50,
  "offset": 0,
  "history": [
    {
      "id": 100,
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2026-01-20T10:30:00Z",
      "topic": "Python",
      "questions_count": 5,
      "pass_rate": 85.5,
      "passed": true,
      "time_spent": 450,
      "questions": [
        {
          "question": "What is a decorator?",
          "user_answer": "A decorator is...",
          "score": 90.0,
          "correct": true
        }
      ]
    }
  ]
}
```

**Errors:**
- `404 Not Found`: User not found
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Cannot access other user's history

---

#### Get Achievements

Get all unlocked achievements for a user.

**Endpoint:** `GET /profile/{user_id}/achievements`

**Authentication:** Required

**Path Parameters:**
- `user_id` (integer): User ID

**Response:** `200 OK`
```json
{
  "total_achievements": 5,
  "unlocked_achievements": 3,
  "progress_percentage": 60.0,
  "achievements": [
    {
      "id": 1,
      "title": "First Interview",
      "description": "Completed your first interview",
      "icon": "trophy",
      "category": "milestone",
      "unlocked": true,
      "unlocked_at": "2025-12-02T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Perfect Score",
      "description": "Achieved 100% on an interview",
      "icon": "star",
      "category": "performance",
      "unlocked": false,
      "unlocked_at": null
    }
  ]
}
```

---

### Category Endpoints

#### Get Category Statistics

Get aggregate statistics for a specific category.

**Endpoint:** `GET /categories/{category}/stats`

**Authentication:** Required

**Path Parameters:**
- `category` (string): Category name

**Response:** `200 OK`
```json
{
  "category": "Python",
  "total_questions": 150,
  "difficulty_breakdown": {
    "Easy": 50,
    "Medium": 75,
    "Hard": 25
  },
  "average_score": 78.5,
  "total_attempts": 1250,
  "pass_rate": 72.0,
  "popular_questions": [
    {
      "question": "What is a decorator?",
      "attempts": 125,
      "average_score": 82.0
    }
  ]
}
```

---

## Request/Response Examples

### Complete Interview Flow

#### 1. Register/Login
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

#### 2. Start Interview
```bash
curl -X POST http://localhost:8000/interview/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Python",
    "num_questions": 3,
    "user_id": 1
  }'
```

#### 3. Submit Answer
```bash
curl -X POST http://localhost:8000/interview/answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "question_id": 1,
    "user_answer": "Your detailed answer here",
    "user_id": 1
  }'
```

#### 4. End Interview
```bash
curl -X POST http://localhost:8000/interview/end \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": 1
  }'
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2026-01-20T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Codes

```json
{
  "AUTH_001": "Invalid credentials",
  "AUTH_002": "Token expired",
  "AUTH_003": "Invalid token",
  "USER_001": "User not found",
  "USER_002": "User already exists",
  "INT_001": "Invalid session ID",
  "INT_002": "Question not found",
  "INT_003": "Session already completed",
  "VAL_001": "Validation error"
}
```

---

## Rate Limiting

**Current Limits:**
- Login/Register: 5 requests per minute
- Interview endpoints: 60 requests per minute
- Profile endpoints: 100 requests per minute

**Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642673400
```

**Rate Limit Exceeded Response:**
```json
{
  "detail": "Rate limit exceeded. Please try again in 30 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 30
}
```

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response:**
```json
{
  "total": 250,
  "limit": 50,
  "offset": 0,
  "data": [...]
}
```

**Navigation:**
- First page: `?limit=50&offset=0`
- Second page: `?limit=50&offset=50`
- Third page: `?limit=50&offset=100`

---

## Webhooks (Future Feature)

Coming soon: Webhooks for real-time notifications of:
- Interview completion
- Achievement unlocked
- Streak milestones

---

## Support

For API support:
- Email: api-support@smartvoiceinterviewer.com
- Documentation: https://docs.smartvoiceinterviewer.com
- Status Page: https://status.smartvoiceinterviewer.com
