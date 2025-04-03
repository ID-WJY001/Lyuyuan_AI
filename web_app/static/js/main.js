/**
 * 绿园中学物语：追女生模拟
 * Web版本JavaScript交互
 */

// 游戏状态
const gameState = {
    initialized: false,
    gameStarted: false,
    closeness: 30,
    relationship: "初始阶段",
    scene: "学校 - 百团大战",
    timeInfo: "2023年9月1日 上午"
};

// DOM加载完成后执行
$(document).ready(function() {
    // 绑定按钮事件
    $("#start-game").click(startGame);
    $("#load-saved-game").click(showLoadGameModal);
    $("#send-button").click(sendMessage);
    $("#user-input").keypress(function(e) {
        if (e.which === 13) { // Enter键
            sendMessage();
        }
    });
    $("#save-game").click(showSaveGameModal);
    $("#load-game").click(showLoadGameModal);
    $("#confirm-save").click(saveGame);
    $("#confirm-load").click(loadGame);
    
    // 初始化提示
    console.log("绿园中学物语：追女生模拟 - Web版本已加载");
});

/**
 * 开始新游戏
 */
function startGame() {
    if (gameState.gameStarted) return;
    
    // 显示加载动画
    showLoading("正在开始游戏...");
    
    // 调用API开始游戏
    $.ajax({
        url: "/api/start_game",
        type: "POST",
        contentType: "application/json",
        success: function(data) {
            // 隐藏欢迎界面，显示游戏界面
            $("#welcome-screen").fadeOut(500, function() {
                $(".game-screen").fadeIn(500);
                
                // 更新游戏状态
                updateGameState(data.game_state);
                
                // 添加游戏介绍到聊天历史
                addSystemMessage(data.intro_text);
                
                // 滚动到底部
                scrollChatToBottom();
                
                // 设置游戏已开始
                gameState.gameStarted = true;
                gameState.initialized = true;
                
                // 聚焦到输入框
                $("#user-input").focus();
            });
        },
        error: function(xhr, status, error) {
            showError("无法开始游戏: " + error);
        },
        complete: function() {
            hideLoading();
        }
    });
}

/**
 * 发送用户消息
 */
function sendMessage() {
    const userInput = $("#user-input").val().trim();
    if (userInput === "") return;
    
    // 添加用户消息到对话框
    addUserMessage(userInput);
    
    // 清空输入框
    $("#user-input").val("");
    
    // 滚动到底部
    scrollChatToBottom();
    
    // 显示加载动画
    showTypingIndicator();
    
    // 发送消息到服务器
    $.ajax({
        url: "/api/chat",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ message: userInput }),
        success: function(data) {
            // 移除输入指示器
            removeTypingIndicator();
            
            // 添加AI回复
            addAssistantMessage(data.response);
            
            // 更新游戏状态
            updateGameState(data.game_state);
            
            // 更新角色图像
            updateCharacterImage(data.game_state.closeness);
            
            // 滚动到底部
            scrollChatToBottom();
        },
        error: function(xhr, status, error) {
            removeTypingIndicator();
            showError("发送消息失败: " + error);
        }
    });
}

/**
 * 更新游戏状态显示
 */
function updateGameState(state) {
    if (!state) return;
    
    // 更新好感度
    const closeness = state.closeness || 30;
    $("#affection-value").text(closeness);
    $("#affection-bar").css("width", closeness + "%").attr("aria-valuenow", closeness);
    
    // 好感度颜色
    if (closeness >= 80) {
        $("#affection-bar").removeClass().addClass("progress-bar bg-success");
    } else if (closeness >= 50) {
        $("#affection-bar").removeClass().addClass("progress-bar bg-info");
    } else if (closeness >= 30) {
        $("#affection-bar").removeClass().addClass("progress-bar bg-warning");
    } else {
        $("#affection-bar").removeClass().addClass("progress-bar bg-danger");
    }
    
    // 更新关系状态
    $("#relationship-status").text(state.relationship_state || "初始阶段");
    
    // 更新场景信息
    $("#scene-info").text(state.scene || "学校 - 百团大战");
    
    // 更新全局状态
    gameState.closeness = closeness;
    gameState.relationship = state.relationship_state || "初始阶段";
    gameState.scene = state.scene || "学校 - 百团大战";
}

/**
 * 根据好感度更新角色图像
 */
function updateCharacterImage(closeness) {
    // 使用固定的图片，不再根据好感度切换
    let imageName = "SuTang.jpg";
    
    // 设置图像源
    $("#character-image").attr("src", `/static/images/${imageName}`);
}

/**
 * 添加系统消息到聊天历史
 */
function addSystemMessage(text) {
    const formattedText = formatMessage(text);
    const messageHtml = `<div class="system-message fade-in">${formattedText}</div>`;
    $("#chat-history").append(messageHtml);
}

/**
 * 添加用户消息到聊天历史
 */
function addUserMessage(text) {
    const formattedText = formatMessage(text);
    const messageHtml = `<div class="user-message">${formattedText}</div>`;
    $("#chat-history").append(messageHtml);
}

