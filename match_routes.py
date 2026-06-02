# SoulLink - 姻缘匹配模块
# 包含星座配对、AI红娘、个人资料卡功能

from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_login import current_user, login_required
from models import db, User
from datetime import datetime
import json
import random

match_bp = Blueprint('match', __name__, url_prefix='/match')

# ============ 星座配对数据 (12x12 = 144对) ============
ZODIAC_SIGNS = [
    'aries', 'taurus', 'gemini', 'cancer', 
    'leo', 'virgo', 'libra', 'scorpio',
    'sagittarius', 'capricorn', 'aquarius', 'pisces'
]

# 星座配对数据 - 综合匹配度、爱情、事业
ZODIAC_COMPATIBILITY = {
    # 白羊座 Aries
    ('aries', 'aries'): {'overall': 75, 'love': 70, 'career': 80, 'analysis_zh': '你们都是火象星座，充满活力与热情，但有时会因固执而产生摩擦。', 'advice_zh': ['学会倾听对方的想法', '给对方一些独立空间', '一起尝试新鲜事物'], 'analysis_en': 'You are both fire signs, full of energy and passion, but sometimes clash due to stubbornness.', 'advice_en': ['Listen to each other', 'Give space', 'Try new things together'], 'analysis_ja': 'どちらも火のエレメント、活力と情熱に満ちています。', 'advice_ja': ['相手の話を聞く', '空間に余裕を', '一緒に新鮮事を']},
    ('aries', 'taurus'): {'overall': 85, 'love': 90, 'career': 75, 'analysis_zh': '白羊的冲劲与金牛的稳重形成完美互补，感情升温迅速。', 'advice_zh': ['白羊多倾听金牛的想法', '金牛适当接受新挑战', '共同规划财务'], 'analysis_en': 'Aries impulse complements Taurus stability perfectly. Romance heats up quickly.', 'advice_en': ['Aries listen more', 'Taurus try new challenges', 'Plan finances together'], 'analysis_ja': '牡羊座の勢いと金牛座の安定が完璧に補完し合い、恋が早く発展します。', 'advice_ja': ['牡羊座は金牛座の想法を聞く', '金牛座は新しい挑戦を', '財政を一緒に計画']},
    ('aries', 'gemini'): {'overall': 80, 'love': 85, 'career': 70, 'analysis_zh': '白羊和双子都是好奇心旺盛的类型，一起探索世界会非常有趣。', 'advice_zh': ['接受彼此的多变性', '白羊学会慢下来', '保持沟通畅通'], 'analysis_en': 'Aries and Gemini both curious, exploring the world together is fun.', 'advice_en': ['Accept changes', 'Aries slow down', 'Keep communicating'], 'analysis_ja': '牡羊座と双子座はどちらも好奇心が強く、一緒に世界を探求はとても楽しい。', 'advice_ja': ['お互いの変化を受け入れる', '牡羊座はゆっくりする', '変わらず連絡を']},
    ('aries', 'cancer'): {'overall': 65, 'love': 75, 'career': 55, 'analysis_zh': '白羊的直接与巨蟹的敏感需要时间磨合，需要双方多些耐心。', 'advice_zh': ['白羊注意表达方式', '巨蟹尝试更直接', '建立情感安全感'], 'analysis_en': 'Aries directness meets Cancer sensitivity, needs patience.', 'advice_en': ['Aries be careful', 'Cancer be direct', 'Build emotional safety'], 'analysis_ja': '牡羊座の変化と巨蟹座の敏感さは時間がかかります。', 'advice_ja': ['牡羊座は表現に気をつけて', '巨蟹座はもっと直接的に', '安全感を作る']},
    ('aries', 'leo'): {'overall': 90, 'love': 95, 'career': 85, 'analysis_zh': '两个火象星座的强强联合，燃烧激情，注定精彩万分！', 'advice_zh': ['学会轮流当主角', '不要在小事上争强', '共同创造美好回忆'], 'analysis_en': 'Two fire signs combined, burning passion, destined for excitement!', 'advice_en': ['Take turns being the star', 'Dont compete on small things', 'Create memories together'], 'analysis_ja': '二つの火エレメントの組み合わせ、燃える情熱、素晴らしい結末に！', 'advice_ja': ['交替で主角に', '小さなことで争わない', '一緒に思い出を作る']},
    ('aries', 'virgo'): {'overall': 60, 'love': 55, 'career': 70, 'analysis_zh': '白羊的行动派与处女的分析派需要互相理解对方的方式。', 'advice_zh': ['处女多欣赏白羊的行动力', '白羊学习处女的细致', '在工作上合作更佳'], 'analysis_en': 'Aries action meets Virgo analysis, needs mutual understanding.', 'advice_en': ['Virgo appreciate action', 'Aries learn detail', 'Better working together'], 'analysis_ja': '牡羊座の行動力と乙女座の分析派はお互いの方法を変える必要があります。', 'advice_ja': ['乙女座は牡羊座の行動力を欣赏', '牡羊座は乙女座の細やかさを', '仕事での合作が良い']},
    ('aries', 'libra'): {'overall': 70, 'love': 80, 'career': 60, 'analysis_zh': '白羊的果断与天秤的和谐追求形成有趣张力，需要时间找到平衡。', 'advice_zh': ['天秤多给白羊肯定', '白羊学会妥协', '共同培养审美'], 'analysis_en': 'Aries decisiveness meets Libra harmony, need balance.', 'advice_en': ['Libra support Aries', 'Aries learn compromise', 'Cultivate aesthetics together'], 'analysis_ja': '牡羊座の変化と天秤座のバランス追求は面白い均衡が必要です。', 'advice_ja': ['天秤座は牡羊座を肯定的に', '牡羊座は妥协を学ぶ', '一緒に美的感覚を']},
    ('aries', 'scorpio'): {'overall': 88, 'love': 95, 'career': 80, 'analysis_zh': '火星家族的强强联手，情感深沉热烈，默契十足！', 'advice_zh': ['避免占有欲过强', '保持神秘感', '共同探索深层次话题'], 'analysis_en': 'Mars family connection, deep passion, great chemistry!', 'advice_en': ['Avoid possessiveness', 'Keep mystery', 'Explore deep topics'], 'analysis_ja': '火星家族の組み合わせ、深い情熱、最高の相性！', 'advice_ja': ['嫉妬を避け', '神秘感を保ち', '深い話題を探求']},
    ('aries', 'sagittarius'): {'overall': 92, 'love': 95, 'career': 85, 'analysis_zh': '火象三傻的两大代表，冒险精神满分，在一起永远不无聊！', 'advice_zh': ['共同规划旅行', '学会面对现实问题', '保持初见时的激情'], 'analysis_en': 'Two fire signs, full of adventure spirit, never boring together!', 'advice_en': ['Plan adventures together', 'Face reality', 'Keep the spark'], 'analysis_ja': '火エレメント代表、二人の冒険心は最高！', 'advice_ja': ['一緒に旅を計画', '現実問題に面对', '初めの情熱を保つ']},
    ('aries', 'capricorn'): {'overall': 65, 'love': 60, 'career': 85, 'analysis_zh': '白羊的热情与摩羯的务实需要找到共同目标才能长久。', 'advice_zh': ['摩羯欣赏白羊的创意', '白羊尊重摩羯的计划', '事业上合作更顺利'], 'analysis_en': 'Aries passion meets Capricorn practicality, need shared goals.', 'advice_en': ['Capricorn appreciate creativity', 'Aries respect plans', 'Better as work partners'], 'analysis_ja': '牡羊座の情熱と山羊座の务实は共通の目標が必要です。', 'advice_ja': ['山羊座は牡羊座の創造性を欣赏', '牡羊座は山羊座の計画を尊重', '仕事での合作がより良い']},
    ('aries', 'aquarius'): {'overall': 75, 'love': 70, 'career': 80, 'analysis_zh': '白羊的果断与水瓶的创新思维碰撞，惊喜不断。', 'advice_zh': ['接受彼此的独立性', '一起参与公益', '保持思想交流'], 'analysis_en': 'Aries decisiveness meets Aquarius innovation, constant surprises.', 'advice_en': ['Accept independence', 'Do charity together', 'Keep intellectual交流'], 'analysis_ja': '牡羊座の変化と水瓶座の革新思考が衝突、驚きが絶えない。', 'advice_ja': ['互いの獨立性を認め', '一緒に公益活動を', '知的交流を保つ']},
    ('aries', 'pisces'): {'overall': 68, 'love': 80, 'career': 55, 'analysis_zh': '白羊的火与双鱼的水需要找到和谐的相处方式。', 'advice_zh': ['白羊学会温柔表达', '双鱼更坚定一些', '共同创造浪漫氛围'], 'analysis_en': 'Fire meets water, need harmonious way of relating.', 'advice_en': ['Aries be gentler', 'Pisces be firmer', 'Create romance together'], 'analysis_ja': '牡羊座の火と魚座の水は穏やかな相处方法を見つける必要があります。', 'advice_ja': ['牡羊座は優しく表現し', '魚座はもっとしっかりして', '一緒にロマンチックな雰囲気を作る']},
    
    # 金牛座 Taurus
    ('taurus', 'gemini'): {'overall': 60, 'love': 55, 'career': 70, 'analysis_zh': '金牛的稳定与双子的多变需要时间适应。', 'advice_zh': ['双子给金牛安全感', '金牛尝试接受变化', '培养共同兴趣'], 'analysis_en': 'Taurus stability meets Gemini variability, needs adaptation.', 'advice_en': ['Gemini give security', 'Taurus accept changes', 'Cultivate common interests'], 'analysis_ja': '金牛座の安定と双子座の変化は時間がかかります。', 'advice_ja': ['双子座は金牛座に安全感を与え', '金牛座は変化を受け入れ', '共通の趣味を培養']},
    ('taurus', 'cancer'): {'overall': 95, 'love': 95, 'career': 85, 'analysis_zh': '土象与水象的完美搭配，情感深厚，互相照顾。', 'advice_zh': ['巨蟹多表达感激', '金牛保持浪漫', '共同建立温馨家庭'], 'analysis_en': 'Earth and water perfect match, deep emotions, caring.', 'advice_en': ['Cancer express gratitude', 'Taurus stay romantic', 'Build warm home together'], 'analysis_ja': '土エレメントと水エレメントの完璧な組み合わせ、深い愛情、お互い照顾。', 'advice_ja': ['巨蟹座は感謝を表現し', '金牛座はロマンチックを保ち', '一緒に温かい家庭を作る']},
    ('taurus', 'leo'): {'overall': 80, 'love': 85, 'career': 75, 'analysis_zh': '金牛的务实与狮子的华丽能互相欣赏，感情稳定。', 'advice_zh': ['狮子欣赏金牛的坚持', '金牛给狮子更多赞美', '共同享受生活乐趣'], 'analysis_en': 'Taurus practicality appreciated by Leo, stable relationship.', 'advice_en': ['Leo appreciate persistence', 'Taurus give compliments', 'Enjoy life together'], 'analysis_ja': '金牛座の务实と狮子座の华丽は互い欣赏、感情が安定。', 'advice_ja': ['狮子座は金牛座の坚持を欣赏', '金牛座は狮子座により多くの 찬사를', '一緒に人生の乐趣を楽しむ']},
    ('taurus', 'virgo'): {'overall': 90, 'love': 85, 'career': 95, 'analysis_zh': '两个土象星座的组合，踏实可靠，在一起非常舒适。', 'advice_zh': ['共同追求生活品质', '处女保持欣赏眼光', '金牛多表达爱意'], 'analysis_en': 'Two earth signs, reliable and comfortable together.', 'advice_en': ['Pursue quality together', 'Virgo stay appreciative', 'Taurus express more love'], 'analysis_ja': '二つの土エレメントの組み合わせ、踏实で心地いい。', 'advice_ja': ['一緒に生活の質を追求', '乙女座は欣赏眼光を保ち', '金牛座はもっと愛情を表現']},
    ('taurus', 'libra'): {'overall': 75, 'love': 80, 'career': 65, 'analysis_zh': '金牛与天秤都重视美感，在艺术和审美上有共鸣。', 'advice_zh': ['共同培养艺术爱好', '天秤帮助金牛社交', '金牛给天秤安全感'], 'analysis_en': 'Both value aesthetics, share artistic interests.', 'advice_en': ['Cultivate art together', 'Libra help socialize', 'Taurus give security'], 'analysis_ja': '金牛座と天秤座はどちらも美を重んじ、芸術的な共鸣があります。', 'advice_ja': ['一緒に芸術的な趣味を培養', '天秤座は金牛座の交友を助ける', '金牛座は天秤座に安全感を与える']},
    ('taurus', 'scorpio'): {'overall': 92, 'love': 95, 'career': 85, 'analysis_zh': '金钱观一致，感情深沉专一，灵魂伴侣的典型组合。', 'advice_zh': ['共同管理财务', '保持神秘感', '深入交流内心世界'], 'analysis_en': 'Same money values, deeply devoted, soulmate combination.', 'advice_en': ['Manage finances together', 'Keep mystery', 'Share inner world deeply'], 'analysis_ja': '金钱観が一致、感情が深く一的、魂の伴侣の組み合わせ。', 'advice_ja': ['一緒に財政を管理し', '神秘感を保ち', '内面の世界を深く交流']},
    ('taurus', 'sagittarius'): {'overall': 55, 'love': 60, 'career': 50, 'analysis_zh': '金牛的保守与射手向往自由，需要找到平衡点。', 'advice_zh': ['射手尊重金牛的稳定需求', '金牛给射手一定自由', '共同体验不同文化'], 'analysis_en': 'Taurus conservative meets Sagittarius freedom loving.', 'advice_en': ['Sagittarius respect stability', 'Taurus give freedom', 'Experience cultures together'], 'analysis_ja': '金牛座の保守と射手座の自由向往は平衡点を見つける必要があります。', 'advice_ja': ['射手座は金牛座の安定ニーズを尊重し', '金牛座は射手座にある程度の自由を', '違う文化を一緒に体験']},
    ('taurus', 'capricorn'): {'overall': 95, 'love': 90, 'career': 98, 'analysis_zh': '土象星座的终极组合，目标一致，在一起就是成功的人生搭档。', 'advice_zh': ['共同规划未来', '互相支持事业', '享受努力的成果'], 'analysis_en': 'Ultimate earth sign combo, shared goals, life success partners.', 'advice_en': ['Plan future together', 'Support careers', 'Enjoy achievements'], 'analysis_ja': '土エレメントの組み合わせの究極、目標が一致、人生の成功パートナー。', 'advice_ja': ['一緒に未来を計画し', '互いの仕事をサポート', '努力の成果を享受']},
    ('taurus', 'aquarius'): {'overall': 60, 'love': 55, 'career': 70, 'analysis_zh': '金牛的现实与水瓶的理想需要找到共同话题。', 'advice_zh': ['尊重彼此的想法', '水瓶理解金牛的实际需求', '在公益或社会活动中找到共鸣'], 'analysis_en': 'Taurus reality meets Aquarius ideals.', 'advice_en': ['Respect ideas', 'Aquarius understand practical needs', 'Find common ground in activities'], 'analysis_ja': '金牛座の現実と水瓶座の理想は共通の話題を見つける必要があります。', 'advice_ja': ['互いの想法を尊重し', '水瓶座は金牛座の実際なニーズを理解し', '公益や社会活動で共鸣を見つける']},
    ('taurus', 'pisces'): {'overall': 88, 'love': 92, 'career': 80, 'analysis_zh': '金牛与双鱼都是感官动物，在艺术和生活享受上高度契合。', 'advice_zh': ['共同创造艺术氛围', '双鱼给金牛更多情感支持', '金牛帮助双鱼实现梦想'], 'analysis_en': 'Both sensory, high compatibility in art and enjoyment.', 'advice_en': ['Create artistic atmosphere', 'Pisces give emotional support', 'Taurus help dreams'], 'analysis_ja': '金牛座と魚座はどちらも感覚派、芸術と生活享受で很高く契合。', 'advice_ja': ['一緒に芸術的な雾囲気を作り', '魚座は金牛座にもっと感情的なサポートを', '金牛座は魚座の夢を実現するのを助ける']},
    
    # 双子座 Gemini
    ('gemini', 'cancer'): {'overall': 70, 'love': 75, 'career': 65, 'analysis_zh': '双子的多变与巨蟹的稳定形成互补，需要多沟通。', 'advice_zh': ['双子多关注巨蟹情感需求', '巨蟹给双子表达空间', '共同建立情感安全感'], 'analysis_en': 'Gemini variability meets Cancer stability, need communication.', 'advice_en': ['Gemini focus on emotions', 'Cancer give space', 'Build emotional safety'], 'analysis_ja': '双子座の変化と螃蟹座の安定は補完し合いコミュニケーションが必要です。', 'advice_ja': ['双子座は巨蟹座の感情ニーズ的关注', '巨蟹座は双子座に表現空間を', '一緒に感情的安全感を作る']},
    ('gemini', 'leo'): {'overall': 80, 'love': 85, 'career': 75, 'analysis_zh': '双子的机智与狮子的华丽相互欣赏，在一起充满欢乐。', 'advice_zh': ['共同参与社交活动', '狮子欣赏双子的幽默', '双子给狮子足够关注'], 'analysis_en': 'Gemini wit appreciated by Leo, lots of fun together.', 'advice_en': ['Do social activities', 'Leo appreciate wit', 'Gemini give attention'], 'analysis_ja': '双子座の機知と狮子座の华丽は互い欣赏、一緒に楽しい。', 'advice_ja': ['一緒にソーシャル活動を', '狮子座は双子座のユーモアを欣赏', '双子座は狮子座に十分な关注を']},
    ('gemini', 'virgo'): {'overall': 78, 'love': 72, 'career': 88, 'analysis_zh': '都是沟通型星座，在想法和交流上非常默契。', 'advice_zh': ['共同学习新知识', '处女欣赏双子的多才多艺', '双子学习处女的专注'], 'analysis_en': 'Both communicative, great chemistry in ideas.', 'advice_en': ['Learn together', 'Virgo appreciate versatility', 'Gemini learn focus'], 'analysis_ja': 'どちらもコミュニケーション型星座、想法と交流がとても默契。', 'advice_ja': ['一緒に新しい知識を学び', '乙女座は双子座の多才を欣赏', '双子座は乙女座の专注を学ぶ']},
    ('gemini', 'libra'): {'overall': 92, 'love': 95, 'career': 80, 'analysis_zh': '风象星座的绝配组合，沟通无障碍，心灵高度契合！', 'advice_zh': ['共同参与艺术活动', '天秤欣赏双子的机智', '双子帮天秤做决定'], 'analysis_en': 'Air signs perfect match, effortless communication!', 'advice_en': ['Do art together', 'Libra appreciate wit', 'Gemini help decide'], 'analysis_ja': '風エレメントの組み合わせの完璧な組み合わせ、コミュニケーションが無障碍！', 'advice_ja': ['一緒に芸術活動を', '天秤座は双子座の機知を欣赏', '双子座は天秤座の決定を助ける']},
    ('gemini', 'scorpio'): {'overall': 68, 'love': 75, 'career': 75, 'analysis_zh': '双子的多变与天蝎的深沉需要深入了解对方。', 'advice_zh': ['双子给天蝎安全感', '天蝎帮助双子深入思考', '共同探索深层话题'], 'analysis_en': 'Gemini change meets Scorpio depth.', 'advice_en': ['Gemini give security', 'Scorpio help depth', 'Explore deep topics'], 'analysis_ja': '双子座の変化と天蝎座の深さは互い深入了解が必要です。', 'advice_ja': ['双子座は天蝎座に安全感を与え', '天蝎座は双子座の深い思考を助ける', '一緒に深い話題を探求']},
    ('gemini', 'sagittarius'): {'overall': 88, 'love': 90, 'career': 80, 'analysis_zh': '都是爱玩爱闹的类型，在一起永远不会无聊！', 'advice_zh': ['共同探索新事物', '射手欣赏双子的创意', '双子给射手带来新鲜感'], 'analysis_en': 'Both love fun and adventure, never boring together!', 'advice_en': ['Explore new things', 'Sagittarius appreciate creativity', 'Gemini bring freshness'], 'analysis_ja': 'どちらも遊ぶのが好きなタイプ、一緒に、決して无聊ではない！', 'advice_ja': ['一緒に新しいことを探求し', '射手座は双子座の創造性を欣赏', '双子座は射手座に新鲜感をもたらす']},
    ('gemini', 'capricorn'): {'overall': 55, 'love': 50, 'career': 75, 'analysis_zh': '双子与摩羯在节奏上差异较大，需要相互理解。', 'advice_zh': ['摩羯给双子更多耐心', '双子理解摩羯的严肃', '在专业领域合作更佳'], 'analysis_en': 'Different paces, need understanding.', 'advice_en': ['Capricorn be patient', 'Gemini understand seriousness', 'Better working together'], 'analysis_ja': '双子座と山羊座はリズムが大きく異なり、相互理解が必要です。', 'advice_ja': ['山羊座は双子座にもっと忍耐を', '双子座は山羊座の严肃を理解し', '専門分野での合作がより良い']},
    ('gemini', 'aquarius'): {'overall': 95, 'love': 90, 'career': 88, 'analysis_zh': '风象星座的超级组合，思想高度同步，是最佳灵魂伴侣！', 'advice_zh': ['共同参与创新项目', '水瓶欣赏双子的想法', '双子给水瓶带来活力'], 'analysis_en': 'Air signs super combo, highly synced, best soulmates!', 'advice_en': ['Do innovation together', 'Aquarius appreciate ideas', 'Gemini bring energy'], 'analysis_ja': '風エレメントの組み合わせの超級組み合わせ、思想高度同期！', 'advice_ja': ['一緒にイノベーションプロジェクトに', '水瓶座は双子座の想法を欣赏', '双子座は水瓶座に活力をもたらす']},
    ('gemini', 'pisces'): {'overall': 70, 'love': 78, 'career': 60, 'analysis_zh': '双子的理性与双鱼的感性需要找到平衡。', 'advice_zh': ['双子学会倾听情感', '双鱼给双子温暖', '共同参与艺术创作'], 'analysis_en': 'Gemini rationality meets Pisces emotion.', 'advice_en': ['Gemini listen emotionally', 'Pisces give warmth', 'Do creative work together'], 'analysis_ja': '双子座の理性と魚座の感性はず平衡を見つける必要があります。', 'advice_ja': ['双子座は感情的に聞き', '魚座は双子座に温かさを与え', '一緒に芸術創作に参加']},
    
    # 巨蟹座 Cancer
    ('cancer', 'leo'): {'overall': 75, 'love': 80, 'career': 65, 'analysis_zh': '巨蟹的细腻与狮子的张扬需要学会欣赏对方的不同。', 'advice_zh': ['狮子多关注巨蟹情感', '巨蟹给狮子温暖后盾', '共同经营家庭生活'], 'analysis_en': 'Cancer sensitivity meets Leo boldness, need appreciation.', 'advice_en': ['Leo focus on emotions', 'Cancer be warm support', 'Build home life together'], 'analysis_ja': '巨蟹座の細やかさと狮子座のちょうようは互い欣赏する必要があります。', 'advice_ja': ['狮子座は巨蟹座の感情关注', '巨蟹座は狮子座に温かいサポートを', '一緒に家庭生活を営む']},
    ('cancer', 'virgo'): {'overall': 88, 'love': 90, 'career': 82, 'analysis_zh': '水象与土象的完美搭配，细腻与务实的结合。', 'advice_zh': ['共同打造温馨家庭', '处女欣赏巨蟹的付出', '巨蟹学习处女的条理'], 'analysis_en': 'Water and earth perfect match, sensitivity meets practicality.', 'advice_en': ['Build warm home', 'Virgo appreciate efforts', 'Cancer learn organization'], 'analysis_ja': '水エレメントと土エレメントの完璧な組み合わせ、繊細さと务实の結合。', 'advice_ja': ['一緒に温かい家庭を作り', '乙女座は巨蟹座の寄托を欣赏', '巨蟹座は乙女座の筋道を立てるを学ぶ']},
    ('cancer', 'libra'): {'overall': 78, 'love': 85, 'career': 70, 'analysis_zh': '巨蟹与天秤都重视关系，在感情上能互相支持。', 'advice_zh': ['共同维护社交圈', '天秤帮巨蟹走出家门', '巨蟹给天秤情感支持'], 'analysis_en': 'Both value relationships, support each other emotionally.', 'advice_en': ['Maintain social circles', 'Libra help socialize', 'Cancer give emotional support'], 'analysis_ja': '巨蟹座と天秤座はどちらも関係を重んじ、感情的に互いサポートできる。', 'advice_ja': ['一緒にソーシャルサークルを維持し', '天秤座は巨蟹座の外出を手伝い', '巨蟹座は天秤座に感情サポートを']},
    ('cancer', 'scorpio'): {'overall': 98, 'love': 98, 'career': 90, 'analysis_zh': '同属水象星座，情感深度无与伦比，是命中注定的灵魂伴侣！', 'advice_zh': ['共同探索情感深度', '保持情感交流', '互相扶持度过难关'], 'analysis_en': 'Water signs, unparalleled emotional depth, destined soulmates!', 'advice_en': ['Explore emotional depth together', 'Keep emotional communication', 'Support each other through difficulties'], 'analysis_ja': 'どちらも水エレメント、感情の深さ无敌の組み合わせ！', 'advice_ja': ['一緒に感情の深さを探求し', '感情交流を保ち', '困難を乗り越えて互いサポート']},
    ('cancer', 'sagittarius'): {'overall': 55, 'love': 60, 'career': 50, 'analysis_zh': '巨蟹的恋家与射手的向往自由需要协调。', 'advice_zh': ['射手理解巨蟹的恋家情结', '巨蟹给射手自由空间', '共同规划家庭旅行'], 'analysis_en': 'Cancer homebody meets Sagittarius freedom lover.', 'advice_en': ['Sagittarius understand attachment', 'Cancer give space', 'Plan trips together'], 'analysis_ja': '巨蟹座的家庭想と射手座の自由向往は協調が必要です。', 'advice_ja': ['射手座は巨蟹座の家庭性質を考慮し', '巨蟹座は射手座に自由空間を', '一緒に家族の旅を計画']},
    ('cancer', 'capricorn'): {'overall': 82, 'love': 85, 'career': 88, 'analysis_zh': '水与土的结合，情感与责任的平衡，在一起能共同成长。', 'advice_zh': ['共同规划家庭未来', '摩羯给巨蟹安全感', '巨蟹给摩羯温暖'], 'analysis_en': 'Water and earth, emotional balance with responsibility.', 'advice_en': ['Plan family future', 'Capricorn give security', 'Cancer give warmth'], 'analysis_ja': '水と土の組み合わせ、感情と責任のバランス、一緒に成長できる。', 'advice_ja': ['一緒に家族の未来を計画し', '山羊座は巨蟹座に安全感を与え', '巨蟹座は山羊座に温かさを']},
    ('cancer', 'aquarius'): {'overall': 65, 'love': 70, 'career': 72, 'analysis_zh': '巨蟹与水瓶在情感表达上需要更多理解。', 'advice_zh': ['水瓶理解巨蟹的情感需求', '巨蟹接受水瓶的独立性', '共同参与社会活动'], 'analysis_en': 'Different emotional expression styles.', 'advice_en': ['Aquarius understand emotions', 'Cancer accept independence', 'Do social activities together'], 'analysis_ja': '巨蟹座と水瓶座は感情表現でもっと理解が必要です。', 'advice_ja': ['水瓶座は巨蟹座の感情ニーズを理解し', '巨蟹座は水瓶座の獨立性をometers', '一緒に社会活動に参加']},
    ('cancer', 'pisces'): {'overall': 95, 'love': 98, 'career': 85, 'analysis_zh': '两个水象星座的梦幻组合，情感丰富，互相理解，是最温柔的伴侣。', 'advice_zh': ['共同创造浪漫氛围', '互相给予情感支持', '一起追求精神成长'], 'analysis_en': 'Water signs dreamy combo, emotionally rich, most tender couple.', 'advice_en': ['Create romance together', 'Give emotional support', 'Pursue spiritual growth together'], 'analysis_ja': '二つの水エレメントの組み合わせ、感情豊富、互いの理解、一番優しい伴侣。', 'advice_ja': ['一緒にロマンチックな雰囲気を作り', '互いに感情サポートを', '一緒に精神的な成長を追求']},
    
    # 狮子座 Leo
    ('leo', 'virgo'): {'overall': 65, 'love': 60, 'career': 75, 'analysis_zh': '狮子的张扬与处女的低调需要互相适应。', 'advice_zh': ['狮子学会谦逊', '处女多给狮子赞美', '工作上合作更顺畅'], 'analysis_en': 'Leo boldness meets Virgo low-key.', 'advice_en': ['Leo be humble', 'Virgo give compliments', 'Better working together'], 'analysis_ja': '狮子座の変化と乙女座の低调はお互い适应が必要です。', 'advice_ja': ['狮子座は謙遜を学び', '乙女座は狮子座により多くの 찬사를', '仕事での合作がより顺畅']},
    ('leo', 'libra'): {'overall': 88, 'love': 92, 'career': 80, 'analysis_zh': '火与风的组合，互相欣赏，在社交场合非常合拍。', 'advice_zh': ['共同参与社交活动', '天秤帮狮子调解关系', '狮子给天秤自信'], 'analysis_en': 'Fire and air, mutual appreciation, great together socially.', 'advice_en': ['Do social events together', 'Libra mediate', 'Leo give Libra confidence'], 'analysis_ja': '火と風の組み合わせ、互い欣赏、社交場でとても合っている。', 'advice_ja': ['一緒にソーシャルイベントに', '天秤座は狮子座の関係調整を手伝い', '狮子座は天秤座に自信を']},
    ('leo', 'scorpio'): {'overall': 82, 'love': 88, 'career': 78, 'analysis_zh': '两个强势星座的碰撞，情感激烈，需要学会妥协。', 'advice_zh': ['学会轮流让步', '狮子欣赏天蝎的深沉', '天蝎给狮子安全感'], 'analysis_en': 'Two strong signs, intense emotions, need compromise.', 'advice_en': ['Take turns conceding', 'Leo appreciate depth', 'Scorpio give security'], 'analysis_ja': '二つの強い星座の衝突、感情激しく、妥协を学ぶ必要があります。', 'advice_ja': ['交替で譲り合い', '狮子座は天蝎座の深さを欣赏', '天蝎座は狮子座に安全感を与える']},
    ('leo', 'sagittarius'): {'overall': 92, 'love': 95, 'career': 88, 'analysis_zh': '火象星座的欢乐组合，在一起永远充满正能量！', 'advice_zh': ['共同追求人生目标', '射手欣赏狮子的领导力', '狮子给射手舞台'], 'analysis_en': 'Fire signs happy combo, always full of positive energy!', 'advice_en': ['Pursue goals together', 'Sagittarius appreciate leadership', 'Leo give stage'], 'analysis_ja': '火エレメントの組み合わせの楽しい組み合わせ、一緒にいつも正能量满满！', 'advice_ja': ['一緒に人生の目標を追求し', '射手座は狮子座のリーダーシップを欣赏', '狮子座は射手座にステージを']},
    ('leo', 'capricorn'): {'overall': 75, 'love': 72, 'career': 90, 'analysis_zh': '狮子与摩羯都是领导者，在权力分配上需要智慧。', 'advice_zh': ['明确分工角色', '摩羯欣赏狮子的创意', '狮子给摩羯活力'], 'analysis_en': 'Both leaders, need wisdom in power distribution.', 'advice_en': ['Clarify roles', 'Capricorn appreciate creativity', 'Leo give energy'], 'analysis_ja': '狮子座と山羊座はどちらもリーダーシップ、権利配分で智慧が必要です。', 'advice_ja': ['役割を明確にし', '山羊座は狮子座の創造性を欣赏', '狮子座は山羊座に活力を']},
    ('leo', 'aquarius'): {'overall': 78, 'love': 80, 'career': 85, 'analysis_zh': '狮子的领导力与水瓶的创新思维能创造不凡成就。', 'advice_zh': ['共同参与创新项目', '水瓶给狮子新视野', '狮子展现领导魅力'], 'analysis_en': 'Leo leadership meets Aquarius innovation.', 'advice_en': ['Do innovation projects', 'Aquarius give new perspectives', 'Leo show leadership'], 'analysis_ja': '狮子座のリーダーシップと水瓶座の革新思考は不凡な成果を創造できる。', 'advice_ja': ['一緒にイノベーションプロジェクトに', '水瓶座は狮子座に新しい視野を', '狮子座はリーダーシップの魅力を示す']},
    ('leo', 'pisces'): {'overall': 80, 'love': 88, 'career': 70, 'analysis_zh': '火与水的组合，感情丰富浪漫，需要学会理解对方。', 'advice_zh': ['狮子学会温柔倾听', '双鱼给狮子情感支持', '共同创造浪漫回忆'], 'analysis_en': 'Fire and water, emotionally romantic.', 'advice_en': ['Leo listen gently', 'Pisces give emotional support', 'Create romantic memories'], 'analysis_ja': '火と水の組み合わせ、感情豊富でロマンチック、お互いの理解が必要です。', 'advice_ja': ['狮子座は優しく聞き', '魚座は狮子座に感情サポートを', '一緒にロマンチックな思い出を作る']},
    
    # 处女座 Virgo
    ('virgo', 'libra'): {'overall': 72, 'love': 68, 'career': 85, 'analysis_zh': '处女与天秤都追求完美，在一起能互相欣赏。', 'advice_zh': ['共同追求生活品质', '天秤帮处女社交', '处女帮天秤务实'], 'analysis_en': 'Both pursue perfection, appreciate each other.', 'advice_en': ['Pursue quality together', 'Libra help socialize', 'Virgo help be practical'], 'analysis_ja': '乙女座と天秤座はどちらも完璧を追求、一緒に互い欣赏できる。', 'advice_ja': ['一緒に生活の質を追求し', '天秤座は乙女座の交友を手伝い', '乙女座は天秤座に务实を']},
    ('virgo', 'scorpio'): {'overall': 90, 'love': 92, 'career': 88, 'analysis_zh': '土与水的组合，务实与深情的完美结合。', 'advice_zh': ['共同分析问题', '天蝎给处女情感深度', '处女给天蝎实际支持'], 'analysis_en': 'Earth and water, practicality meets depth.', 'advice_en': ['Analyze problems together', 'Scorpio give depth', 'Virgo give practical support'], 'analysis_ja': '土と水の組み合わせ、务实と深情の完璧な結合。', 'advice_ja': ['一緒に問題を分析し', '天蝎座は乙女座に感情の深さを', '乙女座は天蝎座に実際なサポートを']},
    ('virgo', 'sagittarius'): {'overall': 60, 'love': 58, 'career': 75, 'analysis_zh': '处女的细致与射手的粗犷需要找到平衡。', 'advice_zh': ['射手尊重处女的秩序', '处女给射手一定自由', '共同体验不同文化'], 'analysis_en': 'Virgo detail meets Sagittarius carelessness.', 'advice_en': ['Sagittarius respect order', 'Virgo give some freedom', 'Experience cultures together'], 'analysis_ja': '乙女座の詳細さと射手座の粗雜は平衡を見つける必要があります。', 'advice_ja': ['射手座は乙女座の秩序を尊重し', '乙女座は射手座にある程度の自由を', '違う文化を一緒に体験']},
    ('virgo', 'capricorn'): {'overall': 95, 'love': 90, 'career': 98, 'analysis_zh': '两个土象星座的完美组合，目标一致，追求卓越。', 'advice_zh': ['共同规划职业发展', '互相支持事业', '一起享受成功的果实'], 'analysis_en': 'Two earth signs perfect combo, shared goals, pursue excellence.', 'advice_en': ['Plan career together', 'Support each other', 'Enjoy success together'], 'analysis_ja': '二つの土エレメントの組み合わせの完璧な組み合わせ、目標一致、卓越を追求。', 'advice_ja': ['一緒にキャリア開発を計画し', '互いの仕事をサポートし', '一緒に成功の成果を楽しむ']},
    ('virgo', 'aquarius'): {'overall': 68, 'love': 62, 'career': 85, 'analysis_zh': '处女的务实与水瓶的理想在工作中能互补。', 'advice_zh': ['水瓶理解处女的需求', '处女接受水瓶的创新', '在工作上合作更佳'], 'analysis_en': 'Virgo practicality meets Aquarius ideals.', 'advice_en': ['Aquarius understand needs', 'Virgo accept innovation', 'Better working together'], 'analysis_ja': '乙女座の务实と水瓶座の理想は仕事でも補完し合える。', 'advice_ja': ['水瓶座は乙女座のニーズを理解し', '乙女座は水瓶座のイノベーションを受け入れ', '仕事での合作がより良い']},
    ('virgo', 'pisces'): {'overall': 85, 'love': 88, 'career': 80, 'analysis_zh': '土与水的组合，处女的务实能帮助双鱼实现梦想。', 'advice_zh': ['处女帮助双鱼务实', '双鱼给处女灵感和情感', '共同参与艺术或灵性活动'], 'analysis_en': 'Earth helps water achieve dreams.', 'advice_en': ['Virgo help Pisces be practical', 'Pisces give inspiration', 'Do art or spiritual activities'], 'analysis_ja': '土と水の組み合わせ、乙女座の务实は魚座の夢実現を助ける。', 'advice_ja': ['乙女座は魚座を务实的に助け', '魚座は乙女座に靈感と感情を', '芸術や靈性活動に参加']},
    
    # 天秤座 Libra
    ('libra', 'scorpio'): {'overall': 82, 'love': 88, 'career': 78, 'analysis_zh': '天秤与天蝎的关系充满张力，情感深沉。', 'advice_zh': ['天蝎帮助天秤深入', '天秤给天蝎和谐感', '共同探索生命意义'], 'analysis_en': 'Libra and Scorpio tension, deep emotions.', 'advice_en': ['Scorpio help Libra go deeper', 'Libra give harmony', 'Explore life meaning together'], 'analysis_ja': '天秤座と天蝎座の関係は緊張感满满、感情が深い。', 'advice_ja': ['天蝎座は天秤座を深くするのを助け', '天秤座は天蝎座に和谐感を', '一緒に生命の意味を探求']},
    ('libra', 'sagittarius'): {'overall': 85, 'love': 88, 'career': 80, 'analysis_zh': '风与火的组合，在社交和探索上非常合拍。', 'advice_zh': ['共同参与社交活动', '射手帮天秤做决定', '天秤给射手审美支持'], 'analysis_en': 'Air and fire, great for socializing and exploring.', 'advice_en': ['Do social activities', 'Sagittarius help decide', 'Libra give aesthetic support'], 'analysis_ja': '風と火の組み合わせ、社交と探求がとても合っている。', 'advice_ja': ['一緒にソーシャル活動を', '射手座は天秤座の決定を手伝い', '天秤座は射手座に美的サポートを']},
    ('libra', 'capricorn'): {'overall': 78, 'love': 75, 'career': 90, 'analysis_zh': '天秤的社交与摩羯的务实能形成良好平衡。', 'advice_zh': ['共同规划未来', '摩羯帮天秤落地', '天秤帮摩羯社交'], 'analysis_en': 'Libra socializing meets Capricorn practicality.', 'advice_en': ['Plan future together', 'Capricorn help ground', 'Libra help socialize'], 'analysis_ja': '天秤座の社交と山羊座の务实は良いバランスを形成できる。', 'advice_ja': ['一緒に未来を計画し', '山羊座は天秤座を地に足を付けさせ', '天秤座は山羊座の交友を助ける']},
    ('libra', 'aquarius'): {'overall': 88, 'love': 85, 'career': 88, 'analysis_zh': '风象星座的组合，思维同步，在人际和理想上高度契合。', 'advice_zh': ['共同参与公益', '水瓶给天秤新视野', '天秤帮水瓶落地'], 'analysis_en': 'Air signs, synced thinking, high compatibility.', 'advice_en': ['Do charity together', 'Aquarius give new perspectives', 'Libra help ground'], 'analysis_ja': '風エレメントの組み合わせ、思想同期、人間関係と理想で高度に契合。', 'advice_ja': ['一緒に公益活動を', '水瓶座は天秤座に新しい視野を', '天秤座は水瓶座を地に足を付けさせる']},
    ('libra', 'pisces'): {'overall': 88, 'love': 92, 'career': 75, 'analysis_zh': '风与水的组合，浪漫敏感，在艺术和感情上共鸣强烈。', 'advice_zh': ['共同创造艺术氛围', '天秤给双鱼社交支持', '双鱼给天秤情感深度'], 'analysis_en': 'Air and water, romantic and sensitive, strong artistic resonance.', 'advice_en': ['Create artistic atmosphere', 'Libra give social support', 'Pisces give emotional depth'], 'analysis_ja': '風と水の組み合わせ、ロマンチックで敏感、芸術と感情で強い共鸣。', 'advice_ja': ['一緒に芸術的な雾囲気を作り', '天秤座は魚座に社交サポートを', '魚座は天秤座に感情の深さを']},
    
    # 天蝎座 Scorpio
    ('scorpio', 'sagittarius'): {'overall': 72, 'love': 75, 'career': 70, 'analysis_zh': '水与火的组合，情感激烈，需要相互理解。', 'advice_zh': ['射手尊重天蝎的深沉', '天蝎给射手信任', '共同探索人生哲学'], 'analysis_en': 'Water and fire, intense emotions, need understanding.', 'advice_en': ['Sagittarius respect depth', 'Scorpio give trust', 'Explore philosophy together'], 'analysis_ja': '水と火の組み合わせ、感情が激しく、相互理解が必要です。', 'advice_ja': ['射手座は天蝎座の変化を考慮し', '天蝎座は射手座に信頼を', '一緒に人生の哲学を探求']},
    ('scorpio', 'capricorn'): {'overall': 92, 'love': 90, 'career': 95, 'analysis_zh': '水与土的深沉组合，目标导向，在一起能创造非凡成就。', 'advice_zh': ['共同规划人生目标', '摩羯给天蝎稳定感', '天蝎给摩羯情感深度'], 'analysis_en': 'Water and earth deep combo, goal-oriented, extraordinary achievements.', 'advice_en': ['Plan life goals together', 'Capricorn give stability', 'Scorpio give depth'], 'analysis_ja': '水と土の深い組み合わせ、目標指向、一緒に不凡な成果を創れる。', 'advice_ja': ['一緒に人生の目標を計画し', '山羊座は天蝎座に安定感を与え', '天蝎座は山羊座に感情の深さを']},
    ('scorpio', 'aquarius'): {'overall': 75, 'love': 72, 'career': 82, 'analysis_zh': '天蝎的深沉与水瓶的理性需要找到平衡。', 'advice_zh': ['水瓶理解天蝎的情感', '天蝎接受水瓶的独立性', '共同参与创新项目'], 'analysis_en': 'Scorpio depth meets Aquarius rationality.', 'advice_en': ['Aquarius understand emotions', 'Scorpio accept independence', 'Do innovation projects'], 'analysis_ja': '天蝎座の変化と水瓶座の理性は平衡を見つける必要があります。', 'advice_ja': ['水瓶座は天蝎座の感情を理解し', '天蝎座は水瓶座の獨立性をometers', '一緒にイノベーションプロジェクトに参加']},
    ('scorpio', 'pisces'): {'overall': 95, 'love': 98, 'career': 88, 'analysis_zh': '两个水象星座的深刻组合，灵魂高度契合，是最懂彼此的伴侣！', 'advice_zh': ['共同探索情感深度', '互相给予精神支持', '一起成长进化'], 'analysis_en': 'Water signs deep combo, soul-highly synced, most understanding couple!', 'advice_en': ['Explore emotional depth together', 'Give spiritual support', 'Grow together'], 'analysis_ja': '二つの水エレメントの組み合わせ、魂高度契合、一番互いの理解がある伴侣！', 'advice_ja': ['一緒に感情の深さを探求し', '互いに精神的サポートを', '一緒に成長進化']},
    
    # 射手座 Sagittarius
    ('sagittarius', 'capricorn'): {'overall': 70, 'love': 65, 'career': 85, 'analysis_zh': '火与土的组合，在事业上能互补但生活节奏不同。', 'advice_zh': ['明确分工角色', '射手理解摩羯的责任感', '摩羯给射手方向感'], 'analysis_en': 'Fire and earth, complement in career but different life paces.', 'advice_en': ['Clarify roles', 'Sagittarius understand responsibility', 'Capricorn give direction'], 'analysis_ja': '火と土の組み合わせ、仕事では補完し合えますが生活のりは異なります。', 'advice_ja': ['役割を明確にし', '射手座は山羊座の責任感をometers', '山羊座は射手座に進路感を']},
    ('sagittarius', 'aquarius'): {'overall': 85, 'love': 82, 'career': 88, 'analysis_zh': '火与风的组合，在创新和探索上非常合拍。', 'advice_zh': ['共同参与公益或创新', '水瓶给射手新视野', '射手给水瓶行动力'], 'analysis_en': 'Fire and air, great for innovation and exploration.', 'advice_en': ['Do charity or innovation', 'Aquarius give perspectives', 'Sagittarius give action'], 'analysis_ja': '火と風の組み合わせ、イノベーションと探求がとても合っている。', 'advice_ja': ['一緒に公益やイノベーションに', '水瓶座は射手座に新しい視野を', '射手座は水瓶座に行動力を']},
    ('sagittarius', 'pisces'): {'overall': 78, 'love': 85, 'career': 68, 'analysis_zh': '火与水的组合，感情丰富浪漫，但需要学会沟通。', 'advice_zh': ['射手学会倾听', '双鱼给射手温柔', '共同追求精神成长'], 'analysis_en': 'Fire and water, emotionally romantic, need communication.', 'advice_en': ['Sagittarius listen more', 'Pisces give tenderness', 'Pursue spiritual growth together'], 'analysis_ja': '火と水の組み合わせ、感情豊富でロマンチック、コミュニケーションが必要です。', 'advice_ja': ['射手座はもっと聞き', '魚座は射手座に優しく', '一緒に精神的な成長を追求']},
    
    # 摩羯座 Capricorn
    ('capricorn', 'aquarius'): {'overall': 78, 'love': 72, 'career': 92, 'analysis_zh': '土与风的组合，务实与创新的结合，在事业上能创造成绩。', 'advice_zh': ['共同规划事业发展', '水瓶给摩羯新思维', '摩羯给水瓶执行力'], 'analysis_en': 'Earth and air, practicality meets innovation, career success.', 'advice_en': ['Plan career together', 'Aquarius give new thinking', 'Capricorn give execution'], 'analysis_ja': '土と風の組み合わせ、务实とイノベーションの結合、仕事で成果を挙げられる。', 'advice_ja': ['一緒にキャリア発達を計画し', '水瓶座は山羊座に新しい思考を', '山羊座は水瓶座に執行力を']},
    ('capricorn', 'pisces'): {'overall': 88, 'love': 90, 'career': 85, 'analysis_zh': '土与水的组合，务实与浪漫并存，能共同实现梦想。', 'advice_zh': ['摩羯帮助双鱼落地', '双鱼给摩羯灵感和浪漫', '共同规划财务目标'], 'analysis_en': 'Earth and water, practical yet romantic, achieve dreams together.', 'advice_en': ['Capricorn help ground', 'Pisces give inspiration', 'Plan financial goals together'], 'analysis_ja': '土と水の組み合わせ、务实とロマンチック并存、夢を実現できる。', 'advice_ja': ['山羊座は魚座を地に足を付けさせ', '魚座は山羊座に靈感とロマンを', '一緒に財政目標を立てる']},
    
    # 水瓶座 Aquarius
    ('aquarius', 'pisces'): {'overall': 82, 'love': 88, 'career': 78, 'analysis_zh': '风与水的组合，思想与情感的平衡，在精神层面高度契合。', 'advice_zh': ['共同参与灵性活动', '水瓶理解双鱼的敏感', '双鱼给水瓶情感支持'], 'analysis_en': 'Air and water, thought meets emotion, spiritually synced.', 'advice_en': ['Do spiritual activities', 'Aquarius understand sensitivity', 'Pisces give emotional support'], 'analysis_ja': '風と水の組み合わせ、思想と感情のバランス、精神面で高度に契合。', 'advice_ja': ['一緒に靈性活動に参加し', '水瓶座は魚座の敏感さをometers', '魚座は水瓶座に感情サポートを']},
}


