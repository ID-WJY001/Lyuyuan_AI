#!/bin/bash
# API自动化测试脚本

BASE_URL="http://localhost:5000"
PASSED=0
FAILED=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "  Lyuyuan AI API 自动化测试"
echo "=================================="
echo ""

# 测试函数
test_api() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5

    echo -n "测试: $test_name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 开始测试
echo "开始测试..."
echo ""

# 测试1: 开始游戏 - 苏糖
test_api "开始游戏(苏糖)" "POST" "/api/start_game" '{"role":"su_tang"}' "200"

# 测试2: 开始游戏 - 林雨含
test_api "开始游戏(林雨含)" "POST" "/api/start_game" '{"role":"lin_yuhan"}' "200"

# 测试3: 开始游戏 - 罗一莫
test_api "开始游戏(罗一莫)" "POST" "/api/start_game" '{"role":"luo_yimo"}' "200"

# 测试4: 开始游戏 - 顾盼
test_api "开始游戏(顾盼)" "POST" "/api/start_game" '{"role":"gu_pan"}' "200"

# 测试5: 开始游戏 - 夏星晚
test_api "开始游戏(夏星晚)" "POST" "/api/start_game" '{"role":"xia_xingwan"}' "200"

# 测试6: 列出存档
test_api "列出存档" "GET" "/api/saves" "" "200"

# 测试7: 空消息错误
test_api "空消息错误" "POST" "/api/chat" '{"message":""}' "400"

echo ""
echo "=================================="
echo "  测试结果"
echo "=================================="
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo "总计: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}有测试失败！${NC}"
    exit 1
fi
