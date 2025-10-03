# 🚀 Django Vue LLM Mini - Live API Server

**Live API Server**: `http://189.90.231.233:8000`

## 📚 **Interactive API Documentation** (Click to explore!)

### 🎯 **Primary Documentation**
- **Swagger UI**: http://189.90.231.233:8000/api/docs/ 
  *Interactive API explorer - test endpoints directly in your browser*
  
- **ReDoc**: http://189.90.231.233:8000/api/redoc/
  *Clean, professional documentation format*

### 🔧 **Developer Tools** 
- **OpenAPI Schema**: http://189.90.231.233:8000/api/schema/
- **Admin Panel**: http://189.90.231.233:8000/admin/ (admin/admin123)
- **DRF Browsable API**: http://189.90.231.233:8000/api-auth/

---

## 🔗 **Quick API Test Links**

### Authentication
```bash
# Get JWT Token (Login)
curl -X POST http://189.90.231.233:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Articles (No Auth Required)
- **All Articles**: http://189.90.231.233:8000/api/articles/
- **Featured Articles**: http://189.90.231.233:8000/api/articles/featured/
- **API Statistics**: http://189.90.231.233:8000/api/articles/stats/
- **Search Example**: http://189.90.231.233:8000/api/articles/?search=django&status=published

### Sample Article Creation
```bash
curl -X POST http://189.90.231.233:8000/api/articles/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article from API",
    "content": "This article was created via the REST API to demonstrate the functionality.",
    "status": "published",
    "tags": "api,test,demo"
  }'
```

---

## 📋 **All Available Endpoints**

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Login & get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/token/verify/` | Verify token validity |

### 📰 Articles
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/articles/` | List articles (paginated, filterable) | ❌ |
| POST | `/api/articles/` | Create new article | ✅ |
| GET | `/api/articles/{id}/` | Get specific article | ❌ |
| PUT/PATCH | `/api/articles/{id}/` | Update article | ✅ (Author only) |
| DELETE | `/api/articles/{id}/` | Delete article | ✅ (Author only) |
| GET | `/api/articles/featured/` | Featured articles only | ❌ |
| GET | `/api/articles/my_articles/` | Current user's articles | ✅ |
| GET | `/api/articles/by_author/?author=username` | Articles by author | ❌ |
| GET | `/api/articles/by_tag/?tag=python` | Articles by tag | ❌ |
| GET | `/api/articles/stats/` | Article statistics | ❌ |
| POST | `/api/articles/{id}/toggle_featured/` | Toggle featured status | ✅ (Staff) |

---

## 🔍 **Advanced Search & Filtering**

### Search Parameters
```bash
# Search across multiple fields
?search=django

# Filter by specific fields
?title=tutorial&status=published&featured=true

# Date filtering
?created_after=2023-01-01&created_before=2023-12-31

# Ordering
?ordering=-created_at  # Newest first
?ordering=view_count   # Most viewed first
?ordering=title        # Alphabetical
```

### Example Advanced Query
```
http://189.90.231.233:8000/api/articles/?search=django&status=published&ordering=-view_count&page=1
```

---

## 📱 **Frontend Integration Examples**

### JavaScript/Fetch
```javascript
// Get articles
const response = await fetch('http://189.90.231.233:8000/api/articles/');
const data = await response.json();
console.log(data.results); // Array of articles

// Login and get token
const loginResponse = await fetch('http://189.90.231.233:8000/api/auth/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const tokens = await loginResponse.json();

// Create article with token
const createResponse = await fetch('http://189.90.231.233:8000/api/articles/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${tokens.access}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'My New Article',
    content: 'Article content here...',
    status: 'published'
  })
});
```

### Python/Requests
```python
import requests

# Get articles
response = requests.get('http://189.90.231.233:8000/api/articles/')
articles = response.json()

# Login
login_data = {'username': 'admin', 'password': 'admin123'}
token_response = requests.post('http://189.90.231.233:8000/api/auth/token/', json=login_data)
tokens = token_response.json()

# Create article
headers = {'Authorization': f"Bearer {tokens['access']}"}
article_data = {
    'title': 'Python API Article', 
    'content': 'Created with Python requests',
    'status': 'published'
}
create_response = requests.post('http://189.90.231.233:8000/api/articles/', 
                               json=article_data, headers=headers)
```

---

## 📦 **Share This API**

### For Developers
1. **Share the Swagger URL**: http://189.90.231.233:8000/api/docs/
2. **Import Postman Collection**: Use `/postman_collection.json` file
3. **Share this README**: Contains all endpoints and examples

### For Non-Technical Users
- **Direct them to**: http://189.90.231.233:8000/api/docs/
- **Admin access**: http://189.90.231.233:8000/admin/ (admin/admin123)

### For Testing
- **Quick test**: http://189.90.231.233:8000/api/articles/stats/
- **Sample data**: http://189.90.231.233:8000/api/articles/

---

## ✨ **Key Features Highlight**
- ✅ **No authentication required** for reading articles
- ✅ **JWT authentication** for creating/editing
- ✅ **Real-time search** across title, content, tags, author  
- ✅ **Advanced filtering** by status, dates, view counts
- ✅ **Automatic pagination** (20 items per page)
- ✅ **Auto-generated slugs** and excerpts
- ✅ **View count tracking** for analytics
- ✅ **Interactive API documentation**
- ✅ **CORS enabled** for frontend integration

**Server Info**: Python 3.12, Django 5.0, DRF 3.15, SQLite Database