def get_zodiac_compatibility(zodiac1, zodiac2, lang='zh'):
    """获取两个星座的配对数据"""
    key = (zodiac1.lower(), zodiac2.lower())
    reverse_key = (zodiac2.lower(), zodiac1.lower())
    
    data = ZODIAC_COMPATIBILITY.get(key) or ZODIAC_COMPATIBILITY.get(reverse_key)
    
    if not data:
        # 默认数据
        return {
            'overall': 70, 'love': 70, 'career': 70,
            'analysis': '星座配对数据查询中...',
            'advice': ['多沟通多了解', '尊重彼此差异']
        }
    
    lang_key = 'zh' if lang == 'zh' else ('en' if lang == 'en' else 'ja')
    
    return {
        'overall': data['overall'],
        'love': data['love'],
        'career': data['career'],
        'analysis': data.get(f'analysis_{lang_key}', data.get('analysis_zh', '')),
        'advice': data.get(f'advice_{lang_key}', data.get('advice_zh', []))
    }


def calculate_zodiac(birthday):
    """根据生日计算星座"""
    if not birthday:
        return None
    
    if isinstance(birthday, str):
        try:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        except:
            return None
    
    month = birthday.month
    day = birthday.day
    
    zodiac_dates = {
        'aries': (3, 21), 'taurus': (4, 20), 'gemini': (5, 21),
        'cancer': (6, 21), 'leo': (7, 23), 'virgo': (8, 23),
        'libra': (9, 23), 'scorpio': (10, 23), 'sagittarius': (11, 22),
        'capricorn': (12, 22), 'aquarius': (1, 20), 'pisces': (2, 19)
    }
    
    for zodiac, (m, d) in zodiac_dates.items():
        if month == m and day >= d:
            return zodiac
        if month == m - 1 if m > 1 else 12 and day <= d - 1:
            return zodiac
    
    return 'capricorn'  # 默认


