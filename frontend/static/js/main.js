// Main UI script for Green Garden High School Story

// 游戏状态
const gameState = {
    initialized: false,
    gameStarted: false,
    closeness: 30,
    relationship: "初始阶段",
    scene: "学校 - 百团大战",
    timeInfo: "2025年9月1日 上午"
};

// DOM加载完成后执行
$(document).ready(function() {
    // 绑定按钮事件（仅绑定实际存在的元素）
    $("#start-game").click(startGame);
    $("#send-button").click(sendMessage);
    $("#user-input").on('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // 初始化提示
    console.log("绿园中学物语 - Web版本已加载");

    // 窗口大小改变时调整聊天窗口高度
    $(window).on('resize', function() { adjustChatHeight(); });

    // 初始调整聊天窗口高度
    adjustChatHeight();

    // 初始化游戏状态
    initGameState();

    // 保存/读取按钮绑定
    $("#save-button").on('click', saveGame);
    $("#load-button").on('click', loadGame);
    $("#list-saves-button").on('click', listSaves);

    // 欢迎页：切换角色时更新预览图
    $("#role-select").on('change', function() {
        const key = String($(this).val() || 'su_tang').toLowerCase();
        updatePreviewImage(key);
        updateRoleBrief(key);
    });

    // 首次进入时，根据默认选项初始化预览图
    const initKey = String($("#role-select").val() || 'su_tang').toLowerCase();
    updatePreviewImage(initKey);
    updateRoleBrief(initKey);
});


function startGame() {
    if (gameState.gameStarted) return;
    
    // 显示加载动画
    showLoading("正在开始游戏...");
    
    // 调用API开始游戏
    $.ajax({
        url: "/api/start_game",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            // 预留：将所选角色传给后端，默认示例为苏糖
            role: $("#role-select").val() || "su_tang"
        }),
        success: function(data) {
            // 隐藏欢迎界面，显示游戏界面
            $("#welcome-screen").fadeOut(500, function() {
                $(".game-screen").fadeIn(500);
                
                // 更新游戏状态
                updateGameState(data.game_state);
                
                // 优先使用后端历史记录（仅 user/assistant）；否则使用 intro_text
                if (Array.isArray(data.history) && data.history.length > 0) {
                    renderHistory(data.history);
                } else if (data.intro_text) {
                    addSystemMessage(data.intro_text);
                }
                
                // 滚动到底部
                scrollChatToBottom();
                
                // 设置游戏已开始
                gameState.gameStarted = true;
                gameState.initialized = true;
                
                // 聚焦到输入框
                $("#user-input").focus();

                // 根据后端返回的角色键切换默认图（若返回）
                if (data.character_key) {
                    updateCharacterImage(undefined, data.character_key);
                }
                if (data.character_name) {
                    $("#character-name").text(String(data.character_name));
                } else if (data.character_key) {
                    $("#character-name").text(mapKeyToName(data.character_key));
                }
            });
        },
        error: function(xhr, status, error) {
            addSystemMessage("无法开始游戏：" + escapeHtml(String(error || '未知错误')));
        },
        complete: function() {
            hideLoading();
        }
    });
}

// 保存当前游戏到选定槽位
function saveGame() {
    const slot = $("#save-slot").val() || '1';
    const label = $("#save-label").val().trim();
    showLoading("正在保存...");
    $.ajax({
        url: "/api/save",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ slot, label: label || undefined }),
        success: function(res) {
            if (res && res.success) {
                showSuccess("保存成功 (槽位 " + slot + ")");
            } else {
                showError("保存失败");
            }
        },
        error: function(xhr, status, error) {
            showError("保存失败：" + escapeHtml(String(error || '未知错误')));
        },
        complete: function() { hideLoading(); }
    });
}

// 从选定槽位读取游戏
function loadGame() {
    const slot = $("#save-slot").val() || '1';
    showLoading("正在读取...");
    $.ajax({
        url: "/api/load",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ slot }),
        success: function(res) {
            if (res && res.success && res.game_state) {
                updateGameState(res.game_state);
                // 根据返回的角色键刷新头像（若存在）
                if (res.character_key) {
                    updateCharacterImage(res.game_state.closeness, res.character_key);
                }
                // 若在欢迎界面，切换到游戏界面
                if ($("#welcome-screen").is(":visible")) {
                    $("#welcome-screen").hide();
                    $(".game-screen").show();
                }
                // 重建聊天历史
                if (Array.isArray(res.history) && res.history.length > 0) {
                    renderHistory(res.history);
                }
                // 标记游戏已开始，避免再次点击“开始游戏”把状态重置
                gameState.gameStarted = true;
                gameState.initialized = true;
                // 聚焦与滚动
                $("#user-input").focus();
                adjustChatHeight();
                scrollChatToBottom();
                showSuccess("读取成功 (槽位 " + slot + ")");
            } else {
                showError("读取失败或槽位为空");
            }
        },
        error: function(xhr, status, error) {
            showError("读取失败：" + escapeHtml(String(error || '未知错误')));
        },
        complete: function() { hideLoading(); }
    });
}

