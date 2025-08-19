import aiosqlite
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    is_bot BOOLEAN,
                    is_premium BOOLEAN,
                    language TEXT DEFAULT 'fa',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ads table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    gift_link TEXT NOT NULL,
                    price TEXT NOT NULL,
                    description TEXT DEFAULT 'توضیحات ندارد',
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'unpaid',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Support requests table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS support_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    admin_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    responded_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            await db.commit()
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None,
                      language_code: str = None, is_bot: bool = False,
                      is_premium: bool = False, language: str = 'fa'):
        """Add or update user information"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code, is_bot, is_premium, language, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name, language_code, is_bot, is_premium, language))
            await db.commit()
    
    async def create_ad(self, user_id: int, gift_link: str, price: str, description: str = 'توضیحات ندارد') -> int:
        """Create a new ad and return its ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO ads (user_id, gift_link, price, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, gift_link, price, description))
            await db.commit()
            return cursor.lastrowid
    
    async def get_ad(self, ad_id: int) -> Optional[Dict[str, Any]]:
        """Get ad by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT a.*, u.username, u.first_name, u.last_name
                FROM ads a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.id = ?
            """, (ad_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_pending_ads(self) -> List[Dict[str, Any]]:
        """Get all pending ads"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT a.*, u.username, u.first_name, u.last_name
                FROM ads a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.status = 'pending' AND a.payment_status = 'paid'
                ORDER BY a.created_at ASC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def update_ad_status(self, ad_id: int, status: str):
        """Update ad status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE ads SET status = ?, approved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, ad_id))
            await db.commit()
    
    async def update_payment_status(self, ad_id: int, status: str):
        """Update payment status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE ads SET payment_status = ?
                WHERE id = ?
            """, (status, ad_id))
            await db.commit()
    
    async def get_user_ads(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all ads by user"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM ads
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Support requests methods
    async def create_support_request(self, user_id: int, message: str) -> int:
        """Create a new support request"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO support_requests (user_id, message)
                VALUES (?, ?)
            """, (user_id, message))
            await db.commit()
            return cursor.lastrowid
    
    async def get_pending_support_requests(self) -> List[Dict[str, Any]]:
        """Get all pending support requests"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT sr.*, u.username, u.first_name, u.last_name
                FROM support_requests sr
                JOIN users u ON sr.user_id = u.user_id
                WHERE sr.status = 'pending'
                ORDER BY sr.created_at ASC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_support_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Get support request by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT sr.*, u.username, u.first_name, u.last_name
                FROM support_requests sr
                JOIN users u ON sr.user_id = u.user_id
                WHERE sr.id = ?
            """, (request_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def respond_to_support_request(self, request_id: int, response: str):
        """Respond to a support request"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE support_requests 
                SET status = 'responded', admin_response = ?, responded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (response, request_id))
            await db.commit()
    
    # User management methods for super admin
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM users
                ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with stats"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT u.*, 
                       COUNT(DISTINCT a.id) as total_ads,
                       COUNT(DISTINCT CASE WHEN a.status = 'approved' THEN a.id END) as approved_ads,
                       COUNT(DISTINCT sr.id) as support_requests
                FROM users u
                LEFT JOIN ads a ON u.user_id = a.user_id
                LEFT JOIN support_requests sr ON u.user_id = sr.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id
            """, (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_user_stats(self) -> Dict[str, int]:
        """Get general user statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT 
                    COUNT(DISTINCT u.user_id) as total_users,
                    COUNT(DISTINCT a.id) as total_ads,
                    COUNT(DISTINCT CASE WHEN a.status = 'approved' THEN a.id END) as approved_ads,
                    COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN a.id END) as pending_ads,
                    COUNT(DISTINCT sr.id) as total_support_requests,
                    COUNT(DISTINCT CASE WHEN sr.status = 'pending' THEN sr.id END) as pending_support_requests
                FROM users u
                LEFT JOIN ads a ON u.user_id = a.user_id
                LEFT JOIN support_requests sr ON u.user_id = sr.user_id
            """)
            row = await cursor.fetchone()
            return dict(row) if row else {}
    
    async def update_user_language(self, user_id: int, language: str):
        """Update user's preferred language"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET language = ?, last_seen = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (language, user_id))
            await db.commit()
    
    async def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT language FROM users WHERE user_id = ?
            """, (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else 'fa'  # Default to Persian
    
    async def get_user(self, user_id: int) -> Optional[tuple]:
        """Get user by ID - returns tuple for compatibility"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT user_id, username, first_name, last_name, language_code, 
                       is_bot, is_premium, language, created_at, last_seen
                FROM users WHERE user_id = ?
            """, (user_id,))
            row = await cursor.fetchone()
            return row if row else None