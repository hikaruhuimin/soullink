content = open('templates/agent_profile.html', 'r').read()

# Add voice button next to chat button
old_actions = '''            <div class="profile-actions">
                <button class="btn-chat" id="startChatBtn" data-agent-id="{{ current_agent.id }}">
                    <span>💬</span>
                    <span>开始聊天</span>
                </button>
            </div>'''

new_actions = '''            <div class="profile-actions" style="display: flex; gap: 12px; justify-content: center;">
                <button class="btn-chat" id="startChatBtn" data-agent-id="{{ current_agent.id }}">
                    <span>💬</span>
                    <span>开始聊天</span>
                </button>
                <button class="btn-voice-demo" id="voiceDemoBtn" onclick="playVoiceDemo('{{ current_agent.id }}', this)" style="
                    display: inline-flex; align-items: center; gap: 8px;
                    padding: 12px 24px; border-radius: 50px;
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
                    border: 1px solid rgba(139, 92, 246, 0.4);
                    color: #c4b5fd; font-size: 0.9375rem; font-weight: 500;
                    cursor: pointer; transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                ">
                    <span>🔊</span>
                    <span>语音试听</span>
                </button>
            </div>'''

content = content.replace(old_actions, new_actions)

# Add voice demo function in the script section
voice_js = '''
// Voice demo function
function playVoiceDemo(agentId, btn) {
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span>⏳</span><span>生成语音中...</span>';
    btn.disabled = true;
    btn.style.opacity = '0.7';
    
    fetch(`/api/tts/demo/${agentId}`)
        .then(res => {
            if (!res.ok) throw new Error('TTS failed');
            return res.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            btn.innerHTML = '<span>🔊</span><span>播放中...</span>';
            btn.style.opacity = '1';
            btn.classList.add('playing');
            audio.play();
            audio.onended = () => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
                btn.classList.remove('playing');
                URL.revokeObjectURL(url);
            };
            audio.onerror = () => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
                showToast('语音播放失败');
            };
        })
        .catch(err => {
            console.error('Voice demo error:', err);
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            btn.style.opacity = '1';
            showToast('语音生成失败，请稍后重试');
        });
}
'''

# Insert before the closing </script> tag
if 'playVoiceDemo' not in content:
    last_script = content.rfind('</script>')
    content = content[:last_script] + voice_js + content[last_script:]

# Also add voice button CSS for playing state
voice_css = '''
.btn-voice-demo:hover {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.35), rgba(59, 130, 246, 0.35)) !important;
    border-color: rgba(139, 92, 246, 0.6) !important;
    transform: scale(1.05);
}
.btn-voice-demo.playing {
    animation: voicePulse 1.5s ease-in-out infinite;
}
@keyframes voicePulse {
    0%, 100% { box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }
    50% { box-shadow: 0 0 25px rgba(139, 92, 246, 0.6); }
}
'''
style_end = content.find('</style>')
if style_end >= 0:
    content = content[:style_end] + voice_css + content[style_end:]

open('templates/agent_profile.html', 'w').write(content)
print('done')
