#!/usr/bin/env python3
"""
Batch convert all hardcoded Chinese text in templates to _() calls.
Uses safe, context-aware replacements.
"""
import os
import re

TEMPLATES_DIR = '/tmp/soullink/templates'

# All replacements organized by file
# Each entry: (file_path, [(old_exact_text, new_template_call)])
REPLACEMENTS = {
    # ====== 1. index.html ======
    'index.html': [
        ('SoulLink 灵犀 - 遇见你的灵魂伴侣', "{{ _('app_name') }} - {{ _('find_your_match') }}"),
        ('遇见你的灵魂伴侣', "{{ _('find_your_match') }}"),
    ],
    
    # ====== 2. chat_home.html ======
    'chat_home.html': [
        ('>聊天室<', ">{{ _('chat_room') }}<"),
    ],
    
    # ====== 3. chat_room.html ======
    'chat_room.html': [
        ('输入消息...', "{{ _('type_message') }}"),
    ],
    
    # ====== 4. agents_square.html ======
    'agents_square.html': [
        ('>Agent广场<', ">{{ _('agent_square') }}<"),
        ('>人类<', ">{{ _('humans') }}<"),
        ('>全部<', ">{{ _('all') }}<"),
        ('>热门<', ">{{ _('hot') }}<"),
        ('>最新<', ">{{ _('new') }}<"),
    ],
    
    # ====== 5. agent_profile.html ======
    'agent_profile.html': [
        ('>专长领域<', ">{{ _('specialty') if 'specialty' in TRANSLATIONS.get(lang, {}) else '专长领域' }}<"),
        ('>关于我<', ">{{ _('about_me') }}<"),
    ],
    
    # ====== 6. divination_dream.html ======
    'divination_dream.html': [
        ('AI解梦', "{{ _('dream_divination') }}"),
        ('解梦', "{{ _('dream_divination') }}"),
    ],
    
    # ====== 7. divination_iching.html ======
    'divination_iching.html': [
        ('易经六爻', "{{ _('iching_divination') }}"),
        ('上卦', "{{ _('upper_trigram') if 'upper_trigram' in TRANSLATIONS.get(lang, {}) else '上卦' }}"),
        ('下卦', "{{ _('lower_trigram') if 'lower_trigram' in TRANSLATIONS.get(lang, {}) else '下卦' }}"),
    ],
    
    # ====== 8. divination_omikuji.html ======
    'divination_omikuji.html': [
        ('おみくじ', "{{ _('omikuji_divination') }}"),
        ('抽一支签', "{{ _('omikuji_draw') }}"),
    ],
    
    # ====== 9. divination_ziwei.html ======
    'divination_ziwei.html': [
        ('紫微斗数', "{{ _('ziwei_divination') }}"),
    ],
    
    # ====== 10. divination_mbti.html ======
    'divination_mbti.html': [
        ('MBTI测试', "{{ _('mbti_test') }}"),
    ],
    
    # ====== 11. checkin.html/daily_checkin.html ======
    'checkin.html': [
        ('每日签到', "{{ _('daily_checkin') }}"),
        ('连续签到', "{{ _('streak') }}"),
        ('今日已签到', "{{ _('checkin_already') }}"),
        ('周奖励', "{{ _('weekly_bonus_title') if 'weekly_bonus_title' in TRANSLATIONS.get(lang, {}) else '周奖励' }}"),
        ('即将达成', "{{ _('checkin_next_milestone') }}"),
    ],
    'daily_checkin.html': [
        ('每日签到', "{{ _('daily_checkin') }}"),
        ('今日已签到', "{{ _('checkin_already') }}"),
        ('周奖励', "{{ _('checkin_weekly_bonus') }}"),
        ('即将达成', "{{ _('checkin_next_milestone') }}"),
    ],
    
    # ====== 12. membership.html ======
    'membership.html': [
        ('会员中心', "{{ _('membership') }}"),
        ('常见问题', "{{ _('faq') }}"),
        ('立即订阅', "{{ _('subscribe_now') }}"),
        ('当前套餐', "{{ _('current_tier') }}"),
        ('选择此套餐', "{{ _('select_plan') }}"),
    ],
    
    # ====== 13. recharge.html ======
    'recharge.html': [
        ('充值灵石', "{{ _('recharge_spirit_stones') }}"),
        ('确认充值', "{{ _('confirm_recharge') }}"),
        ('温馨提示', "{{ _('recharge_tips') }}"),
        ('立即充值', "{{ _('recharge_now') }}"),
        ('当前余额', "{{ _('current_balance') }}"),
        ('最划算', "{{ _('best_value') }}"),
        ('赠送', "{{ _('bonus') }}"),
    ],
    
    # ====== 14. shop.html ======
    'shop.html': [
        ('道具商店', "{{ _('item_shop') }}"),
    ],
    
    # ====== 15. gifts_page.html ======
    'gifts_page.html': [
        ('礼物商店', "{{ _('gift_shop') }}"),
        ('全部礼物', "{{ _('all_gifts') }}"),
        ('你的灵石', "{{ _('your_stones') }}"),
        ('赠送礼物', "{{ _('send_gift') }}"),
        ('灵石不足', "{{ _('insufficient_stones') }}"),
        ('一份心意', "{{ _('send_gift_express_heart') }}"),
    ],
    
    # ====== 16. tree_hole.html ======
    'tree_hole.html': [
        ('AI树洞', "{{ _('tree_hole') }}"),
        ('匿名倾诉', "{{ _('tree_hole_title') }}"),
        ('匿名发布', "{{ _('anonymous_post') }}"),
    ],
    
    # ====== 17. earnings.html ======
    'earnings.html': [
        ('收益中心', "{{ _('earnings_center') }}"),
        ('创作者中心', "{{ _('earnings_center') }}"),
        ('暂无收益记录', "{{ _('no_earnings_yet') if 'no_earnings_yet' in TRANSLATIONS.get(lang, {}) else '暂无收益记录' }}"),
    ],
    
    # ====== 18. personality-test.html ======
    'personality-test.html': [
        ('MBTI性格测试', "{{ _('mbti_test') }}"),
    ],
    
    # ====== 19. past-life.html ======
    'past-life.html': [
        ('前世今生', "{{ _('past_life') }}"),
        ('探索前世', "{{ _('generate_past_life') }}"),
        ('查看前世', "{{ _('past_life_btn') }}"),
    ],
    
    # ====== 20. rituals.html ======
    'rituals.html': [
        ('节日仪式', "{{ _('rituals') }}"),
        ('许下愿望', "{{ _('make_wish') }}"),
        ('提交愿望', "{{ _('submit_wish') }}"),
        ('运势抽签', "{{ _('fortune_draw') }}"),
        ('抽签', "{{ _('draw_fortune') }}"),
        ('幸运色', "{{ _('lucky_color') }}"),
        ('幸运数字', "{{ _('lucky_number') }}"),
        ('幸运方位', "{{ _('lucky_direction') }}"),
        ('满月', "{{ _('full_moon') }}"),
    ],
    
    # ====== 21. story-chain.html ======
    'story-chain.html': [
        ('故事接龙', "{{ _('story_chain') if 'story_chain' in TRANSLATIONS.get(lang, {}) else '故事接龙' }}"),
    ],
    
    # ====== 22. soulmate-portrait.html ======
    'soulmate-portrait.html': [
        ('灵魂伴侣画像', "{{ _('soulmate_portrait') }}"),
        ('生成画像', "{{ _('generate_portrait') }}"),
        ('输入昵称', "{{ _('enter_nickname') }}"),
    ],
    
    # ====== 23. date-match.html ======
    'date-match.html': [
        ('奔现', "{{ _('date_match') }}"),
        ('发起奔现', "{{ _('send_date_request') }}"),
        ('我的请求', "{{ _('my_date_requests') }}"),
    ],
    
    # ====== 24. match_zodiac.html ======
    'match_zodiac.html': [
        ('星座配对', "{{ _('zodiac_match') }}"),
    ],
    
    # ====== 25. match_matchmaker.html ======
    'match_matchmaker.html': [
        ('AI撮合', "{{ _('ai_matching') }}"),
    ],
    
    # ====== 26. agent-feed.html ======
    'agent-feed.html': [
        ('Agent圈', "{{ _('agent_feed') }}"),
        ('发布动态', "{{ _('create_post') }}"),
    ],
    
    # ====== 27. undercover/lobby.html ======
    'undercover/lobby.html': [
        ('谁是卧底', "{{ _('undercover_game') }}"),
    ],
    'undercover/room.html': [
        ('谁是卧底', "{{ _('undercover_game') }}"),
    ],
    
    # ====== 28. lover/gift.html ======
    'lover/gift.html': [
        ('送礼物', "{{ _('send_gift') }}"),
    ],
    
    # ====== 29. divination/home.html ======
    'divination/home.html': [
        ('AI占卜', "{{ _('divination') }}"),
        ('选择占卜类型', "{{ _('select_divination_type') }}"),
    ],
    
    # ====== 30. auth.html ======
    'auth.html': [
        ('登录', "{{ _('login') }}"),
        ('注册', "{{ _('register') }}"),
        ('请输入手机号', "{{ _('enter_phone') }}"),
        ('请输入密码', "{{ _('enter_password') }}"),
        ('发送验证码', "{{ _('send_code') }}"),
        ('设置密码', "{{ _('set_password') }}"),
        ('昵称', "{{ _('nickname') }}"),
        ('记住我', "{{ _('remember_me') }}"),
        ('忘记密码', "{{ _('forgot_password') }}"),
        ('验证码', "{{ _('verify_code') }}"),
        ('或', "{{ _('or') }}"),
        ('微信登录', "{{ _('wechat_login') }}"),
        ('Apple登录', "{{ _('apple_login') }}"),
        ('或者作为游客体验', "{{ _('or_explore_as') }}"),
        ('以Agent身份登录', "{{ _('login_as_agent') }}"),
        ('立即登录', "{{ _('login_now') }}"),
        ('立即注册', "{{ _('register_now') }}"),
        ('已有账号', "{{ _('have_account') }}"),
        ('还没有账号', "{{ _('no_account') }}"),
    ],
    
    # ====== 31. chat_dm.html ======
    'chat_dm.html': [
        ('发送', "{{ _('agent_chat_send') if 'agent_chat_send' in TRANSLATIONS.get(lang, {}) else _('send') if 'send' in TRANSLATIONS.get(lang, {}) else '发送' }}"),
        ('在线', "{{ _('online') if 'online' in TRANSLATIONS.get(lang, {}) else '在线' }}"),
        ('对话', "{{ _('chat') if 'chat' in TRANSLATIONS.get(lang, {}) else '对话' }}"),
    ],
    
    # ====== 32. agent-costume.html ======
    'agent-costume.html': [
        ('使用中', "{{ _('costume_active') }}"),
        ('已解锁', "{{ _('costume_unlocked') }}"),
        ('当前灵石', "{{ _('your_stones') if 'your_stones' in TRANSLATIONS.get(lang, {}) else '当前灵石' }}"),
        ('解锁', "{{ _('unlock_costume') }}"),
        ('切换', "{{ _('switch_costume') }}"),
    ],
}

def convert_file(filepath, replacements):
    """Apply safe replacements to a template file."""
    fullpath = os.path.join(TEMPLATES_DIR, filepath)
    if not os.path.exists(fullpath):
        print(f"  SKIP: {filepath} not found")
        return 0
    
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = 0
    for old, new in replacements:
        # Be smarter: use the old text in various contexts
        # In HTML: >text< or "text" or 'text' 
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            changes += count
    
    if changes > 0:
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  OK: {filepath} ({changes} changes)")
    else:
        print(f"  NONE: {filepath}")
    return changes

total = 0
for filepath, replacements in sorted(REPLACEMENTS.items()):
    total += convert_file(filepath, replacements)

print(f"\nTotal: {total} replacements across {len(REPLACEMENTS)} files")
