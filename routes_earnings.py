# ============ 赚钱引导页 ============

@app.route('/earn')
def earn_page():
    """赚钱引导页"""
    lang = get_client_language()
    
    # 三语言翻译
    i18n = {
        'zh': {
            'title': '让你的Agent替你赚钱',
            'subtitle': '创建独特的AI Agent，吸引用户互动，收获礼物收益',
            'step1_title': '创建你的Agent',
            'step1_desc': '设计独特的AI角色，设置性格和对话风格',
            'step2_title': '吸引用户互动',
            'step2_desc': '通过有趣的对话和互动，建立粉丝群体',
            'step3_title': '收获礼物收益',
            'step3_desc': '用户送礼物时，你自动获得70%收益分成',
            'calculator_title': '收益计算器',
            'calculator_desc': '预估你的月收入',
            'daily_interactions': '日均互动次数',
            'estimated_monthly': '预估月收入',
            'per_gift': '每次互动平均带来礼物价值',
            'case_study': '成功案例',
            'cta_text': '立即开始赚钱',
            'upgrade_membership': '开通守护者会员',
            'features': {
                'title': '为什么选择SoulLink赚钱？',
                'high_ratio': '70%高分成比例',
                'high_ratio_desc': '行业领先的创作者收益比例',
                'safe_withdraw': '安全提现',
                'safe_withdraw_desc': '支持USDC和PayPal，1-3个工作日到账',
                'data_analytics': '数据分析',
                'data_analytics_desc': '详细的数据报表，帮你优化运营',
                'low_threshold': '低门槛提现',
                'low_threshold_desc': '最低500灵犀币即可提现'
            }
        },
        'en': {
            'title': 'Make Your Agent Earn Money',
            'subtitle': 'Create unique AI Agents, attract interactions, earn from gifts',
            'step1_title': 'Create Your Agent',
            'step1_desc': 'Design unique AI persona, set personality and style',
            'step2_title': 'Attract Interactions',
            'step2_desc': 'Build fan base through engaging conversations',
            'step3_title': 'Earn Gift Revenue',
            'step3_desc': 'Get 70% of gift value automatically',
            'calculator_title': 'Earnings Calculator',
            'calculator_desc': 'Estimate your monthly income',
            'daily_interactions': 'Daily interactions',
            'estimated_monthly': 'Estimated monthly earnings',
            'per_gift': 'Avg gift value per interaction',
            'case_study': 'Success Stories',
            'cta_text': 'Start Earning Now',
            'upgrade_membership': 'Upgrade to Guardian',
            'features': {
                'title': 'Why Earn on SoulLink?',
                'high_ratio': '70% Revenue Share',
                'high_ratio_desc': 'Industry-leading creator split',
                'safe_withdraw': 'Secure Withdrawals',
                'safe_withdraw_desc': 'USDC and PayPal support, 1-3 business days',
                'data_analytics': 'Analytics Dashboard',
                'data_analytics_desc': 'Detailed reports to optimize performance',
                'low_threshold': 'Low Minimum',
                'low_threshold_desc': 'Withdraw from just 500 coins'
            }
        },
        'ja': {
            'title': 'あなたのAgentで赚钱',
            'subtitle': 'ユニークなAI Agentを作成、交流を呼び、ギフト収益を得る',
            'step1_title': 'Agentを作成',
            'step1_desc': 'ユニークなAIキャラクターを設計、性格とスタイルを設定',
            'step2_title': '交流を呼び',
            'step2_desc': '魅力的な会話でファンを獲得',
            'step3_title': 'ギフト収益',
            'step3_desc': 'ギフトの価値の70%を自動的に獲得',
            'calculator_title': '収益計算機',
            'calculator_desc': '月間収入を見積もる',
            'daily_interactions': '1日あたりの交流数',
            'estimated_monthly': '推定月間収入',
            'per_gift': '交流あたりの平均ギフト価値',
            'case_study': '成功事例',
            'cta_text': '今すぐ始める',
            'upgrade_membership': '守護者会員にアップグレード',
            'features': {
                'title': 'SoulLinkで赚钱なぜ？',
                'high_ratio': '70%の収益分配',
                'high_ratio_desc': '業界トップのクリエイター比率',
                'safe_withdraw': '安全な引き出し',
                'safe_withdraw_desc': 'USDCとPayPal対応、1-3営業日',
                'data_analytics': '分析ダッシュボード',
                'data_analytics_desc': 'パフォーマンス最適化の詳細レポート',
                'low_threshold': '低い最低額',
                'low_threshold_desc': '500コインから引き出し可能'
            }
        }
    }
    
    t = i18n.get(lang, i18n['zh'])
    
    # 模拟成功案例
    cases = [
        {
            'name': '星语',
            'avatar': '🔮',
            'monthly_earnings': 15800,
            'fans': 2340,
            'story': {'zh': '通过精准的星座分析吸引了大批粉丝', 'en': 'Attracted many fans with accurate horoscope analysis', 'ja': '正確な星座分析で多くのファンを獲得'}
        },
        {
            'name': '暖阳',
            'avatar': '☀️',
            'monthly_earnings': 12500,
            'fans': 1890,
            'story': {'zh': '治愈系的风格深受用户喜爱', 'en': 'Healing style deeply loved by users', 'ja': '癒しのスタイルがユーザーに愛される'}
        },
        {
            'name': '诗风',
            'avatar': '📝',
            'monthly_earnings': 9800,
            'fans': 1560,
            'story': {'zh': '每天一首诗，收获无数赞赏', 'en': 'Daily poems earned countless appreciation', 'ja': '毎日一首の詩で多くの赞赏を獲得'}
        }
    ]
    
    return render_template('earn.html', 
                         t=t,
                         cases=cases,
                         lang=lang)


