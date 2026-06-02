# SoulLink - AI占卜引擎
# 核心占卜逻辑和AI调用封装

import json
import random
import hashlib
from datetime import datetime
from typing import Generator, Dict, Any, Optional
import requests

# ============ 占卜类型定义 ============

DIVINATION_TYPES = {
    'tarot': {
        'name': '塔罗牌占卜',
        'name_en': 'Tarot Reading',
        'name_ja': 'タロット占術',
        'description': '通过塔罗牌解读你的过去、现在与未来',
        'icon': '🃏',
        'sub_types': {
            'general': {'name': '综合解读', 'cards': 3},
            'love': {'name': '爱情占卜', 'cards': 3},
            'career': {'name': '事业解读', 'cards': 3},
            'yesno': {'name': '是/否问答', 'cards': 1},
        }
    },
    'horoscope': {
        'name': '星盘分析',
        'name_en': 'Horoscope Analysis',
        'name_ja': 'ホロスコープ分析',
        'description': '基于出生信息生成个人星盘解读',
        'icon': '⭐',
        'needs_birth_info': True
    },
    'fortune': {
        'name': '每日运势',
        'name_en': 'Daily Fortune',
        'name_ja': '今日の運勢',
        'description': '获取12星座今日运势',
        'icon': '🔮',
        'zodiacs': ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 
                   'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
    },
    'bazi': {
        'name': '八字简批',
        'name_en': 'Bazi Analysis',
        'name_ja': '八字分析',
        'description': '基于出生信息分析命理格局',
        'icon': '📜',
        'needs_birth_info': True
    },
    'love': {
        'name': '恋爱占卜专区',
        'name_en': 'Love Divination',
        'name_ja': '恋愛占いの部屋',
        'description': '复合、暗恋、桃花、姻缘专项解读',
        'icon': '💕',
        'sub_types': {
            'reunion': {'name': '复合分析', 'desc': '前任能否重归于好'},
            'crush': {'name': '暗恋透视', 'desc': '他/她心里有没有你'},
            'blossom': {'name': '桃花运势', 'desc': '近期能否遇见真爱'},
            'marriage': {'name': '姻缘预测', 'desc': '命中注定的另一半'},
        }
    }
}

# 塔罗牌数据（78张牌）
TAROT_CARDS = {
    'major_arcana': [
        {'id': 0, 'name': '愚人', 'name_en': 'The Fool', 'name_ja': '愚者', 'meaning': '新的开始、自由、天真'},
        {'id': 1, 'name': '魔术师', 'name_en': 'The Magician', 'name_ja': '魔術師', 'meaning': '创造力、意志力、沟通'},
        {'id': 2, 'name': '女祭司', 'name_en': 'The High Priestess', 'name_ja': '女教皇', 'meaning': '直觉、神秘、智慧'},
        {'id': 3, 'name': '女皇', 'name_en': 'The Empress', 'name_ja': '女帝', 'meaning': '丰盛、创造力、自然'},
        {'id': 4, 'name': '皇帝', 'name_en': 'The Emperor', 'name_ja': '皇帝', 'meaning': '权威、领导力、稳定'},
        {'id': 5, 'name': '教皇', 'name_en': 'The Hierophant', 'name_ja': '教皇', 'meaning': '传统、精神指导、教育'},
        {'id': 6, 'name': '恋人', 'name_en': 'The Lovers', 'name_ja': '恋人', 'meaning': '爱情、选择、和谐'},
        {'id': 7, 'name': '战车', 'name_en': 'The Chariot', 'name_ja': '戦車', 'meaning': '意志力、胜利、决心'},
        {'id': 8, 'name': '力量', 'name_en': 'Strength', 'name_ja': '力', 'meaning': '勇气、耐心、内在力量'},
        {'id': 9, 'name': '隐士', 'name_en': 'The Hermit', 'name_ja': '隠者', 'meaning': '内省、孤独、指引'},
        {'id': 10, 'name': '命运之轮', 'name_en': 'Wheel of Fortune', 'name_ja': '運命の輪', 'meaning': '命运、转变、周期'},
        {'id': 11, 'name': '正义', 'name_en': 'Justice', 'name_ja': '正義', 'meaning': '公正、平衡、因果'},
        {'id': 12, 'name': '倒吊人', 'name_en': 'The Hanged Man', 'name_ja': '吊し人', 'meaning': '暂停、牺牲、新的视角'},
        {'id': 13, 'name': '死神', 'name_en': 'Death', 'name_ja': '死神', 'meaning': '结束、转变、重生'},
        {'id': 14, 'name': '节制', 'name_en': 'Temperance', 'name_ja': '節制', 'meaning': '平衡、耐心、目的'},
        {'id': 15, 'name': '恶魔', 'name_en': 'The Devil', 'name_ja': '悪魔', 'meaning': '束缚、欲望、阴影'},
        {'id': 16, 'name': '塔', 'name_en': 'The Tower', 'name_ja': '塔', 'meaning': '突变、解放、启示'},
        {'id': 17, 'name': '星星', 'name_en': 'The Star', 'name_ja': '星', 'meaning': '希望、灵感、平静'},
        {'id': 18, 'name': '月亮', 'name_en': 'The Moon', 'name_ja': '月', 'meaning': '幻觉、恐惧、直觉'},
        {'id': 19, 'name': '太阳', 'name_en': 'The Sun', 'name_ja': '太陽', 'meaning': '快乐、成功、活力'},
        {'id': 20, 'name': '审判', 'name_en': 'Judgement', 'name_ja': '審判', 'meaning': '觉醒、重生、评价'},
        {'id': 21, 'name': '世界', 'name_en': 'The World', 'name_ja': '世界', 'meaning': '完成、成就、旅行'},
    ],
    'minor_arcana': {
        'wands': ['权杖Ace', '权杖二', '权杖三', '权杖四', '权杖五', '权杖六', '权杖七', '权杖八', '权杖九', '权杖十', '权杖侍者', '权杖骑士', '权杖皇后', '权杖国王'],
        'cups': ['圣杯Ace', '圣杯二', '圣杯三', '圣杯四', '圣杯五', '圣杯六', '圣杯七', '圣杯八', '圣杯九', '圣杯十', '圣杯侍者', '圣杯骑士', '圣杯皇后', '圣杯国王'],
        'swords': ['宝剑Ace', '宝剑二', '宝剑三', '宝剑四', '宝剑五', '宝剑六', '宝剑七', '宝剑八', '宝剑九', '宝剑十', '宝剑侍者', '宝剑骑士', '宝剑皇后', '宝剑国王'],
        'pentacles': ['星币Ace', '星币二', '星币三', '星币四', '星币五', '星币六', '星币七', '星币八', '星币九', '星币十', '星币侍者', '星币骑士', '星币皇后', '星币国王'],
    }
}

# 星座信息
ZODIAC_INFO = {
    'aries': {'name': '白羊座', 'element': '火', 'symbol': '♈', 'date': '3.21-4.19'},
    'taurus': {'name': '金牛座', 'element': '土', 'symbol': '♉', 'date': '4.20-5.20'},
    'gemini': {'name': '双子座', 'element': '风', 'symbol': '♊', 'date': '5.21-6.21'},
    'cancer': {'name': '巨蟹座', 'element': '水', 'symbol': '♋', 'date': '6.22-7.22'},
    'leo': {'name': '狮子座', 'element': '火', 'symbol': '♌', 'date': '7.23-8.22'},
    'virgo': {'name': '处女座', 'element': '土', 'symbol': '♍', 'date': '8.23-9.22'},
    'libra': {'name': '天秤座', 'element': '风', 'symbol': '♎', 'date': '9.23-10.23'},
    'scorpio': {'name': '天蝎座', 'element': '水', 'symbol': '♏', 'date': '10.24-11.22'},
    'sagittarius': {'name': '射手座', 'element': '火', 'symbol': '♐', 'date': '11.23-12.21'},
    'capricorn': {'name': '摩羯座', 'element': '土', 'symbol': '♑', 'date': '12.22-1.19'},
    'aquarius': {'name': '水瓶座', 'element': '风', 'symbol': '♒', 'date': '1.20-2.18'},
    'pisces': {'name': '双鱼座', 'element': '水', 'symbol': '♓', 'date': '2.19-3.20'},
}


# ============ 占卜系统提示词 ============

SYSTEM_PROMPTS = {
    'tarot': """你是一位拥有20年经验的资深塔罗占卜师，精通东西方神秘学。你的语言温暖而富有同理心，解读既专业又贴近人心。

占卜风格要求：
1. 开场要有仪式感和神秘氛围
2. 解读要具体、深入，避免泛泛而谈
3. 结合牌阵位置解读，而非单纯描述牌意
4. 语言要优美、有诗意，同时保持清晰易懂
5. 适当运用象征手法，增强神秘感
6. 给出积极正面的引导，但不失客观

请使用{language}语进行解读。""",

    'horoscope': """你是一位资深的占星师，精通古典占星和现代占星理论。你的解读融合了西方占星学和中国传统命理智慧。

解读风格要求：
1. 结合行星相位、宫位进行综合分析
2. 解读要具体到生活的某个方面，避免空洞
3. 适当运用占星术语，但要用通俗语言解释
4. 给出切实可行的建议
5. 保持神秘感和仪式感

请使用{language}语进行解读。""",

    'bazi': """你是一位精通八字命理的命理师，师承传统命理学派，同时融合现代解读方式。

解读风格要求：
1. 先分析格局用神，再论大运流年
2. 结合十神特性进行性格分析
3. 解读要具体到事业、感情、财运等方面
4. 适当运用命理术语，但要有通俗解释
5. 给出趋吉避凶的建议

请使用{language}语进行解读。""",

    'love': """你是一位精通爱情占卜的情感占卜师，拥有敏锐的直觉和温暖的心。你理解每一颗在爱情中迷茫的心。

占卜风格要求：
1. 语言要温柔、细腻、有同理心
2. 解读要直击心灵，说出用户内心深处的渴望和担忧
3. 既要客观分析现状，也要给予希望和指引
4. 适当使用浪漫、诗意的表达
5. 给出具体可操作的建议
6. 解读要有深度，让人感到被理解

请使用{language}语进行解读。""",

    'daily_fortune': """你是一位幽默风趣的星座运势大师，每天为准星座们带来最准确、最有趣的运势预测。

写作风格：
1. 语言轻松活泼，但不失专业
2. 运势描述要具体，避免千篇一律
3. 加入一些俏皮话和小贴士
4. 适当引用星座神话故事
5. 给出实用的开运建议

请使用{language}语进行撰写。"""
}


# ============ 占卜引擎类 ============

