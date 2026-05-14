/**
 * AgentPortrait - Creates animated agent portrait with glow and particles
 */
class AgentPortrait {
    static init(container, agentId, options = {}) {
        if (!container) return;
        const opts = {
            mood: options.mood || 'happy',
            size: options.size || 'medium',
            showStatus: options.showStatus !== false,
            particleCount: options.particleCount || 6,
            particleInterval: options.particleInterval || 3000,
        };

        // Set data attributes
        container.dataset.agentId = agentId;
        container.dataset.mood = opts.mood;

        // Add size class
        if (opts.size) {
            container.classList.add('size-' + opts.size);
        }

        // Ensure inner elements exist
        let frame = container.querySelector('.portrait-frame');
        let glow = container.querySelector('.portrait-glow');
        let particles = container.querySelector('.portrait-particles');
        let overlay = container.querySelector('.portrait-overlay');

        if (!frame) {
            frame = document.createElement('div');
            frame.className = 'portrait-frame';
            container.appendChild(frame);
        }

        if (!glow) {
            glow = document.createElement('div');
            glow.className = 'portrait-glow';
            container.appendChild(glow);
        }

        if (!particles) {
            particles = document.createElement('div');
            particles.className = 'portrait-particles';
            container.appendChild(particles);
        }

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'portrait-overlay';
            frame.appendChild(overlay);
        }

        // Ensure img exists inside frame
        let img = frame.querySelector('.portrait-img');
        if (!img) {
            img = document.createElement('img');
            img.className = 'portrait-img';
            img.alt = 'Agent';
            img.onerror = function() { this.style.display = 'none'; };
            frame.appendChild(img);
        }

        // Set avatar from data attribute or options
        const avatarUrl = options.avatar || container.dataset.avatar || '';
        if (avatarUrl) {
            img.src = avatarUrl;
        }

        // Start particle animation
        if (opts.particleCount > 0) {
            AgentPortrait._startParticles(particles, opts);
        }

        // Mood-based glow color
        if (opts.mood && glow) {
            const moodColors = {
                happy: 'rgba(255, 215, 0, 0.4)',
                excited: 'rgba(255, 100, 150, 0.4)',
                sad: 'rgba(100, 150, 255, 0.3)',
                angry: 'rgba(255, 50, 50, 0.4)',
                mysterious: 'rgba(150, 100, 255, 0.4)',
                sassy: 'rgba(255, 150, 200, 0.4)',
                commanding: 'rgba(200, 150, 50, 0.4)',
                default: 'rgba(107, 91, 123, 0.3)',
            };
            glow.style.background =
                'radial-gradient(circle, ' + (moodColors[opts.mood] || moodColors.default) + ' 0%, transparent 70%)';
        }
    }

    static _startParticles(container, opts) {
        function createParticle() {
            if (!container || !container.parentElement) return;
            const particle = document.createElement('div');
            particle.className = 'particle';
            const size = 3 + Math.random() * 4;
            particle.style.cssText =
                'position:absolute;width:' +
                size +
                'px;height:' +
                size +
                'px;border-radius:50%;background:rgba(255,255,255,0.6);' +
                'left:' +
                (20 + Math.random() * 60) +
                '%;top:' +
                (10 + Math.random() * 80) +
                '%;' +
                'animation:particleFade ' +
                (1.5 + Math.random() * 2) +
                's ease-out forwards;';
            container.appendChild(particle);
            setTimeout(function () {
                if (particle.parentElement) particle.remove();
            }, 3500);
        }

        // Create initial particles
        for (let i = 0; i < Math.min(opts.particleCount, 3); i++) {
            setTimeout(createParticle, i * 300);
        }

        // Periodic particles
        if (container._particleInterval) clearInterval(container._particleInterval);
        container._particleInterval = setInterval(createParticle, opts.particleInterval);
    }

    static setMood(container, mood) {
        if (!container) return;
        container.dataset.mood = mood;
        const glow = container.querySelector('.portrait-glow');
        if (glow) {
            const moodColors = {
                happy: 'rgba(255, 215, 0, 0.4)',
                excited: 'rgba(255, 100, 150, 0.4)',
                sad: 'rgba(100, 150, 255, 0.3)',
                angry: 'rgba(255, 50, 50, 0.4)',
                mysterious: 'rgba(150, 100, 255, 0.4)',
                sassy: 'rgba(255, 150, 200, 0.4)',
                commanding: 'rgba(200, 150, 50, 0.4)',
                default: 'rgba(107, 91, 123, 0.3)',
            };
            glow.style.background =
                'radial-gradient(circle, ' + (moodColors[mood] || moodColors.default) + ' 0%, transparent 70%)';
        }
    }
}