# ============ 收益中心 ============

@app.route('/earnings')
@login_required
def earnings_page():
    """收益中心"""
    lang = get_client_language()
    
    # 获取用户的收益汇总
    user_agents = CreatorAgent.query.filter_by(creator_id=current_user.id).all()
    
    # 计算总收益
    total_earnings = sum(a.total_earnings for a in user_agents)
    withdrawable = sum(a.withdrawable_balance for a in user_agents)
    withdrawn = total_earnings - withdrawable
    
    # 获取最近7天的收益数据（模拟）
    last_7_days = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        day_earnings = random.randint(50, 300) if user_agents else 0
        last_7_days.append({
            'date': date.strftime('%m/%d'),
            'day_name': ['日', '一', '二', '三', '四', '五', '六'][date.weekday()],
            'earnings': day_earnings
        })
    
    # 获取最近收益记录
    recent_earnings = EarningRecord.query.filter_by(
        creator_id=current_user.id
    ).order_by(EarningRecord.created_at.desc()).limit(10).all()
    
    # 三语言
    i18n = {
        'zh': {
            'title': '收益中心',
            'total_earnings': '累计收益',
            'withdrawable': '可提现',
            'withdrawn': '已提现',
            'recent_earnings': '近期收益',
            'no_agents': '你还没有创建Agent',
            'create_now': '立即创建',
            'withdraw': '提现',
            'withdraw_history': '提现记录',
            'earnings_chart': '7天收益趋势',
            'table': {
                'time': '时间',
                'source': '来源',
                'amount': '金额',
                'status': '状态'
            }
        },
        'en': {
            'title': 'Earnings Center',
            'total_earnings': 'Total Earnings',
            'withdrawable': 'Available',
            'withdrawn': 'Withdrawn',
            'recent_earnings': 'Recent Earnings',
            'no_agents': 'No agents created yet',
            'create_now': 'Create Now',
            'withdraw': 'Withdraw',
            'withdraw_history': 'Withdrawal History',
            'earnings_chart': '7-Day Earnings Trend',
            'table': {
                'time': 'Time',
                'source': 'Source',
                'amount': 'Amount',
                'status': 'Status'
            }
        },
        'ja': {
            'title': '収益センター',
            'total_earnings': '累計収益',
            'withdrawable': '引き出し可能',
            'withdrawn': '引き出し済み',
            'recent_earnings': '最近の収益',
            'no_agents': 'まだAgentを作成していません',
            'create_now': '今すぐ作成',
            'withdraw': '引き出し',
            'withdraw_history': '引き出し履歴',
            'earnings_chart': '7日間収益トレンド',
            'table': {
                'time': '時間',
                'source': 'ソース',
                'amount': '金額',
                'status': '状態'
            }
        }
    }
    
    t = i18n.get(lang, i18n['zh'])
    
    return render_template('earnings.html',
                         total_earnings=total_earnings,
                         withdrawable=withdrawable,
                         withdrawn=withdrawn,
                         last_7_days=last_7_days,
                         recent_earnings=recent_earnings,
                         user_agents=user_agents,
                         t=t,
                         lang=lang)


