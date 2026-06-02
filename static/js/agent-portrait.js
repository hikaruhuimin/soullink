/**
 * SoulLink Agent Portrait Animation System
 * Agent肖像动画交互控制
 */

const AgentPortrait = (function() {
    'use strict';
    
    // 存储所有已初始化的肖像实例
    const portraits = new Map();
    
    // 默认配置
    const defaultOptions = {
        mood: 'happy',
        size: 'medium',
        showStatus: true,
        statusOnline: true,
        particleCount: 5,
        particleInterval: 3000
    };
    
    // 粒子配置
    const particleConfig = {
        happy: { color: 'rgba(255, 215, 100, 0.9)', count: 5, speed: 4000 },
        sad: { color: 'rgba(150, 180, 220, 0.7)', count: 3, speed: 6000 },
        excited: { color: 'rgba(200, 150, 255, 0.9)', count: 8, speed: 2000 },
        love: { color: 'rgba(255, 180, 200, 0.9)', count: 6, speed: 3500 },
        mysterious: { color: 'rgba(150, 100, 200, 0.7)', count: 4, speed: 8000 }
    };
    
    /**
     * 初始化Agent肖像
     * @param {HTMLElement|string} container - 容器元素或选择器
     * @param {string} agentId - Agent ID
     * @param {object} options - 配置选项
     * @returns {object} 肖像实例
     */
    function init(container, agentId, options = {}) {
        const el = typeof container === 'string' ? document.querySelector(container) : container;
        if (!el) {
            console.warn('AgentPortrait: Container not found');
            return null;
        }
        
        const config = { ...defaultOptions, ...options };
        const portraitImg = el.querySelector('.portrait-img');
        
        if (!portraitImg) {
            console.warn('AgentPortrait: .portrait-img not found');
            return null;
        }
        
        // 存储实例
        const instance = {
            el,
            agentId,
            config,
            particleTimer: null,
            isAnimating: false
        };
        
        portraits.set(agentId, instance);
        
        // 设置属性
        el.setAttribute('data-agent-id', agentId);
        el.setAttribute('data-mood', config.mood);
        if (config.size) {
            el.classList.add(`size-${config.size}`);
        }
        
        // 添加入场动画类
        el.classList.add('agent-portrait');
        
        // 初始化粒子
        initParticles(instance);
        
        // 初始化状态指示器
        if (config.showStatus) {
            initStatus(el, config.statusOnline);
        }
        
        return instance;
    }
    
    /**
     * 初始化粒子效果
     */
    function initParticles(instance) {
        const { el, config } = instance;
        const particlesContainer = el.querySelector('.portrait-particles');
        
        if (!particlesContainer) return;
        
        const mood = config.mood || 'happy';
        const pConfig = particleConfig[mood] || particleConfig.happy;
        
        // 清除现有粒子
        particlesContainer.innerHTML = '';
        
        // 创建粒子
        for (let i = 0; i < pConfig.count; i++) {
            createParticle(particlesContainer, i, pConfig);
        }
        
        // 定时重置粒子动画
        instance.particleTimer = setInterval(() => {
            if (!instance.isAnimating) {
                resetParticles(particlesContainer, pConfig);
            }
        }, config.particleInterval || 3000);
    }
    
    /**
     * 创建单个粒子
     */
    function createParticle(container, index, config) {
        const particle = document.createElement('div');
        particle.className = 'portrait-particle';
        
        // 随机位置（围绕肖像周边）
        const angle = (index / config.count) * Math.PI * 2 + Math.random() * 0.5;
        const radius = 40 + Math.random() * 20;
        const x = 50 + Math.cos(angle) * radius;
        const y = 50 + Math.sin(angle) * radius;
        
        particle.style.cssText = `
            left: ${x}%;
            top: ${y}%;
            animation: particleFloat ${config.speed}ms ease-in-out infinite;
            animation-delay: ${index * (config.speed / config.count)}ms;
            background: ${config.color};
            box-shadow: 0 0 6px 2px ${config.color};
            width: ${3 + Math.random() * 3}px;
            height: ${3 + Math.random() * 3}px;
        `;
        
        container.appendChild(particle);
    }
    
    /**
     * 重置粒子动画
     */
    function resetParticles(container, config) {
        const particles = container.querySelectorAll('.portrait-particle');
        particles.forEach((p, i) => {
            p.style.animation = 'none';
            p.offsetHeight; // 触发重排
            p.style.animation = `particleFloat ${config.speed}ms ease-in-out infinite`;
            p.style.animationDelay = `${i * (config.speed / particles.length)}ms`;
        });
    }
    
    /**
     * 初始化状态指示器
     */
    function initStatus(el, isOnline) {
        const existing = el.querySelector('.portrait-status');
        if (existing) existing.remove();
        
        const status = document.createElement('div');
        status.className = `portrait-status ${isOnline ? '' : 'offline'}`;
        el.querySelector('.portrait-frame').appendChild(status);
    }
    
    /**
     * 说话动画
     * @param {string} agentId - Agent ID
     * @param {number} duration - 持续时间(ms)，默认3000
     */
    function talk(agentId, duration = 3000) {
        const instance = portraits.get(agentId);
        if (!instance) return;
        
        const { el } = instance;
        instance.isAnimating = true;
        
        // 添加说话状态
        el.classList.remove('gift', 'blush');
        el.classList.add('talking');
        
        // 创建消息气泡
        showMessageBubble(el);
        
        // 指定时间后恢复
        setTimeout(() => {
            el.classList.remove('talking');
            instance.isAnimating = false;
        }, duration);
    }
    
    /**
     * 显示消息气泡
     */
    function showMessageBubble(el) {
        const existing = el.querySelector('.portrait-message-bubble');
        if (existing) existing.remove();
        
        const bubble = document.createElement('div');
        bubble.className = 'portrait-message-bubble';
        bubble.textContent = '💬';
        el.appendChild(bubble);
        
        setTimeout(() => {
            bubble.style.animation = 'bubblePop 0.3s ease-out reverse';
            setTimeout(() => bubble.remove(), 300);
        }, 2000);
    }
    
    /**
     * 收礼物动画
     * @param {string} agentId - Agent ID
     * @param {number} duration - 持续时间(ms)，默认4000
     */
    function gift(agentId, duration = 4000) {
        const instance = portraits.get(agentId);
        if (!instance) return;
        
        const { el } = instance;
        instance.isAnimating = true;
        
        // 移除其他动画状态
        el.classList.remove('talking', 'blush');
        
        // 添加礼物动画
        el.classList.add('gift');
        
        // 创建星星爆发
        createStarBurst(el);
        
        // 创建心形升起
        createHeartRise(el);
        
        // 指定时间后恢复
        setTimeout(() => {
            el.classList.remove('gift');
            instance.isAnimating = false;
        }, duration);
    }
    
    /**
     * 创建星星爆发效果
     */
    function createStarBurst(el) {
        const burstContainer = document.createElement('div');
        burstContainer.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            z-index: 100;
            pointer-events: none;
        `;
        el.appendChild(burstContainer);
        
        const starCount = 8 + Math.floor(Math.random() * 5);
        
        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'star-burst';
            
            const angle = (i / starCount) * Math.PI * 2;
            const distance = 60 + Math.random() * 40;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            
            star.style.cssText = `
                position: absolute;
                left: 0;
                top: 0;
                --burst-x: ${x}px;
                --burst-y: ${y}px;
                animation: starBurst 0.8s ease-out forwards;
                animation-delay: ${i * 30}ms;
            `;
            
            burstContainer.appendChild(star);
        }
        
        setTimeout(() => burstContainer.remove(), 1000);
    }
    
    /**
     * 创建心形升起效果
     */
    function createHeartRise(el) {
        const heartCount = 2 + Math.floor(Math.random() * 2);
        
        for (let i = 0; i < heartCount; i++) {
            const heart = document.createElement('div');
            heart.className = 'heart-rise';
            heart.textContent = '❤️';
            
            const side = i % 2 === 0 ? -1 : 1;
            heart.style.cssText = `
                left: ${45 + side * 20}%;
                bottom: 30%;
                animation-delay: ${i * 200}ms;
                font-size: ${14 + Math.random() * 8}px;
            `;
            
            el.appendChild(heart);
            
            setTimeout(() => heart.remove(), 2500);
        }
    }
    
    /**
     * 脸红动画（亲密度提升）
     * @param {string} agentId - Agent ID
     * @param {number} duration - 持续时间(ms)，默认3000
     */
    function blush(agentId, duration = 3000) {
        const instance = portraits.get(agentId);
        if (!instance) return;
        
        const { el } = instance;
        instance.isAnimating = true;
        
        // 移除其他动画状态
        el.classList.remove('talking', 'gift');
        
        // 添加脸红状态
        el.classList.add('blush');
        
        // 创建爱心粒子
        createLoveParticles(el);
        
        // 指定时间后恢复
        setTimeout(() => {
            el.classList.remove('blush');
            instance.isAnimating = false;
        }, duration);
    }
    
    /**
     * 创建爱心粒子
     */
    function createLoveParticles(el) {
        const particleContainer = el.querySelector('.portrait-particles');
        if (!particleContainer) return;
        
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'portrait-particle';
            particle.style.cssText = `
                left: ${30 + Math.random() * 40}%;
                top: ${60 + Math.random() * 20}%;
                background: rgba(255, 100, 130, 0.9);
                box-shadow: 0 0 8px 3px rgba(255, 100, 130, 0.6);
                animation: heartParticleRise 2.5s ease-out forwards;
                animation-delay: ${i * 150}ms;
            `;
            
            particleContainer.appendChild(particle);
            setTimeout(() => particle.remove(), 3000);
        }
    }
    
    /**
     * 设置情绪状态
     * @param {string} agentId - Agent ID
     * @param {string} mood - 情绪状态
     */
    function setMood(agentId, mood) {
        const instance = portraits.get(agentId);
        if (!instance) return;
        
        const { el, config } = instance;
        const validMoods = ['happy', 'sad', 'excited', 'love', 'mysterious'];
        const newMood = validMoods.includes(mood) ? mood : 'happy';
        
        // 更新属性
        el.setAttribute('data-mood', newMood);
        instance.config.mood = newMood;
        
        // 重新初始化粒子
        clearInterval(instance.particleTimer);
        initParticles(instance);
    }
    
    /**
     * 获取Agent肖像实例
     * @param {string} agentId - Agent ID
     * @returns {object|null} 实例
     */
    function getInstance(agentId) {
        return portraits.get(agentId) || null;
    }
    
    /**
     * 销毁肖像实例
     * @param {string} agentId - Agent ID
     */
    function destroy(agentId) {
        const instance = portraits.get(agentId);
        if (instance) {
            clearInterval(instance.particleTimer);
            instance.el.classList.remove('agent-portrait', 'talking', 'gift', 'blush');
            portraits.delete(agentId);
        }
    }
    
    /**
     * 创建HTML结构
     * @param {string} agentId - Agent ID
     * @param {string} avatarUrl - 头像URL
     * @param {object} options - 配置选项
     * @returns {string} HTML字符串
     */
    function createHTML(agentId, avatarUrl, options = {}) {
        const config = { ...defaultOptions, ...options };
        const size = config.size ? `size-${config.size}` : '';
        const mood = config.mood || 'happy';
        
        return `
            <div class="agent-portrait ${size}" data-agent-id="${agentId}" data-mood="${mood}">
                <div class="portrait-frame">
                    <img src="${avatarUrl}" alt="${agentId}" class="portrait-img">
                    <div class="portrait-overlay"></div>
                    <div class="portrait-particles"></div>
                    <div class="portrait-glow"></div>
                </div>
            </div>
        `;
    }
    
    /**
     * 自动绑定页面上的Agent肖像
     * 扫描所有带有 data-agent-portrait 属性的元素
     */
    function autoBind() {
        const elements = document.querySelectorAll('[data-agent-portrait]');
        elements.forEach(el => {
            const agentId = el.dataset.agentId;
            const avatarUrl = el.dataset.avatar;
            const mood = el.dataset.mood;
            const size = el.dataset.size;
            
            if (agentId && avatarUrl) {
                // 替换内容为完整结构
                el.outerHTML = createHTML(agentId, avatarUrl, { mood, size });
                
                // 初始化
                const newEl = document.querySelector(`[data-agent-id="${agentId}"]`);
                if (newEl) {
                    init(newEl, agentId, { mood, size, showStatus: false });
                }
            }
        });
    }
    
    // 公开API
    return {
        init,
        talk,
        gift,
        blush,
        setMood,
        getInstance,
        destroy,
        createHTML,
        autoBind
    };
})();

// 页面加载完成后自动绑定
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AgentPortrait.autoBind());
} else {
    AgentPortrait.autoBind();
}
