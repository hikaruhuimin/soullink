/* SoulLink - 流星效果脚本 */
/* 深邃星空背景 - 流星动画 */

(function() {
    'use strict';
    
    function createShootingStar() {
        const container = document.querySelector('.starry-bg');
        if (!container) return;
        
        const star = document.createElement('div');
        star.className = 'shooting-star';
        
        // 随机起始位置
        const startX = Math.random() * 60 + 40; // 40% - 100%
        const startY = Math.random() * 40 + 5;  // 5% - 45%
        
        star.style.top = startY + '%';
        star.style.left = startX + '%';
        
        container.appendChild(star);
        
        // 动画结束后移除
        setTimeout(function() {
            if (star.parentNode) {
                star.parentNode.removeChild(star);
            }
        }, 1500);
    }
    
    function scheduleNextStar() {
        // 8-20秒随机间隔
        const delay = 8000 + Math.random() * 12000;
        setTimeout(function() {
            createShootingStar();
            scheduleNextStar();
        }, delay);
    }
    
    // 页面加载后3秒开始
    function init() {
        setTimeout(function() {
            createShootingStar();
            scheduleNextStar();
        }, 3000);
    }
    
    // 等待DOM加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