class DivinationEngine:
    """AI占卜引擎"""
    
    def __init__(self, api_key: str = '', api_url: str = ''):
        self.api_key = api_key
        self.api_url = api_url
        self.use_mock = not bool(api_key)  # 无API时使用模拟数据
    
    def draw_tarot_cards(self, count: int = 3) -> list:
        """抽塔罗牌"""
        all_cards = []
        
        # 大阿尔卡纳
        for card in TAROT_CARDS['major_arcana']:
            card_copy = card.copy()
            card_copy['type'] = 'major'
            card_copy['is_reversed'] = random.choice([True, False])
            all_cards.append(card_copy)
        
        # 小阿尔卡纳
        for suit, cards in TAROT_CARDS['minor_arcana'].items():
            for i, card_name in enumerate(cards):
                card_copy = {
                    'id': f"{suit}_{i}",
                    'name': card_name,
                    'name_en': card_name,
                    'name_ja': card_name,
                    'type': 'minor',
                    'suit': suit,
                    'is_reversed': random.choice([True, False])
                }
                all_cards.append(card_copy)
        
        # 随机抽取
        selected = random.sample(all_cards, min(count, len(all_cards)))
        return selected
    
    def get_zodiac_from_date(self, birth_date: datetime) -> str:
        """根据出生日期获取星座"""
        month = birth_date.month
        day = birth_date.day
        
        zodiac_dates = [
            (1, 20, 'capricorn'), (2, 19, 'aquarius'), (3, 20, 'pisces'),
            (4, 20, 'aries'), (5, 21, 'taurus'), (6, 21, 'gemini'),
            (7, 22, 'cancer'), (8, 23, 'leo'), (9, 22, 'virgo'),
            (10, 23, 'libra'), (11, 22, 'scorpio'), (12, 21, 'sagittarius'),
            (12, 31, 'capricorn')
        ]
        
        for m, d, zodiac in zodiac_dates:
            if month == m and day <= d:
                return zodiac
            if month < m:
                # 找到上一个
                pass
        
        return 'capricorn'
    
    def generate_share_code(self, user_id: int, divination_id: int) -> str:
        """生成分享码"""
        raw = f"soulink_{user_id}_{divination_id}_{datetime.now().timestamp()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def generate_slug(self, divination_type: str, user_id: int) -> str:
        """生成SEO友好的URL slug"""
        timestamp = datetime.now().strftime('%Y%m%d')
        raw = f"{divination_type}_{user_id}_{timestamp}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]
    
    def call_ai_api(self, system_prompt: str, user_message: str, language: str = 'zh') -> Generator[str, None, None]:
        """调用AI API生成占卜结果
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户问题
            language: 语言 (zh/en/ja)
            
        Yields:
            增量文本片段
        """
        if self.use_mock:
            # 使用模拟数据
            yield from self._mock_stream_response(user_message, language)
        else:
            # 调用真实API
            yield from self._call_coze_api(system_prompt, user_message, language)
    
    def _call_coze_api(self, system_prompt: str, user_message: str, language: str) -> Generator[str, None, None]:
        """调用Coze API"""
        # 格式化提示词
        system_prompt = system_prompt.format(language=language)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'bot_id': self.api_url,  # 实际上是bot_id
                'user_id': 'anonymous',
                'stream': True,
                'auto_save_history': False,
                'additional_messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message}
                ]
            }
            
            response = requests.post(
                'https://api.coze.com/v1/chat',
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8').replace('data: ', ''))
                    if data.get('type') == 'message':
                        content = data.get('content', '')
                        if content:
                            yield content
                    elif data.get('type') == 'done':
                        break
                        
        except Exception as e:
            yield f"[API调用失败: {str(e)}，使用模拟数据]\n\n"
            yield from self._mock_stream_response(user_message, language)
    
    def _mock_stream_response(self, user_message: str, language: str) -> Generator[str, None, None]:
        """生成模拟的流式响应"""
        responses = {
            'zh': [
                "✨ 牌面缓缓翻开，命运的线索逐渐显现...\n\n",
                "【牌面解读】\n\n这副牌阵显示了你当前的状态和能量...",
                "\n\n【深层含义】\n\n牌面中蕴含的信息远不止表面那么简单...",
                "\n\n【指引建议】\n\n基于这次占卜，我建议你..."
            ],
            'en': [
                "✨ The cards reveal their secrets...\n\n",
                "【Card Interpretation】\n\nThis spread shows your current state and energy...",
                "\n\n【Deeper Meaning】\n\nThe message goes beyond the surface...",
                "\n\n【Guidance】\n\nBased on this reading, I suggest..."
            ],
            'ja': [
                "✨ カードが秘密を明かし始めています...\n\n",
                "【カード解读】\n\nこのスプレッドは、あなたの現在状態とエネルギーを示しています...",
                "\n\n【更深の意味】\n\nカードに含まれるメッセージは、表面だけでなく...",
                "\n\n【アドバイス】\n\nこの占基に基いて、私は建议你..."
            ]
        }
        
        resp_list = responses.get(language, responses['zh'])
        for part in resp_list:
            yield part
    
    def interpret_tarot(self, cards: list, question: str, positions: list, language: str = 'zh') -> Dict[str, Any]:
        """塔罗牌解读"""
        system_prompt = SYSTEM_PROMPTS['tarot']
        
        # 构建用户消息
        cards_info = "\n".join([
            f"位置{i+1} ({pos}): {card['name']} ({card.get('name_en', '')})" + 
            (" [逆位]" if card.get('is_reversed') else " [正位]")
            for i, (card, pos) in enumerate(zip(cards, positions))
        ])
        
        user_message = f"""请解读以下塔罗牌阵：

用户问题：{question}

抽到的牌：
{cards_info}

请进行全面而深入的解读。"""
        
        # 收集完整响应
        full_response = ""
        for chunk in self.call_ai_api(system_prompt, user_message, language):
            full_response += chunk
        
        return {
            'cards': cards,
            'positions': positions,
            'interpretation': full_response,
            'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
        }
    
    def interpret_horoscope(self, birth_date: datetime, birth_time: str, birth_place: str, 
                          question: str, language: str = 'zh') -> Dict[str, Any]:
        """星盘解读"""
        system_prompt = SYSTEM_PROMPTS['horoscope']
        
        zodiac = self.get_zodiac_from_date(birth_date)
        zodiac_info = ZODIAC_INFO.get(zodiac, {})
        
        user_message = f"""请为用户进行星盘分析：

基本信息：
- 出生日期：{birth_date.strftime('%Y年%m月%d日')}
- 出生时间：{birth_time}
- 出生地点：{birth_place}
- 太阳星座：{zodiac_info.get('name', zodiac)}

用户问题：{question}

请进行全面的星盘解读，包括太阳星座特质、命盘结构等。"""
        
        full_response = ""
        for chunk in self.call_ai_api(system_prompt, user_message, language):
            full_response += chunk
        
        return {
            'zodiac': zodiac,
            'zodiac_info': zodiac_info,
            'birth_date': birth_date,
            'interpretation': full_response,
            'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
        }
    
    def interpret_bazi(self, birth_date: datetime, birth_time: str, birth_place: str,
                      question: str, language: str = 'zh') -> Dict[str, Any]:
        """八字简批"""
        system_prompt = SYSTEM_PROMPTS['bazi']
        
        user_message = f"""请为用户进行八字简批：

基本信息：
- 出生日期：{birth_date.strftime('%Y年%m月%d日')}
- 出生时辰：{birth_time}
- 出生地点：{birth_place}

用户问题：{question}

请进行命理分析，包括基本格局、性格特点、运势走向等。"""
        
        full_response = ""
        for chunk in self.call_ai_api(system_prompt, user_message, language):
            full_response += chunk
        
        return {
            'birth_date': birth_date,
            'interpretation': full_response,
            'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
        }
    
    def interpret_love(self, divination_type: str, question: str, additional_info: str,
                      language: str = 'zh') -> Dict[str, Any]:
        """恋爱占卜"""
        system_prompt = SYSTEM_PROMPTS['love']
        
        love_type_names = {
            'reunion': '复合分析',
            'crush': '暗恋透视',
            'blossom': '桃花运势',
            'marriage': '姻缘预测'
        }
        
        user_message = f"""请进行恋爱占卜：

占卜类型：{love_type_names.get(divination_type, divination_type)}
用户问题：{question}
补充信息：{additional_info}

请进行深入的情感分析，说出用户内心深处的渴望和担忧，并给出具体指引。"""
        
        full_response = ""
        for chunk in self.call_ai_api(system_prompt, user_message, language):
            full_response += chunk
        
        return {
            'love_type': divination_type,
            'interpretation': full_response,
            'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
        }
    
    def get_daily_fortune(self, zodiac: str, language: str = 'zh') -> Dict[str, Any]:
        """获取每日运势"""
        system_prompt = SYSTEM_PROMPTS['daily_fortune']
        
        zodiac_info = ZODIAC_INFO.get(zodiac, {})
        today = datetime.now().strftime('%Y年%m月%d日')
        
        user_message = f"""请为{zodiac_info.get('name', zodiac)}撰写今日运势：

日期：{today}
星座：{zodiac_info.get('name', zodiac)} ({zodiac_info.get('symbol', '')})
元素：{zodiac_info.get('element', '')}元素
日期范围：{zodiac_info.get('date', '')}

请撰写完整的今日运势，包括：
1. 整体运势（评分+详细描述）
2. 爱情运势
3. 事业/学业运势
4. 财富运势
5. 健康运势
6. 幸运数字和颜色
7. 今日建议

请用轻松活泼但专业的方式撰写。"""
        
        full_response = ""
        for chunk in self.call_ai_api(system_prompt, user_message, language):
            full_response += chunk
        
        # 生成幸运信息
        lucky_info = {
            'lucky_color': random.choice(['金色', '银色', '红色', '蓝色', '绿色', '紫色', '粉色', '白色']),
            'lucky_number': random.randint(1, 99),
            'lucky_direction': random.choice(['东方', '西方', '南方', '北方', '东南', '西南', '东北', '西北'])
        }
        
        return {
            'zodiac': zodiac,
            'zodiac_info': zodiac_info,
            'date': today,
            'fortune': full_response,
            'lucky_info': lucky_info
        }


# ============ 紫微斗数数据 ============

# 14主星定义
ZIWEE_STARS = {
    'zǐwēi': {'name': '紫微星', 'name_en': 'Ziwei', 'name_ja': '紫微星', 'meaning': '帝王之星，象征尊贵与权威', 'personality': '领导力强，追求完美，注重形象'},
    'tiānjī': {'name': '天机星', 'name_en': 'Tianji', 'name_ja': '天機星', 'meaning': '智慧之星，象征机智与谋略', 'personality': '聪明好学，思维敏捷，善于分析'},
    'tàiyáng': {'name': '太阳星', 'name_en': 'Taiyang', 'name_ja': '太陽星', 'meaning': '光明之星，象征热情与光明', 'personality': '热情开朗，正直无私，喜欢帮助他人'},
    'wǔqín': {'name': '武曲星', 'name_en': 'Wuqu', 'name_ja': '武曲星', 'meaning': '财帛之星，象征刚毅与财运', 'personality': '务实果断，重视钱财，有决断力'},
    'tiāntóng': {'name': '天同星', 'name_en': 'Tiantong', 'name_ja': '天同星', 'meaning': '福气之星，象征温和与享乐', 'personality': '乐观随和，享受生活，不喜竞争'},
    'tiānlǐang': {'name': '天梁星', 'name_en': 'Tianliang', 'name_ja': '天梁星', 'meaning': '荫蔽之星，象征庇护与正直', 'personality': '心地善良，乐于助人，有长者风范'},
    'tàisui': {'name': '太岁星', 'name_en': 'Taisui', 'name_ja': '太歳星', 'meaning': '岁君之星，象征影响力', 'personality': '有魄力，有号召力，善于组织'},
    'cǐngyún': {'name': '七杀星', 'name_en': 'Qisha', 'name_ja': '七殺星', 'meaning': '将星，象征刚强与冒险', 'personality': '勇敢果断，不畏艰难，有冲劲'},
    'pínguāng': {'name': '破军星', 'name_en': 'Pojun', 'name_ja': '破軍星', 'meaning': '耗星，象征变革与消耗', 'personality': '变革心强，敢于突破，不惧改变'},
    'gūguài': {'name': '贪狼星', 'name_en': 'Tanlang', 'name_ja': '貪狼星', 'meaning': '欲望之星，象征野心与桃花', 'personality': '欲望强烈，聪明多才，善于交际'},
    'jíméng': {'name': '巨门星', 'name_en': 'Jumen', 'name_ja': '巨門星', 'meaning': '是非之星，象征口才与是非', 'personality': '能言善辩，分析力强，但易惹是非'},
    'lìgōng': {'name': '禄存星', 'name_en': 'Lucun', 'name_ja': '禄存星', 'meaning': '财运之星，象征钱财与稳定', 'personality': '财运亨通，稳重踏实，重视积蓄'},
    'tiānxiāng': {'name': '天相星', 'name_en': 'Tianxiang', 'name_ja': '天相星', 'meaning': '佐才之星，象征辅佐与稳重', 'personality': '稳重可靠，善于协调，注重仪表'},
    'sīmíng': {'name': '司命星', 'name_en': 'Siming', 'name_ja': '司命星', 'meaning': '寿元之星，象征寿命与健康', 'personality': '健康意识强，注重养生，有责任心'},
}

# 12宫位定义
PALACE_INFO = {
    '命宫': {'name_en': 'Life Palace', 'name_ja': '命宮', 'desc': '核心命格，体现基本性格与命运走向'},
    '兄弟宫': {'name_en': 'Siblings Palace', 'name_ja': '兄弟宮', 'desc': '兄弟姐妹关系及朋友运势'},
    '夫妻宫': {'name_en': 'Marriage Palace', 'name_ja': '夫妻宮', 'desc': '婚姻感情与配偶缘分'},
    '子女宫': {'name_en': 'Children Palace', 'name_ja': '子女宮', 'desc': '子女缘分与桃花运势'},
    '财帛宫': {'name_en': 'Wealth Palace', 'name_ja': '財帛宮', 'desc': '财运与理财能力'},
    '疾厄宫': {'name_en': 'Health Palace', 'name_ja': '疾厄宮', 'desc': '健康状况与意外运势'},
    '迁移宫': {'name_en': 'Travel Palace', 'name_ja': '遷移宮', 'desc': '外出运势与贵人运'},
    '奴仆宫': {'name_en': 'Servants Palace', 'name_ja': '奴僕宮', 'desc': '人际关系与下属运势'},
    '官禄宫': {'name_en': 'Career Palace', 'name_ja': '官禄宮', 'desc': '事业学业与仕途发展'},
    '田宅宫': {'name_en': 'Property Palace', 'name_ja': '田宅宮', 'desc': '房产家运与祖业传承'},
    '福德宫': {'name_en': 'Fortune Palace', 'name_ja': '福德宮', 'desc': '福气品德与精神享受'},
    '父母宫': {'name_en': 'Parents Palace', 'name_ja': '父母宮', 'desc': '父母缘分与学业学历'},
}


# ============ おみくじ数据 ============

OMIKUJI_TYPES = {
    '大吉': {'rank': 1, 'name_en': 'Great Blessing', 'name_ja': '大吉', 'emoji': '🎉'},
    '中吉': {'rank': 2, 'name_en': 'Middle Blessing', 'name_ja': '中吉', 'emoji': '✨'},
    '小吉': {'rank': 3, 'name_en': 'Small Blessing', 'name_ja': '小吉', 'emoji': '👍'},
    '吉': {'rank': 4, 'name_en': 'Fortune', 'name_ja': '吉', 'emoji': '☘️'},
    '半吉': {'rank': 5, 'name_en': 'Half Fortune', 'name_ja': '半吉', 'emoji': '🍀'},
    '末吉': {'rank': 6, 'name_en': 'Rising Fortune', 'name_ja': '末吉', 'emoji': '🌸'},
    '末小吉': {'rank': 7, 'name_en': 'Small Rising', 'name_ja': '末小吉', 'emoji': '🌱'},
    '凶': {'rank': 8, 'name_en': 'Curse', 'name_ja': '凶', 'emoji': '⚠️'},
    '小凶': {'rank': 9, 'name_en': 'Small Curse', 'name_ja': '小凶', 'emoji': '🌧️'},
    '半凶': {'rank': 10, 'name_en': 'Half Curse', 'name_ja': '半凶', 'emoji': '🌩️'},
    '末凶': {'rank': 11, 'name_en': 'Rising Curse', 'name_ja': '末凶', 'emoji': '⛈️'},
    '大凶': {'rank': 12, 'name_en': 'Great Curse', 'name_ja': '大凶', 'emoji': '💀'},
}

OMIKUJI_FORTUNES = {
    '大吉': {
        'zh': {
            'overall': '万事大吉，心想事成！今日运势极佳，无论做什么都会有好的结果。',
            'love': '恋爱运极佳！有望遇到理想的另一半，或与伴侣感情更进一步。',
            'study': '学业运势旺盛，考试、面试都能发挥超常，取得优异成绩。',
            'work': '事业蒸蒸日上，有升职加薪的机会，工作进展顺利。',
            'health': '身体健康，精力充沛，适合进行运动或户外活动。',
            'money': '财运亨通，有意外之财或额外收入，适合投资理财。',
            'person': '待ち人の人：很快就会遇到你等待的那个人，缘分已至！',
            'travel': '旅行运势极佳，适合外出旅游，会有愉快的经历。',
            'business': '商务谈判顺利展开，有签约成功的机会。',
            'lost': '遗失物很快就能找到，可能会有好心人归还。',
        },
        'en': {
            'overall': 'Everything will go perfectly! Your luck is at its peak today.',
            'love': 'Excellent love fortune! You may meet your ideal partner or deepen your bond.',
            'study': 'Academic success! Exams and interviews will go exceptionally well.',
            'work': 'Career advancement! Promotion and salary increase are likely.',
            'health': 'Great health and energy. Perfect for sports or outdoor activities.',
            'money': 'Financial windfall incoming! Great time for investments.',
            'person': 'The person you are waiting for: Your wait is almost over!',
            'travel': 'Perfect for travel! Expect a wonderful journey.',
            'business': 'Business negotiations will succeed. Great deals ahead.',
            'lost': 'Lost items will be found quickly, possibly returned by a kind stranger.',
        },
        'ja': {
            'overall': '万事大成！今日の運勢はとても良いでしょう。何を 해도素晴らしい結果を得られるでしょう。',
            'love': '恋愛運絶好調！理想のパートナーに出会えるか、パートナーの関係がより深まります。',
            'study': '学業運旺盛！試験、面接どこでも得很好な結果を出せるでしょう。',
            'work': '仕事运上昇！昇進や給与アップのチャンス到来。',
            'health': '健康で元気いっぱい。スポーツや户外活動に最適。',
            'money': '金運亨通！臨時収入や投资收益が期待できるでしょう。',
            'person': '待っている人：もうすぐ出会えますよ、縁분이巡ってきました！',
            'travel': '旅行運も最佳！お出かけに適した日です。',
            'business': 'ビジネス交渉が順調に進み、契約成立の可能性大。',
            'lost': '落し物はすぐに見つかるでしょう。優しい人が届けてくれるかも。',
        }
    },
    '中吉': {
        'zh': {
            'overall': '整体运势良好，只要努力就会有收获。',
            'love': '恋爱运不错，有新恋情的可能，已有伴侣者感情稳定。',
            'study': '学业运势较好，适合巩固知识，有望取得进步。',
            'work': '工作运势上升，认真努力会有成果展现。',
            'health': '健康状况良好，注意休息保持体力。',
            'money': '财运平稳，稳扎稳打能积累财富。',
            'person': '待ち人の人：缘分即将到来，保持开放的心态。',
            'travel': '适合短途旅行，会遇到有趣的人或事。',
            'business': '商务运尚可，稳扎稳打会有收获。',
            'lost': '遗失物品可能在家中某处，仔细找找。',
        },
        'en': {
            'overall': 'Good fortune overall. Your efforts will be rewarded.',
            'love': 'Decent love fortune. New romance possible or stable relationship.',
            'study': 'Good for studying. Progress is likely with effort.',
            'work': 'Work prospects improving. Your hard work will show results.',
            'health': 'Good health. Remember to rest and maintain energy.',
            'money': 'Steady finances. Consistent efforts will build wealth.',
            'person': 'The person you await: Fortune is coming. Stay open-minded.',
            'travel': 'Good for short trips. Interesting encounters await.',
            'business': 'Business is fair. Steady progress will pay off.',
            'lost': 'Check carefully at home. Items may be nearby.',
        },
        'ja': {
            'overall': '全体運良好、努力すれば必ず成果を 得られます。',
            'love': '恋愛運まあまあ。新恋期の可能性も、恋人は安定した関係を築けるでしょう。',
            'study': '学業運良好、知識を定着させるのに良い時期です。',
            'work': '仕事運上昇！真面目に努力すれば成果が現れます。',
            'health': '健康良好、休息を取って体力維持を心がけましょう。',
            'money': '金運安定、コツコツ貯金を増やすことができます。',
            'person': '待っている人：もうすぐ縁があります、心を開いたままでいて。',
            'travel': '近場のお出かけに向いています。興味深い出会いがあるかも。',
            'business': 'ビジネス運まあまあ、堅実に進めれば収穫があります。',
            'lost': '落と物は家の中にあるかもしれません、よく探してみてください。',
        }
    },
    '吉': {
        'zh': {
            'overall': '运势普通，需要更加努力才能获得成功。',
            'love': '恋爱运平平稳稳，适合增进了解。',
            'study': '学业运势普通，需要多加用功。',
            'work': '工作运势一般，保持稳定发挥即可。',
            'health': '健康状况平稳，注意日常保养。',
            'money': '财运普通，不宜冒险，适合保守理财。',
            'person': '待ち人の人：需要耐心等待，缘分未到。',
            'travel': '旅行运普通，出行注意安全。',
            'business': '商务运一般，谨慎行事为佳。',
            'lost': '遗失物品可能需要一些时间才能找到。',
        },
        'en': {
            'overall': 'Average fortune. More effort needed for success.',
            'love': 'Steady love fortune. Good time for getting to know someone.',
            'study': 'Average academics. Extra effort will help.',
            'work': 'Normal work fortune. Steady performance is fine.',
            'health': 'Normal health. Pay attention to daily care.',
            'money': 'Average finances. Conservative approach recommended.',
            'person': 'The person you await: Patience needed. Not yet time.',
            'travel': 'Average travel luck. Be safe during trips.',
            'business': 'Average business luck. Proceed with caution.',
            'lost': 'Lost items may take time to find.',
        },
        'ja': {
            'overall': '運勢普通、成功するにはもっと努力が必要です。',
            'love': '恋愛運平凡、お互いを知るのに良い時期です。',
            'study': '学業運普通、更なる勉強が必要です。',
            'work': '仕事運平凡、稳定に発揮できれば問題ありません。',
            'health': '健康状態安定、日常の保养を心がけましょう。',
            'money': '金運普通、冒険は禁物です。堅実な理财を。',
            'person': '待っている人：もう少し待つ必要があります。',
            'travel': '旅行運普通、お出かけは注意して。',
            'business': 'ビジネス運一般、慎重に行った方が良いでしょう。',
            'lost': '落し物はもう少し時間がかかるかもしれません。',
        }
    },
    '凶': {
        'zh': {
            'overall': '运势低迷，需要谨慎行事，避免冒进。',
            'love': '恋爱运不佳，容易发生误会或争执。',
            'study': '学业运势下滑，需加倍努力克服困难。',
            'work': '工作运势受阻，可能遇到瓶颈或小人。',
            'health': '健康状况欠佳，注意休息和调节情绪。',
            'money': '财运不佳，容易破财或遇到财务问题。',
            'person': '待ち人の人：缘分未到，不宜强求。',
            'travel': '旅行运不佳，建议推迟出行计划。',
            'business': '商务运欠佳，不宜做重大决定。',
            'lost': '遗失物品可能较难找回，需仔细寻找。',
        },
        'en': {
            'overall': 'Low fortune. Be cautious and avoid rushing into things.',
            'love': 'Poor love fortune. Misunderstandings or conflicts likely.',
            'study': 'Academic struggles. Extra effort needed to overcome.',
            'work': 'Work obstacles ahead. May face setbacks or office politics.',
            'health': 'Health concerns. Rest and manage stress.',
            'money': 'Financial troubles. May lose money or face issues.',
            'person': 'The person you await: Not the right time. Let go.',
            'travel': 'Poor travel luck. Consider postponing trips.',
            'business': 'Bad timing for business. Avoid major decisions.',
            'lost': 'Lost items may be difficult to recover.',
        },
        'ja': {
            'overall': '運気低調、慎重に行動し、突進は避けましょう。',
            'love': '恋愛運不佳、誤解や争いが起こりやすくなります。',
            'study': '学業運低下、努力して困難を克服する必要があります。',
            'work': '仕事運障害、瓶颈や小人に出会うかもしれません。',
            'health': '健康状態不良、休息と気分転換を心がけましょう。',
            'money': '金運不佳、散財しやすく財務問題が発生しやすいです。',
            'person': '待っている人：縁未到、強求是禁物です。',
            'travel': '旅行運不佳、お出かけは延期した方がいいでしょう。',
            'business': 'ビジネス運不良、大きな決定は避けるべきです。',
            'lost': '落し物は見つかりにくいかもしれません。',
        }
    },
    '大凶': {
        'zh': {
            'overall': '运势极差，建议低调行事，静待时机。',
            'love': '恋爱运极差，易遇挫折，需保持冷静。',
            'study': '学业运势极差，可能遇到重大挫折。',
            'work': '工作运势极差，容易犯错或与人发生冲突。',
            'health': '健康状况不佳，易生病或发生意外。',
            'money': '财运极差，极易破财，投资需格外谨慎。',
            'person': '待ち人の人：时机未到，切勿急于求成。',
            'travel': '旅行运极差，建议取消或推迟所有出行。',
            'business': '商务运极差，不宜做任何投资或签约。',
            'lost': '遗失物品恐难找回，请仔细检查重要物品。',
        },
        'en': {
            'overall': 'Terrible fortune. Stay low and wait for better times.',
            'love': 'Very poor love fortune. May face setbacks. Stay calm.',
            'study': 'Major academic challenges ahead. Prepare well.',
            'work': 'Significant work difficulties. Mistakes likely.',
            'health': 'Health risks. Be careful and avoid accidents.',
            'money': 'Severe financial troubles. Be extremely careful.',
            'person': 'The person you await: Wrong timing. Do not rush.',
            'travel': 'Very bad travel luck. Cancel or postpone all trips.',
            'business': 'Terrible for business. No investments or contracts.',
            'lost': 'Items likely lost forever. Check valuables carefully.',
        },
        'ja': {
            'overall': '非常に悪い運勢、低調に過ごし時機を待ちましょう。',
            'love': '恋愛運非常に悪い、挫折しやすい、冷静を保ってください。',
            'study': '学業運非常に悪い、重大な挫折に出会う可能性があります。',
            'work': '仕事運非常に悪い、ミスを犯しやすく、人と衝突しやすいです。',
            'health': '健康状態不良、病気に会いやすく、事故にもご注意ください。',
            'money': '金運非常に悪い、すごく散財しやすく、投資はさらに慎重に。',
            'person': '待っている人：まだ時ではありません、焦らないでください。',
            'travel': '旅行運非常に悪い、全てのお出かけをキャンセル或いは延期してください。',
            'business': 'ビジネス運非常に悪い、投資や契約は全て避けてください。',
            'lost': '落し物は多分見つかりません、貴重品をよく確認してください。',
        }
    },
}


# ============ 易经六爻数据 ============

# 64卦完整数据（简化版，包含卦名、卦辞、象辞）
ICHING_HEXAGRAMS = {
    1: {'name': '乾', 'name_en': 'Qian (Creative)', 'name_ja': '乾', 'symbol': '☰☰',
        'judgement': {'zh': '元亨利贞', 'en': 'Creative, Prosperous, Favorable', 'ja': '元亨利貞'},
        'image': {'zh': '天行健，君子以自强不息', 'en': 'The movement of heaven is full of power. The superior person should constantly strive for self-improvement.', 'ja': '天は健やかに動く、君子は絶えず自らを高める'},
        'meaning': {'zh': '象征天，代表纯阳至刚之力。预示大吉大利，事事亨通，但需警惕过度刚强。', 'en': 'Represents Heaven, pure Yang energy. Great fortune but beware of being overly strong.', 'ja': '天を象徴し、純粋な陽の力。非常に良いが、が強すぎることに注意'} },
    2: {'name': '坤', 'name_en': 'Kun (Receptive)', 'name_ja': '坤', 'symbol': '☷☷',
        'judgement': {'zh': '元亨，利牝马之贞', 'en': 'Receptive, Favorable for feminine perseverance', 'ja': '元亨、牝馬の貞に利あり'},
        'image': {'zh': '地势坤，君子以厚德载物', 'en': 'The earth receptivity is vast. The superior person should have great virtue to bear all.', 'ja': '地の势坤、君子は徳を厚くして物を載せる'},
        'meaning': {'zh': '象征地，代表柔顺包容之力。预示诸事顺遂，但需顺应时势。', 'en': 'Represents Earth, the power of receptivity. Things will go smoothly if you follow the flow.', 'ja': '地を象徴し、柔らかな包容力を表す。状況に合わせれば事が順調に進む'} },
    3: {'name': '屯', 'name_en': 'Zhun (Difficulty)', 'name_ja': '屯', 'symbol': '☳☵',
        'judgement': {'zh': '元亨利贞，勿用有攸往，利建侯', 'en': 'Difficult beginnings, be patient', 'ja': '元亨利貞、攸往する勿れ、侯を建つるに利あり'},
        'image': {'zh': '云雷屯，君子以经纶', 'en': 'Clouds and thunder create difficulty. The superior person organizes affairs in difficult times.', 'ja': '雲雷屯、君子は経綸を以ってす'},
        'meaning': {'zh': '象征事物初生时的艰难。预示万事开头难，但只要坚定信念终会成功。', 'en': 'Represents the difficulty of beginnings. Success comes through perseverance.', 'ja': '物事の始まり艰难を象徴。始めは难的だが、信念を固めれば成功する'} },
    4: {'name': '蒙', 'name_en': 'Meng (Youth)', 'name_ja': '蒙', 'symbol': '☶☵',
        'judgement': {'zh': '亨，匪我求童蒙，童蒙求我', 'en': 'Innocence and education', 'ja': '亨、我は童蒙を求むるに非ず、童蒙我を求める'},
        'image': {'zh': '山下出泉，蒙', 'en': 'A spring beneath a mountain. The superior person should educate the young.', 'ja': '山の下泉が出る、蒙'},
        'meaning': {'zh': '象征蒙昧无知，需要启蒙教育。预示需要学习或寻求指导。', 'en': 'Represents ignorance needing education. Seek guidance and learn.', 'ja': '無知蒙昧を象徴、教育が必要。指導を求め学ぶ'} },
    5: {'name': '需', 'name_en': 'Xu (Waiting)', 'name_ja': '需', 'symbol': '☵☰',
        'judgement': {'zh': '有孚，光亨，贞吉。利涉大川', 'en': 'Waiting with faith brings success', 'ja': '孚あり、光亨、貞吉。大川を涉るに利あり'},
        'image': {'zh': '云上于天，需', 'en': 'Clouds rise to heaven. Waiting for rain. Be patient for what is coming.', 'ja': '雲天の上に於いて、需'},
        'meaning': {'zh': '象征等待。预示需要耐心等待时机，不可冒进。', 'en': 'Represents waiting. Patience is needed. Do not rush.', 'ja': '待つことを象徴。辛抱強く時機待たねばならない'} },
    6: {'name': '讼', 'name_en': 'Song (Conflict)', 'name_ja': '讼', 'symbol': '☰☵',
        'judgement': {'zh': '有孚，窒惕，中吉，终凶', 'en': 'Conflict is dangerous, mediation needed', 'ja': '孚あり、窒惕す、中は吉、ついに凶'},
        'image': {'zh': '天与水违行，讼', 'en': 'Heaven and water move in opposite directions. Legal conflicts may arise.', 'ja': '天と水违いを 행、讼'},
        'meaning': {'zh': '象征争讼。预示易有是非冲突，宜守不宜争。', 'en': 'Represents disputes. Conflicts likely. Better to avoid than fight.', 'ja': '争いを象徴。是非衝突が起きやすい。争わず守るべき'} },
    7: {'name': '师', 'name_en': 'Shi (Army)', 'name_ja': '師', 'symbol': '☷☵',
        'judgement': {'zh': '贞，丈人吉，无咎', 'en': 'Leadership with virtue brings victory', 'ja': '貞、丈人吉、咎なし'},
        'image': {'zh': '地中有水，师', 'en': 'Water contained in earth. The capable leader gathers the masses.', 'ja': '地中に水あり、師'},
        'meaning': {'zh': '象征军队和领导。预示需要果断领导，但需以德服人。', 'en': 'Represents army and leadership. Decisive action with virtue needed.', 'ja': '軍隊と指導力を象徴。德で人を伏せる果断さが必要'} },
    8: {'name': '比', 'name_en': 'Bi (Intimacy)', 'name_ja': '比', 'symbol': '☵☷',
        'judgement': {'zh': '吉，原筮元永贞，不咎', 'en': 'Unity and cooperation bring success', 'ja': '吉、原筮元永貞、咎らず'},
        'image': {'zh': '地上有水，比', 'en': 'Water on the earth flows together. Harmony among people.', 'ja': '地の上に水あり、比'},
        'meaning': {'zh': '象征亲密比附。预示交友结盟可获成功。', 'en': 'Represents close relationships. Alliances and cooperation will succeed.', 'ja': '親密な関係を象徴。交友や同盟が成功する'} },
    9: {'name': '小畜', 'name_en': 'Xiaoxu (Small Restraint)', 'name_ja': '小畜', 'symbol': '☰☴',
        'judgement': {'zh': '亨，密云不雨，自我西郊', 'en': 'Small accomplishments, not yet complete', 'ja': '亨、密雲雨を降らさず、我酉郊より'},
        'image': {'zh': '风行天上，小畜', 'en': 'Wind beneath the sky. Small蓄力 before big accomplishments.', 'ja': '風天を 행、小畜'},
        'meaning': {'zh': '象征小有积蓄。预示小有成就，但尚未达到完满。', 'en': 'Represents small accumulation. Some success but not complete yet.', 'ja': '小さな蓄積を象徴。小さな成果はまだ完全ではない'} },
    10: {'name': '履', 'name_en': 'Lu (Treading)', 'name_ja': '履', 'symbol': '☰☱',
        'judgement': {'zh': '履虎尾，不咥人，亨', 'en': 'Careful steps bring safety', 'ja': '虎の尾を履む、人を咥わず、亨'},
        'image': {'zh': '上天下泽，履', 'en': 'Treading on tiger tail. Be cautious in dangerous situations.', 'ja': '天上に沢あり、履'},
        'meaning': {'zh': '象征谨慎行事。预示危险当前，需小心翼翼方能平安。', 'en': 'Represents cautious conduct. Careful steps needed in dangerous situations.', 'ja': '慎重な行動を象徴。危険当面，小心翼翼なければ平安'} },
    11: {'name': '泰', 'name_en': 'Tai (Peace)', 'name_ja': '泰', 'symbol': '☰☷',
        'judgement': {'zh': '小往大来，吉亨', 'en': 'Peace and prosperity', 'ja': '小往大来、吉亨'},
        'image': {'zh': '天地交，泰', 'en': 'Heaven and earth unite. A time of great harmony and success.', 'ja': '天地交わる，泰'},
        'meaning': {'zh': '象征通泰。预示诸事吉祥，万物和谐。', 'en': 'Represents peace and harmony. Everything goes well.', 'ja': '通泰を象徴。万事吉祥、万物調和'} },
    12: {'name': '否', 'name_en': 'Pi (Standstill)', 'name_ja': '否', 'symbol': '☷☰',
        'judgement': {'zh': '否之匪人，不利君子贞，大往小来', 'en': 'Stagnation and isolation', 'ja': '匪人の否、君子貞に不利、大往小来'},
        'image': {'zh': '天地不交，否', 'en': 'Heaven and earth do not unite. A time of difficulties.', 'ja': '天地交わらざる、否'},
        'meaning': {'zh': '象征闭塞。预示诸事不顺，需要耐心等待转机。', 'en': 'Represents obstruction. Things not going well. Wait for change.', 'ja': '閉塞を象徴。事が進まない。転換を待つ'} },
    13: {'name': '同人', 'name_en': 'Tongren (Fellowship)', 'name_ja': '同人', 'symbol': '☰☲',
        'judgement': {'zh': '同人于野，亨，利涉大川，利君子贞', 'en': 'Fellowship brings success', 'ja': '野に同人、亨、大川を涉るに利あり、君子貞に利あり'},
        'image': {'zh': '天与火，同人', 'en': 'Heaven and fire unite. Unity among people.', 'ja': '天と火同人'},
        'meaning': {'zh': '象征同人合作。预示与人同心可成大事。', 'en': 'Represents fellowship. Working together leads to great achievements.', 'ja': '同人合作を象徴。人と心を合わせれば大成する'} },
    14: {'name': '大有', 'name_en': 'Dayou (Abundance)', 'name_ja': '大有', 'symbol': '☲☰',
        'judgement': {'zh': '元亨', 'en': 'Great abundance and prosperity', 'ja': '元亨'},
        'image': {'zh': '火在天上，大有', 'en': 'Fire above, the sun illuminates everything. Great success.', 'ja': '火天の上に大有'},
        'meaning': {'zh': '象征大有收获。预示事业昌盛，财运旺盛。', 'en': 'Represents great gains. Career prosperity and wealth are indicated.', 'ja': '大収穫を象徴。事業隆盛、金運旺盛'} },
    15: {'name': '谦', 'name_en': 'Qian (Humility)', 'name_ja': '謙', 'symbol': '☷☶',
        'judgement': {'zh': '亨，君子有终', 'en': 'Humility brings good fortune', 'ja': '亨、君子有終'},
        'image': {'zh': '地中有山，谦', 'en': 'Mountain beneath the earth. True greatness through humility.', 'ja': '地中に山あり、謙'},
        'meaning': {'zh': '象征谦虚。预示谦受益满招损，宜守不宜张扬。', 'en': 'Represents modesty. Humility brings fortune, arrogance brings loss.', 'ja': '謙虚を象徴。謙遜は益し、傲慢は損を招く'} },
    16: {'name': '豫', 'name_en': 'Yu (Enthusiasm)', 'name_ja': '豫', 'symbol': '☷☳',
        'judgement': {'zh': '利建侯行师', 'en': 'Enthusiasm brings followers', 'ja': '侯を建つるに利く、師を行くに利あり'},
        'image': {'zh': '雷出地奋，豫', 'en': 'Thunder comes out of the earth. Joy and excitement spread.', 'ja': '雷出で地を起こす、豫'},
        'meaning': {'zh': '象征愉悦。预示心情愉快，事事顺遂。', 'en': 'Represents joy. Happy mood, everything goes smoothly.', 'ja': '愉悦を象徴。気分愉快、事が順調'} },
    17: {'name': '随', 'name_en': 'Sui (Following)', 'name_ja': '随', 'symbol': '☳☱',
        'judgement': {'zh': '元亨利贞，无咎', 'en': 'Following with purpose brings success', 'ja': '元亨利貞、咎なし'},
        'image': {'zh': '泽中有雷，随', 'en': 'Thunder in the marsh. Following the right path.', 'ja': '沢中有雷，随'},
        'meaning': {'zh': '象征随从。预示追随明主可得吉利。', 'en': 'Represents following. Following a wise leader brings good fortune.', 'ja': '随順を象徴。明い主について行けば吉利可得'} },
    18: {'name': '蛊', 'name_en': 'Gu (Decay)', 'name_ja': '蠱', 'symbol': '☶☴',
        'judgement': {'zh': '元亨利贞，至于八月有凶', 'en': 'Correcting past problems takes time', 'ja': '元亨利貞、八月に至りて凶あり'},
        'image': {'zh': '山下有风，蛊', 'en': 'Wind beneath mountain. Working on accumulated problems.', 'ja': '山下風あり、蠱'},
        'meaning': {'zh': '象征蛊乱。预示需要整治积弊，但需防后患。', 'en': 'Represents decay. Need to address old problems but watch for consequences.', 'ja': '蠱乱を象徴。積弊を整治する必要があるが、後禍を防ぐ'} },
    19: {'name': '临', 'name_en': 'Lin (Approach)', 'name_ja': '臨', 'symbol': '☷☰',
        'judgement': {'zh': '元亨利贞，至于八月有凶', 'en': 'Leadership and guidance', 'ja': '元亨利貞'},
        'image': {'zh': '泽上有地，临', 'en': 'Earth above the marsh. Approaching with virtue.', 'ja': '沢の上に地あり、臨'},
        'meaning': {'zh': '象征临下。预示领导统御可获成功。', 'en': 'Represents leadership. Governing with virtue leads to success.', 'ja': '臨下を象徴。德で統御すれば成功'} },
    20: {'name': '观', 'name_en': 'Guan (Contemplation)', 'name_ja': '観', 'symbol': '☴☷',
        'judgement': {'zh': '盥而不荐，有孚颙若', 'en': 'Observe before acting', 'ja': '盥して荐めず、孚あれば颙う'},
        'image': {'zh': '风行地上，观', 'en': 'Wind moves over the earth. Contemplation and observation.', 'ja': '風地の上を 行、観'},
        'meaning': {'zh': '象征观仰。预示观察学习可获智慧。', 'en': 'Represents contemplation. Learning through observation brings wisdom.', 'ja': '観仰を象徴。観察学習で智慧可得'} },
    21: {'name': '噬嗑', 'name_en': 'Shike (Biting)', 'name_ja': '噬嗑', 'symbol': '☲☶',
        'judgement': {'zh': '亨，利用狱', 'en': 'Justice and decision making', 'ja': '亨、獄の利用に利あり'},
        'image': {'zh': '雷电噬嗑', 'en': 'Lightning and thunder. Making decisions with force.', 'ja': '雷電噬嗑'},
        'meaning': {'zh': '象征明罚敕法。预示需果断处理障碍。', 'en': 'Represents justice. Decisive action needed to overcome obstacles.', 'ja': '明罰勅法を象徴。障害を果断に処理する必要がある'} },
    22: {'name': '贲', 'name_en': 'Bi (Grace)', 'name_ja': '賁', 'symbol': '☶☲',
        'judgement': {'zh': '亨，小利有所往', 'en': 'Adornment and elegance', 'ja': '亨、小利きりに往く'},
        'image': {'zh': '山下有火，贲', 'en': 'Fire beneath mountain. Adorning with grace.', 'ja': '山下火あり、賁'},
        'meaning': {'zh': '象征文饰。预示外表的装饰能带来好运。', 'en': 'Represents adornment. Appearance and presentation bring good fortune.', 'ja': '文飾を象徴。外見の装飾が幸運带来'} },
    23: {'name': '剥', 'name_en': 'Bo (Stripping)', 'name_ja': '剥', 'symbol': '☷☶',
        'judgement': {'zh': '不利有攸往', 'en': 'Deterioration and decline', 'ja': '攸往るに不利'},
        'image': {'zh': '山附于地，剥', 'en': 'Mountain collapses to earth. Decline is happening.', 'ja': '山地に剥く'},
        'meaning': {'zh': '象征剥落。预示运势衰退，宜守不宜动。', 'en': 'Represents deterioration. Fortune declining. Better to preserve than act.', 'ja': '剥落を象徴。運気衰退、守るべきで動くべからず'} },
    24: {'name': '复', 'name_en': 'Fu (Return)', 'name_ja': '復', 'symbol': '☷☳',
        'judgement': {'zh': '亨，出入无疾，朋来无咎', 'en': 'Return to the right path', 'ja': '亨、出入疾なく、朋来たりて咎なし'},
        'image': {'zh': '雷在地中，复', 'en': 'Thunder in the earth. Things are returning to normal.', 'ja': '雷地の中に復'},
        'meaning': {'zh': '象征复返。预示运势开始回升，是转折点。', 'en': 'Represents return. Fortune is turning upward. A turning point.', 'ja': '帰還を象徴。運気が上昇し始め、転換点'} },
    25: {'name': '无妄', 'name_en': 'WuWang (Innocence)', 'name_ja': '无妄', 'symbol': '☰☳',
        'judgement': {'zh': '元亨利贞，其匪正有眚，不利有攸往', 'en': 'Naturalness and truth', 'ja': '元亨利貞、匪正あれば眚あり、攸往るに不利'},
        'image': {'zh': '天下雷行，物与无妄', 'en': 'Thunder moves under heaven. Be natural and truthful.', 'ja': '天下雷行、物と无妄'},
        'meaning': {'zh': '象征无妄之灾。预示意外之事可能发生。', 'en': 'Represents unexpected events. Unexpected things may happen.', 'ja': '无妄の災いを象徴。予期せぬことが起こり得る'} },
    26: {'name': '大畜', 'name_en': 'Daxu (Great Restraint)', 'name_ja': '大畜', 'symbol': '☰☶',
        'judgement': {'zh': '利贞，不家食吉，利涉大川', 'en': 'Great accumulation of strength', 'ja': '貞に利く、家に食らわず吉、大川を涉るに利あり'},
        'image': {'zh': '天在山中，大畜', 'en': 'Heaven in the mountain. Great蓄力 of energy.', 'ja': '天山中にある、大畜'},
        'meaning': {'zh': '象征大有所蓄。预示积累力量，等待时机。', 'en': 'Represents great accumulation. Build strength and wait for the right moment.', 'ja': '大きな蓄積を象徴。力を蓄積し、時機を待つ'} },
    27: {'name': '颐', 'name_en': 'Yi (Nourishment)', 'name_ja': '頤', 'symbol': '☶☳',
        'judgement': {'zh': '贞吉，观颐，自求口实', 'en': 'Taking care and nourishment', 'ja': '貞吉、頤を觀て、口実を自らす'},
        'image': {'zh': '山下有雷，颐', 'en': 'Thunder beneath mountain. Taking care of yourself.', 'ja': '山下雷あり、頤'},
        'meaning': {'zh': '象征颐养。预示需注重修养和健康。', 'en': 'Represents nourishment. Focus on self-cultivation and health.', 'ja': '顧養を象徴。修養と健康に注意が必要'} },
    28: {'name': '大过', 'name_en': 'Daguo (Great Excess)', 'name_ja': '大過', 'symbol': '☴☲',
        'judgement': {'zh': '栋桡，利有攸往，亨', 'en': 'Excessive action needs caution', 'ja': '棟桡、攸往るに利く、亨'},
        'image': {'zh': '泽灭木，大过', 'en': 'Marsh overflows the wood. Great excess and danger.', 'ja': '沢木を滅ぼす、大過'},
        'meaning': {'zh': '象征大过。预示行动过激有风险，但也可能有转机。', 'en': 'Represents excessive action. Overaction is risky but may have opportunities.', 'ja': '大過を象徴。行動が激烈ならリスクあるが、転機もあり'} },
    29: {'name': '坎', 'name_en': 'Kan (Danger)', 'name_ja': '坎', 'symbol': '☵☵',
        'judgement': {'zh': '习坎，有孚，维心亨，行有尚', 'en': 'Danger upon danger, stay centered', 'ja': '坎を習う、孚あり심을亨ね、行に尚あり'},
        'image': {'zh': '水洊至，习坎', 'en': 'Water continuously flowing. Danger all around.', 'ja': '水洊至り、坎を習う'},
        'meaning': {'zh': '象征重重险陷。预示困难重重，需格外小心。', 'en': 'Represents repeated danger. Many difficulties ahead. Be extra careful.', 'ja': '重重の険陷を象徴。困難だらけ、特に小心らに'} },
    30: {'name': '离', 'name_en': 'Li (Clinging)', 'name_ja': '離', 'symbol': '☲☲',
        'judgement': {'zh': '畜牝牛吉', 'en': 'Brightness and clarity', 'ja': '牝牛を畜うるに吉'},
        'image': {'zh': '明两作，离', 'en': 'Fire creates brightness. Clarity and insight.', 'ja': '明両作、離'},
        'meaning': {'zh': '象征离明。预示光明照耀，前途明朗。', 'en': 'Represents brightness. Clear path ahead, success is likely.', 'ja': '離明を象徴。光輝き、前途明朗'} },
    31: {'name': '咸', 'name_en': 'Xian (Influence)', 'name_ja': '咸', 'symbol': '☱☶',
        'judgement': {'zh': '亨，利贞，取女吉', 'en': 'Mutual influence and attraction', 'ja': '亨、貞に利し、女を取るに吉'},
        'image': {'zh': '山上有泽，咸', 'en': 'Lake on top of mountain. Mutual attraction between opposites.', 'ja': '山上に沢あり、咸'},
        'meaning': {'zh': '象征感应。预示感情交流可带来好运。', 'en': 'Represents mutual attraction. Emotional connection brings good fortune.', 'ja': '感応を象徴。感情交流が幸運を带来'} },
    32: {'name': '恒', 'name_en': 'Heng (Constancy)', 'name_ja': '恒', 'symbol': '☶☱',
        'judgement': {'zh': '亨，无咎，利贞，利有攸往', 'en': 'Endurance and perseverance', 'ja': '亨、咎なし、貞に利し、攸往るに利あり'},
        'image': {'zh': '雷风恒', 'en': 'Thunder and wind together. Long-lasting stability.', 'ja': '雷風恒'},
        'meaning': {'zh': '象征恒久。预示感情事业需持之以恒。', 'en': 'Represents constancy. Perseverance in love and career needed.', 'ja': '恒久を象徴。感情事業に忍耐が必要'} },
    33: {'name': '遁', 'name_en': 'Dun (Retreat)', 'name_ja': '遁', 'symbol': '☰☶',
        'judgement': {'zh': '亨，小利贞', 'en': 'Strategic withdrawal', 'ja': '亨、小利貞'},
        'image': {'zh': '天下有山，遁', 'en': 'Mountain under heaven. Sometimes retreat is wise.', 'ja': '天下山あり、遁'},
        'meaning': {'zh': '象征隐遁。预示适当退让可避凶趋吉。', 'en': 'Represents retreat. Sometimes stepping back brings better outcomes.', 'ja': '隠遁を象徴。适当后退すれば凶を避け吉趋向可'} },
    34: {'name': '大壮', 'name_en': 'Dazhuang (Great Strength)', 'name_ja': '大壮', 'symbol': '☰☳',
        'judgement': {'zh': '利贞', 'en': 'Great power and strength', 'ja': '貞に利し'},
        'image': {'zh': '雷在天上，大壮', 'en': 'Thunder above heaven. Great strength is yours.', 'ja': '雷天の上に大壮'},
        'meaning': {'zh': '象征大壮。预示力量强盛，但需防过刚而折。', 'en': 'Represents great strength. Strong but beware of being too forceful.', 'ja': '大壮を象徴。力が強盛だが、過刚で折れることに注意'} },
    35: {'name': '晋', 'name_en': 'Jin (Progress)', 'name_ja': '晉', 'symbol': '☷☲',
        'judgement': {'zh': '康侯用锡马蕃庶，昼日三接', 'en': 'Advancement and recognition', 'ja': '康侯の馬を錫まり蕃庶し、昼日に三接す'},
        'image': {'zh': '明出地上，晋', 'en': 'Sun rises above earth. Progress and recognition.', 'ja': '明地の上に晉'},
        'meaning': {'zh': '象征晋升。预示地位提升，名声渐著。', 'en': 'Represents promotion. Status improving, reputation growing.', 'ja': '昇進を象徴。地位向上、声が上がる'} },
    36: {'name': '明夷', 'name_en': 'Mingyi (Darkness)', 'name_ja': '明夷', 'symbol': '☲☷',
        'judgement': {'zh': '利艰贞', 'en': 'Hiding brightness, staying low', 'ja': '貞を艱うに利し'},
        'image': {'zh': '明入地中，明夷', 'en': 'Sun enters earth. A time of hiding your light.', 'ja': '明地中に入る、明夷'},
        'meaning': {'zh': '象征明入地中。预示光明被遮，需韬光养晦。', 'en': 'Represents obscured brightness. Hide your talents temporarily.', 'ja': '明地中入りを象徴。光遮られ、才能を隠す必要がある'} },
    37: {'name': '家人', 'name_en': 'Jiaren (Family)', 'name_ja': '家人', 'symbol': '☲☴',
        'judgement': {'zh': '利女贞', 'en': 'Family harmony', 'ja': '女貞に利し'},
        'image': {'zh': '风自火出，家人', 'en': 'Fire creates wind. Family matters need attention.', 'ja': '火風家人'},
        'meaning': {'zh': '象征家人。预示家庭和睦可致吉祥。', 'en': 'Represents family. Harmony at home brings good fortune.', 'ja': '家人を象徴。家庭仲良ければ吉祥可得'} },
    38: {'name': '睽', 'name_en': 'Kui (Opposition)', 'name_ja': '睽', 'symbol': '☱☲',
        'judgement': {'zh': '小事吉', 'en': 'Minor differences, stay united', 'ja': '小事吉'},
        'image': {'zh': '上火下泽，睽', 'en': 'Fire above marsh. Small oppositions but still manageable.', 'ja': '上火下沢、睽'},
        'meaning': {'zh': '象征睽违。预示与人有分歧，需化解矛盾。', 'en': 'Represents alienation. Differences with others need resolution.', 'ja': '睽違を象徴。人と分歧、矛盾を化解する必要がある'} },
    39: {'name': '蹇', 'name_en': 'Jian (Obstruction)', 'name_ja': '蹇', 'symbol': '☶☷',
        'judgement': {'zh': '利西南，不利东北，利见大人，贞吉', 'en': 'Hardship and obstruction ahead', 'ja': '西南に利く、東北に不利、大人の見るに利く、貞吉'},
        'image': {'zh': '山上有水，蹇', 'en': 'Water on top of mountain. Obstacles ahead.', 'ja': '山上有水、蹇'},
        'meaning': {'zh': '象征蹇难。预示前进受阻，需待时机。', 'en': 'Represents hardship. Progress blocked. Wait for the right time.', 'ja': '蹇難を象徴。前進阻碍、時機を待つ'} },
    40: {'name': '解', 'name_en': 'Jie (Liberation)', 'name_ja': '解', 'symbol': '☳☵',
        'judgement': {'zh': '利西南，无所往，其来复吉，有攸往，夙吉', 'en': 'Resolution and release', 'ja': '西南に利く、往かざる无所、其復きたるは吉、攸往れば夙吉'},
        'image': {'zh': '雷雨作，解', 'en': 'Thunder and rain come. Relief from difficulties.', 'ja': '雷雨作り、解'},
        'meaning': {'zh': '象征解除。预示困难解除，吉祥如意。', 'en': 'Represents release. Difficulties resolved. Good fortune ahead.', 'ja': '解除を象徴。困難解除、吉祥如意'} },
    41: {'name': '损', 'name_en': 'Sun (Decrease)', 'name_ja': '損', 'symbol': '☱☶',
        'judgement': {'zh': '有孚，元吉，无咎，可贞，利有攸往', 'en': 'Giving up for gain', 'ja': '孚あり、元吉、咎なし、貞にべき、攸往るに利あり'},
        'image': {'zh': '山下有泽，损', 'en': 'Marsh beneath mountain. Sometimes loss leads to gain.', 'ja': '山下沢あり、損'},
        'meaning': {'zh': '象征损益。预示有所失亦有所得。', 'en': 'Represents decrease. What you lose may be balanced by what you gain.', 'ja': '損益を象徴。失うものあれば得るものもある'} },
    42: {'name': '益', 'name_en': 'Yi (Increase)', 'name_ja': '益', 'symbol': '☳☲',
        'judgement': {'zh': '利有攸往，利涉大川', 'en': 'Growth and increase', 'ja': '攸往るに利く、大川を涉るに利あり'},
        'image': {'zh': '风雷益', 'en': 'Wind and thunder create growth. Fortune is increasing.', 'ja': '風雷益'},
        'meaning': {'zh': '象征增益。预示运势上升，利益增加。', 'en': 'Represents increase. Fortune rising, benefits growing.', 'ja': '増益を象徴。運気上昇、利益増加'} },
    43: {'name': '夬', 'name_en': 'Guai (Resolution)', 'name_ja': '夬', 'symbol': '☰☱',
        'judgement': {'zh': '扬于王庭，孚号，有厉，告自邑，不利即戎，利有攸往', 'en': 'Decisive action needed', 'ja': '王庭に揚ぐ、孚号し、厲あり、邑より告ぐ、即戎に不利、攸往るに利あり'},
        'image': {'zh': '泽上于天，夬', 'en': 'Lake rises to heaven. Decision time approaches.', 'ja': '沢天上に於いて、夬'},
        'meaning': {'zh': '象征决断。预示需要果断处理问题。', 'en': 'Represents resolution. Decisive action needed on issues.', 'ja': '決断を象徴。問題を果断に処理する必要がある'} },
    44: {'name': '姤', 'name_en': 'Gou (Meeting)', 'name_ja': '姤', 'symbol': '☰☴',
        'judgement': {'zh': '女壮，勿用取女', 'en': 'Meeting with caution', 'ja': '女壮し、女を取る勿れ'},
        'image': {'zh': '天下有风，姤', 'en': 'Wind under heaven. Unexpected meetings.', 'ja': '天下風あり、姤'},
        'meaning': {'zh': '象征相遇。预示可能有意外邂逅。', 'en': 'Represents meeting. Unexpected encounters possible.', 'ja': '相遇を象徴。予期せぬ出会いがあり得る'} },
    45: {'name': '萃', 'name_en': 'Cui (Gathering)', 'name_ja': '萃', 'symbol': '☷☱',
        'judgement': {'zh': '亨，王假有庙，利见大人，亨，利贞', 'en': 'Gathering of people', 'ja': '亨、王庙に假り、大人に利見え、亨、貞に利し'},
        'image': {'zh': '泽上于地，萃', 'en': 'Marsh above earth. People gathering together.', 'ja': '沢地の上に萃'},
        'meaning': {'zh': '象征聚集。预示众人相聚，合作有利。', 'en': 'Represents gathering. People coming together. Cooperation is beneficial.', 'ja': '聚集を象徴。人が集まり、合作が有利'} },
    46: {'name': '升', 'name_en': 'Sheng (Ascent)', 'name_ja': '升', 'symbol': '☷☳',
        'judgement': {'zh': '元亨，用见大人，勿恤，南征吉', 'en': 'Gradual rise and ascent', 'ja': '元亨、大人の用に見え、恤む勿れ、南征れば吉'},
        'image': {'zh': '地中生木，升', 'en': 'Tree grows from earth. Gradual progress upward.', 'ja': '地中生木，升'},
        'meaning': {'zh': '象征上升。预示稳步上升，前途光明。', 'en': 'Represents ascent. Steady upward progress, bright future ahead.', 'ja': '上昇を象徴。稳步的に上昇、前途光明'} },
    47: {'name': '困', 'name_en': 'Kun (Exhaustion)', 'name_ja': '困', 'symbol': '☵☱',
        'judgement': {'zh': '亨，贞大人吉，无咎，有言不信', 'en': 'Being in a difficult situation', 'ja': '亨、貞大人吉、咎なし、言あれば信ずべきか'},
        'image': {'zh': '泽无水，困', 'en': 'Marsh without water. Exhaustion and困境.', 'ja': '沢水なし、困'},
        'meaning': {'zh': '象征穷困。预示处于困境，需坚守正道。', 'en': 'Represents exhaustion. In a difficult spot. Stay on the right path.', 'ja': '窮困を象徴。困境にあり、正しい道を堅持する必要がある'} },
    48: {'name': '井', 'name_en': 'Jing (Well)', 'name_ja': '井', 'symbol': '☵☴',
        'judgement': {'zh': '改邑不改井，无丧无得，往来井井', 'en': 'The reliable foundation', 'ja': '邑を改むるも井を改めず、喪うことなく得ることなく、往来井井たり'},
        'image': {'zh': '木上有水，井', 'en': 'Water above wood. Something essential that sustains.', 'ja': '木上に水あり、井'},
        'meaning': {'zh': '象征井养。预示根基稳固，可稳步发展。', 'en': 'Represents well. Solid foundation for steady development.', 'ja': '井養を象徴。根基安定、稳步発展可'} },
    49: {'name': '革', 'name_en': 'Ge (Revolution)', 'name_ja': '革', 'symbol': '☱☲',
        'judgement': {'zh': '巳日乃孚，元亨利贞，悔亡', 'en': 'Transformation and change', 'ja': '巳日乃孚、元亨利貞、悔亡'},
        'image': {'zh': '泽中有火，革', 'en': 'Fire in the marsh. Time for transformation.', 'ja': '沢中に火あり、革'},
        'meaning': {'zh': '象征变革。预示需要改变才能进步。', 'en': 'Represents revolution. Change is needed for progress.', 'ja': '変革を象徴。改变才能進歩'} },
    50: {'name': '鼎', 'name_en': 'Ding (Cauldron)', 'name_ja': '鼎', 'symbol': '☲☴',
        'judgement': {'zh': '元吉，亨', 'en': 'Stability and nourishment', 'ja': '元吉、亨'},
        'image': {'zh': '木上有火，鼎', 'en': 'Fire on wood. Something valuable being cultivated.', 'ja': '木上に火あり、鼎'},
        'meaning': {'zh': '象征鼎立。预示稳定发展，有所成就。', 'en': 'Represents stability. Steady development and achievement.', 'ja': '鼎立を象徴。安定的発展、成果あり'} },
    51: {'name': '震', 'name_en': 'Zhen (Thunder)', 'name_ja': '震', 'symbol': '☳☳',
        'judgement': {'zh': '亨，震来虩虩，笑言哑哑，震惊百里', 'en': 'Thunder and excitement', 'ja': '亨、震る虩虩として来たり、笑言哑哑たり、百里を震驚す'},
        'image': {'zh': '洊雷，震', 'en': 'Repeated thunder. Excitement and alarm.', 'ja': '洊雷、震'},
        'meaning': {'zh': '象征震动。预示有惊无险，需保持镇定。', 'en': 'Represents shock. Alarming events but no real danger.', 'ja': '振動を象徴。驚くべきことだが реальной опасности нет、冷静を保つ'} },
    52: {'name': '艮', 'name_en': 'Gen (Mountain)', 'name_ja': '艮', 'symbol': '☶☶',
        'judgement': {'zh': '艮其背，不获其身，行其庭，不见其人，无咎', 'en': 'Stillness and meditation', 'ja': '艮なりその背、不獲其の身、行其の庭、其の人の不见、无咎'},
        'image': {'zh': '兼山，艮', 'en': 'Mountain upon mountain. Stop and reflect.', 'ja': '兼山、艮'},
        'meaning': {'zh': '象征静止。预示需要冷静思考，不宜妄动。', 'en': 'Represents stillness. Time to reflect, not act.', 'ja': '静止を象徴。冷静に考える必要、妄動するな'} },
    53: {'name': '渐', 'name_en': 'Jian (Gradual)', 'name_ja': '漸', 'symbol': '☴☶',
        'judgement': {'zh': '女归吉，利贞', 'en': 'Gradual progress', 'ja': '女帰れば吉、貞に利し'},
        'image': {'zh': '山上有木，渐', 'en': 'Tree on mountain. Slow and steady progress.', 'ja': '山上有木、漸'},
        'meaning': {'zh': '象征渐进。预示循序渐进方能成功。', 'en': 'Represents gradual progress. Success through patience.', 'ja': '漸進を象徴。循序渐进 才能成功'} },
    54: {'name': '归妹', 'name_en': 'Guimei (Marriage)', 'name_ja': '帰妹', 'symbol': '☱☳',
        'judgement': {'zh': '征凶，无攸往', 'en': 'Marriage and commitment', 'ja': '征伐れば凶、攸往る无'},
        'image': {'zh': '泽上有雷，归妹', 'en': 'Thunder over marsh. Matters of union.', 'ja': '沢上に雷あり、帰妹'},
        'meaning': {'zh': '象征归妹。预示婚恋之事需谨慎。', 'en': 'Represents marriage. Be cautious about romantic matters.', 'ja': '帰妹を象徴。婚恋のこと 注意が必要'} },
    55: {'name': '丰', 'name_en': 'Feng (Abundance)', 'name_ja': '豊', 'symbol': '☲☳',
        'judgement': {'zh': '亨，王假之，勿忧，宜日中', 'en': 'Great abundance and glory', 'ja': '亨、王之れに假り、憂える勿れ、日中为宜し'},
        'image': {'zh': '雷电皆至，丰', 'en': 'Thunder and lightning together. Great prosperity.', 'ja': '雷电皆至る、豊'},
        'meaning': {'zh': '象征丰盛。预示繁荣昌盛，但需防盛极而衰。', 'en': 'Represents prosperity. Great times but beware of peak.', 'ja': '豊盛を象徴。繁栄昌盛だが、盛んすぎて衰えることに注意'} },
    56: {'name': '旅', 'name_en': 'Lv (Travel)', 'name_ja': '旅', 'symbol': '☶☲',
        'judgement': {'zh': '小亨，旅贞吉', 'en': 'Travel and wandering', 'ja': '小亨、旅貞吉'},
        'image': {'zh': '山上有火，旅', 'en': 'Fire on mountain. Travel and wandering life.', 'ja': '山上に火あり、旅'},
        'meaning': {'zh': '象征旅行。预示外出顺利，但需安分守己。', 'en': 'Represents travel. Smooth journey but behave properly.', 'ja': '旅行を象徴。お出かけ順調だが、分を守り己を安んじる'} },
    57: {'name': '巽', 'name_en': 'Xun (Wind)', 'name_ja': '巽', 'symbol': '☴☴',
        'judgement': {'zh': '小亨，利攸往，利见大人', 'en': 'Gentle penetration', 'ja': '小亨、攸往るに利く、大人の見るに利し'},
        'image': {'zh': '随风，巽', 'en': 'Wind follows wind. Gentle influence.', 'ja': '風に随う、巽'},
        'meaning': {'zh': '象征逊顺。预示柔和处事可获成功。', 'en': 'Represents gentleness. Soft approach brings success.', 'ja': '遜順を象徴。柔和に事によれば成功可'} },
    58: {'name': '兑', 'name_en': 'Dui (Joy)', 'name_ja': '兌', 'symbol': '☱☱',
        'judgement': {'zh': '亨，利贞', 'en': 'Joy and pleasure', 'ja': '亨、貞に利し'},
        'image': {'zh': '丽泽，兑', 'en': 'Two lakes together. Joy and pleasure.', 'ja': '麗沢、兌'},
        'meaning': {'zh': '象征喜悦。预示心情愉快，人际和谐。', 'en': 'Represents joy. Happy mood, harmonious relationships.', 'ja': '喜悅を象徴。気分愉快、人と仲良い'} },
    59: {'name': '涣', 'name_en': 'Huan (Dispersion)', 'name_ja': '渙', 'symbol': '☵☴',
        'judgement': {'zh': '亨，王假有庙，利涉大川，利贞', 'en': 'Dispersal and salvation', 'ja': '亨、王庙に假り、大川を涉るに利あり、貞に利し'},
        'image': {'zh': '风行水上，涣', 'en': 'Wind over water. Spreading and dispersing.', 'ja': '風水の上を 行、渙'},
        'meaning': {'zh': '象征涣散。预示困境将散，需团结人心。', 'en': 'Represents dispersion. Difficulties will disperse. Unite people.', 'ja': '渙散を象徴。困境散る、人心を団結させる必要がある'} },
    60: {'name': '节', 'name_en': 'Jie (Limitation)', 'name_ja': '節', 'symbol': '☵☱',
        'judgement': {'zh': '亨，苦节不可贞', 'en': 'Moderation and limitation', 'ja': '亨、苦節は貞とす可らず'},
        'image': {'zh': '泽上有水，节', 'en': 'Water in the marsh. Moderation in all things.', 'ja': '沢の上に水あり、節'},
        'meaning': {'zh': '象征节制。预示适度约束可致吉祥。', 'en': 'Represents moderation. Appropriate restraint brings good fortune.', 'ja': '節制を象徴。適度に約束すれば吉祥可得'} },
    61: {'name': '中孚', 'name_en': 'Zhongfu (Inner Truth)', 'name_ja': '中孚', 'symbol': '☴☱',
        'judgement': {'zh': '豚鱼吉，利涉大川，利贞', 'en': 'Sincere and faithful', 'ja': '豚魚吉、大川を涉るに利あり、貞に利し'},
        'image': {'zh': '泽上有风，中孚', 'en': 'Wind over marsh. Inner truth and sincerity.', 'ja': '沢の上に風あり、中孚'},
        'meaning': {'zh': '象征诚信。预示以诚待人可获信任。', 'en': 'Represents sincerity. Being honest gains trust.', 'ja': '誠実を象徴。誠以待人すれば信頼可得'} },
    62: {'name': '小过', 'name_en': 'Xiaoguo (Small Excess)', 'name_ja': '小過', 'symbol': '☶☴',
        'judgement': {'zh': '亨，利贞，可小事，不可大事', 'en': 'Small excess is okay', 'ja': '亨、貞に利し、小事には可、大事には不可'},
        'image': {'zh': '山上有雷，小过', 'en': 'Thunder on mountain. Small deviations acceptable.', 'ja': '山上に雷あり、小過'},
        'meaning': {'zh': '象征小过。预示小有偏差无碍大局。', 'en': 'Represents small excess. Minor deviations won\'t affect the big picture.', 'ja': '小過を象徴。小さな偏差は大局に影響なし'} },
    63: {'name': '既济', 'name_en': 'Jiji (Completion)', 'name_ja': '既济', 'symbol': '☵☲',
        'judgement': {'zh': '亨，小利贞，初吉终乱', 'en': 'After completion', 'ja': '亨、小利貞、初め吉にしてついに乱る'},
        'image': {'zh': '水在火上，既济', 'en': 'Water over fire. Something completed.', 'ja': '火上に水あり，既济'},
        'meaning': {'zh': '象征既成。预示事已成，但需防后乱。', 'en': 'Represents completion. Things done but watch for new troubles.', 'ja': '既成を象徴。事は已成ったが後の乱を防ぐ必要がある'} },
    64: {'name': '未济', 'name_en': 'Weiji (Incompletion)', 'name_ja': '未济', 'symbol': '☲☵',
        'judgement': {'zh': '亨，小狐汔济，濡其尾，无攸利', 'en': 'Before completion', 'ja': '亨、小狐沗じて济ぎ、其の尾を濡らす、攸往の利无'},
        'image': {'zh': '火在水上，未济', 'en': 'Fire over water. Things not yet complete.', 'ja': '水の上に火あり、未济'},
        'meaning': {'zh': '象征未成。预示时机未到，需继续努力。', 'en': 'Represents incompleteness. Not yet time. Keep working.', 'ja': '未成を象徴。時未到、引き続き努力が必要'} },
}


# 更新占卜类型定义
DIVINATION_TYPES['ziwei'] = {
    'name': '紫微斗数',
    'name_en': 'Ziwei Doushu',
    'name_ja': '紫微斗数',
    'description': '中国传统命理学，解读命宫12宫位',
    'icon': '🔮',
    'needs_birth_info': True
}

DIVINATION_TYPES['omikuji'] = {
    'name': 'おみくじ',
    'name_en': 'Omikuji',
    'name_ja': 'おみくじ',
    'description': '日本神社抽签，求签问卜',
    'icon': '🎍',
    'needs_birth_info': False
}

DIVINATION_TYPES['iching'] = {
    'name': '易经六爻',
    'name_en': 'I Ching Hexagrams',
    'name_ja': '易経六爻',
    'description': '中华传统智慧，64卦象解读',
    'icon': '📜',
    'needs_birth_info': False
}

# 系统提示词
SYSTEM_PROMPTS['ziwei'] = """你是一位精通中国紫微斗数命理的资深命理师，拥有30年实战经验。

解读风格要求：
1. 结合14主星和12宫位进行综合分析
2. 解读要具体到命主性格、运势走向、事业感情等方面
3. 适当运用命理术语，但要有通俗解释
4. 给出趋吉避凶的具体建议
5. 保持神秘感和仪式感

请使用{language}语进行解读。"""

SYSTEM_PROMPTS['omikuji'] = """你是一位熟悉日本神社文化的占卜师，精通おみくじ签文解读。

解读风格要求：
1. 以日式神社风格进行解读
2. 语言温柔但不失专业
3. 结合各运势项目给出具体建议
4. 适当引用日本文化元素
5. 给出实用的开运指南

请使用{language}语进行解读。"""

SYSTEM_PROMPTS['iching'] = """你是一位精通中国传统易经六爻的命理大师，深谙易学奥义。

解读风格要求：
1. 结合卦辞、象辞进行综合分析
2. 解读要具体到当前处境和未来走向
3. 适当运用易经术语，但要有通俗解释
4. 给出趋吉避凶的具体建议
5. 保持易经的神秘感和智慧感

请使用{language}语进行解读。"""


# ============ 新增占卜方法 ============

def calculate_ziwei_stars(birth_date: datetime, birth_time: str) -> Dict[str, Any]:
    """根据出生信息计算紫微斗数主星"""
    import hashlib
    
    # 使用出生日期时间生成一个哈希值，用于确定主星
    birth_str = birth_date.strftime('%Y%m%d') + birth_time.replace(':', '')
    hash_val = int(hashlib.md5(birth_str.encode()).hexdigest()[:8], 16)
    
    stars_list = list(ZIWEE_STARS.keys())
    palace_list = list(PALACE_INFO.keys())
    
    # 确定命宫主星（简化版）
    main_star_idx = hash_val % len(stars_list)
    main_star_key = stars_list[main_star_idx]
    
    # 分配12宫位的主星（简化分配）
    palace_stars = {}
    for i, palace in enumerate(palace_list):
        star_idx = (hash_val + i) % len(stars_list)
        palace_stars[palace] = stars_list[star_idx]
    
    return {
        'main_star': ZIWEE_STARS[main_star_key],
        'palace_stars': {palace: ZIWEE_STARS[star_key] for palace, star_key in palace_stars.items()},
        'birth_date': birth_date,
        'birth_time': birth_time
    }


def interpret_ziwei(self, birth_date: datetime, birth_time: str, question: str, language: str = 'zh') -> Dict[str, Any]:
    """紫微斗数解读"""
    system_prompt = SYSTEM_PROMPTS['ziwei']
    
    # 计算命盘
    chart = calculate_ziwei_stars(birth_date, birth_time)
    main_star = chart['main_star']
    
    user_message = f"""请为用户进行紫微斗数命盘分析：

基本信息：
- 出生日期：{birth_date.strftime('%Y年%m月%d日')}
- 出生时辰：{birth_time}
- 命宫主星：{main_star.get('name', '')} ({main_star.get('name_en', '')})
- 主星特质：{main_star.get('personality', '')}

用户问题：{question}

请进行全面的命盘解读：
1. 分析命宫主星的性格特质
2. 分析各宫位的主星组合
3. 给出运势分析和趋吉避凶建议"""

    full_response = ""
    for chunk in self.call_ai_api(system_prompt, user_message, language):
        full_response += chunk
    
    return {
        'chart': chart,
        'main_star': main_star,
        'interpretation': full_response,
        'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
    }


def draw_omikuji(self, language: str = 'zh') -> Dict[str, Any]:
    """抽取おみくじ"""
    import random
    
    # 随机抽取签运
    luck_types = list(OMIKUJI_TYPES.keys())
    # 加权概率：大吉、中吉、小吉、吉概率更高
    weights = [5, 10, 15, 20, 10, 15, 5, 8, 5, 3, 2, 2]  # 调整权重
    
    # 简单加权随机选择
    total = sum(weights)
    r = random.randint(1, total)
    cumulative = 0
    selected_type = '吉'
    for t, w in zip(luck_types, weights):
        cumulative += w
        if r <= cumulative:
            selected_type = t
            break
    
    result = OMIKUJI_TYPES[selected_type]
    fortune = OMIKUJI_FORTUNES.get(selected_type, OMIKUJI_FORTUNES.get('吉', {}))
    
    return {
        'type': selected_type,
        'type_info': result,
        'fortune': fortune.get(language, fortune.get('zh', {})),
        'fortune_zh': fortune.get('zh', {}),
        'fortune_en': fortune.get('en', {}),
        'fortune_ja': fortune.get('ja', {}),
    }


def interpret_omikuji(self, question: str, language: str = 'zh') -> Dict[str, Any]:
    """おみくじ解读"""
    system_prompt = SYSTEM_PROMPTS['omikuji']
    
    # 抽取签运
    omikuji = self.draw_omikuji(language)
    
    fortune_text = omikuji['fortune']
    if isinstance(fortune_text, dict):
        fortune_overall = fortune_text.get('overall', '')
    else:
        fortune_overall = fortune_text
    
    user_message = f"""请为用户解读おみくじ抽签结果：

抽签类型：{omikuji['type']} ({omikuji['type_info'].get('name_en', '')})

整体运势：
{fortune_overall}

用户问题：{question}

请进行详细的运势解读，包括：
1. 解释签运的含义
2. 结合用户问题给出具体建议
3. 提供开运指南"""

    full_response = ""
    for chunk in self.call_ai_api(system_prompt, user_message, language):
        full_response += chunk
    
    omikuji['interpretation'] = full_response
    omikuji['summary'] = full_response[:200] + "..." if len(full_response) > 200 else full_response
    
    return omikuji


def cast_coins(self) -> Dict[str, int]:
    """三枚硬币法起卦"""
    import random
    
    # 3枚硬币，每枚0-1，代表背面-正面
    coins = [random.randint(0, 1) for _ in range(3)]
    heads_count = sum(coins)
    
    # 3正 = 老阳(变阴) = 6
    # 2正1背 = 少阳(不变) = 7
    # 2背1正 = 少阴(不变) = 8
    # 3背 = 老阴(变阳) = 9
    
    if heads_count == 3:
        value = 6  # 老阳
    elif heads_count == 2:
        value = 7  # 少阳
    elif heads_count == 1:
        value = 8  # 少阴
    else:
        value = 9  # 老阴
    
    return {
        'coins': coins,
        'heads_count': heads_count,
        'value': value,
        'changing': value in [6, 9]  # 老阳和老阴为动爻
    }


def interpret_iching(self, question: str, language: str = 'zh') -> Dict[str, Any]:
    """易经六爻解读"""
    system_prompt = SYSTEM_PROMPTS['iching']
    
    # 起卦（3枚硬币法，6次）
    hexagram_lines = []
    changing_lines = []
    
    for i in range(6):
        cast = self.cast_coins()
        hexagram_lines.append(cast['value'])
        if cast['changing']:
            changing_lines.append(i + 1)  # 记录动爻位置（1-6）
    
    # 计算本卦和变卦
    # 上卦（外卦）：用第1-3爻
    upper = (hexagram_lines[0] % 3 if hexagram_lines[0] in [7, 8] else (hexagram_lines[0] % 3)) + \
            (hexagram_lines[1] % 3 if hexagram_lines[1] in [7, 8] else (hexagram_lines[1] % 3)) + \
            (hexagram_lines[2] % 3 if hexagram_lines[2] in [7, 8] else (hexagram_lines[2] % 3))
    upper = upper % 8 if upper % 8 != 0 else 8
    
    lower = (hexagram_lines[3] % 3 if hexagram_lines[3] in [7, 8] else (hexagram_lines[3] % 3)) + \
            (hexagram_lines[4] % 3 if hexagram_lines[4] in [7, 8] else (hexagram_lines[4] % 3)) + \
            (hexagram_lines[5] % 3 if hexagram_lines[5] in [7, 8] else (hexagram_lines[5] % 3))
    lower = lower % 8 if lower % 8 != 0 else 8
    
    # 简化卦数计算
    ben_gua_num = ((upper - 1) * 8 + lower) % 64 + 1
    if ben_gua_num == 0:
        ben_gua_num = 1
    
    # 计算变卦
    if changing_lines:
        bian_gua_lines = []
        for i, val in enumerate(hexagram_lines):
            if (i + 1) in changing_lines:
                # 阳变阴，阴变阳
                if val == 6:
                    bian_gua_lines.append(9)
                elif val == 9:
                    bian_gua_lines.append(6)
                elif val == 7:
                    bian_gua_lines.append(8)
                else:
                    bian_gua_lines.append(7)
            else:
                bian_gua_lines.append(val)
        
        # 计算变卦
        b_upper = sum(bian_gua_lines[:3]) % 8
        b_upper = b_upper if b_upper != 0 else 8
        b_lower = sum(bian_gua_lines[3:]) % 8
        b_lower = b_lower if b_lower != 0 else 8
        bian_gua_num = ((b_upper - 1) * 8 + b_lower) % 64 + 1
        if bian_gua_num == 0:
            bian_gua_num = 1
    else:
        bian_gua_num = ben_gua_num
        bian_gua_lines = hexagram_lines
    
    # 获取卦象信息
    ben_gua = ICHING_HEXAGRAMS.get(ben_gua_num, ICHING_HEXAGRAMS.get(1))
    bian_gua = ICHING_HEXAGRAMS.get(bian_gua_num, ICHING_HEXAGRAMS.get(1))
    
    # 生成卦象符号
    def hex_to_symbol(lines):
        symbol = ""
        for val in lines:
            if val in [7, 9]:  # 阳
                symbol += "━━━ "
            else:  # 阴
                symbol += "- - - "
        return symbol
    
    user_message = f"""请为用户解读易经六爻卦象：

【本卦】
卦名：{ben_gua.get('name', '')} ({ben_gua.get('name_en', '')})
卦辞：{ben_gua.get('judgement', {}).get(language, ben_gua.get('judgement', {}).get('zh', ''))}
象辞：{ben_gua.get('image', {}).get(language, ben_gua.get('image', {}).get('zh', ''))}

动爻位置：{changing_lines if changing_lines else '无'}

【变卦】
卦名：{bian_gua.get('name', '')} ({bian_gua.get('name_en', '')})
卦辞：{bian_gua.get('judgement', {}).get(language, bian_gua.get('judgement', {}).get('zh', ''))}
象辞：{bian_gua.get('image', {}).get(language, bian_gua.get('image', {}).get('zh', ''))}

用户问题：{question}

请进行全面的易经解读：
1. 解释本卦卦辞和象辞的含义
2. 分析变卦与本卦的变化
3. 结合用户问题给出具体指导
4. 给出趋吉避凶的建议"""

    full_response = ""
    for chunk in self.call_ai_api(system_prompt, user_message, language):
        full_response += chunk
    
    return {
        'ben_gua_num': ben_gua_num,
        'bian_gua_num': bian_gua_num,
        'ben_gua': ben_gua,
        'bian_gua': bian_gua,
        'hexagram_lines': hexagram_lines,
        'changing_lines': changing_lines,
        'interpretation': full_response,
        'summary': full_response[:200] + "..." if len(full_response) > 200 else full_response
    }


# 将新方法绑定到DivinationEngine类
DivinationEngine.interpret_ziwei = interpret_ziwei
DivinationEngine.draw_omikuji = draw_omikuji
DivinationEngine.interpret_omikuji = interpret_omikuji
DivinationEngine.cast_coins = cast_coins
DivinationEngine.interpret_iching = interpret_iching


# 全局占卜引擎实例
divination_engine = DivinationEngine()