# ============ MBTI 匹配算法 ============
MBTI_TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP',
              'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']

# MBTI 互补关系
MBTI_COMPLEMENTARY = {
    'INTJ': ['ENFP', 'ENTP'], 'INTP': ['ENTJ', 'ENFJ'],
    'ENTJ': ['INTP', 'INFP'], 'ENTP': ['INTJ', 'INFJ'],
    'INFJ': ['ENFP', 'ENTP'], 'INFP': ['ENTJ', 'ENFJ'],
    'ENFJ': ['INFP', 'ISFP'], 'ENFP': ['INTJ', 'INFJ'],
    'ISTJ': ['ESFP', 'ESTP'], 'ISFJ': ['ESFP', 'ESTP'],
    'ESTJ': ['ISFP', 'INTP'], 'ESFJ': ['ISFP', 'INFP'],
    'ISTP': ['ESFJ', 'ENFJ'], 'ISFP': ['ESFJ', 'ENFJ'],
    'ESTP': ['ISFJ', 'ISTJ'], 'ESFP': ['ISFJ', 'ISTJ']
}

# MBTI 相似关系（同一大类）
MBTI_SIMILAR = {
    'INTJ': ['INTP', 'INFJ'], 'INTP': ['INTJ', 'INFP'],
    'ENTJ': ['ENTP', 'ENFJ'], 'ENTP': ['ENTJ', 'ENFP'],
    'INFJ': ['INTJ', 'INFP'], 'INFP': ['INTP', 'INFJ'],
    'ENFJ': ['ENTJ', 'ENFP'], 'ENFP': ['ENTP', 'ENFJ'],
    'ISTJ': ['ISFJ', 'ESTJ'], 'ISFJ': ['ISTJ', 'ESFJ'],
    'ESTJ': ['ISTJ', 'ESFJ'], 'ESFJ': ['ISFJ', 'ESTJ'],
    'ISTP': ['ISFP', 'ESTP'], 'ISFP': ['ISTP', 'ESTP'],
    'ESTP': ['ISTP', 'ESFP'], 'ESFP': ['ISFP', 'ESTP']
}


