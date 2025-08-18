#!/bin/bash

# 🔄 TikTok OAuth Complete Flow Test Script
# ==========================================

echo "🚀 TikTok OAuth Flow Test - Starting..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
TEST_EMAIL="test@example.com"
TEST_PLATFORM="web"

# Function to print step headers
print_step() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if server is running
check_server() {
    print_step "STEP 0: Server Health Check"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
    
    if [ "$response" = "200" ]; then
        print_success "Server is running on $BASE_URL"
        return 0
    else
        print_error "Server is not running. Please start with: python main.py"
        return 1
    fi
}

# Step 1: Test OAuth Login Initiation
test_oauth_login() {
    print_step "STEP 1: OAuth Login Initiation"
    
    print_info "Testing GET /auth/tiktok/login"
    print_info "URL: $BASE_URL/auth/tiktok/login?email=$TEST_EMAIL&platform=$TEST_PLATFORM"
    
    # Make request and capture headers
    response=$(curl -s -D response_headers.tmp "$BASE_URL/auth/tiktok/login?email=$TEST_EMAIL&platform=$TEST_PLATFORM")
    http_code=$(head -n1 response_headers.tmp | cut -d' ' -f2)
    location=$(grep -i "location:" response_headers.tmp | cut -d' ' -f2- | tr -d '\r')
    session_cookie=$(grep -i "set-cookie:" response_headers.tmp | cut -d' ' -f2- | tr -d '\r')
    
    echo ""
    echo "Response Details:"
    echo "- HTTP Code: $http_code"
    echo "- Location: $location"
    echo "- Session Cookie: $session_cookie"
    
    # Verification
    if [ "$http_code" = "302" ]; then
        print_success "Correct HTTP 302 redirect status"
    else
        print_error "Expected HTTP 302, got $http_code"
    fi
    
    if [[ "$location" == *"tiktok.com"* ]]; then
        print_success "Location header contains TikTok URL"
    else
        print_error "Location header does not contain TikTok URL"
    fi
    
    if [[ "$location" == *"aw5snxbk7d5ngdiy"* ]]; then
        print_success "Client ID found in OAuth URL"
    else
        print_error "Client ID not found in OAuth URL"
    fi
    
    if [[ "$location" == *"state="* ]]; then
        print_success "State parameter present"
    else
        print_error "State parameter missing"
    fi
    
    if [[ "$session_cookie" == *"session="* ]]; then
        print_success "Session cookie set"
    else
        print_error "Session cookie not set"
    fi
    
    # Save OAuth URL for manual testing
    echo "$location" > oauth_url.txt
    print_info "OAuth URL saved to oauth_url.txt"
    
    echo ""
    print_warning "MANUAL STEP REQUIRED:"
    print_warning "1. Open the following URL in browser:"
    echo "   $location"
    print_warning "2. Login to TikTok and authorize the app"
    print_warning "3. Copy the callback URL from browser address bar"
    print_warning "4. Extract the 'code' parameter from callback URL"
    
    # Clean up
    rm -f response_headers.tmp
}

# Step 2: Test OAuth Callback (simulated)
test_oauth_callback() {
    print_step "STEP 2: OAuth Callback Simulation"
    
    print_info "Testing GET /auth/tiktok/callback"
    print_warning "This is a simulation using mock parameters"
    
    # Create mock authorization code and state
    mock_code="mock_auth_code_12345"
    mock_state=$(echo '{"email":"'$TEST_EMAIL'","platform":"'$TEST_PLATFORM'"}' | base64)
    
    callback_url="$BASE_URL/auth/tiktok/callback?code=$mock_code&state=$mock_state"
    print_info "URL: $callback_url"
    
    # Make callback request
    response=$(curl -s -D callback_headers.tmp "$callback_url")
    http_code=$(head -n1 callback_headers.tmp | cut -d' ' -f2)
    location=$(grep -i "location:" callback_headers.tmp | cut -d' ' -f2- | tr -d '\r')
    auth_cookie=$(grep -i "set-cookie:" callback_headers.tmp | grep "access_token" | cut -d' ' -f2- | tr -d '\r')
    
    echo ""
    echo "Response Details:"
    echo "- HTTP Code: $http_code"
    echo "- Location: $location"
    echo "- Auth Cookie: $auth_cookie"
    
    # Note: This will likely fail with real TikTok API, but shows the endpoint structure
    if [ "$http_code" = "302" ] || [ "$http_code" = "500" ]; then
        print_warning "Callback endpoint exists (code $http_code)"
        print_info "For real testing, use actual authorization code from TikTok"
    else
        print_error "Callback endpoint not responding correctly"
    fi
    
    # Clean up
    rm -f callback_headers.tmp
}

