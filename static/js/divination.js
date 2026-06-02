/**
 * SoulLink - 占卜功能JavaScript
 */

// ============ 全局状态 ============

const divinationState = {
    selectedCards: [],
    cardCount: 3,
    subType: 'general',
    question: '',
    positions: ['过去', '现在', '未来'],
    isLoading: false
};

// ============ 塔罗牌相关 ============

document.addEventListener('DOMContentLoaded', function() {
    // 检查是否在塔罗牌页面
    if (document.querySelector('.tarot-divination')) {
        initTarotDivination();
    }
    
    // 检查是否在恋爱占卜页面
    if (document.querySelector('.love-divination')) {
        initLoveDivination();
    }
    
    // 检查是否在星盘页面
    if (document.querySelector('.horoscope-divination')) {
        initHoroscopeDivination();
    }
    
    // 检查是否在八字页面
    if (document.querySelector('.bazi-divination')) {
        initBaziDivination();
    }
});

// ============ 塔罗牌初始化 ============

function initTarotDivination() {
    // 子类型选择
    document.querySelectorAll('.sub-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.sub-type-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            divinationState.subType = this.dataset.sub;
            
            // 根据类型调整位置标签
            updatePositions();
        });
    });
    
    // 牌数选择
    document.querySelectorAll('.count-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.count-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            divinationState.cardCount = parseInt(this.dataset.count);
            updatePositions();
        });
    });
    
    // 抽牌按钮
    document.getElementById('drawCards')?.addEventListener('click', drawCards);
    
    // 返回上一步
    document.getElementById('backToStep1')?.addEventListener('click', () => {
        goToStep(1);
    });
    
    // 开始解读
    document.getElementById('startInterpret')?.addEventListener('click', startInterpretation);
    
    // 问题字数统计
    const questionInput = document.getElementById('divinationQuestion');
    if (questionInput) {
        questionInput.addEventListener('input', function() {
            const charCount = document.querySelector('.char-count');
            if (charCount) {
                charCount.textContent = this.value.length;
            }
        });
    }
}

function updatePositions() {
    const count = divinationState.cardCount;
    const subType = divinationState.subType;
    
    // 根据牌数和类型设置位置标签
    if (subType === 'yesno') {
        divinationState.positions = ['答案'];
    } else if (count === 1) {
        divinationState.positions = ['核心'];
    } else if (count === 3) {
        divinationState.positions = ['过去', '现在', '未来'];
    } else if (count === 5) {
        divinationState.positions = ['现状', '障碍', '过去', '建议', '未来'];
    }
}

async function drawCards() {
    const btn = document.getElementById('drawCards');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> 抽牌中...';
    }
    
    try {
        const response = await fetch('/api/divination/tarot/draw', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                count: divinationState.cardCount,
                sub_type: divinationState.subType
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showToast(data.message || '抽牌失败', 'error');
            return;
        }
        
        divinationState.selectedCards = data.cards;
        
        // 显示抽到的牌
        displayDrawnCards(data.cards);
        
        // 显示选中牌预览
        displaySelectedCardsPreview(data.cards);
        
        // 切换到下一步
        goToStep(2);
        
        // 更新剩余次数
        if (data.remaining_count !== undefined) {
            updateRemainingCount(data.remaining_count);
        }
        
    } catch (error) {
        showToast('网络错误，请重试', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🃏</span> 洗牌并抽牌';
        }
    }
}

function displayDrawnCards(cards) {
    const container = document.getElementById('drawnCards');
    if (!container) return;
    
    container.innerHTML = `
        <div class="drawn-cards-title">你抽到的牌</div>
        <div class="tarot-spread">
            ${cards.map((card, index) => `
                <div class="spread-card" data-index="${index}">
                    <div class="card-emoji">${card.is_reversed ? '🔄' : '🃏'}</div>
                </div>
            `).join('')}
        </div>
        <div class="drawn-cards-list">
            ${cards.map((card, index) => `
                <div class="drawn-card-item">
                    <span class="card-position">${divinationState.positions[index] || '第' + (index + 1) + '张'}</span>
                    <span class="card-name">${card.name}</span>
                    ${card.is_reversed ? '<span class="card-reversed">逆位</span>' : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    // 添加翻转动画
    setTimeout(() => {
        container.querySelectorAll('.spread-card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('flipped');
            }, index * 300);
        });
    }, 100);
}

function displaySelectedCardsPreview(cards) {
    const container = document.getElementById('selectedCardsDisplay');
    if (!container) return;
    
    container.innerHTML = `
        <div class="selected-cards">
            ${cards.map((card, index) => `
                <div class="selected-card">
                    <div class="selected-card-position">${divinationState.positions[index]}</div>
                    <div class="selected-card-name">${card.name}</div>
                    <div class="selected-card-status">${card.is_reversed ? '逆位' : '正位'}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function goToStep(step) {
    // 更新步骤指示器
    document.querySelectorAll('.step').forEach(s => {
        s.classList.toggle('active', parseInt(s.dataset.step) === step);
    });
    
    // 切换内容区
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.toggle('active', parseInt(content.dataset.step) === step);
    });
}

