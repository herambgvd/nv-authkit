# AuthKit - Postman Testing Guide

This comprehensive Postman collection provides complete API testing for the AuthKit with RBAC functionality.

## 📋 Collection Overview

### **Included Test Suites:**
- 🏥 **Health & Status** - API health checks and system status
- 🔐 **Authentication** - User registration, login, and token management
- 👤 **User Management** - Profile management and user operations
- 🔑 **Permissions Management** - CRUD operations for permissions
- 👥 **Roles Management** - Role creation and management
- 🔗 **Role Assignment** - User-role assignment and permission checking
- 📊 **Test Scenarios** - Complete user journeys and RBAC flows

### **Total Endpoints Covered:** 35+
### **Automated Tests:** 50+ assertions
### **Test Scenarios:** 10+ complete workflows

## 🚀 Quick Setup

### **Option 1: Import into Postman GUI**

1. **Download Files:**
   - Collection: `fastapi-user-management-collection.json`
   - Environment: `fastapi-user-management-environment.json`

2. **Import into Postman:**
   - Open Postman → Import → Upload Files
   - Import both collection and environment files

3. **Configure Environment:**
   - Select "FastAPI User Management - Local" environment
   - Update variables if needed:
     ```
     base_url: http://localhost:8001
     admin_email: your-admin-email
     admin_password: your-admin-password
     test_email: test-user-email
     test_password: test-password
     ```

4. **Start Testing:**
   - Run "Health Check" first to verify API is running
   - Use "Login Admin" to get admin tokens
   - Execute other requests as needed

### **Option 2: Command Line with Newman**

1. **Install Newman:**
   ```bash
   npm install -g newman
   npm install -g newman-reporter-html  # Optional for HTML reports
   ```

2. **Run Tests:**
   ```bash
   # Make the test runner executable
   chmod +x run_postman_tests.sh
   
   # Run all tests
   ./run_postman_tests.sh
   ```

3. **Run Specific Test Suites:**
   ```bash
   # Health checks only
   newman run fastapi-user-management-collection.json \
     --environment fastapi-user-management-environment.json \
     --folder "🏥 Health & Status"
   
   # Authentication tests only
   newman run fastapi-user-management-collection.json \
     --environment fastapi-user-management-environment.json \
     --folder "🔐 Authentication"
   ```

## 🔧 Prerequisites

### **1. API Server Running**
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **2. Database Setup**
```bash
# Initialize database and RBAC
python scripts/init_db.py
python scripts/init_rbac.py

# Create superuser
python scripts/create_superuser.py
```

### **3. Environment Variables**
Update the Postman environment with your actual credentials:
- `admin_email`: Email of the superuser account
- `admin_password`: Password of the superuser account
- `test_email`: Email for regular user testing
- `test_password`: Password for regular user testing

## 📊 Test Categories

### **🏥 Health & Status (5 tests)**
- **Root Endpoint** - Basic API connectivity
- **Health Check** - Comprehensive health status
- **Database Health** - Database connectivity
- **Readiness Check** - Kubernetes readiness probe
- **Liveness Check** - Kubernetes liveness probe

### **🔐 Authentication (10 tests)**
- **Register User** - New user registration with validation
- **Login User** - User authentication and token generation
- **Login Admin** - Admin authentication for privileged operations
- **Refresh Token** - Token refresh mechanism
- **Get Current User** - Authenticated user profile retrieval
- **Forgot Password** - Password reset request
- **Reset Password** - Password reset with token
- **Change Password** - Authenticated password change
- **Verify Email** - Email verification process
- **Resend Verification** - Resend verification email

### **👤 User Management (7 tests)**
- **Get User Profile** - Retrieve current user profile
- **Update User Profile** - Modify user profile information
- **List Users (Admin)** - Paginated user listing with filters
- **Get User by ID (Admin)** - Retrieve specific user details
- **Update User (Admin)** - Admin user modifications
- **Delete User (Admin)** - User deletion (admin only)
- **User Statistics (Admin)** - User statistics and analytics

### **🔑 Permissions Management (5 tests)**
- **Create Permission** - Define new permissions
- **List Permissions** - Retrieve permissions with pagination
- **Get Permission by ID** - Specific permission details
- **Update Permission** - Modify permission details
- **Delete Permission** - Remove permissions

### **👥 Roles Management (6 tests)**
- **Create Role** - Define new roles with permissions
- **List Roles** - Retrieve roles with user counts
- **Get Role by ID** - Specific role details with permissions
- **Update Role** - Modify role configuration
- **Delete Role** - Remove roles (non-system only)
- **Role Statistics** - Role and permission analytics

### **🔗 Role Assignment (3 tests)**
- **Assign Roles to User** - Single user role assignment
- **Bulk Assign Roles** - Multiple user role operations
- **Check User Permission** - Runtime permission validation

### **📊 Test Scenarios (2 complete workflows)**

