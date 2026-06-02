# SoulLink User Model Extension for Paywall
# Add this to models.py or use as a mixin

import json
from datetime import date

# Add these properties/methods to the User class in models.py

USER_PAYWALL_EXT = '''
    # ============ Paywall Fields (Add to User class) ============
    
    # These fields should already exist from db_update_paywall.sql
    # membership_type = db.Column(db.String(20), default='free')
    # membership_expires = db.Column(db.DateTime)
    # daily_usage = db.Column(db.Text, default='{}')
    # usage_reset_date = db.Column(db.Date)
    
    @property
    def is_pro_member(self):
        """Check if user is a Pro member (either by membership_type or legacy VIP)"""
        # Check new membership_type field
        if hasattr(self, 'membership_type') and self.membership_type == 'pro':
            # Also check if membership hasn't expired
            if hasattr(self, 'membership_expires') and self.membership_expires:
                from datetime import datetime
                if self.membership_expires < datetime.utcnow():
                    return False
            return True
        # Fallback to legacy VIP check
        if hasattr(self, 'is_vip') and self.is_vip:
            return True
        return False
    
    def get_daily_usage(self):
        """Get daily usage as a dictionary, resetting if needed"""
        from datetime import date
        
        # Check if we need to reset for a new day
        if hasattr(self, 'usage_reset_date') and self.usage_reset_date:
            if isinstance(self.usage_reset_date, str):
                reset_date = date.fromisoformat(self.usage_reset_date)
            else:
                reset_date = self.usage_reset_date
            
            if reset_date < date.today():
                # New day, reset usage
                return {}
        
        # Parse daily_usage JSON
        if hasattr(self, 'daily_usage') and self.daily_usage:
            try:
                if isinstance(self.daily_usage, str):
                    return json.loads(self.daily_usage)
                return self.daily_usage
            except json.JSONDecodeError:
                return {}
        return {}
    
    def check_feature_limit(self, feature_name):
        """Check if user can use a specific feature"""
        from paywall import check_feature_access
        return check_feature_access(self, feature_name)
    
    def record_usage(self, feature_name, amount=1):
        """Record usage of a feature"""
        from paywall import record_feature_usage
        record_feature_usage(self, feature_name, amount)
'''

# SQL to add columns to users table
ADD_COLUMNS_SQL = '''
-- Add paywall columns to users table
ALTER TABLE users ADD COLUMN membership_type VARCHAR(20) DEFAULT 'free';
ALTER TABLE users ADD COLUMN membership_expires DATETIME;
ALTER TABLE users ADD COLUMN daily_usage TEXT DEFAULT '{}';
ALTER TABLE users ADD COLUMN usage_reset_date DATE;
'''

print("User model extension created")
print("To apply:")
print("1. Run the SQL in ADD_COLUMNS_SQL on your database")
print("2. Add the USER_PAYWALL_EXT methods to the User class in models.py")
