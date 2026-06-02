# SoulLink - 微信支付 V3 API 模块
# 支持Native支付（扫码支付）和JSAPI支付（微信公众号内支付）

import os
import json
import time
import uuid
import base64
import hashlib
import logging
from datetime import datetime

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.backends import default_backend
from cryptography import x509

logger = logging.getLogger(__name__)

# ============ 配置 ============
def _decode_b64_env(env_key: str) -> str:
    """从环境变量读取base64编码内容并解码"""
    val = os.environ.get(env_key, "")
    if val:
        try:
            return base64.b64decode(val).decode('utf-8')
        except Exception:
            return val  # 如果不是base64，原样返回
    return ""

WXPAY_CONFIG = {
    "mch_id": os.environ.get("WX_MCH_ID", ""),
    "app_id": os.environ.get("WX_APP_ID", ""),
    "app_secret": os.environ.get("WX_APP_SECRET", ""),
    "api_v2_key": os.environ.get("WX_API_V2_KEY", ""),
    "api_v3_key": os.environ.get("WX_API_V3_KEY", ""),
    "cert_pem": os.environ.get("WX_CERT_PEM", "") or _decode_b64_env("WX_CERT_PEM_B64"),
    "key_pem": os.environ.get("WX_KEY_PEM", "") or _decode_b64_env("WX_KEY_PEM_B64"),
    "cert_p12_b64": os.environ.get("WX_CERT_P12_B64", ""),
    "notify_url": os.environ.get("WX_NOTIFY_URL", "https://ghealthorg.com/api/wxpay/notify"),
}

WXPAY_ENABLED = bool(WXPAY_CONFIG["mch_id"] and WXPAY_CONFIG["app_id"] and WXPAY_CONFIG["api_v3_key"])

# 微信支付V3 API 基础URL
WXPAY_BASE_URL = "https://api.mch.weixin.qq.com"

# 灵石充值套餐映射
LINGSTONE_PACKAGES = {
    'starter':  {'name': '新手礼包',   'amount': 30,  'price': 30,  'bonus': 5,   'icon': '🌱'},
    'standard': {'name': '标准充值',   'amount': 68,  'price': 68,  'bonus': 15,  'icon': '💎'},
    'premium':  {'name': '超值礼包',   'amount': 198, 'price': 198, 'bonus': 50,  'icon': '👑'},
    'ultimate': {'name': '尊享大礼包', 'amount': 498, 'price': 498, 'bonus': 150, 'icon': '🚀'},
}

# VIP套餐映射
VIP_PACKAGES = {
    'pro_monthly': {'name': '月度Pro会员', 'price': 29.9, 'duration_days': 30},
    'pro_yearly':  {'name': '年度Pro会员', 'price': 299,  'duration_days': 365},
}


def _load_private_key():
    """加载商户私钥"""
    key_pem = WXPAY_CONFIG["key_pem"]
    if not key_pem:
        # 尝试从文件加载
        key_path = os.environ.get("WX_KEY_PEM_PATH", "")
        if key_path and os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                key_pem = f.read().decode()
        elif os.path.exists('./微信证书/apiclient_key.pem'):
            with open('./微信证书/apiclient_key.pem', 'rb') as f:
                key_pem = f.read().decode()
    
    if not key_pem:
        logger.error("WeChat Pay private key not configured")
        return None
    
    try:
        if isinstance(key_pem, str):
            key_pem = key_pem.encode()
        return serialization.load_pem_private_key(key_pem, password=None, backend=default_backend())
    except Exception as e:
        logger.error(f"Failed to load private key: {e}")
        return None


def _load_certificate():
    """加载商户证书"""
    cert_pem = WXPAY_CONFIG["cert_pem"]
    if not cert_pem:
        cert_path = os.environ.get("WX_CERT_PEM_PATH", "")
        if cert_path and os.path.exists(cert_path):
            with open(cert_path, 'rb') as f:
                cert_pem = f.read().decode()
        elif os.path.exists('./微信证书/apiclient_cert.pem'):
            with open('./微信证书/apiclient_cert.pem', 'rb') as f:
                cert_pem = f.read().decode()
    
    if not cert_pem:
        logger.error("WeChat Pay certificate not configured")
        return None
    
    try:
        if isinstance(cert_pem, str):
            cert_pem = cert_pem.encode()
        return x509.load_pem_x509_certificate(cert_pem, default_backend())
    except Exception as e:
        logger.error(f"Failed to load certificate: {e}")
        return None