#### **Complete User Journey:**
1. Register new user with random data
2. Login and obtain tokens
3. Retrieve user profile
4. Update profile information
5. Verify all changes persist

#### **RBAC Flow Test:**
1. Create test permission
2. Create test role with permission
3. Assign role to user
4. Verify user has permission
5. Test permission checking

## 🧪 Automated Testing Features

### **Pre-request Scripts:**
- **Dynamic data generation** (timestamps, random emails, etc.)
- **Token management** (automatic token storage)
- **Environment variable updates**

### **Test Assertions:**
- **Status code validation** (200, 201, 404, etc.)
- **Response structure validation**
- **Data integrity checks**
- **Token format validation**
- **Permission verification**
- **Response time checks** (< 2000ms)

### **Global Test Scripts:**
- **Response time monitoring**
- **JSON format validation**
- **Token auto-extraction and storage**
- **Error message validation**

## 🔍 Advanced Usage

### **Environment Variables Management**

The collection uses environment variables for:
- **Authentication tokens** (auto-managed)
- **User IDs** (auto-extracted from responses)
- **Test data IDs** (permissions, roles)
- **Configuration** (URLs, credentials)

### **Running Specific Tests:**

```bash
# Test only authentication
newman run collection.json -e environment.json --folder "🔐 Authentication"

# Test with HTML report
newman run collection.json -e environment.json \
  --reporters cli,html \
  --reporter-html-export report.html

# Test with delays (for rate limiting)
newman run collection.json -e environment.json --delay-request 500

# Test with custom timeout
newman run collection.json -e environment.json --timeout-request 10000
```

### **Continuous Integration:**

```yaml
# GitHub Actions example
- name: Run API Tests
  run: |
    npm install -g newman
    newman run fastapi-user-management-collection.json \
      --environment fastapi-user-management-environment.json \
      --reporters cli,junit \
      --reporter-junit-export test-results.xml
```

## 🚨 Troubleshooting

### **Common Issues:**

1. **"Connection refused" errors:**
   - Ensure API server is running on correct port
   - Check `base_url` in environment variables

2. **Authentication failures:**
   - Verify admin credentials in environment
   - Ensure superuser account exists
   - Check if tokens have expired

3. **Permission denied errors:**
   - Verify user has required roles/permissions
   - Check if using admin token for admin operations
   - Ensure RBAC system is properly initialized

4. **Database errors:**
   - Run database migrations: `alembic upgrade head`
   - Initialize RBAC: `python scripts/init_rbac.py`
   - Check database connectivity

### **Debug Tips:**

- **Enable verbose output:** Use `-v` flag with Newman
- **Check individual requests:** Run single requests to isolate issues
- **Verify environment:** Check all environment variables are set
- **Review logs:** Check FastAPI server logs for detailed error info

## 📈 Test Reports

### **Available Report Formats:**
- **CLI Output** - Real-time console feedback
- **JSON Reports** - Machine-readable test results
- **HTML Reports** - Visual test reports with charts
- **JUnit XML** - CI/CD integration format

### **Report Locations:**
- JSON: `test-reports/*.json`
- HTML: `test-reports/*.html`
- Console: Real-time output

### **Sample Report Data:**
```json
{
  "collection": "AuthKit",
  "environment": "Local",
  "totalTests": 45,
  "passedTests": 43,
  "failedTests": 2,
  "avgResponseTime": 125,
  "totalTime": "00:02:15"
}
```

## 🎯 Best Practices

### **Test Organization:**
- **Sequential execution** for dependent tests
- **Folder-based organization** for logical grouping
- **Descriptive test names** for easy identification
- **Comprehensive assertions** for reliable validation

### **Data Management:**
- **Dynamic test data** to avoid conflicts
- **Cleanup procedures** for test isolation
- **Environment-specific configs** for different stages
- **Sensitive data protection** using secret variables

### **Maintenance:**
- **Regular collection updates** for API changes
- **Version control** for collection and environment files
- **Documentation updates** for new features
- **Test result analysis** for continuous improvement

## 🤝 Contributing

To contribute to the test collection:

1. **Update collection** with new endpoints
2. **Add appropriate assertions** for validation
3. **Update environment variables** if needed
4. **Test thoroughly** before committing
5. **Update documentation** for new features

## 📚 Additional Resources

- **FastAPI Documentation:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Postman Learning Center:** [https://learning.postman.com/](https://learning.postman.com/)
- **Newman Documentation:** [https://github.com/postmanlabs/newman](https://github.com/postmanlabs/newman)
- **API Testing Best Practices:** [https://www.postman.com/api-testing/](https://www.postman.com/api-testing/)

---

## 📞 Support

For issues with the test collection:
1. Check the troubleshooting section above
2. Verify your environment setup
3. Review the API documentation
4. Check the FastAPI server logs

Happy Testing! 🚀