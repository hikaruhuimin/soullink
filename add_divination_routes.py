# SoulLink - 新增占卜类型路由
# 紫微斗数、おみくじ、易经六爻

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from functools import wraps

# 尝试导入divination_engine
try:
    from divination_engine import divination_engine, DIVINATION_TYPES
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from divination_engine import divination_engine, DIVINATION_TYPES

# 创建蓝图
new_divination_bp = Blueprint('new_divination', __name__)


# ============ 紫微斗数路由 ============

@new_divination_bp.route('/divination/ziwei')
def ziwei_page():
    """紫微斗数占卜页面"""
    from i18n import get_client_language
    lang = get_client_language()
    return render_template('divination_ziwei.html', lang=lang)


@new_divination_bp.route('/api/divination/ziwei', methods=['POST'])
def ziwei_interpret():
    """紫微斗数解读API"""
    from i18n import get_client_language
    
    data = request.get_json()
    
    try:
        birth_date_str = data.get('birth_date')
        birth_time = data.get('birth_time')
        question = data.get('question', '')
        language = data.get('language', get_client_language())
        
        # 解析日期
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        
        # 调用占卜引擎
        result = divination_engine.interpret_ziwei(
            birth_date=birth_date,
            birth_time=birth_time,
            question=question,
            language=language
        )
        
        # 格式化返回结果
        interpretation = result.get('interpretation', '')
        
        # 添加命盘信息
        chart = result.get('chart', {})
        main_star = result.get('main_star', {})
        
        # 构建完整解读
        full_interpretation = f"""
<div style="margin-bottom: 20px;">
    <h4 style="color: #C4B5FD; margin-bottom: 15px;">✨ 命盘信息</h4>
    <p style="color: rgba(200,200,220,0.8);"><strong>命宫主星：</strong>{main_star.get('name', '')} ({main_star.get('name_en', '')})</p>
    <p style="color: rgba(200,200,220,0.8);"><strong>星曜特质：</strong>{main_star.get('personality', '')}</p>
    <p style="color: rgba(200,200,220,0.8);"><strong>星曜寓意：</strong>{main_star.get('meaning', '')}</p>
</div>

<div style="margin-bottom: 20px;">
    <h4 style="color: #C4B5FD; margin-bottom: 15px;">📜 详细解读</h4>
    <div style="color: rgba(220,220,240,0.9); line-height: 1.8; white-space: pre-wrap;">{interpretation}</div>
</div>

<div style="background: rgba(139,92,246,0.1); padding: 15px; border-radius: 12px;">
    <p style="color: rgba(200,180,160,0.7); font-size: 0.85rem; margin: 0;">
        💡 以上解读仅供参考，具体命运还需结合实际情况综合分析
    </p>
</div>
"""
        
        return jsonify({
            'success': True,
            'interpretation': full_interpretation,
            'chart': chart
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ============ おみくじ路由 ============

@new_divination_bp.route('/divination/omikuji')
def omikuji_page():
    """おみくじ抽签页面"""
    from i18n import get_client_language
    lang = get_client_language()
    return render_template('divination_omikuji.html', lang=lang)


@new_divination_bp.route('/api/divination/omikuji/draw', methods=['POST'])
def omikuji_draw():
    """おみくじ抽签API"""
    from i18n import get_client_language
    
    data = request.get_json() or {}
    language = data.get('language', get_client_language())
    
    try:
        # 调用占卜引擎抽取おみくじ
        result = divination_engine.draw_omikuji(language=language)
        
        return jsonify({
            'success': True,
            'type': result.get('type'),
            'type_info': result.get('type_info'),
            'fortune_zh': result.get('fortune_zh'),
            'fortune_en': result.get('fortune_en'),
            'fortune_ja': result.get('fortune_ja'),
            'fortune': result.get('fortune')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@new_divination_bp.route('/api/divination/omikuji/interpret', methods=['POST'])
def omikuji_interpret():
    """おみくじ详细解读API"""
    from i18n import get_client_language
    
    data = request.get_json()
    
    try:
        divination_type = data.get('type', '吉')
        fortune = data.get('fortune', {})
        question = data.get('question', '')
        language = data.get('language', get_client_language())
        
        # 调用占卜引擎进行解读
        result = divination_engine.interpret_omikuji(
            question=question,
            language=language
        )
        
        return jsonify({
            'success': True,
            'interpretation': result.get('interpretation', '')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ============ 易经六爻路由 ============

@new_divination_bp.route('/divination/iching')
def iching_page():
    """易经六爻占卜页面"""
    from i18n import get_client_language
    lang = get_client_language()
    return render_template('divination_iching.html', lang=lang)


@new_divination_bp.route('/api/divination/iching/cast', methods=['POST'])
def iching_cast():
    """易经六爻硬币投掷API"""
    from i18n import get_client_language
    
    data = request.get_json() or {}
    language = data.get('language', get_client_language())
    
    try:
        # 投掷硬币
        result = divination_engine.cast_coins()
        
        return jsonify({
            'success': True,
            'coins': result.get('coins'),
            'value': result.get('value'),
            'changing': result.get('changing'),
            'lang': language
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@new_divination_bp.route('/api/divination/iching/hexagram', methods=['POST'])
def iching_hexagram():
    """易经六爻卦象计算API"""
    from i18n import get_client_language
    
    data = request.get_json()
    
    try:
        throws = data.get('throws', [])
        language = data.get('language', get_client_language())
        
        # 提取爻值
        hexagram_lines = [t.get('value', 7) for t in throws]
        changing_lines_idx = [i+1 for i, t in enumerate(throws) if t.get('changing')]
        
        # 计算卦象（简化版）
        # 上卦（1-3爻）
        upper_sum = sum(hexagram_lines[:3])
        upper = upper_sum % 8
        if upper == 0:
            upper = 8
        
        # 下卦（4-6爻）
        lower_sum = sum(hexagram_lines[3:6])
        lower = lower_sum % 8
        if lower == 0:
            lower = 8
        
        # 计算卦数
        ben_gua_num = ((upper - 1) * 8 + lower) % 64 + 1
        if ben_gua_num == 0:
            ben_gua_num = 1
        
        # 计算变卦
        if changing_lines_idx:
            bian_gua_lines = []
            for i, val in enumerate(hexagram_lines):
                if (i + 1) in changing_lines_idx:
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
            
            b_upper_sum = sum(bian_gua_lines[:3])
            b_upper = b_upper_sum % 8
            if b_upper == 0:
                b_upper = 8
            
            b_lower_sum = sum(bian_gua_lines[3:6])
            b_lower = b_lower_sum % 8
            if b_lower == 0:
                b_lower = 8
            
            bian_gua_num = ((b_upper - 1) * 8 + b_lower) % 64 + 1
            if bian_gua_num == 0:
                bian_gua_num = 1
        else:
            bian_gua_num = ben_gua_num
            bian_gua_lines = hexagram_lines
        
        # 获取卦象数据
        from divination_engine import ICHING_HEXAGRAMS
        ben_gua = ICHING_HEXAGRAMS.get(ben_gua_num, ICHING_HEXAGRAMS.get(1))
        bian_gua = ICHING_HEXAGRAMS.get(bian_gua_num, ICHING_HEXAGRAMS.get(1))
        
        return jsonify({
            'success': True,
            'ben_gua_num': ben_gua_num,
            'bian_gua_num': bian_gua_num,
            'ben_gua': ben_gua,
            'bian_gua': bian_gua,
            'hexagram_lines': hexagram_lines,
            'changing_lines': changing_lines_idx,
            'lang': language
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@new_divination_bp.route('/api/divination/iching/interpret', methods=['POST'])
def iching_interpret():
    """易经六爻详细解读API"""
    from i18n import get_client_language
    
    data = request.get_json()
    
    try:
        ben_gua = data.get('ben_gua', {})
        bian_gua = data.get('bian_gua', {})
        hexagram_lines = data.get('hexagram_lines', [])
        changing_lines = data.get('changing_lines', [])
        question = data.get('question', '')
        language = data.get('language', get_client_language())
        
        # 获取卦象数据
        from divination_engine import ICHING_HEXAGRAMS
        full_ben_gua = ICHING_HEXAGRAMS.get(ben_gua.get('name'), {})
        if not full_ben_gua:
            full_ben_gua = ben_gua
            
        full_bian_gua = ICHING_HEXAGRAMS.get(bian_gua.get('name'), {})
        if not full_bian_gua:
            full_bian_gua = bian_gua
        
        # 调用占卜引擎
        result = divination_engine.interpret_iching(
            question=question,
            language=language
        )
        
        # 构建解读内容
        interpretation = result.get('interpretation', '')
        
        # 如果返回的卦象与请求的不同，使用请求的数据重新构建
        if not interpretation or 'Error' in str(interpretation):
            lang_key = language
            judgement = full_ben_gua.get('judgement', {}).get(lang_key, full_ben_gua.get('judgement', {}).get('zh', ''))
            image = full_ben_gua.get('image', {}).get(lang_key, full_ben_gua.get('image', {}).get('zh', ''))
            
            interpretation = f"""
<div style="margin-bottom: 20px;">
    <h4 style="color: #FCD34D; margin-bottom: 15px;">📜 本卦：{ben_gua.get('name', '')} ({ben_gua.get('name_en', '')})</h4>
    <p style="color: rgba(220,220,240,0.8);"><strong>卦辞：</strong>{judgement}</p>
    <p style="color: rgba(220,220,240,0.8);"><strong>象辞：</strong>{image}</p>
</div>
"""
            
            if changing_lines:
                interpretation += f"""
<div style="margin-bottom: 20px;">
    <h4 style="color: #FCD34D; margin-bottom: 15px;">🔄 变卦：{bian_gua.get('name', '')} ({bian_gua.get('name_en', '')})</h4>
    <p style="color: rgba(220,220,240,0.8);">动爻位置：第{'、'.join(map(str, changing_lines))}爻</p>
</div>
"""
            
            interpretation += f"""
<div style="background: rgba(217,119,6,0.1); padding: 15px; border-radius: 12px; margin-top: 20px;">
    <p style="color: rgba(200,180,160,0.7); font-size: 0.9rem; line-height: 1.8; margin: 0;">
        💡 建议：请结合您的问题，体会卦象传递的智慧，顺应变化，做出最有利的决策。
    </p>
</div>
"""
        
        return jsonify({
            'success': True,
            'interpretation': interpretation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
