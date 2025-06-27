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
    $("#send-button").click(sendMessage);
    $("#user-input").keypress(function(e) {
        if (e.which === 13) { // Enter键
            sendMessage();
        }
    });
    
    // 初始化提示
    console.log("绿园中学物语：追女生模拟 - Web版本已加载");
    
    // 开始游戏按钮点击事件
    $("#start-btn").click(startGame);
    
    // 发送消息按钮点击事件
    $("#send-btn").click(sendMessage);
    
    // 输入框回车键发送消息
    $("#message-input").keypress(function(e) {
        if (e.which === 13) {
            sendMessage();
            return false;
        }
    });
    
    // 窗口大小改变时调整聊天窗口高度
    $(window).resize(function() {
        adjustChatHeight();
    });
    
    // 初始调整聊天窗口高度
    adjustChatHeight();
    
    // 初始化游戏状态
    initGameState();
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
 * 发送用户消息 (伪打字机版本)
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
    
    // 显示旧的“正在输入”动画，让用户知道系统有反应
    showTypingIndicator(); 
    
    // 发送消息到服务器 (这里是你原来的、能正常工作的 $.ajax 调用)
    $.ajax({
        url: "/api/chat",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ message: userInput }),
        success: function(data) {
            // 1. 成功后，立刻移除“正在输入”的动画
            removeTypingIndicator();
            
            // 2. 获取到完整的回复文本
            const fullResponseText = data.response;

            // 3. 创建一个空的AI消息气泡
            const assistantMessageHtml = `<div class="assistant-message"></div>`;
            $("#chat-history").append(assistantMessageHtml);
            const messageElement = $("#chat-history .assistant-message").last();

            // 4. --- 伪打字机效果的核心 ---
            let charIndex = 0;
            const typingSpeed = 50; // 打字速度，单位是毫秒，数字越小越快

            const typingInterval = setInterval(function() {
                if (charIndex < fullResponseText.length) {
                    // 添加一个字
                    messageElement.html(formatMessage(fullResponseText.substring(0, charIndex + 1)));
                    charIndex++;
                    // 每打一个字都滚动到底部
                    scrollChatToBottom();
                } else {
                    // 所有字都打完了，清除定时器
                    clearInterval(typingInterval);
                    
                    // 打字结束后，再更新游戏状态（好感度条等），这样动画效果更自然
                    updateGameState(data.game_state);
                    updateCharacterImage(data.game_state.closeness);
                }
            }, typingSpeed);

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
    
    // 获取当前显示的好感度值
    const oldCloseness = parseInt($("#affection-value").text()) || 30;
    
    // 更新好感度
    const closeness = parseInt(state.closeness) || 30;
    
    // 如果好感度发生变化，添加动画效果
    if (oldCloseness !== closeness) {
        // 显示变化提示
        const delta = closeness - oldCloseness;
        const deltaText = delta > 0 ? `+${delta}` : delta;
        const deltaClass = delta > 0 ? 'text-success' : 'text-danger';
        
        // 创建好感度变化指示器
        const indicator = $(`<span class="affection-change ${deltaClass}" style="position:absolute;right:10px;opacity:1">${deltaText}</span>`);
        $("#affection-value").parent().css("position", "relative").append(indicator);
        
        // 动画效果：淡出并上移
        indicator.animate({
            top: "-=20px",
            opacity: 0
        }, 1500, function() {
            $(this).remove();
        });
        
        // 好感度数值变化动画
        $({value: oldCloseness}).animate({value: closeness}, {
            duration: 800,
            step: function() {
                $("#affection-value").text(Math.round(this.value));
            },
            complete: function() {
                $("#affection-value").text(closeness);
            }
        });
        
        // 进度条动画 - 使用直接JavaScript更改宽度，避免任何Bootstrap的过渡效果
        const progressBar = document.getElementById("affection-bar");
        
        // 1. 清除任何可能的样式或类
        progressBar.style.transition = "none";
        
        // 2. 动画更新宽度 - 使用requestAnimationFrame实现平滑动画
        const startWidth = oldCloseness;  
        const endWidth = closeness;
        const duration = 800; // 与其他动画保持一致的时长
        const startTime = performance.now();
        
        function updateProgressBar(currentTime) {
            const elapsedTime = currentTime - startTime;
            
            if (elapsedTime < duration) {
                // 计算当前宽度百分比 (线性动画)
                const progress = elapsedTime / duration;
                const currentWidth = startWidth + (endWidth - startWidth) * progress;
                
                // 更新宽度
                progressBar.style.width = currentWidth + "%";
                
                // 继续动画
                requestAnimationFrame(updateProgressBar);
            } else {
                // 动画结束，设置最终宽度
                progressBar.style.width = endWidth + "%";
                progressBar.setAttribute("aria-valuenow", endWidth);
            }
        }
        
        // 开始动画
        requestAnimationFrame(updateProgressBar);
    } else {
        // 无变化时直接更新
        $("#affection-value").text(closeness);
        $("#affection-bar").css("width", closeness + "%").attr("aria-valuenow", closeness);
    }
    
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
    
    // 确保正确获取关系状态
    const relationshipState = state.relationship_state || state.relationship || "初始阶段";
    
    // 更新关系状态显示
    $("#relationship-status").text(relationshipState);
    
    // 更新场景信息
    $("#scene-info").text(state.scene || "学校 - 百团大战");
    
    // 更新全局状态
    gameState.closeness = closeness;
    gameState.relationship = relationshipState;
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

// 调整聊天窗口高度
function adjustChatHeight() {
    const windowHeight = $(window).height();
    const navbarHeight = $(".navbar").outerHeight();
    const inputAreaHeight = $(".message-input-container").outerHeight();
    const bufferHeight = 20; // 额外的间距
    
    const chatHeight = windowHeight - navbarHeight - inputAreaHeight - bufferHeight;
    $("#chat-history").css("height", chatHeight + "px");
}

// 初始化游戏状态
function initGameState() {
    // 实现初始化游戏状态的逻辑
} 