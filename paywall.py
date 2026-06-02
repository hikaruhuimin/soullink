# SoulLink Paywall Module
from datetime import datetime, date, timedelta
from functools import wraps
from flask import session, request, jsonify, redirect, flash, url_for
import json
import os

MEMBERSHIP_FREE = "free"
MEMBERSHIP_PRO = "pro"

FEATURE_DIVINATION = "divination"
FEATURE_SOULMATE_PORTRAIT = "soulmate_portrait"
FEATURE_AI_MATCHMAKER = "ai_matchmaker"
FEATURE_LOVE_LETTER = "love_letter"
FEATURE_PAST_LIFE = "past_life"
FEATURE_VOICE_COMPANION = "voice_companion"
FEATURE_AI_RITUAL = "ai_ritual"
FEATURE_DAILY_CHECKIN = "daily_checkin"
FEATURE_CHAT_ROOM = "chat_room"
FEATURE_TREE_HOLE = "tree_hole"

FEATURE_NAMES = {
    FEATURE_DIVINATION: {"zh": "AI Divination", "en": "AI Divination", "ja": "AI Divination"},
    FEATURE_SOULMATE_PORTRAIT: {"zh": "Soulmate Portrait", "en": "Soulmate Portrait", "ja": "Soulmate Portrait"},
    FEATURE_AI_MATCHMAKER: {"zh": "AI Matchmaker", "en": "AI Matchmaker", "ja": "AI Matchmaker"},
    FEATURE_LOVE_LETTER: {"zh": "AI Love Letter", "en": "AI Love Letter", "ja": "AI Love Letter"},
    FEATURE_PAST_LIFE: {"zh": "Past Life", "en": "Past Life", "ja": "Past Life"},
    FEATURE_VOICE_COMPANION: {"zh": "AI Voice", "en": "AI Voice", "ja": "AI Voice"},
    FEATURE_AI_RITUAL: {"zh": "Festival Rituals", "en": "Festival Rituals", "ja": "Festival Rituals"},
    FEATURE_DAILY_CHECKIN: {"zh": "Daily Check-in", "en": "Daily Check-in", "ja": "Daily Check-in"},
    FEATURE_CHAT_ROOM: {"zh": "Chat Room", "en": "Chat Room", "ja": "Chat Room"},
    FEATURE_TREE_HOLE: {"zh": "AI Tree Hole", "en": "AI Tree Hole", "ja": "AI Tree Hole"}
}

LIMIT_TYPE_DAILY = "daily"
LIMIT_TYPE_LIFETIME = "lifetime"
LIMIT_TYPE_UNLIMITED = "unlimited"

FEATURE_LIMITS = {
    FEATURE_DIVINATION: {"limit": 1, "limit_type": LIMIT_TYPE_DAILY, "display": {"zh": "AI Divination", "en": "AI Divination", "ja": "AI Divination"}},
    FEATURE_SOULMATE_PORTRAIT: {"limit": 1, "limit_type": LIMIT_TYPE_LIFETIME, "display": {"zh": "Soulmate Portrait", "en": "Soulmate Portrait", "ja": "Soulmate Portrait"}},
    FEATURE_AI_MATCHMAKER: {"limit": 1, "limit_type": LIMIT_TYPE_DAILY, "display": {"zh": "AI Matchmaker", "en": "AI Matchmaker", "ja": "AI Matchmaker"}},
    FEATURE_LOVE_LETTER: {"limit": 1, "limit_type": LIMIT_TYPE_LIFETIME, "display": {"zh": "AI Love Letter", "en": "AI Love Letter", "ja": "AI Love Letter"}},
    FEATURE_PAST_LIFE: {"limit": 1, "limit_type": LIMIT_TYPE_LIFETIME, "display": {"zh": "Past Life", "en": "Past Life", "ja": "Past Life"}},
    FEATURE_VOICE_COMPANION: {"limit": 180, "limit_type": LIMIT_TYPE_DAILY, "display": {"zh": "AI Voice", "en": "AI Voice", "ja": "AI Voice"}},
    FEATURE_AI_RITUAL: {"limit": 1, "limit_type": LIMIT_TYPE_DAILY, "display": {"zh": "Festival Rituals", "en": "Festival Rituals", "ja": "Festival Rituals"}},
    FEATURE_DAILY_CHECKIN: {"limit": -1, "limit_type": LIMIT_TYPE_UNLIMITED, "display": {"zh": "Daily Check-in", "en": "Daily Check-in", "ja": "Daily Check-in"}},
    FEATURE_CHAT_ROOM: {"limit": -1, "limit_type": LIMIT_TYPE_UNLIMITED, "display": {"zh": "Chat Room", "en": "Chat Room", "ja": "Chat Room"}},
    FEATURE_TREE_HOLE: {"limit": -1, "limit_type": LIMIT_TYPE_UNLIMITED, "display": {"zh": "AI Tree Hole", "en": "AI Tree Hole", "ja": "AI Tree Hole"}},
}

FREE_LIMITS = {
    "divination_per_day": 1,
    "chat_messages_per_day": 20,
    "agents_per_user": 3,
    "voice_minutes_per_day": 10,
}

