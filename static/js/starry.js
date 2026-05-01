/**
 * SoulLink - 深邃星象图系统 v2
 * 简化版：直接2D绘制，不用3D投影，确保可见
 */
(function() {
    'use strict';

    let canvas, ctx, W, H;
    let stars = [];
    let meteors = [];
    let rotation = 0;
    let animId = null;

    // 星座数据（相对坐标0-1）
    const CONSTELLATIONS = [
        {
            name: '猎户座', nameEn: 'Orion',
            stars: [
                {x:0.35,y:0.12},{x:0.65,y:0.12},{x:0.42,y:0.45},
                {x:0.50,y:0.47},{x:0.58,y:0.49},{x:0.30,y:0.82},{x:0.70,y:0.85}
            ],
            lines: [[0,2],[1,4],[2,3],[3,4],[2,5],[4,6]],
            cx: 0.15, cy: 0.20
        },
        {
            name: '北斗七星', nameEn: 'Big Dipper',
            stars: [
                {x:0.2,y:0.3},{x:0.3,y:0.25},{x:0.42,y:0.22},{x:0.55,y:0.25},
                {x:0.6,y:0.35},{x:0.72,y:0.38},{x:0.78,y:0.30}
            ],
            lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],
            cx: 0.82, cy: 0.12
        },
        {
            name: '仙后座', nameEn: 'Cassiopeia',
            stars: [{x:0.2,y:0.5},{x:0.35,y:0.3},{x:0.5,y:0.55},{x:0.65,y:0.25},{x:0.8,y:0.5}],
            lines: [[0,1],[1,2],[2,3],[3,4]],
            cx: 0.50, cy: 0.08
        },
        {
            name: '天蝎座', nameEn: 'Scorpius',
            stars: [
                {x:0.3,y:0.1},{x:0.35,y:0.2},{x:0.4,y:0.35},{x:0.45,y:0.5},
                {x:0.5,y:0.6},{x:0.6,y:0.7},{x:0.7,y:0.75},{x:0.8,y:0.7}
            ],
            lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]],
            cx: 0.25, cy: 0.55
        },
        {
            name: '仙女座', nameEn: 'Andromeda',
            stars: [{x:0.5,y:0.2},{x:0.4,y:0.35},{x:0.3,y:0.5},{x:0.6,y:0.35},{x:0.7,y:0.5}],
            lines: [[2,1],[1,0],[0,3],[3,4]],
            cx: 0.75, cy: 0.30
        },
        {
            name: '狮子座', nameEn: 'Leo',
            stars: [{x:0.3,y:0.2},{x:0.2,y:0.35},{x:0.35,y:0.45},{x:0.55,y:0.45},{x:0.7,y:0.35},{x:0.65,y:0.55}],
            lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[3,5]],
            cx: 0.40, cy: 0.72
        },
        {
            name: '天鹅座', nameEn: 'Cygnus',
            stars: [{x:0.5,y:0.1},{x:0.5,y:0.35},{x:0.5,y:0.6},{x:0.3,y:0.4},{x:0.7,y:0.4}],
            lines: [[0,1],[1,2],[3,1],[1,4]],
            cx: 0.88, cy: 0.50
        },
        {
            name: '双子座', nameEn: 'Gemini',
            stars: [{x:0.35,y:0.1},{x:0.55,y:0.1},{x:0.3,y:0.4},{x:0.6,y:0.4},{x:0.25,y:0.7},{x:0.65,y:0.7}],
            lines: [[0,2],[2,4],[1,3],[3,5],[0,1]],
            cx: 0.12, cy: 0.75
        },
        {
            name: '天琴座', nameEn: 'Lyra',
            stars: [{x:0.5,y:0.1},{x:0.35,y:0.35},{x:0.65,y:0.35},{x:0.4,y:0.6},{x:0.6,y:0.6}],
            lines: [[0,1],[0,2],[1,3],[2,4],[3,4]],
            cx: 0.60, cy: 0.65
        },
        {
            name: '金牛座', nameEn: 'Taurus',
            stars: [{x:0.3,y:0.2},{x:0.45,y:0.3},{x:0.6,y:0.25},{x:0.55,y:0.45},{x:0.35,y:0.55}],
            lines: [[0,1],[1,2],[1,3],[3,4]],
            cx: 0.90, cy: 0.75
        },
        {
            name: '射手座', nameEn: 'Sagittarius',
            stars: [{x:0.4,y:0.2},{x:0.5,y:0.3},{x:0.45,y:0.45},{x:0.55,y:0.45},{x:0.5,y:0.6},{x:0.6,y:0.7}],
            lines: [[0,1],[1,2],[1,3],[2,4],[3,4],[4,5]],
            cx: 0.30, cy: 0.85
        },
        {
            name: '英仙座', nameEn: 'Perseus',
            stars: [{x:0.5,y:0.1},{x:0.45,y:0.3},{x:0.55,y:0.3},{x:0.5,y:0.5},{x:0.4,y:0.7}],
            lines: [[0,1],[0,2],[1,3],[2,3],[3,4]],
            cx: 0.70, cy: 0.88
        }
    ];

    function init() {
        if (!document.querySelector('.starry-bg')) return;

        canvas = document.getElementById('starry-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'starry-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;';
            document.body.insertBefore(canvas, document.body.firstChild);
        }

        ctx = canvas.getContext('2d');
        resize();
        generateStars();
        window.addEventListener('resize', resize);
        animate();
    }

    function resize() {
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W;
        canvas.height = H;
    }

    function generateStars() {
        stars = [];
        // 远层 - 暗小
        for (let i = 0; i < 200; i++) {
            stars.push({
                x: Math.random(), y: Math.random(),
                size: 0.5 + Math.random() * 0.8,
                alpha: 0.15 + Math.random() * 0.35,
                twinkle: 0.5 + Math.random() * 2,
                phase: Math.random() * Math.PI * 2,
                layer: 0
            });
        }
        // 中层
        for (let i = 0; i < 100; i++) {
            stars.push({
                x: Math.random(), y: Math.random(),
                size: 1 + Math.random() * 1.5,
                alpha: 0.3 + Math.random() * 0.4,
                twinkle: 0.8 + Math.random() * 1.5,
                phase: Math.random() * Math.PI * 2,
                layer: 1
            });
        }
        // 近层 - 亮大
        for (let i = 0; i < 40; i++) {
            stars.push({
                x: Math.random(), y: Math.random(),
                size: 2 + Math.random() * 2,
                alpha: 0.6 + Math.random() * 0.4,
                twinkle: 1 + Math.random(),
                phase: Math.random() * Math.PI * 2,
                layer: 2
            });
        }
    }

    function draw(time) {
        ctx.clearRect(0, 0, W, H);
        rotation += 0.00003;

        // 绘制星星
        stars.forEach(s => {
            const t = time * 0.001 * s.twinkle + s.phase;
            const a = s.alpha * (0.6 + 0.4 * Math.sin(t));

            // 缓慢旋转偏移
            const dx = (s.x - 0.5) * Math.cos(rotation) - (s.y - 0.5) * Math.sin(rotation) + 0.5;
            const dy = (s.x - 0.5) * Math.sin(rotation) + (s.y - 0.5) * Math.cos(rotation) + 0.5;

            const sx = dx * W;
            const sy = dy * H;

            ctx.beginPath();
            ctx.arc(sx, sy, s.size, 0, Math.PI * 2);

            const colors = [
                `rgba(160,180,240,${a})`,
                `rgba(200,215,255,${a})`,
                `rgba(255,255,245,${a})`
            ];
            ctx.fillStyle = colors[s.layer];
            ctx.fill();

            // 大星加光晕
            if (s.size > 2.5) {
                const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, s.size * 5);
                g.addColorStop(0, `rgba(255,255,255,${a * 0.25})`);
                g.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.beginPath();
                ctx.arc(sx, sy, s.size * 5, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            }
        });

        // 绘制星座
        CONSTELLATIONS.forEach((c, ci) => {
            const drift = Math.sin(time * 0.00005 + ci) * 0.01;
            const cx = c.cx + drift;
            const cy = c.cy + Math.cos(time * 0.00004 + ci * 0.7) * 0.008;

            // 连线
            ctx.strokeStyle = 'rgba(140,160,220,0.25)';
            ctx.lineWidth = 0.8;
            c.lines.forEach(([a, b]) => {
                const s1 = c.stars[a], s2 = c.stars[b];
                const x1 = (cx + (s1.x - 0.5) * 0.12) * W;
                const y1 = (cy + (s1.y - 0.5) * 0.15) * H;
                const x2 = (cx + (s2.x - 0.5) * 0.12) * W;
                const y2 = (cy + (s2.y - 0.5) * 0.15) * H;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            });

            // 星座里的星星
            c.stars.forEach((s, si) => {
                const sx = (cx + (s.x - 0.5) * 0.12) * W;
                const sy = (cy + (s.y - 0.5) * 0.15) * H;
                const bright = 0.5 + 0.3 * Math.sin(time * 0.001 + si);

                ctx.beginPath();
                ctx.arc(sx, sy, 1.8, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(200,210,255,${bright})`;
                ctx.fill();

                // 小光晕
                const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, 5);
                g.addColorStop(0, `rgba(180,200,255,${bright * 0.3})`);
                g.addColorStop(1, 'rgba(180,200,255,0)');
                ctx.beginPath();
                ctx.arc(sx, sy, 5, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            });

            // 星座名
            const labelX = cx * W;
            const labelY = (cy + 0.09) * H;
            ctx.font = '11px "Noto Sans SC", sans-serif';
            ctx.fillStyle = 'rgba(200,190,160,0.4)';
            ctx.textAlign = 'center';
            ctx.fillText(c.name, labelX, labelY);
        });

        // 绘制流星
        drawMeteors(time);
    }

    function drawMeteors(time) {
        // 随机生成流星
        if (Math.random() < 0.003) {
            meteors.push({
                x: Math.random() * W * 0.8 + W * 0.1,
                y: 0,
                speed: 5 + Math.random() * 10,
                angle: Math.PI * 0.2 + Math.random() * 0.15,
                length: 60 + Math.random() * 140,
                life: 1.0,
                isFireball: Math.random() < 0.1
            });
        }

        meteors = meteors.filter(m => {
            m.x += Math.cos(m.angle) * m.speed;
            m.y += Math.sin(m.angle) * m.speed;
            m.life -= 0.012;

            if (m.life <= 0 || m.x > W || m.y > H) return false;

            const tailX = m.x - Math.cos(m.angle) * m.length;
            const tailY = m.y - Math.sin(m.angle) * m.length;

            const g = ctx.createLinearGradient(tailX, tailY, m.x, m.y);
            g.addColorStop(0, 'rgba(255,255,255,0)');
            g.addColorStop(0.7, `rgba(200,220,255,${m.life * 0.5})`);
            g.addColorStop(1, `rgba(255,255,255,${m.life * 0.9})`);

            ctx.beginPath();
            ctx.moveTo(tailX, tailY);
            ctx.lineTo(m.x, m.y);
            ctx.strokeStyle = g;
            ctx.lineWidth = m.isFireball ? 2.5 : 1.2;
            ctx.stroke();

            // 头部光晕
            const headG = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, m.isFireball ? 12 : 6);
            headG.addColorStop(0, `rgba(255,255,255,${m.life * 0.8})`);
            headG.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.beginPath();
            ctx.arc(m.x, m.y, m.isFireball ? 12 : 6, 0, Math.PI * 2);
            ctx.fillStyle = headG;
            ctx.fill();

            return true;
        });
    }

    function animate() {
        draw(performance.now());
        animId = requestAnimationFrame(animate);
    }

    // 启动
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