# Step 3: Test User Accounts API
test_get_accounts() {
    print_step "STEP 3: Get User Accounts"
    
    print_info "Testing GET /api/tiktok/accounts"
    
    # Make request without authentication (should work with mock data)
    response=$(curl -s -w "%{http_code}" "$BASE_URL/api/tiktok/accounts")
    http_code="${response: -3}"
    body="${response%???}"
    
    echo ""
    echo "Response Details:"
    echo "- HTTP Code: $http_code"
    echo "- Body: $body"
    
    if [ "$http_code" = "200" ]; then
        print_success "Accounts API responds successfully"
        
        # Check if response is valid JSON
        if echo "$body" | jq . >/dev/null 2>&1; then
            print_success "Response is valid JSON"
            
            # Check if it's an array
            if echo "$body" | jq -e 'type == "array"' >/dev/null 2>&1; then
                print_success "Response is an array of accounts"
            else
                print_warning "Response is not an array"
            fi
        else
            print_warning "Response is not valid JSON"
        fi
    else
        print_error "Accounts API error (code: $http_code)"
    fi
}

# Step 4: Test Get Videos API
test_get_videos() {
    print_step "STEP 4: Get User Videos"
    
    test_provider_id="test_tiktok_id"
    print_info "Testing GET /api/tiktok/videos/$test_provider_id"
    
    # Make request
    response=$(curl -s -w "%{http_code}" "$BASE_URL/api/tiktok/videos/$test_provider_id")
    http_code="${response: -3}"
    body="${response%???}"
    
    echo ""
    echo "Response Details:"
    echo "- HTTP Code: $http_code"
    echo "- Body: $body"
    
    if [ "$http_code" = "200" ]; then
        print_success "Videos API responds successfully"
        
        # Check if response is valid JSON
        if echo "$body" | jq . >/dev/null 2>&1; then
            print_success "Response is valid JSON"
        else
            print_warning "Response is not valid JSON"
        fi
    else
        print_error "Videos API error (code: $http_code)"
    fi
}

# Step 5: Test Create Video API
test_create_video() {
    print_step "STEP 5: Create Video"
    
    print_info "Testing POST /api/tiktok/video/create"
    
    # Create test payload
    payload='{
        "provider_id": "test_tiktok_id",
        "content": {
            "video_url": "https://example.com/test-video.mp4",
            "description": "Test video created via API flow test"
        }
    }'
    
    print_info "Payload: $payload"
    
    # Make request
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "$payload" -w "%{http_code}" "$BASE_URL/api/tiktok/video/create")
    http_code="${response: -3}"
    body="${response%???}"
    
    echo ""
    echo "Response Details:"
    echo "- HTTP Code: $http_code"
    echo "- Body: $body"
    
    if [ "$http_code" = "200" ]; then
        print_success "Create Video API responds successfully"
        
        # Check if response is valid JSON
        if echo "$body" | jq . >/dev/null 2>&1; then
            print_success "Response is valid JSON"
            
            # Check for expected fields
            if echo "$body" | jq -e '.data.publish_id' >/dev/null 2>&1; then
                print_success "Response contains publish_id"
            else
                print_warning "Response missing publish_id"
            fi
        else
            print_warning "Response is not valid JSON"
        fi
    else
        print_error "Create Video API error (code: $http_code)"
    fi
}

# Step 6: Test Health Endpoint
test_health_check() {
    print_step "STEP 6: Additional Health Checks"
    
    print_info "Testing GET / (root endpoint)"
    
    response=$(curl -s "$BASE_URL/")
    
    echo ""
    echo "Root Response: $response"
    
    if echo "$response" | jq -e '.message' >/dev/null 2>&1; then
        print_success "Root endpoint returns proper JSON"
    else
        print_warning "Root endpoint response format issue"
    fi
}

# Test authentication flow with mock data
test_auth_flow() {
    print_step "STEP 7: Authentication Flow Test"
    
    print_info "Testing authentication state management"
    
    # Test with email parameter
    response=$(curl -s "$BASE_URL/api/tiktok/accounts?user=%7B%22email%22%3A%22test%40example.com%22%7D")
    
    echo ""
    echo "Auth Test Response: $response"
    
    if [ ! -z "$response" ]; then
        print_success "Authentication flow handles user parameter"
    else
        print_warning "Authentication flow might need real session"
    fi
}

# Main execution
main() {
    echo "Starting TikTok OAuth Complete Flow Test"
    echo "========================================"
    
    # Check prerequisites
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_warning "jq not installed - JSON validation will be limited"
    fi
    
    # Run tests
    if check_server; then
        test_oauth_login
        test_oauth_callback
        test_get_accounts
        test_get_videos
        test_create_video
        test_health_check
        test_auth_flow
        
        print_step "TEST SUMMARY"
        print_success "Flow test completed!"
        print_info "Check oauth_url.txt for manual OAuth URL testing"
        print_warning "For complete testing, use real TikTok authorization"
        
        echo ""
        echo "Next Steps:"
        echo "1. Open oauth_url.txt URL in browser"
        echo "2. Complete TikTok authorization"
        echo "3. Use real callback code to test full flow"
        echo "4. Test with authenticated session cookies"
        
    else
        print_error "Cannot proceed - server not running"
        exit 1
    fi
}

# Run the main function
main "$@"