# Stripe configuration loaded from environment variables
# IMPORTANT: Never hardcode Stripe keys in code!
STRIPE_CONFIG = {
    "enabled": os.environ.get("STRIPE_ENABLED", "false").lower() == "true",
    "secret_key": os.environ.get("STRIPE_SECRET_KEY", ""),
    "publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
    "webhook_secret": os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
    "test_mode": os.environ.get("STRIPE_TEST_MODE", "true").lower() == "true"
}

# For backwards compatibility with existing code
PAYWALL_ENABLED = STRIPE_CONFIG["enabled"]

PRICING = {
    "pro_monthly": {"name": {"zh": "Monthly Pro", "en": "Monthly Pro", "ja": "Monthly Pro"}, "amount": 499, "currency": "usd", "interval": "month", "features": ["unlimited_divination", "unlimited_voice", "exclusive_agents", "priority_support"]},
    "pro_yearly": {"name": {"zh": "Yearly Pro", "en": "Yearly Pro", "ja": "Yearly Pro"}, "amount": 3999, "currency": "usd", "interval": "year", "features": ["unlimited_divination", "unlimited_voice", "exclusive_agents", "priority_support", "early_access"]}
}

def get_user_from_session():
    from models import User
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

def is_pro_member(user):
    if user is None:
        return False
    if hasattr(user, "membership_type") and user.membership_type == MEMBERSHIP_PRO:
        if hasattr(user, "membership_expires") and user.membership_expires:
            if user.membership_expires < datetime.utcnow():
                return False
        return True
    if hasattr(user, "is_vip") and user.is_vip:
        return True
    return False

def get_feature_limit(feature_name):
    return FEATURE_LIMITS.get(feature_name, {})

def get_current_usage(user, feature_name):
    if user is None:
        return 0
    usage_data = {}
    if hasattr(user, "daily_usage") and user.daily_usage:
        try:
            usage_data = json.loads(user.daily_usage)
        except:
            usage_data = {}
    fl = get_feature_limit(feature_name)
    lt = fl.get("limit_type", LIMIT_TYPE_DAILY)
    if lt == LIMIT_TYPE_LIFETIME:
        return usage_data.get("lifetime_" + feature_name, 0)
    today_key = date.today().isoformat()
    return usage_data.get("daily", {}).get(feature_name, {}).get(today_key, 0)

def check_daily_limit(user, feature_name):
    if user is None:
        return True, None, -1
    if is_pro_member(user):
        return True, None, -1
    fl = get_feature_limit(feature_name)
    if fl.get("limit_type") == LIMIT_TYPE_UNLIMITED:
        return True, None, -1
    limit = fl.get("limit", 1)
    used = get_current_usage(user, feature_name)
    remaining = max(0, limit - used)
    if used >= limit:
        lang = session.get("language", "zh")
        dn = fl.get("display", {}).get(lang, feature_name)
        return False, "You have used all your free " + dn + " for today. Upgrade to Pro!", 0
    return True, None, remaining

def increment_usage(user, feature_name, amount=1):
    if user is None:
        return True, 0
    from models import db
    usage_data = {}
    if hasattr(user, "daily_usage") and user.daily_usage:
        try:
            usage_data = json.loads(user.daily_usage)
        except:
            pass
    fl = get_feature_limit(feature_name)
    lt = fl.get("limit_type", LIMIT_TYPE_DAILY)
    if lt == LIMIT_TYPE_LIFETIME:
        cur = usage_data.get("lifetime_" + feature_name, 0)
        usage_data["lifetime_" + feature_name] = cur + amount
    else:
        today_key = date.today().isoformat()
        if "daily" not in usage_data:
            usage_data["daily"] = {}
        if feature_name not in usage_data["daily"]:
            usage_data["daily"][feature_name] = {}
        cur = usage_data["daily"][feature_name].get(today_key, 0)
        usage_data["daily"][feature_name][today_key] = cur + amount
    user.daily_usage = json.dumps(usage_data, ensure_ascii=False)
    if hasattr(user, "usage_reset_date"):
        user.usage_reset_date = date.today()
    try:
        db.session.commit()
        return True, cur + amount
    except:
        db.session.rollback()
        return False, cur

def reset_daily_usage():
    from models import User, db
    today = date.today()
    for user in User.query.all():
        if hasattr(user, "usage_reset_date") and user.usage_reset_date and user.usage_reset_date < today:
            try:
                if hasattr(user, "daily_usage") and user.daily_usage:
                    usage_data = json.loads(user.daily_usage)
                    if "daily" in usage_data:
                        usage_data["daily"] = {}
                    user.daily_usage = json.dumps(usage_data)
                user.usage_reset_date = today
                db.session.commit()
            except:
                db.session.rollback()

