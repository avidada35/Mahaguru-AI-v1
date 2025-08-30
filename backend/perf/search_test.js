import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users over 30 seconds
    { duration: '1m', target: 10 },   // Stay at 10 users for 1 minute
    { duration: '30s', target: 20 },  // Ramp up to 20 users over 30 seconds
    { duration: '1m', target: 20 },   // Stay at 20 users for 1 minute
    { duration: '30s', target: 0 },   // Ramp down to 0 users over 30 seconds
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],    // Less than 10% of requests should fail
  },
};

// Test data
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || '';

// Test queries
const TEST_QUERIES = [
  'What is Mahaguru AI?',
  'How does the search work?',
  'What are the main features?',
  'How to use the API?',
  'What is vector search?',
];

export function setup() {
  // Any setup code can go here
  return { token: API_KEY };
}

export default function (data) {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${data.token}`,
    },
  };

  // Select a random test query
  const query = TEST_QUERIES[Math.floor(Math.random() * TEST_QUERIES.length)];
  
  // Make the request
  const res = http.post(
    `${BASE_URL}/api/v1/ai/search`,
    JSON.stringify({
      query: query,
      top_k: 5,
      use_hybrid: true,
    }),
    params
  );

  // Check the response
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has results': (r) => {
      const body = JSON.parse(r.body);
      return body.results && body.results.length > 0;
    },
  });

  // Add a small delay between requests
  sleep(1);
}
