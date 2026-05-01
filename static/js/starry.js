/**
 * SoulLink - 深邃星象图系统
 * 真实星座连线 + 3D旋转 + 流星效果
 * 
 * 使用Canvas绘制，性能优化，支持requestAnimationFrame
 */

(function() {
    'use strict';

    // ==================== 配置 ====================
    const CONFIG = {
        // 星星层配置
        layers: [
            { count: 300, minSize: 0.5, maxSize: 1.2, minAlpha: 0.2, maxAlpha: 0.5, parallax: 0.1 },
            { count: 150, minSize: 1, maxSize: 2, minAlpha: 0.4, maxAlpha: 0.7, parallax: 0.3 },
            { count: 50, minSize: 2, maxSize: 3.5, minAlpha: 0.7, maxAlpha: 1.0, parallax: 0.6 }
        ],
        // 星空旋转速度（度/秒）
        rotationSpeed: 0.008,
        // 星座旋转速度（略慢于背景）
        constellationRotationSpeed: 0.006,
        // 流星配置
        meteor: {
            minInterval: 4000,
            maxInterval: 12000,
            minSpeed: 8,
            maxSpeed: 15,
            minLength: 80,
            maxLength: 200
        }
    };

    // ==================== 真实星座数据 ====================
    // 坐标范围 0-1，代表相对位置
    // mag: 星等，越小越亮
    const CONSTELLATIONS = [
        // 猎户座 Orion - 冬季最著名的星座
        {
            name: '猎户座',
            nameEn: 'Orion',
            color: 'rgba(200, 220, 255, 0.35)',
            stars: [
                {x: 0.28, y: 0.18, mag: 0.5},   // 参宿四 Betelgeuse (左肩，红超巨星)
                {x: 0.68, y: 0.18, mag: 0.2},   // 参宿五 Bellatrix (右肩)
                {x: 0.40, y: 0.48, mag: 1.7},   // 参宿一 Alnitak (腰带左)
                {x: 0.48, y: 0.50, mag: 1.7},   // 参宿二 Alnilam (腰带中)
                {x: 0.56, y: 0.52, mag: 2.0},   // 参宿三 Mintaka (腰带右)
                {x: 0.25, y: 0.82, mag: 2.0},   // 参宿六 Saiph (左脚)
                {x: 0.72, y: 0.85, mag: 0.1}    // 参宿七 Rigel (右脚，最亮)
            ],
            lines: [[0,1], [0,3], [1,4], [2,3], [3,4], [2,5], [4,6]]
        },
        
        // 金牛座 Taurus
        {
            name: '金牛座',
            nameEn: 'Taurus',
            color: 'rgba(255, 200, 150, 0.3)',
            stars: [
                {x: 0.75, y: 0.25, mag: 0.9},   // 毕宿五 Aldebaran (眼睛)
                {x: 0.72, y: 0.18, mag: 3.0},
                {x: 0.78, y: 0.15, mag: 3.5},
                {x: 0.82, y: 0.22, mag: 3.2},
                {x: 0.70, y: 0.35, mag: 3.5},
                {x: 0.55, y: 0.38, mag: 3.0},   // 昴宿六 Alcyone (七姐妹)
                {x: 0.52, y: 0.32, mag: 3.2},
                {x: 0.58, y: 0.30, mag: 3.4},
                {x: 0.50, y: 0.36, mag: 3.6},
                {x: 0.53, y: 0.42, mag: 3.8}
            ],
            lines: [[0,1], [0,4], [1,2], [2,3], [3,0], [5,6], [6,7], [7,8], [8,9], [5,9]]
        },
        
        // 双子座 Gemini
        {
            name: '双子座',
            nameEn: 'Gemini',
            color: 'rgba(180, 220, 255, 0.3)',
            stars: [
                {x: 0.82, y: 0.12, mag: 1.2},   // 北河二 Castor
                {x: 0.85, y: 0.18, mag: 1.6},   // 北河三 Pollux
                {x: 0.75, y: 0.28, mag: 2.0},
                {x: 0.78, y: 0.35, mag: 2.5},
                {x: 0.88, y: 0.30, mag: 2.8},
                {x: 0.80, y: 0.48, mag: 3.0},
                {x: 0.92, y: 0.42, mag: 3.2},
                {x: 0.85, y: 0.55, mag: 3.5}
            ],
            lines: [[0,2], [2,5], [5,7], [1,3], [3,6], [6,8], [2,3], [5,6]]
        },
        
        // 大熊座-北斗七星 Ursa Major (Big Dipper)
        {
            name: '北斗七星',
            nameEn: 'Big Dipper',
            color: 'rgba(255, 230, 180, 0.4)',
            stars: [
                {x: 0.08, y: 0.15, mag: 1.8},   // 天枢 Dubhe
                {x: 0.15, y: 0.12, mag: 2.4},   // 天璇 Merak
                {x: 0.22, y: 0.14, mag: 2.5},   // 天玑 Phecda
                {x: 0.28, y: 0.16, mag: 3.3},   // 天权 Megrez (最暗)
                {x: 0.34, y: 0.12, mag: 1.8},   // 玉衡 Alioth
                {x: 0.42, y: 0.08, mag: 2.0},   // 开阳 Mizar
                {x: 0.52, y: 0.05, mag: 1.9}    // 摇光 Alkaid
            ],
            lines: [[0,1], [1,2], [2,3], [3,4], [4,5], [5,6]]
        },
        
        // 仙后座 Cassiopeia
        {
            name: '仙后座',
            nameEn: 'Cassiopeia',
            color: 'rgba(200, 180, 255, 0.35)',
            stars: [
                {x: 0.58, y: 0.08, mag: 2.3},   // 王良一 Caph
                {x: 0.62, y: 0.12, mag: 2.2},   // 王良四 Schedar
                {x: 0.68, y: 0.10, mag: 2.7},   // 策 Navi
                {x: 0.74, y: 0.08, mag: 2.5},   // 王良二 Ruchbah
                {x: 0.80, y: 0.10, mag: 3.4}    // 王良三 Segin
            ],
            lines: [[0,1], [1,2], [2,3], [3,4]]
        },
        
        // 仙女座 Andromeda
        {
            name: '仙女座',
            nameEn: 'Andromeda',
            color: 'rgba(220, 200, 255, 0.3)',
            stars: [
                {x: 0.18, y: 0.35, mag: 2.1},   // 壁宿二 Alpheratz
                {x: 0.25, y: 0.30, mag: 2.3},   // 奎宿九 Mirach
                {x: 0.35, y: 0.25, mag: 3.3},   // 天大将军一
                {x: 0.42, y: 0.22, mag: 2.2},   // 奎宿七 Almach
                {x: 0.15, y: 0.42, mag: 3.8}    // 螣蛇十九
            ],
            lines: [[0,1], [1,2], [2,3]]
        },
        
        // 天鹅座 Cygnus (北十字)
        {
            name: '天鹅座',
            nameEn: 'Cygnus',
            color: 'rgba(180, 210, 255, 0.35)',
            stars: [
                {x: 0.62, y: 0.60, mag: 1.3},   // 天津四 Deneb (尾部)
                {x: 0.65, y: 0.50, mag: 2.5},   // 辇道增七 Albireo
                {x: 0.58, y: 0.42, mag: 2.2},   // 天津三
                {x: 0.55, y: 0.55, mag: 2.9},   // 天津一
                {x: 0.68, y: 0.58, mag: 2.5}    // 天津九
            ],
            lines: [[0,1], [1,2], [2,3], [0,3], [0,4]]
        },
        
        // 狮子座 Leo
        {
            name: '狮子座',
            nameEn: 'Leo',
            color: 'rgba(255, 220, 150, 0.3)',
            stars: [
                {x: 0.42, y: 0.72, mag: 1.4},   // 轩辕十四 Regulus (心脏)
                {x: 0.50, y: 0.68, mag: 2.6},   // 轩辕十三
                {x: 0.58, y: 0.72, mag: 3.0},
                {x: 0.55, y: 0.78, mag: 2.1},   // 五帝座一 Denebola (尾巴)
                {x: 0.48, y: 0.80, mag: 3.4},
                {x: 0.38, y: 0.78, mag: 3.5}
            ],
            lines: [[0,1], [1,2], [0,5], [5,6], [2,3], [3,4], [4,5]]
        },
        
        // 天蝎座 Scorpius
        {
            name: '天蝎座',
            nameEn: 'Scorpius',
            color: 'rgba(255, 150, 150, 0.35)',
            stars: [
                {x: 0.85, y: 0.78, mag: 2.3},   // 尾宿八
                {x: 0.88, y: 0.82, mag: 1.0},   // 尾宿九 Shaula (蝎尾)
                {x: 0.90, y: 0.88, mag: 2.7},
                {x: 0.82, y: 0.85, mag: 2.6},
                {x: 0.78, y: 0.80, mag: 2.3},
                {x: 0.75, y: 0.72, mag: 1.2},   // 心宿二 Antares (心脏，火红)
                {x: 0.72, y: 0.68, mag: 3.0},
                {x: 0.68, y: 0.70, mag: 2.4},
                {x: 0.65, y: 0.75, mag: 2.0},
                {x: 0.62, y: 0.78, mag: 2.5}
            ],
            lines: [[0,1], [1,2], [1,3], [3,4], [4,5], [5,6], [6,7], [7,8], [8,9]]
        },
        
        // 天琴座 Lyra
        {
            name: '天琴座',
            nameEn: 'Lyra',
            color: 'rgba(200, 255, 220, 0.35)',
            stars: [
                {x: 0.70, y: 0.42, mag: 0.0},   // 织女星 Vega (全天第五亮)
                {x: 0.66, y: 0.45, mag: 3.3},
                {x: 0.74, y: 0.45, mag: 3.5},
                {x: 0.68, y: 0.50, mag: 3.8},
                {x: 0.72, y: 0.50, mag: 3.8}
            ],
            lines: [[0,1], [0,2], [1,3], [2,4], [3,4]]
        },
        
        // 天鹰座 Aquila
        {
            name: '天鹰座',
            nameEn: 'Aquila',
            color: 'rgba(255, 240, 200, 0.35)',
            stars: [
                {x: 0.50, y: 0.58, mag: 0.8},   // 牛郎星 Altair (河鼓二)
                {x: 0.45, y: 0.55, mag: 2.7},   // 河鼓一
                {x: 0.55, y: 0.55, mag: 2.7},    // 河鼓三
                {x: 0.50, y: 0.62, mag: 3.5},
                {x: 0.48, y: 0.65, mag: 3.6}
            ],
            lines: [[0,1], [0,2], [1,3], [2,3], [3,4]]
        },
        
        // 小熊座-北极星 Ursa Minor (Little Dipper)
        {
            name: '小熊座',
            nameEn: 'Ursa Minor',
            color: 'rgba(200, 200, 255, 0.4)',
            stars: [
                {x: 0.45, y: 0.02, mag: 2.0},   // 勾陈一 Polaris (北极星)
                {x: 0.48, y: 0.08, mag: 4.3},
                {x: 0.42, y: 0.10, mag: 4.3},
                {x: 0.38, y: 0.15, mag: 2.1},   // 帝星 Kochab
                {x: 0.35, y: 0.12, mag: 3.0}    // 太子 Pherkad
            ],
            lines: [[0,1], [0,2], [1,3], [2,4], [3,4]]
        },
        
        // 英仙座 Perseus
        {
            name: '英仙座',
            nameEn: 'Perseus',
            color: 'rgba(180, 200, 255, 0.3)',
            stars: [
                {x: 0.38, y: 0.28, mag: 1.8},   // 天船三 Mirfak
                {x: 0.42, y: 0.32, mag: 2.9},
                {x: 0.35, y: 0.35, mag: 3.0},
                {x: 0.45, y: 0.38, mag: 2.1},   // 大陵五 Algol (食双星)
                {x: 0.32, y: 0.40, mag: 3.7}
            ],
            lines: [[0,1], [0,2], [1,3], [2,4], [3,4]]
        },
        
        // 飞马座 Pegasus (秋季四边形)
        {
            name: '飞马座',
            nameEn: 'Pegasus',
            color: 'rgba(180, 220, 255, 0.3)',
            stars: [
                {x: 0.15, y: 0.28, mag: 2.5},   // 室宿一 Markab
                {x: 0.28, y: 0.25, mag: 2.5},   // 室宿二
                {x: 0.28, y: 0.35, mag: 2.4},   // 壁宿一 Algenib
                {x: 0.22, y: 0.32, mag: 2.8},   // 雷电一
                {x: 0.35, y: 0.30, mag: 2.9}    // 奎宿五
            ],
            lines: [[0,1], [1,2], [0,3], [3,4], [4,2]]
        },
        
        // 御夫座 Auriga
        {
            name: '御夫座',
            nameEn: 'Auriga',
            color: 'rgba(255, 240, 200, 0.3)',
            stars: [
                {x: 0.55, y: 0.12, mag: 0.1},   // 五车二 Capella (全天第六亮)
                {x: 0.58, y: 0.08, mag: 1.6},
                {x: 0.52, y: 0.08, mag: 1.7},
                {x: 0.48, y: 0.12, mag: 3.0},
                {x: 0.45, y: 0.18, mag: 2.6}
            ],
            lines: [[0,1], [0,2], [1,2], [2,3], [3,4], [4,0]]
        }
    ];

    // ==================== 状态变量 ====================
    let canvas, ctx;
    let width, height;
    let dpr;
    let stars = [];
    let meteors = [];
    let rotation = 0;
    let animationId = null;
    let lastTime = 0;
    let isVisible = true;

    // ==================== 工具函数 ====================
    function random(min, max) {
        return Math.random() * (max - min) + min;
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    // 3D旋转函数
    function rotate3D(x, y, z, angleX, angleY) {
        // 绕Y轴旋转
        let x1 = x * Math.cos(angleY) - z * Math.sin(angleY);
        let z1 = x * Math.sin(angleY) + z * Math.cos(angleY);
        // 绕X轴旋转
        let y1 = y * Math.cos(angleX) - z1 * Math.sin(angleX);
        let z2 = y * Math.sin(angleX) + z1 * Math.cos(angleX);
        return { x: x1, y: y1, z: z2 };
    }

    // 将3D坐标投影到2D
    function project(x, y, z, scale) {
        const perspective = 800;
        const factor = perspective / (perspective + z);
        return {
            x: width / 2 + x * scale * factor,
            y: height / 2 + y * scale * factor,
            scale: factor
        };
    }

    // ==================== 初始化 ====================
    function init() {
        // 检查是否需要初始化
        if (!document.querySelector('.starry-bg')) return;
        
        // 获取或创建canvas
        canvas = document.getElementById('starry-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'starry-canvas';
            document.body.insertBefore(canvas, document.body.firstChild);
        }
        
        ctx = canvas.getContext('2d');
        
        // 设置高DPI
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        
        // 初始化尺寸
        resize();
        
        // 生成星星
        generateStars();
        
        // 绑定事件
        window.addEventListener('resize', resize);
        document.addEventListener('visibilitychange', handleVisibility);
        
        // 开始动画
        lastTime = performance.now();
        animate();
        
        // 启动流星生成
        scheduleMeteor();
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        
        ctx.scale(dpr, dpr);
    }

    function handleVisibility() {
        isVisible = !document.hidden;
        if (isVisible && !animationId) {
            lastTime = performance.now();
            animate();
        }
    }

    // ==================== 星星生成 ====================
    function generateStars() {
        stars = [];
        
        CONFIG.layers.forEach((layer, layerIndex) => {
            for (let i = 0; i < layer.count; i++) {
                stars.push({
                    x: random(-1, 1),           // 3D x坐标
                    y: random(-1, 1),           // 3D y坐标
                    z: random(-0.5, 1),         // 3D z坐标（深度）
                    size: random(layer.minSize, layer.maxSize),
                    alpha: random(layer.minAlpha, layer.maxAlpha),
                    twinkleSpeed: random(0.5, 2),
                    twinklePhase: random(0, Math.PI * 2),
                    layer: layerIndex,
                    parallax: layer.parallax
                });
            }
        });
    }

    // ==================== 绘制函数 ====================
    function draw(time) {
        // 清空画布
        ctx.clearRect(0, 0, width, height);
        
        // 计算旋转角度
        const deltaTime = (time - lastTime) / 1000;
        rotation += CONFIG.rotationSpeed * deltaTime * Math.PI / 180;
        
        // 保存上下文用于旋转
        ctx.save();
        ctx.translate(width / 2, height / 2);
        ctx.rotate(rotation);
        ctx.translate(-width / 2, -height / 2);
        
        // 绘制星星
        drawStars(time);
        
        // 绘制星座
        drawConstellations(time);
        
        // 恢复上下文
        ctx.restore();
        
        // 绘制流星（在旋转之外）
        drawMeteors();
    }

    function drawStars(time) {
        stars.forEach(star => {
            // 闪烁效果
            const twinkle = Math.sin(time * 0.001 * star.twinkleSpeed + star.twinklePhase);
            const alpha = star.alpha * (0.7 + 0.3 * twinkle);
            
            // 3D旋转（根据层级的视差）
            const angleX = rotation * 0.1;
            const angleY = rotation * star.parallax * 0.5;
            
            const rotated = rotate3D(
                star.x * width * 0.6,
                star.y * height * 0.6,
                star.z * 200,
                angleX,
                angleY
            );
            
            const projected = project(rotated.x, rotated.y, rotated.z, 1);
            
            // 根据深度调整大小和亮度
            const depthFactor = Math.max(0.3, Math.min(1, (rotated.z + 200) / 400));
            const size = star.size * depthFactor;
            const finalAlpha = alpha * depthFactor;
            
            if (size < 0.3) return;
            
            // 绘制星星
            ctx.beginPath();
            ctx.arc(projected.x, projected.y, size, 0, Math.PI * 2);
            
            // 根据层级设置颜色
            const colors = [
                `rgba(180, 200, 255, ${finalAlpha})`,     // 远 - 冷色
                `rgba(220, 230, 255, ${finalAlpha})`,     // 中
                `rgba(255, 255, 250, ${finalAlpha})`      // 近 - 白色
            ];
            
            ctx.fillStyle = colors[star.layer] || colors[0];
            ctx.fill();
            
            // 大星星加光晕
            if (size > 2 && depthFactor > 0.5) {
                const gradient = ctx.createRadialGradient(
                    projected.x, projected.y, 0,
                    projected.x, projected.y, size * 4
                );
                gradient.addColorStop(0, `rgba(255, 255, 255, ${finalAlpha * 0.3})`);
                gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                
                ctx.beginPath();
                ctx.arc(projected.x, projected.y, size * 4, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.fill();
            }
        });
    }

    function drawConstellations(time) {
        const constellationAngle = rotation * (CONFIG.constellationRotationSpeed / CONFIG.rotationSpeed);
        
        CONSTELLATIONS.forEach((constellation, cIndex) => {
            // 为每个星座添加微小的独立运动
            const phase = cIndex * 0.5;
            const drift = Math.sin(time * 0.0001 + phase) * 0.02;
            
            // 计算星座在屏幕上的位置
            const constellationX = 0.5 + Math.sin(cIndex * 0.7 + constellationAngle) * 0.2 + drift;
            const constellationY = 0.5 + Math.cos(cIndex * 0.5 + constellationAngle * 0.7) * 0.15;
            
            // 绘制星座连线
            ctx.strokeStyle = constellation.color;
            ctx.lineWidth = 0.8;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            constellation.lines.forEach(line => {
                const star1 = constellation.stars[line[0]];
                const star2 = constellation.stars[line[1]];
                
                const x1 = (constellationX + (star1.x - 0.5) * 0.4) * width;
                const y1 = (constellationY + (star1.y - 0.5) * 0.4) * height;
                const x2 = (constellationX + (star2.x - 0.5) * 0.4) * width;
                const y2 = (constellationY + (star2.y - 0.5) * 0.4) * height;
                
                // 画线
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            });
            
            // 绘制星座星星
            constellation.stars.forEach((star, sIndex) => {
                const x = (constellationX + (star.x - 0.5) * 0.4) * width;
                const y = (constellationY + (star.y - 0.5) * 0.4) * height;
                
                // 根据星等计算大小和亮度
                const size = Math.max(1.5, 4 - star.mag);
                const brightness = Math.max(0.3, 1 - star.mag * 0.15);
                
                // 闪烁
                const twinkle = Math.sin(time * 0.002 + sIndex * 0.8) * 0.15 + 0.85;
                
                // 绘制星星
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(220, 230, 255, ${brightness * twinkle})`;
                ctx.fill();
                
                // 光晕
                const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 3);
                gradient.addColorStop(0, `rgba(200, 220, 255, ${brightness * twinkle * 0.4})`);
                gradient.addColorStop(1, 'rgba(200, 220, 255, 0)');
                
                ctx.beginPath();
                ctx.arc(x, y, size * 3, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.fill();
            });
            
            // 绘制星座名称
            const nameX = (constellationX + 0.15) * width;
            const nameY = (constellationY - 0.18) * height;
            
            ctx.font = '11px "Microsoft YaHei", sans-serif';
            ctx.fillStyle = 'rgba(200, 210, 230, 0.5)';
            ctx.textAlign = 'left';
            ctx.fillText(constellation.name, nameX, nameY);
        });
    }

    // ==================== 流星系统 ====================
    function scheduleMeteor() {
        const delay = random(CONFIG.meteor.minInterval, CONFIG.meteor.maxInterval);
        setTimeout(() => {
            if (isVisible) {
                createMeteor();
            }
            scheduleMeteor();
        }, delay);
    }

    function createMeteor() {
        const isFireball = Math.random() < 0.1; // 10%概率火流星
        
        meteors.push({
            x: random(0.3, 1),
            y: random(-0.1, 0.3),
            speed: random(CONFIG.meteor.minSpeed, CONFIG.meteor.maxSpeed) * (isFireball ? 1.5 : 1),
            length: random(CONFIG.meteor.minLength, CONFIG.meteor.maxLength) * (isFireball ? 1.5 : 1),
            angle: random(35, 55), // 划过角度
            alpha: 1,
            life: 0,
            maxLife: random(40, 80),
            isFireball: isFireball
        });
    }

    function drawMeteors() {
        meteors = meteors.filter(meteor => {
            meteor.life++;
            
            if (meteor.life > meteor.maxLife) {
                return false;
            }
            
            // 计算位置
            const dx = Math.cos(meteor.angle * Math.PI / 180) * meteor.speed;
            const dy = Math.sin(meteor.angle * Math.PI / 180) * meteor.speed;
            
            meteor.x += dx * 0.01;
            meteor.y += dy * 0.01;
            
            // 淡出
            if (meteor.life > meteor.maxLife * 0.6) {
                meteor.alpha *= 0.92;
            }
            
            const x = meteor.x * width;
            const y = meteor.y * height;
            
            // 流星尾巴方向
            const tailAngle = (meteor.angle + 180) * Math.PI / 180;
            const tailX = x + Math.cos(tailAngle) * meteor.length;
            const tailY = y + Math.sin(tailAngle) * meteor.length;
            
            // 绘制流星
            const gradient = ctx.createLinearGradient(tailX, tailY, x, y);
            
            if (meteor.isFireball) {
                gradient.addColorStop(0, 'rgba(255, 200, 100, 0)');
                gradient.addColorStop(0.5, 'rgba(255, 150, 50, 0.5)');
                gradient.addColorStop(1, `rgba(255, 255, 255, ${meteor.alpha})`);
            } else {
                gradient.addColorStop(0, 'rgba(200, 220, 255, 0)');
                gradient.addColorStop(0.6, 'rgba(200, 220, 255, 0.3)');
                gradient.addColorStop(1, `rgba(255, 255, 255, ${meteor.alpha})`);
            }
            
            ctx.beginPath();
            ctx.moveTo(tailX, tailY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = gradient;
            ctx.lineWidth = meteor.isFireball ? 2.5 : 1.5;
            ctx.lineCap = 'round';
            ctx.stroke();
            
            // 流星头部光晕
            const headGradient = ctx.createRadialGradient(x, y, 0, x, y, meteor.isFireball ? 15 : 8);
            headGradient.addColorStop(0, `rgba(255, 255, 255, ${meteor.alpha})`);
            headGradient.addColorStop(0.3, `rgba(200, 220, 255, ${meteor.alpha * 0.5})`);
            headGradient.addColorStop(1, 'rgba(200, 220, 255, 0)');
            
            ctx.beginPath();
            ctx.arc(x, y, meteor.isFireball ? 15 : 8, 0, Math.PI * 2);
            ctx.fillStyle = headGradient;
            ctx.fill();
            
            return true;
        });
    }

    // ==================== 动画循环 ====================
    function animate(time = performance.now()) {
        if (!isVisible) {
            animationId = null;
            return;
        }
        
        draw(time);
        lastTime = time;
        animationId = requestAnimationFrame(animate);
    }

    // ==================== 启动 ====================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
