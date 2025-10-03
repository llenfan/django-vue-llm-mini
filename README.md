# Django Vue LLM Mini - Full Stack Article Management

A complete full-stack application for article management featuring:
- **Backend**: Django 5 REST API with JWT authentication, search, filtering, and pagination
- **Frontend**: Vue 3 + Vite + Pinia modern SPA with responsive design

## 🎯 Live Demo

- **Frontend Application**: http://189.90.231.233:3000
- **Backend API**: http://189.90.231.233:8000/api/articles/
- **API Documentation**: http://189.90.231.233:8000/api/docs/

## 🚀 Quick Start

### Backend Setup (Django)

```bash
# Clone the repository
git clone <repository-url>
cd django-vue-llm-mini

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup (Vue 3)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and will connect to the Django API.

## 🎨 Frontend Features

### Vue 3 Application Stack
- **Vue 3** with Composition API
- **Vite** for fast development and build
- **Pinia** for state management
- **Axios** for HTTP requests

### User Interface Features
- **📱 Responsive Design**: Mobile-first approach with grid layouts
- **🔍 Real-time Search**: Search articles by title, content, or tags
- **🏷️ Smart Filtering**: Filter by status (published/draft), sort by date/title
- **📄 Pagination**: Navigate through article collections
- **🏷️ Tag Filtering**: Click tags to filter articles
- **⭐ Featured Articles**: Special highlighting for featured content
- **⏱️ Loading States**: Skeleton loading and spinners
- **❌ Error Handling**: User-friendly error messages with retry options
- **📊 Article Metadata**: Display author, dates, reading time, view counts

### Architecture Highlights
- **Composition API**: Modern Vue 3 patterns throughout
- **Pinia Store**: Centralized state management with actions/getters
- **Service Layer**: Organized API communication with interceptors
- **JWT Ready**: Token handling and authentication flow
- **CORS Configured**: Cross-origin requests properly handled

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

### Admin Interface
- **Django Admin**: http://127.0.0.1:8000/admin/
- **DRF Browsable API**: http://127.0.0.1:8000/api-auth/

## 🔐 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Login and obtain JWT token pair |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/token/verify/` | Verify token validity |

### Example Login Request
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 📰 Article Endpoints

### Core CRUD Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/articles/` | List articles with pagination, search, filtering | No |
| POST | `/api/articles/` | Create new article | Yes |
| GET | `/api/articles/{id}/` | Retrieve specific article | No |
| PUT | `/api/articles/{id}/` | Update article (full) | Yes (Author) |
| PATCH | `/api/articles/{id}/` | Update article (partial) | Yes (Author) |
| DELETE | `/api/articles/{id}/` | Delete article | Yes (Author) |

### Custom Actions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/articles/featured/` | Featured articles | No |
| GET | `/api/articles/my_articles/` | Current user's articles | Yes |
| GET | `/api/articles/by_author/?author=username` | Articles by specific author | No |
| GET | `/api/articles/by_tag/?tag=python` | Articles with specific tag | No |
| GET | `/api/articles/stats/` | Article statistics | No |
| POST | `/api/articles/{id}/toggle_featured/` | Toggle featured status | Yes (Staff) |

## 🔍 Search & Filtering

### Search Parameters
- `?search=keyword` - Search across title, content, tags, and author
- `?title=text` - Filter by title (partial match)
- `?content=text` - Filter by content (partial match)
- `?author=username` - Filter by author username
- `?status=published` - Filter by status (draft/published/archived)
- `?featured=true` - Filter featured articles
- `?tags=python,django` - Filter by tags

### Date Filtering
- `?created_after=2023-01-01` - Articles created after date
- `?created_before=2023-12-31` - Articles created before date
- `?published_after=2023-01-01` - Articles published after date
- `?published_before=2023-12-31` - Articles published before date

### View Count Filtering
- `?min_views=100` - Articles with minimum view count
- `?max_views=1000` - Articles with maximum view count

### Ordering
- `?ordering=title` - Order by title (A-Z)
- `?ordering=-created_at` - Order by creation date (newest first)
- `?ordering=view_count` - Order by view count (ascending)
- `?ordering=-published_at` - Order by publish date (newest first)

## 📄 Example API Calls

### 1. Get All Articles
```bash
curl "http://127.0.0.1:8000/api/articles/"
```

### 2. Search Articles
```bash
curl "http://127.0.0.1:8000/api/articles/?search=django&status=published&ordering=-created_at"
```

### 3. Create Article (with JWT token)
```bash
curl -X POST "http://127.0.0.1:8000/api/articles/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Django Article",
    "content": "This is a comprehensive guide to Django REST Framework...",
    "status": "published",
    "tags": "django,python,api"
  }'
```

### 4. Filter by Author
```bash
curl "http://127.0.0.1:8000/api/articles/by_author/?author=admin"
```

### 5. Get Featured Articles
```bash
curl "http://127.0.0.1:8000/api/articles/featured/"
```

### 6. Get Article Statistics
```bash
curl "http://127.0.0.1:8000/api/articles/stats/"
```

## 📋 Response Format

### Article List Response
```json
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Sample Article",
      "slug": "sample-article",
      "excerpt": "This is a brief description...",
      "author": {
        "id": 1,
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User"
      },
      "status": "published",
      "featured": false,
      "view_count": 42,
      "tags": "django,python",
      "tags_list": ["django", "python"],
      "reading_time": 3,
      "created_at": "2023-10-01T10:30:00Z",
      "updated_at": "2023-10-01T15:45:00Z",
      "published_at": "2023-10-01T12:00:00Z"
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOW_ALL_ORIGINS=True
```

### Key Features
- ✅ **CRUD Operations** - Full create, read, update, delete support
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Search & Filtering** - Advanced search across multiple fields
- ✅ **Pagination** - Configurable page sizes (default: 20)
- ✅ **Ordering** - Sort by multiple fields
- ✅ **Permissions** - Author-only edit/delete permissions
- ✅ **Auto-generated slugs** - SEO-friendly URLs
- ✅ **View tracking** - Automatic view count increment
- ✅ **Admin interface** - Django admin for backend management
- ✅ **API documentation** - Interactive Swagger/ReDoc docs
- ✅ **CORS support** - Frontend integration ready

## 🛠 Tech Stack
- Python 3.11+
- Django 5.0
- Django REST Framework 3.15
- drf-spectacular (OpenAPI/Swagger)
- JWT Authentication
- SQLite (development) / PostgreSQL (production ready)

## 📱 Frontend Integration

### Vue.js Example
```javascript
// Get articles
const response = await fetch('http://127.0.0.1:8000/api/articles/')
const data = await response.json()

// Login and get token
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
})
const tokens = await loginResponse.json()

// Use token for authenticated requests
const articleResponse = await fetch('http://127.0.0.1:8000/api/articles/', {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
})
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support
- **API Documentation**: Visit `/api/docs/` for interactive documentation
- **Admin Panel**: Use `/admin/` for backend management
- **Issues**: Report bugs and request features via GitHub issues