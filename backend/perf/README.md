# Performance Testing

This directory contains performance tests for the Mahaguru AI backend using [k6](https://k6.io/).

## Prerequisites

1. Install [k6](https://k6.io/docs/get-started/installation/)
2. Set up the Mahaguru AI backend locally or have access to a deployed instance
3. Obtain an API key with appropriate permissions

## Running Tests

### Search Endpoint Test

```bash
# Run with default settings
k6 run search_test.js

# Run with custom URL and API key
k6 run -e BASE_URL=http://localhost:8000 -e API_KEY=your_api_key search_test.js

# Run with more virtual users
k6 run --vus 10 --duration 30s search_test.js
```

### Test Scenarios

1. **Search Load Test**: Simulates multiple users performing searches with different queries.

## Test Configuration

### Environment Variables

- `BASE_URL`: Base URL of the API (default: http://localhost:8000)
- `API_KEY`: API key for authentication

### Thresholds

Tests will fail if:
- 95% of requests take longer than 500ms
- More than 10% of requests fail

## Generating Reports

To generate an HTML report:

```bash
k6 run --out json=test_results.json search_test.js
k6 convert -O test_results.json -o report.html
```

## Adding New Tests

1. Create a new `.js` file in this directory
2. Use the existing tests as a template
3. Update the test scenarios and assertions as needed
4. Document any new environment variables or configuration options

## Best Practices

- Keep tests focused on specific endpoints or features
- Use realistic test data
- Set appropriate thresholds for your performance requirements
- Run tests in a production-like environment for accurate results
