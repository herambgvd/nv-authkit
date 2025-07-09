#!/bin/bash

# FastAPI User Management System - Postman Test Runner
# This script runs automated tests using Newman (Postman CLI)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8001"
COLLECTION_FILE="authkit-collection.json"
ENVIRONMENT_FILE="authkit-environment.json"
REPORTS_DIR="test-reports"

echo -e "${BLUE}🚀 Authkit- Test Runner${NC}"
echo "================================================="

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo -e "${RED}❌ Newman (Postman CLI) is not installed${NC}"
    echo -e "${YELLOW}💡 Install it with: npm install -g newman${NC}"
    echo -e "${YELLOW}💡 Optional: npm install -g newman-reporter-html${NC}"
    exit 1
fi

# Check if API is running
echo -e "${BLUE}🔍 Checking if API is running at ${API_URL}${NC}"
if ! curl -s "${API_URL}/health" > /dev/null; then
    echo -e "${RED}❌ API is not running at ${API_URL}${NC}"
    echo -e "${YELLOW}💡 Start the API with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API is running${NC}"

# Create reports directory
mkdir -p "${REPORTS_DIR}"

# Run health checks first
echo -e "${BLUE}🏥 Running Health Checks${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "🏥 Health & Status" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/health-report.json" \
    --bail

echo -e "${GREEN}✅ Health checks passed${NC}"

# Run authentication tests
echo -e "${BLUE}🔐 Running Authentication Tests${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "🔐 Authentication" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/auth-report.json" \
    --delay-request 100

echo -e "${GREEN}✅ Authentication tests completed${NC}"

# Run user management tests
echo -e "${BLUE}👤 Running User Management Tests${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "👤 User Management" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/users-report.json" \
    --delay-request 100

echo -e "${GREEN}✅ User management tests completed${NC}"

# Run RBAC tests (if admin credentials are available)
echo -e "${BLUE}🔑 Running RBAC Tests${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "🔑 Permissions Management" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/permissions-report.json" \
    --delay-request 200

newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "👥 Roles Management" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/roles-report.json" \
    --delay-request 200

newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "🔗 Role Assignment" \
    --reporters cli,json \
    --reporter-json-export "${REPORTS_DIR}/role-assignment-report.json" \
    --delay-request 200

echo -e "${GREEN}✅ RBAC tests completed${NC}"

# Run complete test scenarios
echo -e "${BLUE}📊 Running Complete Test Scenarios${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --folder "📊 Test Scenarios" \
    --reporters cli,json,html \
    --reporter-json-export "${REPORTS_DIR}/scenarios-report.json" \
    --reporter-html-export "${REPORTS_DIR}/scenarios-report.html" \
    --delay-request 300

echo -e "${GREEN}✅ Test scenarios completed${NC}"

# Run full collection (optional)
echo -e "${BLUE}🎯 Running Full Test Suite${NC}"
newman run "${COLLECTION_FILE}" \
    --environment "${ENVIRONMENT_FILE}" \
    --reporters cli,json,html \
    --reporter-json-export "${REPORTS_DIR}/full-report.json" \
    --reporter-html-export "${REPORTS_DIR}/full-report.html" \
    --delay-request 200 \
    --timeout-request 10000

echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Test Reports Generated:${NC}"
echo "  - JSON Reports: ${REPORTS_DIR}/*.json"
echo "  - HTML Reports: ${REPORTS_DIR}/*.html"
echo ""
echo -e "${YELLOW}💡 View HTML report in browser:${NC}"
echo "  open ${REPORTS_DIR}/full-report.html"