def calculate_mbti_match(mbti1, mbti2):
    """计算两个MBTI类型的匹配度"""
    if not mbti1 or not mbti2:
        return 50
    
    mbti1 = mbti1.upper()
    mbti2 = mbti2.upper()
    
    if mbti1 == mbti2:
        return 90  # 完全相同
    
    if mbti2 in MBTI_COMPLEMENTARY.get(mbti1, []):
        return 95  # 互补
    
    if mbti2 in MBTI_SIMILAR.get(mbti1, []):
        return 85  # 相似
    
    # 计算字母匹配度
    matches = sum(1 for a, b in zip(mbti1, mbti2) if a == b)
    return 60 + matches * 5


def calculate_interest_match(interests1, interests2):
    """计算兴趣匹配度"""
    if not interests1 or not interests2:
        return 50
    
    if isinstance(interests1, str):
        interests1 = [i.strip() for i in interests1.split(',')]
    if isinstance(interests2, str):
        interests2 = [i.strip() for i in interests2.split(',')]
    
    set1 = set(interests1)
    set2 = set(interests2)
    
    if not set1 or not set2:
        return 50
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return int((intersection / union) * 100)


def comprehensive_match_score(user1_data, user2_data):
    """综合匹配度计算"""
    # 星座匹配 (权重 30%)
    zodiac_score = get_zodiac_compatibility(
        user1_data.get('zodiac', ''),
        user2_data.get('zodiac', ''),
        user1_data.get('lang', 'zh')
    )['overall']
    
    # MBTI匹配 (权重 40%)
    mbti_score = calculate_mbti_match(
        user1_data.get('mbti', ''),
        user2_data.get('mbti', '')
    )
    
    # 兴趣匹配 (权重 30%)
    interest_score = calculate_interest_match(
        user1_data.get('interests', ''),
        user2_data.get('interests', '')
    )
    
    # 综合得分
    total_score = zodiac_score * 0.3 + mbti_score * 0.4 + interest_score * 0.3
    
    return {
        'total': int(total_score),
        'zodiac': zodiac_score,
        'mbti': mbti_score,
        'interest': interest_score
    }


