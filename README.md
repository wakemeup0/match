# Address Matcher API

A FastAPI-based REST API for comparing and matching similar addresses using fuzzy string matching. The API supports both single pair and batch address matching with parallel processing capabilities.

## Setup

### Local Development

1. Make sure you have uv installed:
```bash
pip install uv
```

2. Create and activate a new virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Run the server:
```bash
uvicorn main:app --reload
```

### Docker Development

1. Development environment (with hot reload):
```bash
docker compose up api-dev
```
The development server will be available at `http://localhost:8000`

2. Production environment:
```bash
docker compose up api-prod
```
The production server will be available at `http://localhost:8001`

## API Usage

### 1. Single Address Match

**Endpoint:** `POST /match/`

Compare two individual addresses and get their similarity score.

**Request Body:**
```json
{
    "address1": "123 Main Street, New York",
    "address2": "123 Main St, NY",
    "threshold": 80.0  // Optional, defaults to 80.0
}
```

**Response:**
```json
{
    "similarity": 85.7,
    "is_match": true,
    "normalized_address1": "123 main street new york",
    "normalized_address2": "123 main st ny"
}
```

### 2. Batch Address Match

**Endpoint:** `POST /match/batch/`

Compare multiple pairs of addresses in parallel for improved performance.

**Request Body:**
```json
{
    "pairs": [
        {
            "address1": "123 Main Street, New York",
            "address2": "123 Main St, NY",
            "threshold": 80.0
        },
        {
            "address1": "456 Oak Avenue, Chicago, IL",
            "address2": "456 Oak Ave, Chicago, Illinois",
            "threshold": 85.0
        }
    ]
}
```

**Response:**
```json
{
    "results": [
        {
            "similarity": 85.7,
            "is_match": true,
            "normalized_address1": "123 main street new york",
            "normalized_address2": "123 main st ny"
        },
        {
            "similarity": 92.3,
            "is_match": true,
            "normalized_address1": "456 oak avenue chicago il",
            "normalized_address2": "456 oak ave chicago illinois"
        }
    ],
    "total_pairs": 2,
    "average_similarity": 89.0
}
```

### Features

- Address normalization (lowercase, whitespace cleanup)
- Fuzzy string matching using RapidFuzz's token sort ratio
- Configurable similarity threshold
- Single and batch address matching
- Parallel processing for batch operations
- Detailed match results with similarity scores
- Input validation and error handling
- Rate limiting for batch requests (max 1000 pairs per request)

### Performance Considerations

- Batch processing uses parallel execution for improved performance
- Addresses are normalized before comparison
- Token sort ratio algorithm handles word order differences
- Configurable thresholds for different use cases
- Memory-efficient processing of large batches

### Interactive API Documentation

Visit `http://localhost:8000/docs` for the interactive Swagger documentation, which includes:
- Detailed request/response schemas
- Example requests
- Try-it-out functionality
- API endpoint descriptions

## Docker Environments

### Development Environment
- Includes hot-reload functionality
- Mounts local directory for real-time code changes
- Includes development tools (pytest, black, isort)
- Available at `http://localhost:8000`


## License

MIT License - See LICENSE file for details 