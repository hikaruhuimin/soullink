#!/usr/bin/env python3
"""
One-pass template i18n conversion script.
Converts hardcoded Chinese text in templates to use _() function calls.
"""

import re
import os
import sys
sys.path.insert(0, '/tmp/soullink')

from i18n import TRANSLATIONS

# Mapping of Chinese text -> i18n key
# We'll find Chinese text in templates and replace them
TEMPLATES_DIR = '/tmp/soullink/templates'

# Specific template-by-template replacements
# Format: (file_path, old_text, new_text)
REPLACEMENTS = [
    # ===== base.html =====
    ('base.html', '{{ _(\'app_name_full\') }}', '{{ _(\\\'app_name_full\\\') }}'),  # already done
    
    # ===== index.html =====
    ('index.html', 'SoulLink 灵犀 - AI Agent社交平台', '{{ _(\\\'app_name\\\') }}'),
    ('index.html', '遇见你的灵魂伴侣', '{{ _(\\\'find_your_match\\\') }}'),
    ('index.html', '开始探索', '{{ _(\\\'start_exploring\\\') }}'),
    
    # ===== chat_home.html =====
    ('chat_home.html', '聊天室', '{{ _(\\\'chat_room\\\') }}'),
    
    # ===== chat_room.html =====
    ('chat_room.html', '输入消息...', '{{ _(\\\'type_message\\\') }}'),
    ('chat_room.html', '发送', '{{ _(\\\'agent_chat_send\\\') }}'),
    
    # ===== agents_square.html =====
    ('agents_square.html', 'Agent广场', '{{ _(\\\'agent_square\\\') }}'),
    
    # ===== agent_profile.html =====
    ('agent_profile.html', '关于我', '{{ _(\\\'about_me\\\') }}'),
    
    # ===== divination sections =====
    ('divination_dream.html', 'AI解梦', '{{ _(\\\'dream_divination\\\') }}'),
    ('divination_iching.html', '易经六爻', '{{ _(\\\'iching_divination\\\') }}'),
    ('divination_omikuji.html', 'おみくじ', '{{ _(\\\'omikuji_divination\\\') }}'),
    ('divination_ziwei.html', '紫微斗数', '{{ _(\\\'ziwei_divination\\\') }}'),
    ('divination_mbti.html', 'MBTI测试', '{{ _(\\\'mbti_test\\\') }}'),
    
    # ===== checkin.html =====
    ('checkin.html', '每日签到', '{{ _(\\\'daily_checkin\\\') }}'),
    ('checkin.html', '签到', '{{ _(\\\'sign_in\\\') }}'),
    ('checkin.html', '已签到', '{{ _(\\\'signed_in\\\') }}'),
    ('checkin.html', '连续签到', '{{ _(\\\'streak\\\') }}'),
    
    # ===== membership.html =====
    ('membership.html', '会员中心', '{{ _(\\\'membership\\\') }}'),
    ('membership.html', '立即订阅', '{{ _(\\\'subscribe_now\\\') }}'),
    ('membership.html', '当前套餐', '{{ _(\\\'current_tier\\\') }}'),
    ('membership.html', '选择此套餐', '{{ _(\\\'select_plan\\\') }}'),
    ('membership.html', '常见问题', '{{ _(\\\'faq\\\') }}'),
    ('membership.html', '权益对比', '{{ _(\\\'benefit_comparison\\\') }}'),
    
    # ===== recharge.html =====
    ('recharge.html', '充值灵石', '{{ _(\\\'recharge_spirit_stones\\\') }}'),
    ('recharge.html', '当前余额', '{{ _(\\\'current_balance\\\') }}'),
    ('recharge.html', '确认充值', '{{ _(\\\'confirm_recharge\\\') }}'),
    ('recharge.html', '选择支付方式', '{{ _(\\\'select_payment_method\\\') }}'),
    ('recharge.html', '温馨提示', '{{ _(\\\'recharge_tips\\\') }}'),
    ('recharge.html', '立即充值', '{{ _(\\\'recharge_now\\\') }}'),
    
    # ===== shop.html =====
    ('shop.html', '道具商店', '{{ _(\\\'item_shop\\\') }}'),
    
    # ===== gifts_page.html =====
    ('gifts_page.html', '礼物商店', '{{ _(\\\'gift_shop\\\') }}'),
    ('gifts_page.html', '全部礼物', '{{ _(\\\'all_gifts\\\') }}'),
    ('gifts_page.html', '连续送礼奖励', '{{ _(\\\'consecutive_gift_rewards\\\') }}'),
    ('gifts_page.html', '你的灵石', '{{ _(\\\'your_stones\\\') }}'),
    ('gifts_page.html', '充值', '{{ _(\\\'recharge\\\') }}'),
    ('gifts_page.html', '赠送礼物', '{{ _(\\\'send_gift\\\') }}'),
    ('gifts_page.html', '灵石不足', '{{ _(\\\'insufficient_stones\\\') }}'),
    
    # ===== tree_hole.html =====
    ('tree_hole.html', 'AI树洞', '{{ _(\\\'tree_hole\\\') }}'),
    ('tree_hole.html', '匿名倾诉', '{{ _(\\\'anonymous_confession\\\') }}'),
    ('tree_hole.html', '写下你的心事...', '{{ _(\\\'secret_placeholder\\\') }}'),
    ('tree_hole.html', '匿名发布', '{{ _(\\\'anonymous_post\\\') }}'),
    ('tree_hole.html', '发布', '{{ _(\\\'publish\\\') }}'),
    ('tree_hole.html', 'AI温暖回复', '{{ _(\\\'ai_reply\\\') }}'),
    ('tree_hole.html', '赞', '{{ _(\\\'like\\\') }}'),
    ('tree_hole.html', '分享', '{{ _(\\\'share\\\') }}'),
    
    # ===== earnings.html =====
    ('earnings.html', '收益中心', '{{ _(\\\'earnings_center\\\') }}'),
    ('earnings.html', '聊天收益', '{{ _(\\\'chat_earnings\\\') }}'),
    ('earnings.html', '点赞收益', '{{ _(\\\'like_earnings\\\') }}'),
    ('earnings.html', '礼物收益', '{{ _(\\\'gift_earnings\\\') }}'),
    ('earnings.html', '提现', '{{ _(\\\'withdraw\\\') }}'),
    ('earnings.html', '每日任务', '{{ _(\\\'daily_tasks\\\') }}'),
    
    # ===== personality-test.html =====
    ('personality-test.html', 'MBTI性格测试', '{{ _(\\\'mbti_test\\\') }}'),
    
    # ===== past-life.html =====
    ('past-life.html', '前世今生', '{{ _(\\\'past_life\\\') }}'),
    ('past-life.html', '探索前世', '{{ _(\\\'generate_past_life\\\') }}'),
    ('past-life.html', '输入昵称', '{{ _(\\\'enter_nickname\\\') }}'),
    ('past-life.html', '选择生日', '{{ _(\\\'enter_birthday\\\') }}'),
    
    # ===== rituals.html =====
    ('rituals.html', '节日仪式', '{{ _(\\\'rituals\\\') }}'),
    ('rituals.html', '许下愿望', '{{ _(\\\'make_wish\\\') }}'),
    ('rituals.html', '抽签', '{{ _(\\\'draw_fortune\\\') }}'),
    ('rituals.html', '运势抽签', '{{ _(\\\'fortune_draw\\\') }}'),
    ('rituals.html', '幸运色', '{{ _(\\\'lucky_color\\\') }}'),
    ('rituals.html', '幸运数字', '{{ _(\\\'lucky_number\\\') }}'),
    ('rituals.html', '提交愿望', '{{ _(\\\'submit_wish\\\') }}'),
    
    # ===== story-chain.html =====
    ('story-chain.html', '故事接龙', 'Story Chain'),
    
    # ===== soulmate-portrait.html =====
    ('soulmate-portrait.html', '灵魂伴侣画像', '{{ _(\\\'soulmate_portrait\\\') }}'),
    ('soulmate-portrait.html', '生成画像', '{{ _(\\\'generate_portrait\\\') }}'),
    ('soulmate-portrait.html', '输入昵称', '{{ _(\\\'enter_nickname\\\') }}'),
    ('soulmate-portrait.html', '选择生日', '{{ _(\\\'enter_birthday\\\') }}'),
    
    # ===== date-match.html =====
    ('date-match.html', '奔现', '{{ _(\\\'date_match\\\') }}'),
    ('date-match.html', '发起奔现', '{{ _(\\\'send_date_request\\\') }}'),
    ('date-match.html', '我的请求', '{{ _(\\\'my_date_requests\\\') }}'),
    ('date-match.html', '发送奔现邀请', '{{ _(\\\'send_date_invite\\\') }}'),
    
    # ===== match_zodiac.html =====
    ('match_zodiac.html', '星座配对', '{{ _(\\\'zodiac_match\\\') }}'),
    
    # ===== match_matchmaker.html =====
    ('match_matchmaker.html', 'AI撮合', '{{ _(\\\'ai_matching\\\') }}'),
    
    # ===== agent-feed.html =====
    ('agent-feed.html', 'Agent圈', '{{ _(\\\'agent_feed\\\') }}'),
    ('agent-feed.html', '发布动态', '{{ _(\\\'create_post\\\') }}'),
    ('agent-feed.html', '评论', '{{ _(\\\'comment\\\') }}'),
    ('agent-feed.html', '点赞', '{{ _(\\\'like\\\') }}'),
    
    # ===== undercover/lobby.html =====
    ('undercover/lobby.html', '谁是卧底', '{{ _(\\\'undercover_game\\\') }}'),
    
    # ===== lover/gift.html =====
    ('lover/gift.html', '送礼物', '{{ _(\\\'send_gift\\\') }}'),
    ('lover/gift.html', '赠送礼物', '{{ _(\\\'send_gift\\\') }}'),
    ('lover/gift.html', '你的灵石', '{{ _(\\\'your_stones\\\') }}'),
    
    # ===== divination/home.html =====
    ('divination/home.html', 'AI占卜', '{{ _(\\\'divination\\\') }}'),
    ('divination/home.html', '选择占卜类型', '{{ _(\\\'select_divination_type\\\') }}'),
    ('divination/home.html', 'AI智能占卜', '{{ _(\\\'divination\\\') }}'),
]

def convert_template(filepath, replacements):
    """Apply replacements to a template file."""
    fullpath = os.path.join(TEMPLATES_DIR, filepath)
    if not os.path.exists(fullpath):
        print(f"  SKIP: {filepath} not found")
        return
    
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            changes += 1
    
    if changes > 0:
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  OK: {filepath} ({changes} changes)")
    else:
        print(f"  NONE: {filepath} (no changes made)")

# Group replacements by file
from collections import defaultdict
by_file = defaultdict(list)
for filepath, old, new in REPLACEMENTS:
    by_file[filepath].append((old, new))

print("Converting templates...")
for filepath, replacements in by_file.items():
    convert_template(filepath, replacements)

print("\nDone!")