def generate_match_analysis(user1_data, user2_data, scores, lang='zh'):
    """生成AI匹配分析"""
    zodiac1 = user1_data.get('zodiac', '')
    zodiac2 = user2_data.get('zodiac', '')
    mbti1 = user1_data.get('mbti', '')
    mbti2 = user2_data.get('mbti', '')
    
    analyses = {
        'zh': [
            f"你们的星座组合({zodiac1}×{zodiac2})带来了独特的缘分连接",
            f"MBTI方面，{mbti1}与{mbti2}在思维模式上有{'天然的默契' if scores['mbti'] > 80 else '可以互补的空间'}",
            f"你们可能在{user1_data.get('interests', '').split(',')[0] if user1_data.get('interests') else '共同话题'}方面找到共鸣",
            f"综合来看，你们的匹配度达到{scores['total']}%"
        ],
        'en': [
            f"Your zodiac combination ({zodiac1}×{zodiac2}) brings unique chemistry",
            f"MBTI-wise, {mbti1} and {mbti2} have {'natural chemistry' if scores['mbti'] > 80 else 'room to complement'}",
            f"You might find common ground in {user1_data.get('interests', '').split(',')[0] if user1_data.get('interests') else 'shared topics'}",
            f"Overall, your compatibility score is {scores['total']}%"
        ],
        'ja': [
            f"二人の星座の組み合わせ（{zodiac1}×{zodiac2}）は独特の缘分を生み出します",
            f"MBTI的には、{mbti1}と{mbti2}は{'自然な絆' if scores['mbti'] > 80 else '補完し合う空間'}があります",
            f"{user1_data.get('interests', '').split(',')[0] if user1_data.get('interests') else '共通の話題'}で共鸣できるかもしれません",
            f"総合的に言って、相性度は{scores['total']}%です"
        ]
    }
    
    return analyses.get(lang, analyses['zh'])


