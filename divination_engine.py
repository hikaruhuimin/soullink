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


# 全局占卜引擎实例
divination_engine = DivinationEngine()