def _get_serial_no():
    """获取证书序列号"""
    cert = _load_certificate()
    if cert:
        return format(cert.serial_number, 'X')
    return ""


def _sign(message: str) -> str:
    """使用商户私钥对消息进行SHA256withRSA签名"""
    private_key = _load_private_key()
    if not private_key:
        return ""
    
    try:
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        logger.error(f"Sign failed: {e}")
        return ""


def _build_auth_header(method: str, url_path: str, body: str = "") -> str:
    """构建微信支付V3请求的Authorization头"""
    mch_id = WXPAY_CONFIG["mch_id"]
    serial_no = _get_serial_no()
    nonce_str = uuid.uuid4().hex
    timestamp = str(int(time.time()))
    
    # 构造签名串
    sign_message = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body}\n"
    
    signature = _sign(sign_message)
    if not signature:
        return ""
    
    return (
        f'WECHATPAY2-SHA256-RSA2048 '
        f'mchid="{mch_id}",'
        f'nonce_str="{nonce_str}",'
        f'timestamp="{timestamp}",'
        f'serial_no="{serial_no}",'
        f'signature="{signature}"'
    )


def _verify_notification(headers: dict, body: str) -> dict:
    """
    验证微信支付回调通知的签名并解密数据
    返回解密后的通知内容(dict)或None
    """
    api_v3_key = WXPAY_CONFIG["api_v3_key"]
    if not api_v3_key:
        logger.error("API v3 key not configured for notification verification")
        return None
    
    try:
        # 获取微信平台证书相关header
        wx_timestamp = headers.get('Wechatpay-Timestamp', '')
        wx_nonce = headers.get('Wechatpay-Nonce', '')
        wx_signature = headers.get('Wechatpay-Signature', '')
        wx_serial = headers.get('Wechatpay-Serial', '')
        
        if not wx_signature:
            logger.error("Missing Wechatpay-Signature header")
            return None
        
        # 验证签名（需要平台证书，此处简化处理，先解密数据）
        # 注意：生产环境应下载微信平台证书验证签名
        sign_message = f"{wx_timestamp}\n{wx_nonce}\n{body}\n"
        
        # 解密通知内容
        notification = json.loads(body)
        resource = notification.get('resource', {})
        
        if not resource:
            logger.error("No resource in notification")
            return None
        
        ciphertext = resource.get('ciphertext', '')
        nonce = resource.get('nonce', '')
        associated_data = resource.get('associated_data', '')
        
        if not ciphertext or not nonce:
            logger.error("Missing ciphertext or nonce in resource")
            return None
        
        # AES-256-GCM 解密
        decrypted = _decrypt_aes_gcm(api_v3_key, nonce, ciphertext, associated_data)
        if decrypted:
            return json.loads(decrypted)
        
        return None
    except Exception as e:
        logger.error(f"Notification verification failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def _decrypt_aes_gcm(api_v3_key: str, nonce: str, ciphertext: str, associated_data: str) -> str:
    """AES-256-GCM 解密微信支付回调数据"""
    try:
        from Crypto.Cipher import AES
        
        key = api_v3_key.encode('utf-8')
        nonce_bytes = nonce.encode('utf-8')
        ciphertext_bytes = base64.b64decode(ciphertext)
        associated_data_bytes = associated_data.encode('utf-8') if associated_data else b''
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce_bytes)
        cipher.update(associated_data_bytes)
        
        # GCM模式下，密文最后16字节是tag
        decrypted = cipher.decrypt_and_verify(
            ciphertext_bytes[:-16],
            ciphertext_bytes[-16:]
        )
        
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"AES-GCM decrypt failed: {e}")
        import traceback
        traceback.print_exc()
        return ""