// 列出存档
function listSaves() {
    const $panel = $("#saves-list");
    const $ul = $("#saves-list-ul");
    $ul.empty();
    showLoading("正在加载存档列表...");
    $.ajax({
        url: "/api/saves",
        type: "GET",
        success: function(res) {
            const items = (res && res.saves) || [];
            if (!Array.isArray(items) || items.length === 0) {
                $ul.append('<li class="list-group-item">暂无存档</li>');
            } else {
                items.forEach(it => {
                    const role = (it.meta && (it.meta.role || it.meta.character_name)) || '未知角色';
                    const label = (it.meta && it.meta.label) ? (' - ' + it.meta.label) : '';
                    const time = (it.meta && it.meta.timestamp) || it.mtime || '';
                    const slot = it.slot || '';
                    const line = `${escapeHtml(String(role))}${escapeHtml(label)} | 槽位: ${escapeHtml(String(slot))} | 时间: ${escapeHtml(String(time))}`;
                    const li = $(`<li class="list-group-item d-flex justify-content-between align-items-center">${line}<button class="btn btn-sm btn-outline-primary">读取</button></li>`);
                    li.find('button').on('click', function() {
                        // 将下拉选中为该槽位并读取
                        $("#save-slot").val(String(slot));
                        loadGame();
                    });
                    $ul.append(li);
                });
            }
            $panel.show();
        },
        error: function(xhr, status, error) {
            showError("获取存档列表失败：" + escapeHtml(String(error || '未知错误')));
        },
        complete: function() { hideLoading(); }
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
                    updateCharacterImage(
                        data.game_state.closeness,
                        data.character_key || (data.game_state && data.game_state.role)
                    );
                    if (data.character_name) {
                        $("#character-name").text(String(data.character_name));
                    } else if (data.character_key) {
                        $("#character-name").text(mapKeyToName(data.character_key));
                    }
                }
            }, typingSpeed);

        },
        error: function(xhr, status, error) {
            removeTypingIndicator();
            addSystemMessage("发送消息失败：" + escapeHtml(String(error || '未知错误')));
        }
    });
}

// 根据后端的历史记录重建对话
function renderHistory(history) {
    const $chat = $("#chat-history");
    $chat.empty();
    if (!Array.isArray(history)) return;
    history.forEach(msg => {
        const role = (msg && msg.role) || '';
        const content = (msg && msg.content) || '';
        if (role === 'user') {
            addUserMessage(content);
        } else if (role === 'assistant') {
            addAssistantMessage(content);
        } else if (role === 'system') {
            addSystemMessage(content);
        }
    });
    scrollChatToBottom();
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
    
    // 首次进入：直接设置为初始好感度，不做从30到初始值的动画
    if (!gameState.initialized) {
        $("#affection-value").text(closeness);
        $("#affection-bar").css("width", closeness + "%").attr("aria-valuenow", closeness);
    }
    // 非首次，且好感度发生变化时才做动画
    else if (oldCloseness !== closeness) {
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
    } else if (gameState.initialized) {
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
function updateCharacterImage(closeness, characterKey) {
    // 简洁的角色图像策略：
    // - 现在默认使用 su_tang.png
    // - 如果后端返回 character_key，则按 `${character_key}.png` 加载
    const key = String(characterKey || 'su_tang').toLowerCase()
    const srcPng = `/static/images/${key}.png`;
    const fallback = '/static/images/favicon.ico';
    const $img = $("#character-image");

    // 仅在资源加载失败时回退
    $img.off('error').one('error', function() {
        if ($(this).attr('src') !== fallback) {
            $(this).attr('src', fallback);
        }
    });
    $img.attr("src", srcPng);
}

// 欢迎页预览图切换
function updatePreviewImage(characterKey) {
    const key = String(characterKey || 'su_tang').toLowerCase();
    const $img = $("#role-preview-image");
    const srcPng = `/static/images/${key}.png`;
    const fallback = '/static/images/favicon.ico';

    // 仅在加载失败时回退，不做二次同源尝试
    $img.off('error').one('error', function() {
        if ($(this).attr('src') !== fallback) {
            $(this).attr('src', fallback);
        }
    });
    $img.attr('src', srcPng);
}

// 角色键到名称的简单映射
function mapKeyToName(key) {
    const m = {
        'su_tang': '苏糖',
        'lin_yuhan': '林雨含',
        'luo_yimo': '罗一莫',
        'gu_pan': '顾盼',
        'xia_xingwan': '夏星晚'
    };
    return m[String(key).toLowerCase()] || '苏糖';
}

// 欢迎页简要角色与场景介绍
function updateRoleBrief(key) {
    const briefs = {
        'su_tang': '在烘焙社摊位前的温柔女孩；甜点与音乐是她的安全感（初始好感度 30）。',
        'lin_yuhan': '舞蹈社附近的气氛担当；元气直给，也会认真安慰（初始好感度 50）。',
        'luo_yimo': '科技协会附近的慢热同学；话不多但认真听，细节里有温度（初始好感度 35）。',
        'gu_pan': '桌游社附近常能遇到他；会接梗也会收住，让人不尴尬（初始好感度 40）。',
        'xia_xingwan': '操场与网球社之间的身影；自律里有温柔，很会照顾人（初始好感度 38）。'
    };
    $("#role-brief").text(briefs[String(key).toLowerCase()] || '');
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
function escapeHtml(unsafe) {
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatMessage(text) {
    if (!text) return "";
    return escapeHtml(text).replace(/\n/g, "<br>");
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
    // 使用固定视口高度，避免动态跳动带来的“上移”观感
    $("#chat-history").css("height", "60vh");
}

// 初始化游戏状态
function initGameState() {
    // 实现初始化游戏状态的逻辑
} 