/**
 * 添加AI助手消息到聊天历史
 */
function addAssistantMessage(text) {
    const formattedText = formatMessage(text);
    const messageHtml = `<div class="assistant-message">${formattedText}</div>`;
    $("#chat-history").append(messageHtml);
}

/**
 * 格式化消息文本（处理换行等）
 */
function formatMessage(text) {
    if (!text) return "";
    return text.replace(/\n/g, "<br>");
}

/**
 * 滚动聊天区域到底部
 */
function scrollChatToBottom() {
    const chatHistory = document.getElementById("chat-history");
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

/**
 * 显示输入指示器
 */
function showTypingIndicator() {
    const indicator = `<div id="typing-indicator" class="assistant-message" style="padding: 10px 15px;">
        <span class="typing-dot">.</span>
        <span class="typing-dot">.</span>
        <span class="typing-dot">.</span>
    </div>`;
    
    $("#chat-history").append(indicator);
    scrollChatToBottom();
    
    // 添加动画
    animateTypingDots();
}

/**
 * 移除输入指示器
 */
function removeTypingIndicator() {
    $("#typing-indicator").remove();
}

/**
 * 动画化输入点
 */
function animateTypingDots() {
    let opacity = 0.3;
    let increasing = true;
    
    const interval = setInterval(() => {
        if (!document.getElementById("typing-indicator")) {
            clearInterval(interval);
            return;
        }
        
        $(".typing-dot").css("opacity", opacity);
        
        if (increasing) {
            opacity += 0.1;
            if (opacity >= 1) {
                increasing = false;
            }
        } else {
            opacity -= 0.1;
            if (opacity <= 0.3) {
                increasing = true;
            }
        }
    }, 100);
}

/**
 * 显示保存游戏模态框
 */
function showSaveGameModal() {
    $("#save-modal").modal("show");
}

/**
 * 显示加载游戏模态框
 */
function showLoadGameModal() {
    // 加载保存的游戏列表
    $.ajax({
        url: "/api/get_saves",
        type: "GET",
        success: function(data) {
            // 清空现有选项
            $("#load-slot").empty();
            
            // 如果没有存档
            if (!data.saves || data.saves.length === 0) {
                $("#load-slot").append(`<option value="">无可用存档</option>`);
                $("#confirm-load").prop("disabled", true);
                $("#load-modal").modal("show");
                return;
            }
            
            // 添加存档选项
            data.saves.forEach(save => {
                const saveInfo = `存档 ${save.slot} - ${save.relationship}(${save.closeness}%) - ${save.date}`;
                $("#load-slot").append(`<option value="${save.slot}">${saveInfo}</option>`);
            });
            
            $("#confirm-load").prop("disabled", false);
            $("#load-modal").modal("show");
        },
        error: function(xhr, status, error) {
            showError("无法获取存档列表: " + error);
        }
    });
}

/**
 * 保存游戏
 */
function saveGame() {
    const slot = $("#save-slot").val();
    
    $.ajax({
        url: "/api/save",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ slot: slot }),
        success: function(data) {
            $("#save-modal").modal("hide");
            
            if (data.success) {
                showSuccess(data.message);
            } else {
                showError(data.message);
            }
        },
        error: function(xhr, status, error) {
            showError("保存游戏失败: " + error);
        }
    });
}

/**
 * 加载游戏
 */
function loadGame() {
    const slot = $("#load-slot").val();
    if (!slot) return;
    
    $.ajax({
        url: "/api/load",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ slot: slot }),
        success: function(data) {
            $("#load-modal").modal("hide");
            
            if (data.success && data.game_state) {
                // 如果游戏尚未开始，则显示游戏界面
                if (!gameState.gameStarted) {
                    $("#welcome-screen").hide();
                    $(".game-screen").show();
                    gameState.gameStarted = true;
                }
                
                // 清空聊天历史
                $("#chat-history").empty();
                
                // 添加系统消息
                addSystemMessage("游戏已从存档 " + slot + " 加载");
                
                // 更新游戏状态
                updateGameState(data.game_state);
                
                // 更新角色图像
                updateCharacterImage(data.game_state.closeness);
                
                showSuccess(data.message);
            } else {
                showError(data.message);
            }
        },
        error: function(xhr, status, error) {
            showError("加载游戏失败: " + error);
        }
    });
}

/**
 * 显示成功提示
 */
function showSuccess(message) {
    // 使用Bootstrap Toast或其他通知方式
    alert("成功: " + message);
}

/**
 * 显示错误提示
 */
function showError(message) {
    // 使用Bootstrap Toast或其他通知方式
    alert("错误: " + message);
}

/**
 * 显示加载动画
 */
function showLoading(message = "加载中...") {
    // 可以实现一个加载动画
    console.log(message);
}

/**
 * 隐藏加载动画
 */
function hideLoading() {
    // 隐藏加载动画
    console.log("加载完成");
} 