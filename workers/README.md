# Japan Postal Code API - Cloudflare Worker

This Cloudflare Worker provides a REST API to query Japan postal code data from grouped JSON files hosted on GitHub Pages.

## Setup

### 1. Install Dependencies

```bash
cd workers
npm install
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Deploy the Worker

```bash
npm run deploy
```

Or:

```bash
wrangler deploy
```

**Note:** 
- The Worker reads JSON files directly from GitHub Pages: `https://stayforge.github.io/japan-postal-code/datasets/`
- No need to upload files - data is automatically synced from the git repository
- The Worker loads only the needed JSON file based on the query (e.g., `176.json` for queries starting with 176)

## API Usage

### Endpoint

```
GET /?code=<postal_code>
GET /?postal_code=<postal_code>
GET /?q=<postal_code>
GET /<postal_code>
```

### Parameters

- `code`, `postal_code`, or `q`: Postal code to search (3+ digits)
- The input can include dashes or other characters - only digits will be extracted
- Minimum 3 digits required

### Examples

```bash
# Search for postal codes starting with 176
curl "https://your-worker.workers.dev/?code=176"

# Search with dashes (will extract digits)
curl "https://your-worker.workers.dev/?code=176-0005"

# Search with path
curl "https://your-worker.workers.dev/1760005"

# All of these work:
# - 176
# - 1760
# - 176000
# - 176-0005
# - 1760005
```

### Response Format

```json
{
  "query": "176-0005",
  "extracted_digits": "1760005",
  "count": 10,
  "results": [
    {
      "local_government_code": "...",
      "old_postal_code": "...",
      "postal_code": "1760005",
      "prefecture_name_kana": "...",
      "city_name_kana": "...",
      "town_name_kana": "...",
      "prefecture_name": "...",
      "city_name": "...",
      "town_name": "...",
      ...
    },
    ...
  ]
}
```

### Error Responses

**400 Bad Request** - Invalid input (less than 3 digits):
```json
{
  "error": "Postal code must be at least 3 digits",
  "input": "17",
  "extracted_digits": "17"
}
```

**400 Bad Request** - Missing parameter:
```json
{
  "error": "Postal code parameter is required",
  "usage": "Use ?code=176 or ?postal_code=176 or ?q=176 or /176"
}
```

**500 Internal Server Error** - Database or server error:
```json
{
  "error": "Internal server error",
  "message": "..."
}
```

## Local Development

### Run locally with local D1 database

```bash
# Start local development server
wrangler dev

# Or with remote database
wrangler dev --remote
```

## Notes

- The API returns up to 1000 results per query
- Results are ordered by postal code
- CORS headers are included for cross-origin requests
- The database should have an index on `postal_code` for optimal performance