async function startInterpretation() {
    const question = document.getElementById('divinationQuestion')?.value.trim();
    
    if (!question) {
        showToast('请输入你的问题', 'warning');
        return;
    }
    
    if (question.length < 10) {
        showToast('问题至少需要10个字符', 'warning');
        return;
    }
    
    divinationState.question = question;
    
    goToStep(3);
    
    // 显示加载状态
    const interpretingDiv = document.getElementById('interpreting');
    const resultDiv = document.getElementById('interpretationResult');
    
    if (interpretingDiv) interpretingDiv.style.display = 'block';
    if (resultDiv) resultDiv.style.display = 'none';
    
    try {
        // 使用流式API
        const response = await fetch('/api/divination/tarot/interpret/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cards: divinationState.selectedCards,
                question: divinationState.question,
                positions: divinationState.positions,
                sub_type: divinationState.subType,
                language: getCurrentLanguage()
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const resultContent = document.getElementById('resultContent');
        const resultCards = document.getElementById('resultCards');
        
        if (resultContent) resultContent.innerHTML = '';
        
        let fullResponse = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const lines = text.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.chunk) {
                            fullResponse += data.chunk;
                            if (resultContent) {
                                resultContent.innerHTML = formatInterpretation(fullResponse);
                            }
                        }
                        
                        if (data.done) {
                            // 解读完成，显示结果
                            if (interpretingDiv) interpretingDiv.style.display = 'none';
                            if (resultDiv) resultDiv.style.display = 'block';
                            
                            // 显示牌面
                            if (resultCards) {
                                resultCards.innerHTML = `
                                    <div class="result-cards-display">
                                        ${divinationState.selectedCards.map((card, index) => `
                                            <div class="result-card-item ${card.is_reversed ? 'reversed' : ''}">
                                                <div class="card-position">${divinationState.positions[index]}</div>
                                                <div class="card-name">${card.name}</div>
                                                <div class="card-meaning">
                                                    ${card.is_reversed ? '逆位 · ' : ''}${card.meaning || ''}
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                `;
                            }
                        }
                    } catch (e) {
                        console.error('解析错误:', e);
                    }
                }
            }
        }
        
    } catch (error) {
        showToast('解读失败，请重试', 'error');
        goToStep(2);
    }
}

function formatInterpretation(text) {
    // 简单的格式化：将换行转换为段落
    return text
        .split('\n')
        .filter(p => p.trim())
        .map(p => `<p>${p}</p>`)
        .join('');
}

function updateRemainingCount(count) {
    // 可以在这里更新UI显示剩余次数
    console.log('剩余占卜次数:', count);
}

function getCurrentLanguage() {
    const lang = new URLSearchParams(window.location.search).get('lang');
    return lang || 'zh';
}

// ============ 恋爱占卜 ============

function initLoveDivination() {
    const form = document.getElementById('loveForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {
                love_type: formData.get('love_type'),
                question: formData.get('question'),
                additional_info: formData.get('additional_info'),
                language: getCurrentLanguage()
            };
            
            if (!data.question.trim()) {
                showToast('请输入你的问题', 'warning');
                return;
            }
            
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> 占卜中...';
            
            try {
                const response = await fetch('/api/divination/love', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayLoveResult(result.result, result.divination_id);
                } else {
                    showToast(result.message || '占卜失败', 'error');
                }
            } catch (error) {
                showToast('网络错误', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span class="btn-icon">💕</span> 开始恋爱占卜';
            }
        });
    }
}

function displayLoveResult(result, divinationId) {
    const container = document.getElementById('loveResult');
    if (!container) return;
    
    container.style.display = 'block';
    container.innerHTML = `
        <div class="result-card">
            <h2 class="result-title">💕 占卜结果</h2>
            <div class="result-interpretation">
                ${result.interpretation}
            </div>
            <div class="result-actions">
                <a href="/divination/result/${divinationId}" class="btn btn-primary">
                    查看完整结果
                </a>
            </div>
        </div>
    `;
    
    container.scrollIntoView({ behavior: 'smooth' });
}

// ============ 星盘分析 ============

function initHoroscopeDivination() {
    const form = document.getElementById('horoscopeForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            showToast('星盘分析功能开发中', 'info');
        });
    }
}

// ============ 八字简批 ============

function initBaziDivination() {
    const form = document.getElementById('baziForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {
                birth_date: formData.get('birth_date'),
                birth_time: formData.get('birth_time'),
                birth_place: formData.get('birth_place'),
                question: formData.get('question'),
                language: getCurrentLanguage()
            };
            
            if (!data.birth_date || !data.birth_time) {
                showToast('请填写出生日期和时间', 'warning');
                return;
            }
            
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> 分析中...';
            
            try {
                const response = await fetch('/api/divination/bazi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayBaziResult(result.result, result.divination_id);
                } else {
                    showToast(result.message || '分析失败', 'error');
                }
            } catch (error) {
                showToast('网络错误', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span class="btn-icon">📜</span> 开始八字分析';
            }
        });
    }
}

function displayBaziResult(result, divinationId) {
    const container = document.getElementById('baziResult');
    if (!container) return;
    
    container.style.display = 'block';
    container.innerHTML = `
        <div class="result-card">
            <h2 class="result-title">📜 八字简批</h2>
            <div class="result-interpretation">
                ${result.interpretation}
            </div>
            <div class="result-actions">
                <a href="/divination/result/${divinationId}" class="btn btn-primary">
                    查看完整结果
                </a>
            </div>
        </div>
    `;
    
    container.scrollIntoView({ behavior: 'smooth' });
}

// ============ 分享功能 ============

function shareDivination(shareCode) {
    const url = `${window.location.origin}/divination/shared/${shareCode}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'SoulLink 占卜结果',
            text: '来看看我的占卜结果吧！',
            url: url
        });
    } else {
        copyToClipboard(url);
    }
}

// ============ 收藏功能 ============

async function saveFavorite(divinationId) {
    try {
        const response = await fetch(`/api/favorite/${divinationId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('已添加到收藏', 'success');
        } else {
            showToast(data.message || '收藏失败', 'error');
        }
    } catch (error) {
        showToast('收藏失败', 'error');
    }
}