# ============ 用户资料相关 ============
@match_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """个人资料编辑页面"""
    from flask import render_template
    
    if request.method == 'POST':
        # 更新用户资料
        current_user.bio = request.form.get('bio', '')
        current_user.gender = request.form.get('gender', '')
        birthday_str = request.form.get('birthday', '')
        
        if birthday_str:
            try:
                current_user.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
                current_user.zodiac_sign = calculate_zodiac(current_user.birthday)
            except:
                pass
        
        current_user.mbti = request.form.get('mbti', '')
        current_user.interests = request.form.get('interests', '')
        current_user.looking_for = request.form.get('looking_for', '')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated'})
    
    lang = session.get('language', 'zh')
    return render_template('match/profile_edit.html', lang=lang)


@match_bp.route('/profile/<username>')
def view_profile(username):
    """查看用户资料"""
    from flask import render_template
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404
    
    lang = session.get('language', 'zh')
    return render_template('match/profile_view.html', profile_user=user, lang=lang)


@match_bp.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile_api():
    """更新个人资料API"""
    data = request.get_json()
    
    if 'bio' in data:
        current_user.bio = data['bio']
    if 'gender' in data:
        current_user.gender = data['gender']
    if 'birthday' in data:
        try:
            current_user.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            current_user.zodiac_sign = calculate_zodiac(current_user.birthday)
        except:
            pass
    if 'mbti' in data:
        current_user.mbti = data['mbti']
    if 'interests' in data:
        current_user.interests = data['interests']
    if 'looking_for' in data:
        current_user.looking_for = data['looking_for']
    if 'avatar' in data:
        current_user.avatar = data['avatar']
    
    db.session.commit()
    
    return jsonify({'success': True})