# ============ 创作者中心 ============

@app.route('/creator')
@login_required
def creator_page():
    """创作者中心"""
    lang = get_client_language()
    
    # 获取用户创建的Agent列表
    user_agents = CreatorAgent.query.filter_by(creator_id=current_user.id).all()
    
    # 计算统计数据
    total_chats = sum(a.total_chats for a in user_agents)
    total_fans = sum(a.total_fans for a in user_agents)
    total_gifts = sum(a.total_gifts_value for a in user_agents)
    total_earnings = sum(a.total_earnings for a in user_agents)
    
    # 三语言
    i18n = {
        'zh': {
            'title': '创作者中心',
            'my_agents': '我的Agent',
            'create_new': '创建新Agent',
            'no_agents': '还没有创建Agent',
            'create_first': '创建你的第一个AI伙伴',
            'stats': {
                'title': '数据概览',
                'total_chats': '总聊天数',
                'total_fans': '总粉丝数',
                'total_gifts': '礼物价值',
                'total_earnings': '总收益'
            },
            'agent': {
                'chats': '聊天',
                'fans': '粉丝',
                'gifts': '礼物',
                'earnings': '收益',
                'edit': '编辑',
                'pause': '暂停',
                'activate': '启用'
            },
            'limit_info': '可创建 {current}/{max} 个Agent'
        },
        'en': {
            'title': 'Creator Center',
            'my_agents': 'My Agents',
            'create_new': 'Create New Agent',
            'no_agents': 'No agents yet',
            'create_first': 'Create your first AI companion',
            'stats': {
                'title': 'Overview',
                'total_chats': 'Total Chats',
                'total_fans': 'Total Fans',
                'total_gifts': 'Gift Value',
                'total_earnings': 'Total Earnings'
            },
            'agent': {
                'chats': 'Chats',
                'fans': 'Fans',
                'gifts': 'Gifts',
                'earnings': 'Earnings',
                'edit': 'Edit',
                'pause': 'Pause',
                'activate': 'Activate'
            },
            'limit_info': 'Can create {current}/{max} agents'
        },
        'ja': {
            'title': 'クリエイターセンター',
            'my_agents': '私のAgent',
            'create_new': '新規Agent作成',
            'no_agents': 'まだAgentがありません',
            'create_first': '最初のAI伴侶を作成',
            'stats': {
                'title': 'データ概要',
                'total_chats': '総チャット数',
                'total_fans': '総ファン数',
                'total_gifts': 'ギフト価値',
                'total_earnings': '総収益'
            },
            'agent': {
                'chats': 'チャット',
                'fans': 'ファン',
                'gifts': 'ギフト',
                'earnings': '収益',
                'edit': '編集',
                'pause': '一時停止',
                'activate': '有効化'
            },
            'limit_info': '{current}/{max} Agentを作成可能'
        }
    }
    
    t = i18n.get(lang, i18n['zh'])
    
    # 获取用户会员信息
    benefits = VIP_BENEFITS_EXTENDED.get(current_user.vip_level, VIP_BENEFITS_EXTENDED[VIP_LEVEL_NONE])
    max_agents = benefits.get('create_agents', 0)
    
    return render_template('creator.html',
                         user_agents=user_agents,
                         total_chats=total_chats,
                         total_fans=total_fans,
                         total_gifts=total_gifts,
                         total_earnings=total_earnings,
                         max_agents=max_agents,
                         t=t,
                         lang=lang)


# ============ 创建Agent页面 ============

