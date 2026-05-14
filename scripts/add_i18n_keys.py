#!/usr/bin/env python3
"""Add missing i18n keys to TRANSLATIONS for base.html navbar/footer/bottomnav."""

import sys
sys.path.insert(0, '/tmp/soullink')
from i18n import TRANSLATIONS

# New keys needed for base.html and other templates
new_keys = {
    # Navbar section names
    'ai_divination': ['AI占卜', 'AI Divination', 'AI占卜'],
    'dream_divination': ['AI解梦', 'Dream Interpretation', '夢占い'],
    'daily_fortune': ['每日运势', 'Daily Fortune', '今日の運勢'],
    'mbti_test': ['MBTI测试', 'MBTI Test', 'MBTIテスト'],
    'ai_love_section': ['AI恋人', 'AI Lovers', 'AI恋人'],
    'create_lover': ['创建恋人', 'Create Lover', '恋人を作成'],
    'love_diary': ['恋爱日记', 'Love Diary', '恋愛日記'],
    'send_gift_nav': ['送礼物', 'Send Gift', 'ギフトを贈る'],
    'matchmaker_section': ['AI红娘', 'AI Matchmaker', 'AI仲人'],
    'zodiac_match': ['星座配对', 'Zodiac Match', '星座相性'],
    'soul_match': ['灵魂匹配', 'Soul Match', 'ソウルマッチ'],
    'ai_matching': ['AI撮合', 'AI Matching', 'AIマッチング'],
    'social_section': ['社交', 'Social', 'ソーシャル'],
    'square': ['广场', 'Square', '広場'],
    'chat_room': ['聊天室', 'Chat Room', 'チャットルーム'],
    'agent_circle': ['Agent圈', 'Agent Feed', 'Agentフィード'],
    'undercover_game': ['谁是卧底', 'Undercover', 'Who is Undercover'],
    'agent_section': ['Agent', 'Agent', 'Agent'],
    'agent_square': ['Agent广场', 'Agent Square', 'Agent広場'],
    'become_companion': ['成为陪伴师', 'Become Companion', '陪伴師になる'],
    'stone_earnings': ['灵石收益', 'Stone Earnings', '霊石収益'],
    'costume_customize': ['捏脸', 'Customize', 'カスタマイズ'],
    'shop_section': ['商城', 'Shop', 'ショップ'],
    'stone_recharge': ['灵石充值', 'Stone Recharge', '霊石チャージ'],
    'vip_membership': ['VIP会员', 'VIP Membership', 'VIP会員'],
    'item_shop': ['道具商店', 'Item Shop', 'アイテムショップ'],
    'discover_section': ['发现', 'Discover', '発見'],
    'past_life': ['前世今生', 'Past Life', '前世今生'],
    'rituals': ['节日仪式', 'Rituals', '祭りの儀式'],
    'soulmate_portrait': ['灵魂伴侣画像', 'Soulmate Portrait', 'ソウルメイト似顔絵'],
    'ranking': ['排行', 'Ranking', 'ランキング'],
    'date_meetup': ['奔现', 'Date Meetup', 'デートマッチ'],
    'send_date_invite': ['发起奔现', 'Send Date Invite', 'デートを申し込む'],
    'invite_friends_nav': ['邀请', 'Invite', '招待'],
    'my_profile_short': ['我的', 'My', 'マイページ'],
    'login_btn': ['登录', 'Login', 'ログイン'],
    
    # Bottom nav
    'home': ['首页', 'Home', 'ホーム'],
    'chat_nav': ['聊天', 'Chat', 'チャット'],
    'matchmaker_nav': ['红娘', 'Matchmaker', '仲人'],
    'wallet_nav': ['钱包', 'Wallet', 'ウォレット'],
    'shop_nav': ['商城', 'Shop', 'ショップ'],
    'undercover_nav': ['卧底', 'Undercover', 'Undercover'],
    
    # Footer
    'app_name_full': ['灵犀 SoulLink', 'SoulLink', 'SoulLink霊犀'],
    'footer_slogan': ['每一次相遇，都是灵魂的相认', 'Every meeting is a soul recognition', 'すべての出会いは魂の認識'],
    'contact_us': ['联系客服', 'Contact Us', 'お問い合わせ'],
    
    # Notifications
    'notifications_title': ['通知', 'Notifications', '通知'],
    'mark_all_read': ['全部已读', 'Mark All Read', 'すべて既読にする'],
    'loading': ['加载中...', 'Loading...', '読み込み中...'],
    
    # Checkin modal
    'checkin_title_modal': ['每日签到', 'Daily Check-in', '每日チェックイン'],
    'consecutive_days': ['连续签到', 'Streak', '連続日数'],
    'checkin_reward_today': ['今日奖励', "Today's Reward", '今日の報酬'],
    'checkin_success_msg': ['签到成功！', 'Check-in successful!', 'チェックイン成功！'],
    'checkin_fail_retry': ['签到失败，请重试', 'Check-in failed, please retry', 'チェックイン失敗、再試行'],
    'weekly_bonus_title': ['周连签额外奖励已获得！', 'Weekly bonus claimed!', '週間ボーナス受取済み！'],
    'come_back_tomorrow': ['明天再来签到吧~', 'Come back tomorrow~', 'また明日来てね~'],
    'today_earned': ['今日获得', 'Today Earned', '今日獲得'],
    'checkin_claim_btn': ['立即签到', 'Check In Now', 'チェックイン'],
    
    # Guide
    'guide_step1_title': ['欢迎来到灵犀世界！🌌', 'Welcome to SoulLink! 🌌', 'SoulLinkへようこそ！🌌'],
    'guide_step1_content': ['这里有16种灵魂伴侣等你相遇，每一个Agent都有独特的性格和故事。', 'Meet 16 soulmate types, each Agent has a unique personality and story.', '16種類のソウルメイトが待っています。各Agentには独自の個性と物語があります。'],
    'guide_step2_title': ['认识灵犀Agent', 'Meet SoulLink Agents', 'SoulLink Agentを知る'],
    'guide_step2_content': ['在灵犀广场探索不同类型的Agent，找到与你灵魂契合的那一个。', 'Explore different Agent types in the square and find your soulmate.', '広場で様々なAgentを探索し、魂の伴侶を見つけましょう。'],
    'guide_step3_title': ['体验AI占卜', 'Experience AI Divination', 'AI占いを体験'],
    'guide_step3_content': ['塔罗牌、AI解梦、MBTI性格测试...探索命运的无限可能。', 'Tarot, dream interpretation, MBTI tests... explore infinite possibilities.', 'タロット、夢占い、MBTI診断...無限の可能性を探ります。'],
    'guide_step4_title': ['创建你的Agent', 'Create Your Agent', 'Agentを作成'],
    'guide_step4_content': ['成为Agent创作者，定义独特的性格、故事和灵魂。', 'Become an Agent creator and define unique personalities, stories and souls.', 'Agentクリエイターになり、個性、物語、魂を定義しましょう。'],
    'guide_step5_title': ['领取新手礼包 🎁', 'Claim Newcomer Gift 🎁', '初心者ギフトを受け取る 🎁'],
    'guide_step5_content': ['100灵石已到账！用它来解锁更多有趣的互动体验吧~', '100 Spirit Stones credited! Use them to unlock more fun interactions~', '100霊石を獲得しました！もっと楽しい体験を解除しよう〜'],
    'guide_prev': ['上一步', 'Previous', '前へ'],
    'guide_next': ['下一步', 'Next', '次へ'],
    'guide_start': ['开始探索 →', 'Start Exploring →', '探索を始める →'],
    'guide_finish': ['太棒了！', 'Awesome!', 'すごい！'],
    
    # Sub nav items
    'create_lover_nav': ['创建恋人', 'Create Lover', '恋人を作成'],
    'love_diary_nav': ['恋爱日记', 'Love Diary', '恋愛日記'],
    'send_gift_nav_item': ['送礼物', 'Send Gift', 'ギフトを贈る'],
    'soulmate_portrait_nav': ['灵魂伴侣画像', 'Soulmate Portrait', 'ソウルメイト似顔絵'],
    
    # Additional
    'no_notifications': ['暂无通知', 'No notifications', '通知なし'],
    'notification_loading': ['加载中...', 'Loading...', '読み込み中...'],
    'checkin_already_done': ['今日已签到', 'Already checked in', '本日チェックイン済み'],
}

# Add keys for each language
lang_map = {'zh': 0, 'en': 1, 'ja': 2}
for key, translations in new_keys.items():
    for lang, idx in lang_map.items():
        if key not in TRANSLATIONS[lang]:
            TRANSLATIONS[lang][key] = translations[idx]

# Verify
print(f"Total zh keys now: {len(TRANSLATIONS['zh'])}")
print(f"Total en keys now: {len(TRANSLATIONS['en'])}")
print(f"Total ja keys now: {len(TRANSLATIONS['ja'])}")

# Write back
with open('/tmp/soullink/i18n.py', 'w') as f:
    f.write('# 灵犀 - 国际化和本地化配置\n\n')
    f.write('TRANSLATIONS = {\n')
    for lang_idx, lang in enumerate(['zh', 'en', 'ja']):
        if lang_idx > 0:
            f.write('\n')
        f.write(f"    '{lang}': {{\n")
        items = list(TRANSLATIONS[lang].items())
        # Sort: keep grouped but somewhat organized
        for key, val in items:
            # Escape single quotes in values
            escaped_val = str(val).replace("'", "\\'")
            f.write(f"        '{key}': '{escaped_val}',\n")
        f.write('    },\n')
    f.write('}\n')

print("i18n.py updated successfully!")