def generate_out_trade_no() -> str:
    """生成商户订单号"""
    return f"SL{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


def create_native_order(out_trade_no: str, description: str, amount_cents: int, 
                        attach: str = "") -> dict:
    """
    创建Native支付订单（扫码支付）
    
    Args:
        out_trade_no: 商户订单号
        description: 商品描述
        amount_cents: 金额（分）
        attach: 附加数据（回调时原样返回）
    
    Returns:
        {'code_url': 'weixin://wxpay/...', 'out_trade_no': '...'} 或 {'error': '...'}
    """
    if not WXPAY_ENABLED:
        return {'error': 'WeChat Pay not configured'}
    
    url_path = "/v3/pay/transactions/native"
    url = WXPAY_BASE_URL + url_path
    
    body = {
        "appid": WXPAY_CONFIG["app_id"],
        "mchid": WXPAY_CONFIG["mch_id"],
        "description": description,
        "out_trade_no": out_trade_no,
        "notify_url": WXPAY_CONFIG["notify_url"],
        "amount": {
            "total": amount_cents,
            "currency": "CNY"
        },
    }
    
    if attach:
        body["attach"] = attach
    
    body_str = json.dumps(body, ensure_ascii=False)
    
    auth_header = _build_auth_header("POST", url_path, body_str)
    if not auth_header:
        return {'error': 'Failed to build auth header, check certificate configuration'}
    
    try:
        resp = requests.post(
            url,
            data=body_str.encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                'code_url': data.get('code_url', ''),
                'out_trade_no': out_trade_no
            }
        else:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            logger.error(f"WeChat Pay API error: {resp.status_code} - {error_data}")
            return {
                'error': f"WeChat Pay API error: {resp.status_code}",
                'detail': error_data
            }
    except Exception as e:
        logger.error(f"Create native order failed: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f'Network error: {str(e)}'}


def query_order(out_trade_no: str) -> dict:
    """
    查询订单状态
    
    Args:
        out_trade_no: 商户订单号
    
    Returns:
        订单信息dict
    """
    if not WXPAY_ENABLED:
        return {'error': 'WeChat Pay not configured'}
    
    url_path = f"/v3/pay/transactions/out-trade-no/{out_trade_no}?mchid={WXPAY_CONFIG['mch_id']}"
    url = WXPAY_BASE_URL + url_path
    
    auth_header = _build_auth_header("GET", url_path, "")
    if not auth_header:
        return {'error': 'Failed to build auth header'}
    
    try:
        resp = requests.get(
            url,
            headers={
                'Authorization': auth_header,
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            return resp.json()
        else:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            return {
                'error': f"Query failed: {resp.status_code}",
                'detail': error_data
            }
    except Exception as e:
        logger.error(f"Query order failed: {e}")
        return {'error': f'Network error: {str(e)}'}


def close_order(out_trade_no: str) -> dict:
    """关闭订单"""
    if not WXPAY_ENABLED:
        return {'error': 'WeChat Pay not configured'}
    
    url_path = f"/v3/pay/transactions/out-trade-no/{out_trade_no}/close"
    url = WXPAY_BASE_URL + url_path
    
    body = {"mchid": WXPAY_CONFIG["mch_id"]}
    body_str = json.dumps(body)
    
    auth_header = _build_auth_header("POST", url_path, body_str)
    if not auth_header:
        return {'error': 'Failed to build auth header'}
    
    try:
        resp = requests.post(
            url,
            data=body_str.encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
            },
            timeout=10
        )
        
        if resp.status_code in (200, 204):
            return {'success': True}
        else:
            return {'error': f"Close order failed: {resp.status_code}"}
    except Exception as e:
        return {'error': f'Network error: {str(e)}'}


def create_lingstone_order(user_id: int, package_id: str) -> dict:
    """
    创建灵石充值订单
    
    Args:
        user_id: 用户ID
        package_id: 套餐ID
    
    Returns:
        包含支付二维码URL的dict
    """
    pkg = LINGSTONE_PACKAGES.get(package_id)
    if not pkg:
        return {'error': 'Invalid package'}
    
    out_trade_no = generate_out_trade_no()
    description = f"灵石充值-{pkg['name']}"
    amount_cents = pkg['price'] * 100  # 转为分
    
    # 附加数据包含用户ID和套餐ID
    attach = json.dumps({
        'user_id': user_id,
        'package_id': package_id,
        'type': 'lingstone'
    })
    
    result = create_native_order(out_trade_no, description, amount_cents, attach)
    
    if 'error' in result:
        return result
    
    # 创建充值记录
    try:
        from models import db, LingStoneRecharge
        recharge = LingStoneRecharge(
            user_id=user_id,
            amount_paid=pkg['price'],
            lingstones_gained=pkg['amount'],
            bonus_gained=pkg['bonus'],
            payment_method='wechat',
            status='pending',
            order_no=out_trade_no
        )
        db.session.add(recharge)
        db.session.commit()
        logger.info(f"Created recharge record: {out_trade_no} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create recharge record: {e}")
        db.session.rollback()
    
    return {
        'code_url': result['code_url'],
        'out_trade_no': out_trade_no,
        'price': pkg['price'],
        'amount': pkg['amount'],
        'bonus': pkg['bonus']
    }


def create_vip_order(user_id: int, plan_id: str) -> dict:
    """
    创建VIP会员订单
    
    Args:
        user_id: 用户ID
        plan_id: 套餐ID (pro_monthly / pro_yearly)
    
    Returns:
        包含支付二维码URL的dict
    """
    plan = VIP_PACKAGES.get(plan_id)
    if not plan:
        return {'error': 'Invalid plan'}
    
    out_trade_no = generate_out_trade_no()
    description = f"SoulLink {plan['name']}"
    amount_cents = int(plan['price'] * 100)
    
    attach = json.dumps({
        'user_id': user_id,
        'plan_id': plan_id,
        'type': 'vip'
    })
    
    result = create_native_order(out_trade_no, description, amount_cents, attach)
    
    if 'error' in result:
        return result
    
    return {
        'code_url': result['code_url'],
        'out_trade_no': out_trade_no,
        'price': plan['price'],
        'plan_name': plan['name'],
        'duration_days': plan['duration_days']
    }


def handle_payment_success(out_trade_no: str, transaction_id: str, attach_data: dict = None) -> bool:
    """
    处理支付成功回调
    
    Args:
        out_trade_no: 商户订单号
        transaction_id: 微信支付交易号
        attach_data: 附加数据
    
    Returns:
        是否处理成功
    """
    try:
        from models import db, LingStoneRecharge, User, LingStoneTransaction
        
        # 查找充值记录
        recharge = LingStoneRecharge.query.filter_by(order_no=out_trade_no).first()
        
        if recharge and recharge.status == 'pending':
            # 更新充值记录
            recharge.status = 'completed'
            recharge.transaction_id = transaction_id
            recharge.completed_at = datetime.utcnow()
            
            # 给用户加灵石
            user = User.query.get(recharge.user_id)
            if user:
                total_stones = recharge.lingstones_gained + recharge.bonus_gained
                user.spirit_stones = (user.spirit_stones or 0) + total_stones
                
                # 记录灵石交易
                transaction = LingStoneTransaction(
                    user_id=user.id,
                    amount=total_stones,
                    transaction_type='recharge',
                    description=f"微信充值-{recharge.lingstones_gained}灵石+{recharge.bonus_gained}赠送"
                )
                db.session.add(transaction)
            
            db.session.commit()
            logger.info(f"Payment success processed: {out_trade_no}, user {recharge.user_id} got {recharge.lingstones_gained + recharge.bonus_gained} stones")
            return True
        
        # 处理VIP订单（通过attach数据）
        if attach_data and attach_data.get('type') == 'vip':
            user_id = attach_data.get('user_id')
            plan_id = attach_data.get('plan_id')
            plan = VIP_PACKAGES.get(plan_id)
            
            if user_id and plan:
                user = User.query.get(user_id)
                if user and hasattr(user, 'membership_type'):
                    from datetime import timedelta
                    user.membership_type = 'pro'
                    if hasattr(user, 'membership_expires'):
                        now = datetime.utcnow()
                        # 如果当前还有Pro会员，续期
                        if user.membership_expires and user.membership_expires > now:
                            user.membership_expires = user.membership_expires + timedelta(days=plan['duration_days'])
                        else:
                            user.membership_expires = now + timedelta(days=plan['duration_days'])
                    db.session.commit()
                    logger.info(f"VIP activated for user {user_id}: {plan_id}")
                    return True
        
        logger.warning(f"No pending recharge found for order: {out_trade_no}")
        return False
        
    except Exception as e:
        logger.error(f"Handle payment success failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        return False


# ============ Flask 路由注册 ============

def register_wxpay_routes(app, db_obj):
    """注册微信支付相关路由到Flask应用"""
    
    @app.route('/api/wxpay/create', methods=['POST'])
    def wxpay_create_order():
        """创建微信支付订单"""
        from flask import request, jsonify, session
        from flask_login import current_user
        
        if not WXPAY_ENABLED:
            return jsonify({'error': '微信支付未配置'}), 503
        
        if not current_user.is_authenticated:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.get_json(silent=True) or {}
        order_type = data.get('type', 'lingstone')  # lingstone 或 vip
        package_id = data.get('package_id', '')
        
        if not package_id:
            return jsonify({'error': '请选择充值套餐'}), 400
        
        if order_type == 'lingstone':
            result = create_lingstone_order(current_user.id, package_id)
        elif order_type == 'vip':
            result = create_vip_order(current_user.id, package_id)
        else:
            return jsonify({'error': '无效的订单类型'}), 400
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    @app.route('/api/wxpay/query/<out_trade_no>', methods=['GET'])
    def wxpay_query_order(out_trade_no):
        """查询微信支付订单状态"""
        from flask import jsonify
        from flask_login import current_user
        
        if not WXPAY_ENABLED:
            return jsonify({'error': '微信支付未配置'}), 503
        
        result = query_order(out_trade_no)
        
        # 如果订单支付成功，自动处理
        if result.get('trade_state') == 'SUCCESS':
            handle_payment_success(
                out_trade_no,
                result.get('transaction_id', ''),
                None
            )
        
        return jsonify(result)
    
    @app.route('/api/wxpay/notify', methods=['POST'])
    def wxpay_notify():
        """微信支付回调通知"""
        from flask import request, jsonify
        
        if not WXPAY_ENABLED:
            return jsonify({'code': 'FAIL', 'message': 'Not configured'}), 500
        
        body = request.get_data(as_text=True)
        headers = dict(request.headers)
        
        # 验证并解密通知
        decrypt_data = _verify_notification(headers, body)
        
        if decrypt_data:
            out_trade_no = decrypt_data.get('out_trade_no', '')
            transaction_id = decrypt_data.get('transaction_id', '')
            trade_state = decrypt_data.get('trade_state', '')
            attach_str = decrypt_data.get('attach', '')
            
            attach_data = None
            if attach_str:
                try:
                    attach_data = json.loads(attach_str)
                except:
                    pass
            
            if trade_state == 'SUCCESS':
                handle_payment_success(out_trade_no, transaction_id, attach_data)
            
            logger.info(f"WeChat Pay notification: {out_trade_no} - {trade_state}")
            
            # 返回成功响应
            return jsonify({'code': 'SUCCESS', 'message': 'OK'})
        
        logger.error("WeChat Pay notification verification failed")
        return jsonify({'code': 'FAIL', 'message': 'Verification failed'}), 400
    
    @app.route('/api/wxpay/status', methods=['GET'])
    def wxpay_status():
        """检查微信支付是否已配置"""
        from flask import jsonify
        return jsonify({
            'enabled': WXPAY_ENABLED,
            'mch_id': WXPAY_CONFIG['mch_id'][:4] + '****' if WXPAY_CONFIG['mch_id'] else '',
            'app_id': WXPAY_CONFIG['app_id'][:4] + '****' if WXPAY_CONFIG['app_id'] else ''
        })
    
    logger.info(f"WeChat Pay routes registered (enabled={WXPAY_ENABLED})")