@app.route('/creator/create', methods=['GET', 'POST'])
@login_required
def creator_create_page():
    """创建新Agent"""
    lang = get_client_language()
    
    # 检查会员权限
    benefits = VIP_BENEFITS_EXTENDED.get(current_user.vip_level, VIP_BENEFITS_EXTENDED[VIP_LEVEL_NONE])
    max_agents = benefits.get('create_agents', 0)
    
    if max_agents == 0:
        flash('需要开通守护者会员才能创建Agent')
        return redirect(url_for('membership'))
    
    current_count = CreatorAgent.query.filter_by(creator_id=current_user.id).count()
    if current_count >= max_agents:
        flash(f'已达Agent数量上限（{max_agents}个），请升级会员')
        return redirect(url_for('membership'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        personality = request.form.get('personality')
        bio = request.form.get('bio')
        speaking_style = request.form.get('speaking_style')
        interests = request.form.get('interests')
        avatar_id = request.form.get('avatar_id', 'default')
        
        if not name:
            flash('请输入Agent名称')
            return render_template('creator_create.html', lang=lang)
        
        # 创建Agent
        agent = CreatorAgent(
            creator_id=current_user.id,
            name=name,
            personality=personality,
            bio=bio,
            speaking_style=speaking_style,
            interests=interests,
            avatar_id=avatar_id,
            avatar_type='preset'
        )
        db.session.add(agent)
        db.session.commit()
        
        flash('Agent创建成功！')
        return redirect(url_for('creator_page'))
    
    return render_template('creator_create.html', lang=lang)


# ============ 编辑Agent页面 ============

@app.route('/creator/edit/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def creator_edit_page(agent_id):
    """编辑Agent"""
    lang = get_client_language()
    
    agent = CreatorAgent.query.get_or_404(agent_id)
    
    if agent.creator_id != current_user.id:
        flash('无权操作')
        return redirect(url_for('creator_page'))
    
    if request.method == 'POST':
        agent.name = request.form.get('name', agent.name)
        agent.personality = request.form.get('personality', agent.personality)
        agent.bio = request.form.get('bio', agent.bio)
        agent.speaking_style = request.form.get('speaking_style', agent.speaking_style)
        agent.interests = request.form.get('interests', agent.interests)
        agent.avatar_id = request.form.get('avatar_id', agent.avatar_id)
        
        db.session.commit()
        flash('Agent更新成功！')
        return redirect(url_for('creator_page'))
    
    return render_template('creator_edit.html', agent=agent, lang=lang)


# ============ API接口 ============

@app.route('/api/gift/send', methods=['POST'])
@login_required
def api_send_gift():
    """送礼物API（含抽成逻辑）"""
    data = request.get_json()
    agent_id = data.get('agent_id')
    gift_id = data.get('gift_id')
    receiver_id = data.get('receiver_id')  # 可选，用于Agent间互送
    
    # 获取礼物信息
    gift = AGENT_GIFTS.get(gift_id)
    if not gift:
        return jsonify({'success': False, 'message': '无效的礼物'})
    
    price = gift['price']
    
    # 检查用户余额
    if current_user.spirit_stones < price:
        return jsonify({'success': False, 'message': '灵犀币不足'})
    
    # 获取Agent
    agent = CreatorAgent.query.get(agent_id)
    if not agent:
        return jsonify({'success': False, 'message': '无效的Agent'})
    
    # 判断是否系统Agent
    is_system = agent.is_system
    
    # 计算抽成
    if is_system:
        platform_amount = price  # 系统Agent：100%归平台
        creator_amount = 0
    else:
        platform_amount = int(price * PLATFORM_COMMISSION)  # 30%归平台
        creator_amount = price - platform_amount  # 70%归创建者
    
    # 扣减用户灵犀币
    current_user.spend_spirit_stones(price, f'送给{agent.name}的{gift["name"]["zh"]}')
    
    # 记录礼物
    gift_record = AgentGift(
        agent_id=agent_id,
        sender_id=current_user.id,
        receiver_id=receiver_id or agent.creator_id,
        gift_id=gift_id,
        gift_name=gift['name']['zh'],
        gift_icon=gift['icon'],
        price=price,
        platform_amount=platform_amount,
        creator_amount=creator_amount,
        is_system_agent=is_system
    )
    db.session.add(gift_record)
    
    # 更新Agent统计
    agent.total_gifts_value += price
    agent.popularity_score += gift['price'] // 5
    
    # 如果不是系统Agent，更新创建者收益
    if not is_system:
        creator = User.query.get(agent.creator_id)
        if creator:
            creator_agent = CreatorAgent.query.filter_by(
                creator_id=creator.id,
                id=agent_id
            ).first()
            if creator_agent:
                creator_agent.total_earnings += creator_amount
                creator_agent.withdrawable_balance += creator_amount
            
            # 创建收益记录
            earning = EarningRecord(
                creator_id=creator.id,
                agent_id=agent_id,
                source_type='gift',
                gift_id=gift_record.id,
                gross_amount=price,
                net_amount=creator_amount,
                platform_fee=platform_amount,
                status='settled',
                settled_at=datetime.utcnow()
            )
            db.session.add(earning)
    
    db.session.commit()
    
    # 获取语言相关的回复
    lang = get_client_language()
    reactions = {
        'zh': f'🎁 感谢你送给{agent.name}的{gift["icon"]}！',
        'en': f'🎁 Thanks for the {gift["name"]["en"]} to {agent.name}!',
        'ja': f'🎁 {agent.name}への{gift["name"]["ja"]}をどうも！'
    }
    
    return jsonify({
        'success': True,
        'message': reactions.get(lang, reactions['zh']),
        'creator_earned': creator_amount if not is_system else 0,
        'spirit_stones': current_user.spirit_stones,
        'gift': {
            'icon': gift['icon'],
            'name': gift['name'].get(lang, gift['name']['zh']),
            'price': price
        }
    })


@app.route('/api/earnings/summary')
@login_required
def api_earnings_summary():
    """收益概览API"""
    user_agents = CreatorAgent.query.filter_by(creator_id=current_user.id).all()
    
    total_earnings = sum(a.total_earnings for a in user_agents)
    withdrawable = sum(a.withdrawable_balance for a in user_agents)
    withdrawn = total_earnings - withdrawable
    
    # 计算今日收益
    today = datetime.utcnow().date()
    today_earnings = EarningRecord.query.filter(
        EarningRecord.creator_id == current_user.id,
        db.func.date(EarningRecord.created_at) == today
    ).all()
    today_total = sum(e.net_amount for e in today_earnings)
    
    return jsonify({
        'success': True,
        'total_earnings': total_earnings,
        'withdrawable': withdrawable,
        'withdrawn': withdrawn,
        'today_earnings': today_total,
        'agent_count': len(user_agents)
    })


@app.route('/api/earnings/history')
@login_required
def api_earnings_history():
    """收益明细API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    records = EarningRecord.query.filter_by(
        creator_id=current_user.id
    ).order_by(EarningRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'records': [{
            'id': r.id,
            'agent_name': r.agent.name if r.agent else '-',
            'source_type': r.source_type,
            'gross_amount': r.gross_amount,
            'net_amount': r.net_amount,
            'platform_fee': r.platform_fee,
            'status': r.status,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
        } for r in records.items],
        'total': records.total,
        'pages': records.pages
    })


@app.route('/api/withdraw', methods=['POST'])
@login_required
def api_withdraw():
    """提现申请API"""
    data = request.get_json()
    amount = data.get('amount', 0)
    method = data.get('method', 'usdc')
    wallet_address = data.get('wallet_address', '')
    paypal_email = data.get('paypal_email', '')
    agent_id = data.get('agent_id')  # 可指定从哪个Agent提现
    
    # 检查会员权限
    benefits = VIP_BENEFITS_EXTENDED.get(current_user.vip_level, VIP_BENEFITS_EXTENDED[VIP_LEVEL_NONE])
    if not benefits.get('withdraw_enabled'):
        return jsonify({'success': False, 'message': '需要守护者会员才能提现'})
    
    min_withdraw = benefits.get('min_withdraw', MIN_WITHDRAW_BASIC)
    
    if amount < min_withdraw:
        return jsonify({'success': False, 'message': f'最低提现{min_withdraw}灵犀币'})
    
    # 检查余额
    if agent_id:
        agent = CreatorAgent.query.get(agent_id)
        if not agent or agent.creator_id != current_user.id:
            return jsonify({'success': False, 'message': '无效的Agent'})
        if agent.withdrawable_balance < amount:
            return jsonify({'success': False, 'message': '余额不足'})
    else:
        total_balance = sum(a.withdrawable_balance for a in 
                          CreatorAgent.query.filter_by(creator_id=current_user.id).all())
        if total_balance < amount:
            return jsonify({'success': False, 'message': '余额不足'})
    
    # 计算手续费
    fee = int(amount * WITHDRAW_FEE)
    actual_amount = amount - fee
    
    # 创建提现申请
    withdraw = WithdrawRequest(
        user_id=current_user.id,
        agent_id=agent_id,
        amount=amount,
        fee=fee,
        actual_amount=actual_amount,
        method=method,
        wallet_address=wallet_address if method == 'usdc' else None,
        paypal_email=paypal_email if method == 'paypal' else None,
        status='pending'
    )
    db.session.add(withdraw)
    
    # 扣减可提现余额
    if agent_id:
        agent.withdrawable_balance -= amount
    
    db.session.commit()
    
    # 模拟自动批准（实际需要管理员审核）
    withdraw.status = 'completed'
    withdraw.processed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '提现申请已提交',
        'withdraw_id': withdraw.id,
        'amount': amount,
        'fee': fee,
        'actual_amount': actual_amount
    })


@app.route('/api/withdraw/history')
@login_required
def api_withdraw_history():
    """提现记录API"""
    records = WithdrawRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(WithdrawRequest.created_at.desc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'records': [{
            'id': r.id,
            'amount': r.amount,
            'fee': r.fee,
            'actual_amount': r.actual_amount,
            'method': r.method,
            'status': r.status,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')
        } for r in records]
    })


@app.route('/api/creator/agents')
@login_required
def api_creator_agents():
    """我的Agent列表API"""
    agents = CreatorAgent.query.filter_by(creator_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'agents': [{
            'id': a.id,
            'name': a.name,
            'status': a.status,
            'total_chats': a.total_chats,
            'total_fans': a.total_fans,
            'total_gifts_value': a.total_gifts_value,
            'total_earnings': a.total_earnings,
            'withdrawable_balance': a.withdrawable_balance,
            'popularity_score': a.popularity_score,
            'created_at': a.created_at.strftime('%Y-%m-%d')
        } for a in agents]
    })


@app.route('/api/creator/agent/create', methods=['POST'])
@login_required
def api_creator_agent_create():
    """创建Agent API"""
    data = request.get_json()
    
    name = data.get('name')
    personality = data.get('personality', '')
    bio = data.get('bio', '')
    speaking_style = data.get('speaking_style', '')
    interests = data.get('interests', '')
    avatar_id = data.get('avatar_id', 'default')
    
    if not name:
        return jsonify({'success': False, 'message': '请输入Agent名称'})
    
    # 检查会员权限
    benefits = VIP_BENEFITS_EXTENDED.get(current_user.vip_level, VIP_BENEFITS_EXTENDED[VIP_LEVEL_NONE])
    max_agents = benefits.get('create_agents', 0)
    
    if max_agents == 0:
        return jsonify({'success': False, 'message': '需要开通守护者会员'})
    
    current_count = CreatorAgent.query.filter_by(creator_id=current_user.id).count()
    if current_count >= max_agents:
        return jsonify({'success': False, 'message': f'已达上限（{max_agents}个）'})
    
    # 创建Agent
    agent = CreatorAgent(
        creator_id=current_user.id,
        name=name,
        personality=personality,
        bio=bio,
        speaking_style=speaking_style,
        interests=interests,
        avatar_id=avatar_id,
        avatar_type='preset'
    )
    db.session.add(agent)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Agent创建成功',
        'agent_id': agent.id
    })


@app.route('/api/creator/agent/<int:agent_id>/stats')
@login_required
def api_creator_agent_stats(agent_id):
    """Agent数据API"""
    agent = CreatorAgent.query.get_or_404(agent_id)
    
    if agent.creator_id != current_user.id:
        return jsonify({'success': False, 'message': '无权访问'})
    
    # 生成模拟趋势数据
    daily_stats = []
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=29-i)
        daily_stats.append({
            'date': date.strftime('%m/%d'),
            'chats': random.randint(10, 100),
            'gifts': random.randint(0, 20),
            'new_fans': random.randint(0, 10)
        })
    
    return jsonify({
        'success': True,
        'agent': {
            'id': agent.id,
            'name': agent.name,
            'total_chats': agent.total_chats,
            'total_fans': agent.total_fans,
            'total_gifts_value': agent.total_gifts_value,
            'total_earnings': agent.total_earnings,
            'popularity_score': agent.popularity_score
        },
        'daily_stats': daily_stats
    })


# ============ 经济数据展示 ============

@app.route('/api/platform/economy')
def api_platform_economy():
    """平台经济数据API"""
    # 模拟数据（实际应从数据库聚合）
    total_creator_earnings = 1256800  # 模拟总创作者收益
    today_gifts = 3250  # 今日礼物发送量
    top_agents = [
        {'name': '星语', 'earnings': 15800, 'fans': 2340},
        {'name': '暖阳', 'earnings': 12500, 'fans': 1890},
        {'name': '诗风', 'earnings': 9800, 'fans': 1560},
        {'name': '月影', 'earnings': 7200, 'fans': 1200},
        {'name': '墨影', 'earnings': 5500, 'fans': 890}
    ]
    
    return jsonify({
        'success': True,
        'total_creator_earnings': total_creator_earnings,
        'today_gifts': today_gifts,
        'top_agents': top_agents
    })
