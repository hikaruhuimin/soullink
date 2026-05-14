#!/usr/bin/env python3
"""Ultra-simple batch converter: replace Chinese text with _() calls."""
import os

TDIR = '/tmp/soullink/templates'

REPLACEMENTS = [
    # index.html
    ('index.html', '三大温暖体验', "{{ _('warm_experiences') if 'warm_experiences' in TRANSLATIONS.get(lang, {}) else '三大温暖体验' }}"),
    
    # agents_square.html
    ('agents_square.html', 'Agent广场', "{{ _('agent_square') }}"),
    ('agents_square.html', '人类', "{{ _('humans') }}"),
    ('agents_square.html', '全部', "{{ _('all') }}"),
    ('agents_square.html', '热门', "{{ _('hot') }}"),
    ('agents_square.html', '最新', "{{ _('new') }}"),
    
    # checkin.html
    ('checkin.html', '每日签到', "{{ _('daily_checkin') }}"),
    ('checkin.html', '连续签到', "{{ _('streak') }}"),
    ('checkin.html', '今日已签到', "{{ _('checkin_already') }}"),
    ('checkin.html', '周奖励', "{{ _('checkin_weekly_bonus') }}"),
    ('checkin.html', '即将达成', "{{ _('checkin_next_milestone') }}"),
    ('checkin.html', '请先登录', "{{ _('login_required') }}"),
    
    # daily_checkin.html
    ('daily_checkin.html', '每日签到', "{{ _('daily_checkin') }}"),
    ('daily_checkin.html', '今日已签到', "{{ _('checkin_already') }}"),
    ('daily_checkin.html', '周奖励', "{{ _('checkin_weekly_bonus') }}"),
    
    # divination_dream.html
    ('divination_dream.html', 'AI解梦', "{{ _('dream_divination') }}"),
    
    # divination_iching.html
    ('divination_iching.html', '易经六爻', "{{ _('iching_divination') }}"),
    
    # divination_omikuji.html
    ('divination_omikuji.html', 'おみくじ', "{{ _('omikuji_divination') }}"),
    ('divination_omikuji.html', '抽一支签', "{{ _('omikuji_draw') }}"),
    
    # divination_ziwei.html
    ('divination_ziwei.html', '紫微斗数', "{{ _('ziwei_divination') }}"),
    
    # divination_mbti.html
    ('divination_mbti.html', 'MBTI测试', "{{ _('mbti_test') }}"),
    ('divination_mbti.html', 'MBTI性格测试', "{{ _('mbti_test') }}"),
    
    # membership.html
    ('membership.html', '会员中心', "{{ _('membership') }}"),
    ('membership.html', '常见问题', "{{ _('faq') }}"),
    ('membership.html', '立即订阅', "{{ _('subscribe_now') }}"),
    ('membership.html', '当前套餐', "{{ _('current_tier') }}"),
    ('membership.html', '选择此套餐', "{{ _('select_plan') }}"),
    
    # recharge.html
    ('recharge.html', '充值灵石', "{{ _('recharge_spirit_stones') }}"),
    ('recharge.html', '确认充值', "{{ _('confirm_recharge') }}"),
    ('recharge.html', '温馨提示', "{{ _('recharge_tips') }}"),
    ('recharge.html', '当前余额', "{{ _('current_balance') }}"),
    ('recharge.html', '立即充值', "{{ _('recharge_now') }}"),
    ('recharge.html', '最划算', "{{ _('best_value') }}"),
    ('recharge.html', '赠送', "{{ _('bonus') }}"),
    
    # shop.html
    ('shop.html', '道具商店', "{{ _('item_shop') }}"),
    
    # gifts_page.html
    ('gifts_page.html', '礼物商店', "{{ _('gift_shop') }}"),
    ('gifts_page.html', '全部礼物', "{{ _('all_gifts') }}"),
    ('gifts_page.html', '你的灵石', "{{ _('your_stones') }}"),
    ('gifts_page.html', '赠送礼物', "{{ _('send_gift') }}"),
    ('gifts_page.html', '灵石不足', "{{ _('insufficient_stones') }}"),
    ('gifts_page.html', '充值', "{{ _('recharge') }}"),
    ('gifts_page.html', '一份心意', "{{ _('send_gift_express_heart') }}"),
    
    # tree_hole.html
    ('tree_hole.html', 'AI树洞', "{{ _('tree_hole') }}"),
    ('tree_hole.html', '匿名发布', "{{ _('anonymous_post') }}"),
    ('tree_hole.html', '发布', "{{ _('publish') }}"),
    ('tree_hole.html', '匿名倾诉', "{{ _('tree_hole_title') }}"),
    
    # earnings.html
    ('earnings.html', '收益中心', "{{ _('earnings_center') }}"),
    ('earnings.html', '暂无收益记录', "{{ _('no_earnings_yet') }}"),
    
    # past-life.html
    ('past-life.html', '前世今生', "{{ _('past_life') }}"),
    ('past-life.html', '探索前世', "{{ _('generate_past_life') }}"),
    ('past-life.html', '输入昵称', "{{ _('enter_nickname') }}"),
    ('past-life.html', '选择生日', "{{ _('enter_birthday') }}"),
    ('past-life.html', '查看前世', "{{ _('past_life_btn') }}"),
    
    # rituals.html
    ('rituals.html', '节日仪式', "{{ _('rituals') }}"),
    ('rituals.html', '许下愿望', "{{ _('make_wish') }}"),
    ('rituals.html', '提交愿望', "{{ _('submit_wish') }}"),
    ('rituals.html', '运势抽签', "{{ _('fortune_draw') }}"),
    ('rituals.html', '幸运色', "{{ _('lucky_color') }}"),
    ('rituals.html', '幸运数字', "{{ _('lucky_number') }}"),
    ('rituals.html', '幸运方位', "{{ _('lucky_direction') }}"),
    ('rituals.html', '满月', "{{ _('full_moon') }}"),
    ('rituals.html', '抽签', "{{ _('draw_fortune') }}"),
    ('rituals.html', '当前节日', "{{ _('current_festival') }}"),
    ('rituals.html', '下一个节日', "{{ _('next_festival') }}"),
    
    # soulmate-portrait.html
    ('soulmate-portrait.html', '灵魂伴侣画像', "{{ _('soulmate_portrait') }}"),
    ('soulmate-portrait.html', '生成画像', "{{ _('generate_portrait') }}"),
    
    # date-match.html
    ('date-match.html', '奔现', "{{ _('date_match') }}"),
    ('date-match.html', '发起奔现', "{{ _('send_date_request') }}"),
    ('date-match.html', '我的请求', "{{ _('my_date_requests') }}"),
    ('date-match.html', '收到的邀请', "{{ _('received_requests') }}"),
    ('date-match.html', '发出的邀请', "{{ _('sent_requests') }}"),
    
    # match_zodiac.html
    ('match_zodiac.html', '星座配对', "{{ _('zodiac_match') }}"),
    
    # match_matchmaker.html
    ('match_matchmaker.html', 'AI撮合', "{{ _('ai_matching') }}"),
    
    # agent-feed.html
    ('agent-feed.html', 'Agent圈', "{{ _('agent_feed') }}"),
    ('agent-feed.html', '发布动态', "{{ _('create_post') }}"),
    ('agent-feed.html', '评论', "{{ _('comment') }}"),
    ('agent-feed.html', '点赞', "{{ _('like') }}"),
    
    # undercover
    ('undercover/lobby.html', '谁是卧底', "{{ _('undercover_game') }}"),
    ('undercover/room.html', '谁是卧底', "{{ _('undercover_game') }}"),
    
    # lover/gift.html
    ('lover/gift.html', '送礼物', "{{ _('send_gift') }}"),
    
    # divination/home.html
    ('divination/home.html', 'AI占卜', "{{ _('divination') }}"),
    ('divination/home.html', '选择占卜类型', "{{ _('select_divination_type') }}"),
    
    # auth.html - only do simple text replacements, not JS/Python code
    ('auth.html', '登录', "{{ _('login') }}"),
    ('auth.html', '注册', "{{ _('register') }}"),
    ('auth.html', '发送验证码', "{{ _('send_code') }}"),
    ('auth.html', '设置密码', "{{ _('set_password') }}"),
    ('auth.html', '昵称', "{{ _('nickname') }}"),
    ('auth.html', '记住我', "{{ _('remember_me') }}"),
    ('auth.html', '验证码', "{{ _('verify_code') }}"),
    ('auth.html', '微信登录', "{{ _('wechat_login') }}"),
    ('auth.html', 'Apple登录', "{{ _('apple_login') }}"),
    ('auth.html', '立即登录', "{{ _('login_now') }}"),
    ('auth.html', '立即注册', "{{ _('register_now') }}"),
    ('auth.html', '以Agent身份登录', "{{ _('login_as_agent') }}"),
    
    # agent-costume.html
    ('agent-costume.html', '使用中', "{{ _('costume_active') }}"),
    ('agent-costume.html', '已解锁', "{{ _('costume_unlocked') }}"),
    ('agent-costume.html', '解锁', "{{ _('unlock_costume') }}"),
    ('agent-costume.html', '切换', "{{ _('switch_costume') }}"),
    
    # story-chain.html
    ('story-chain.html', '故事接龙', "{{ _('story_chain') if 'story_chain' in TRANSLATIONS.get(lang, {}) else '故事接龙' }}"),
    
    # personality-test.html
    ('personality-test.html', 'MBTI性格测试', "{{ _('mbti_test') }}"),
    ('personality-test.html', 'MBTI测试', "{{ _('mbti_test') }}"),
    
    # chat_dm.html
    ('chat_dm.html', '发送', "{{ _('agent_chat_send') if 'agent_chat_send' in TRANSLATIONS.get(lang, {}) else _('send') if 'send' in TRANSLATIONS.get(lang, {}) else '发送' }}"),
    ('chat_dm.html', '在线', "{{ _('online') if 'online' in TRANSLATIONS.get(lang, {}) else '在线' }}"),
    
    # chat_room.html
    ('chat_room.html', '输入消息...', "{{ _('type_message') }}"),
    
    # chat_home.html
    ('chat_home.html', '聊天室', "{{ _('chat_room') }}"),
    
    # agent_profile.html
    ('agent_profile.html', '专长领域', "{{ _('specialty') if 'specialty' in TRANSLATIONS.get(lang, {}) else '专长领域' }}"),
    ('agent_profile.html', '关于我', "{{ _('about_me') }}"),
]

# Count stats
by_file = {}
for relpath, old, new in REPLACEMENTS:
    if relpath not in by_file:
        by_file[relpath] = []
    by_file[relpath].append((old, new))

total_changes = 0
for relpath, items in sorted(by_file.items()):
    fullpath = os.path.join(TDIR, relpath)
    if not os.path.exists(fullpath):
        print(f"  NOT FOUND: {relpath}")
        continue
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = 0
    for old, new in items:
        c = content.count(old)
        if c > 0:
            content = content.replace(old, new)
            changes += c
    
    if changes > 0:
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(content)
        total_changes += changes
        print(f"  OK: {relpath} ({changes} changes)")
    else:
        print(f"  NONE: {relpath}")

print(f"\nTotal: {total_changes} changes across {len(by_file)} files")