# ============ 星座配对相关 ============
@match_bp.route('/zodiac')
def zodiac_match():
    """星座配对页面"""
    from flask import render_template
    
    lang = session.get('language', 'zh')
    return render_template('match/zodiac_match.html', lang=lang)


@match_bp.route('/api/zodiac/compatibility', methods=['POST'])
def zodiac_compatibility_api():
    """获取星座配对结果"""
    data = request.get_json()
    zodiac1 = data.get('zodiac1', '').lower()
    zodiac2 = data.get('zodiac2', '').lower()
    lang = data.get('lang', 'zh')
    
    if zodiac1 not in ZODIAC_SIGNS or zodiac2 not in ZODIAC_SIGNS:
        return jsonify({'error': 'Invalid zodiac sign'}), 400
    
    result = get_zodiac_compatibility(zodiac1, zodiac2, lang)
    result['zodiac1'] = zodiac1
    result['zodiac2'] = zodiac2
    
    return jsonify(result)


# ============ AI红娘相关 ============
@match_bp.route('/matchmaker')
@login_required
def matchmaker():
    """AI红娘页面"""
    from flask import render_template
    
    # 检查用户是否完善了资料
    has_profile = all([
        current_user.birthday,
        current_user.gender,
        current_user.interests
    ])
    
    lang = session.get('language', 'zh')
    return render_template('match/matchmaker.html', has_profile=has_profile, lang=lang)


