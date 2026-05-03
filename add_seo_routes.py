"""
Add SEO meta tag support to routes
This script adds dynamic SEO meta tags based on page type and language
"""

# Add this to app.py or create a separate SEO helper

SEO_TEMPLATES = {
    'home': {
        'zh': {
            'title': 'SoulLink灵犀 - AI占卜与灵魂伴侣匹配平台',
            'description': '灵犀AI占卜平台，融合塔罗牌、星座、MBTI测试与灵魂伴侣匹配。通过AI占卜探索命运，遇见与你命定契合的他/她。免费体验！',
            'keywords': 'AI占卜, 塔罗牌占卜, 星座配对, MBTI测试, AI红娘, 灵魂伴侣, 姻缘测试, AI恋爱, 灵犀',
        },
        'en': {
            'title': 'SoulLink - AI Fortune Telling & Soulmate Matching Platform',
            'description': 'Discover your cosmic soulmate through AI-powered tarot readings, zodiac compatibility, and MBTI-based matching. Free divination!',
            'keywords': 'AI tarot, AI fortune telling, zodiac compatibility, AI soulmate, MBTI dating, AI astrology',
        },
        'ja': {
            'title': 'SoulLink - AI占いとソウスメイトマッチングプラットフォーム',
            'description': 'タロット占いや星座、AI占いで運命のパートナーと出会う。東洋の神秘とAIが融合した新しい出会い体験。',
            'keywords': 'AI占い, タロットAI, 星座相性, ソウスメイト診断, AI恋愛占い',
        }
    },
    'divination': {
        'zh': {
            'title': 'AI占卜 - 塔罗牌、星座、MBTI命运解读 | SoulLink灵犀',
            'description': '灵犀AI占卜为您提供塔罗牌、星座运势、八字命理、MBTI人格测试等多元占卜服务。',
            'keywords': 'AI占卜, 塔罗牌占卜, 星座运势, MBTI测试, 免费占卜',
        },
        'en': {
            'title': 'AI Divination - Tarot, Horoscope, MBTI Readings | SoulLink',
            'description': 'AI-powered divination services including tarot readings, horoscope analysis, and MBTI personality tests.',
            'keywords': 'AI divination, tarot reading, horoscope, MBTI test, fortune telling',
        },
        'ja': {
            'title': 'AI占い - タロット、星座、MBTI運命診断 | SoulLink',
            'description': 'タロット占いや星座運勢、MBTI性格診断など多角的なAI占星サービス。',
            'keywords': 'AI占い, タロット占星, 星座運勢, MBTI診断',
        }
    },
    'tarot': {
        'zh': {
            'title': 'AI塔罗牌占卜 - 78张神秘塔罗牌解读 | SoulLink灵犀',
            'description': '灵犀AI塔罗牌占卜，智能解读78张塔罗牌含义，免费抽取今日塔罗牌！',
            'keywords': '塔罗牌占卜, AI塔罗, 今日塔罗, 免费塔罗',
        },
        'en': {
            'title': 'AI Tarot Reading - Mystical 78 Cards | SoulLink',
            'description': 'AI-powered tarot readings with interpretations of all 78 tarot cards. Free daily tarot draw!',
            'keywords': 'tarot reading, AI tarot, tarot meaning, daily tarot, free tarot',
        },
        'ja': {
            'title': 'AIタロット占い - 78枚の神秘的なカード | SoulLink',
            'description': '78枚のタロットカードをAIが解釈。今日のタロットカードを無料抽出！',
            'keywords': 'タロット占星, AIタロット, 今日のタロット',
        }
    },
    'horoscope': {
        'zh': {
            'title': '星座配对 - 十二星座爱情兼容性分析 | SoulLink灵犀',
            'description': '基于西洋占星术深度解读12星座间的爱情、友情、事业兼容性。',
            'keywords': '星座配对, 星座相性, 十二星座, 星座爱情',
        },
        'en': {
            'title': 'Zodiac Compatibility - 12 Zodiac Signs Analysis | SoulLink',
            'description': 'Zodiac compatibility analysis based on Western astrology for love, friendship, and career.',
            'keywords': 'zodiac compatibility, zodiac signs, astrology love, horoscope matching',
        },
        'ja': {
            'title': '星座相性 - 12星座の恋愛相性分析 | SoulLink',
            'description': '西洋占星術に基づく星座相性分析。',
            'keywords': '星座相性, 占星術恋愛',
        }
    },
    'mbti': {
        'zh': {
            'title': 'MBTI性格测试 - AI智能16型人格分析 | SoulLink灵犀',
            'description': 'AI智能分析你的16型人格特质，发现你的恋爱人格类型，匹配灵魂伴侣。',
            'keywords': 'MBTI测试, MBTI人格, 16型人格, 恋爱人格',
        },
        'en': {
            'title': 'MBTI Personality Test - AI 16 Types Analysis | SoulLink',
            'description': 'AI-powered MBTI personality test analyzing your 16 personality types.',
            'keywords': 'MBTI test, MBTI personality, 16 personality types, personality test',
        },
        'ja': {
            'title': 'MBTI性格診断 - AIが分析する16類人格 | SoulLink',
            'description': 'AIがあなたの16類人格を分析し、恋愛人格タイプを発見。',
            'keywords': 'MBTIテスト, MBTI人格, 16類人格',
        }
    },
    'auth': {
        'zh': {
            'title': '注册/登录 SoulLink灵犀',
            'description': '立即注册灵犀，开启你的AI占卜与灵魂伴侣探索之旅。',
            'keywords': '注册灵犀, 登录, SoulLink',
        },
        'en': {
            'title': 'Sign Up / Login SoulLink',
            'description': 'Sign up for SoulLink and start your AI divination and soulmate discovery journey.',
            'keywords': 'sign up SoulLink, login, registration',
        },
        'ja': {
            'title': 'SoulLinkに登録/ログイン',
            'description': 'SoulLinkに登録して、AI占星とソウスメイト探索の旅を始めよう。',
            'keywords': 'SoulLink登録, ログイン',
        }
    }
}

def get_seo_data(page_type, lang='zh'):
    """Get SEO data for a specific page and language"""
    lang = lang if lang in ['zh', 'en', 'ja'] else 'zh'
    seo = SEO_TEMPLATES.get(page_type, SEO_TEMPLATES['home'])
    return seo.get(lang, seo['zh'])

def generate_seo_meta_tags(page_type, lang='zh', base_url='https://soullink-cnz2.onrender.com'):
    """Generate HTML meta tags for SEO"""
    seo = get_seo_data(page_type, lang)
    
    og_image = f"{base_url}/static/images/og-image-{lang}.png"
    
    meta_tags = f'''
    <title>{seo['title']}</title>
    <meta name="description" content="{seo['description']}">
    <meta name="keywords" content="{seo['keywords']}">
    <meta property="og:title" content="{seo['title']}">
    <meta property="og:description" content="{seo['description']}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:url" content="{base_url}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{seo['title']}">
    <meta name="twitter:description" content="{seo['description']}">
    <meta name="twitter:image" content="{og_image}">
    '''
    return meta_tags

if __name__ == '__main__':
    # Test
    print(generate_seo_meta_tags('home', 'en'))