def get_reset_info(user=None):
    now = datetime.utcnow()
    tomorrow = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
    seconds_until_reset = int((tomorrow - now).total_seconds())
    next_daily = {"seconds": seconds_until_reset, "formatted": str(seconds_until_reset // 3600) + "h " + str(seconds_until_reset % 3600 // 60) + "m"}
    days_until_sunday = (6 - date.today().weekday()) % 7
    if days_until_sunday == 0 and now.weekday() == 6:
        days_until_sunday = 7
    next_weekly = datetime.combine(date.today() + timedelta(days=days_until_sunday), datetime.min.time())
    weekly_seconds = int((next_weekly - now).total_seconds())
    next_weekly_reset = {"seconds": weekly_seconds, "formatted": str(weekly_seconds // 86400) + "d " + str(weekly_seconds % 86400 // 3600) + "h"}
    return {"daily": next_daily, "weekly": next_weekly_reset, "timezone": "UTC"}

def require_feature_access(feature_name, redirect_to_upgrade=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_user_from_session()
            allowed, msg, remaining = check_daily_limit(user, feature_name)
            if not allowed:
                if redirect_to_upgrade and request.is_xhr:
                    return jsonify({"success": False, "error": "limit_reached", "message": msg, "redirect": url_for("paywall_upgrade", feature=feature_name)}), 403
                elif redirect_to_upgrade:
                    flash(msg, "warning")
                    return redirect(url_for("paywall_upgrade", feature=feature_name))
                else:
                    return jsonify({"success": False, "error": "limit_reached", "message": msg}), 403
            if remaining >= 0:
                session["remaining_" + feature_name] = remaining - 1
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_feature_access(user, feature_name):
    if user is None:
        return {"allowed": True, "is_pro": False, "remaining": -1}
    if is_pro_member(user):
        return {"allowed": True, "is_pro": True, "remaining": -1}
    fl = get_feature_limit(feature_name)
    if fl.get("limit_type") == LIMIT_TYPE_UNLIMITED:
        return {"allowed": True, "is_pro": False, "remaining": -1}
    limit = fl.get("limit", 1)
    used = get_current_usage(user, feature_name)
    remaining = max(0, limit - used)
    return {"allowed": remaining > 0, "is_pro": False, "remaining": remaining}

def record_feature_usage(user, feature_name, amount=1):
    if user is None or is_pro_member(user):
        return True
    fl = get_feature_limit(feature_name)
    if fl.get("limit_type") == LIMIT_TYPE_UNLIMITED:
        return True
    success, _ = increment_usage(user, feature_name, amount)
    return success

def get_upgrade_message(feature_name, lang=None):
    if lang is None:
        lang = session.get("language", "zh")
    fl = get_feature_limit(feature_name)
    dn = fl.get("display", {}).get(lang, feature_name)
    return "Unlock unlimited " + dn

def init_stripe():
    if not STRIPE_CONFIG.get("enabled", False):
        return False
    try:
        import stripe
        if STRIPE_CONFIG.get("secret_key"):
            stripe.api_key = STRIPE_CONFIG["secret_key"]
            return True
    except ImportError:
        pass
    return False

def create_checkout_session(user, plan_id, success_url, cancel_url):
    if not init_stripe():
        return None
    import stripe
    plan = PRICING.get(plan_id)
    if not plan:
        return None
    lang = session.get("language", "zh")
    pname = plan["name"].get(lang, plan["name"].get("zh", "SoulLink Pro"))
    try:
        return stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": plan["currency"], "product_data": {"name": "SoulLink - " + pname}, "unit_amount": plan["amount"], "recurring": {"interval": plan["interval"]}}, "quantity": 1}],
            mode="subscription", success_url=success_url, cancel_url=cancel_url,
            metadata={"user_id": str(user.id), "plan_id": plan_id}
        )
    except Exception as e:
        print("Stripe error: " + str(e))
        return None

def verify_webhook_signature(payload, sig):
    if not init_stripe():
        return None
    import stripe
    try:
        return stripe.Webhook.construct_event(payload, sig, STRIPE_CONFIG["webhook_secret"])
    except:
        return None

def handle_successful_payment(event_data):
    from models import db, User
    try:
        if event_data["type"] == "checkout.session.completed":
            data = event_data["data"]["object"]
            uid = data.get("metadata", {}).get("user_id")
            pid = data.get("metadata", {}).get("plan_id")
            if uid and pid:
                user = User.query.get(int(uid))
                if user and pid in ["pro_monthly", "pro_yearly"]:
                    user.membership_type = MEMBERSHIP_PRO
                    days = 365 if pid == "pro_yearly" else 30
                    user.membership_expires = datetime.utcnow() + timedelta(days=days)
                    db.session.commit()
                    return True
    except:
        db.session.rollback()
    return False

def get_user_usage_stats(user):
    if user is None:
        return {}
    stats = {}
    for fname in FEATURE_LIMITS:
        fl = FEATURE_LIMITS[fname]
        lt = fl.get("limit_type")
        if lt == LIMIT_TYPE_UNLIMITED:
            stats[fname] = {"used": -1, "limit": -1, "remaining": -1, "limit_type": lt}
        else:
            cur = get_current_usage(user, fname)
            lim = fl.get("limit", 1)
            stats[fname] = {"used": cur, "limit": lim, "remaining": max(0, lim - cur), "limit_type": lt}
    return stats