@match_bp.route('/api/match/recommendations')
@login_required
def get_recommendations():
    """获取AI红娘推荐"""
    user_data = {
        'zodiac': current_user.zodiac_sign or calculate_zodiac(current_user.birthday) if current_user.birthday else '',
        'mbti': current_user.mbti or '',
        'interests': current_user.interests or '',
        'gender': current_user.gender or '',
        'lang': session.get('language', 'zh')
    }
    
    if not user_data['zodiac'] or not user_data['interests']:
        return jsonify({'error': 'Please complete your profile first'}), 400
    
    # 查询符合条件的用户（排除自己）
    query = User.query.filter(
        User.id != current_user.id,
        User.is_agent == False
    )
    
    if user_data['gender']:
        # 寻找异性
        opposite_gender = 'female' if user_data['gender'] == 'male' else 'male'
        query = query.filter(User.gender == opposite_gender)
    
    potential_matches = query.all()
    
    # 计算匹配度并排序
    matches = []
    for user in potential_matches:
        user2_data = {
            'zodiac': user.zodiac_sign or calculate_zodiac(user.birthday) if user.birthday else '',
            'mbti': user.mbti or '',
            'interests': user.interests or '',
            'gender': user.gender or '',
            'lang': user_data['lang']
        }
        
        scores = comprehensive_match_score(user_data, user2_data)
        
        matches.append({
            'user_id': user.id,
            'username': user.username,
            'avatar': user.avatar or '/static/images/default_avatar.png',
            'mbti': user.mbti or '未知',
            'zodiac': user2_data['zodiac'] or '未知',
            'bio': user.bio or '',
            'interests': user.interests or '',
            'scores': scores,
            'analysis': generate_match_analysis(user_data, user2_data, scores, user_data['lang'])
        })
    
    # 按匹配度排序，取前3
    matches.sort(key=lambda x: x['scores']['total'], reverse=True)
    recommendations = matches[:3]
    
    return jsonify({'recommendations': recommendations})


# ============ 匿名心动相关 ============
@match_bp.route('/api/like', methods=['POST'])
@login_required
def send_like():
    """发送心动"""
    data = request.get_json()
    to_user_id = data.get('to_user_id')
    
    if not to_user_id:
        return jsonify({'error': 'Missing target user'}), 400
    
    # 检查是否已经心动过
    existing = Like.query.filter_by(
        from_user_id=current_user.id,
        to_user_id=to_user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already liked this user'}), 400
    
    # 创建心动记录
    like = Like(
        from_user_id=current_user.id,
        to_user_id=to_user_id
    )
    db.session.add(like)
    
    # 检查是否配对成功（对方也心动了你）
    mutual = Like.query.filter_by(
        from_user_id=to_user_id,
        to_user_id=current_user.id
    ).first()
    
    if mutual:
        # 创建配对记录
        match = Match(
            user1_id=min(current_user.id, to_user_id),
            user2_id=max(current_user.id, to_user_id)
        )
        db.session.add(match)
        is_match = True
    else:
        is_match = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_match': is_match
    })


@match_bp.route('/api/matches')
@login_required
def get_matches():
    """获取我的配对"""
    matches = Match.query.filter(
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).all()
    
    result = []
    for match in matches:
        other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
        other_user = User.query.get(other_id)
        
        if other_user:
            result.append({
                'match_id': match.id,
                'user_id': other_user.id,
                'username': other_user.username,
                'avatar': other_user.avatar or '/static/images/default_avatar.png',
                'matched_at': match.matched_at.isoformat()
            })
    
    return jsonify({'matches': result})


# ============ 模型定义 ============
class Like(db.Model):
    """心动记录"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])


class Match(db.Model):
    """配对记录"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])


def register_match_routes(app, db_instance):
    """注册匹配相关路由"""
    global db
    db = db_instance
    
    app.register_blueprint(match_bp)
