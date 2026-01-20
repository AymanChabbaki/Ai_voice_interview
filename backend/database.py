"""
SQLite Database Setup for Smart Voice Interviewer
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import bcrypt

DATABASE_FILE = "interview_system.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            bio TEXT,
            experience_level TEXT DEFAULT 'Beginner',
            interests TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # User Stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            interview_count INTEGER DEFAULT 0,
            total_score REAL DEFAULT 0.0,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            last_interview_date TEXT,
            achievements TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Interview History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            date TEXT NOT NULL,
            pass_rate REAL NOT NULL,
            average_score REAL NOT NULL,
            questions_count INTEGER NOT NULL,
            passed INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_user(username: str, email: str, password: str, name: str) -> Optional[Dict]:
    """Create new user"""
    import uuid
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, email, password_hash, name, now, now))
        
        # Initialize stats
        cursor.execute("""
            INSERT INTO user_stats (user_id, achievements)
            VALUES (?, ?)
        """, (user_id, json.dumps([])))
        
        conn.commit()
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "name": name
        }
    except sqlite3.IntegrityError as e:
        return None
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
    user = cursor.fetchone()
    
    if user and verify_password(password, user['password_hash']):
        return dict(user)
    
    conn.close()
    return None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        user_dict = dict(user)
        
        # Get stats
        cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        stats = cursor.fetchone()
        
        if stats:
            stats_dict = dict(stats)
            user_dict.update({
                "interview_count": stats_dict["interview_count"],
                "total_score": stats_dict["total_score"],
                "current_streak": stats_dict["current_streak"],
                "best_streak": stats_dict["best_streak"],
                "last_interview_date": stats_dict["last_interview_date"],
                "achievements": json.loads(stats_dict["achievements"] or "[]")
            })
        
        # Parse interests
        if user_dict.get("interests"):
            user_dict["interests"] = json.loads(user_dict["interests"])
        else:
            user_dict["interests"] = []
        
        conn.close()
        return user_dict
    
    conn.close()
    return None

def update_user_profile(user_id: str, data: Dict) -> bool:
    """Update user profile"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        updates = []
        values = []
        
        if "name" in data:
            updates.append("name = ?")
            values.append(data["name"])
        if "email" in data:
            updates.append("email = ?")
            values.append(data["email"])
        if "bio" in data:
            updates.append("bio = ?")
            values.append(data["bio"])
        if "experience_level" in data:
            updates.append("experience_level = ?")
            values.append(data["experience_level"])
        if "interests" in data:
            updates.append("interests = ?")
            values.append(json.dumps(data["interests"]))
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(user_id)
        
        cursor.execute(f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE user_id = ?
        """, values)
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_interview_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Get user's interview history"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM interview_history
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (user_id, limit))
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return history

def add_interview_history(user_id: str, interview_data: Dict) -> bool:
    """Add interview to history"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO interview_history 
            (user_id, session_id, topic, date, pass_rate, average_score, questions_count, passed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            interview_data["session_id"],
            interview_data["topic"],
            interview_data["date"],
            interview_data["pass_rate"],
            interview_data["average_score"],
            interview_data["questions_count"],
            interview_data["passed"]
        ))
        
        conn.commit()
        return True
    finally:
        conn.close()

def update_user_stats(user_id: str, stats_update: Dict) -> Optional[List[Dict]]:
    """Update user stats and return new achievements"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get current stats
        cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
        current = cursor.fetchone()
        
        if not current:
            return None
        
        current_dict = dict(current)
        achievements = json.loads(current_dict["achievements"] or "[]")
        new_achievements = []
        
        # Update stats
        interview_count = current_dict["interview_count"] + 1
        total_score = current_dict["total_score"] + stats_update.get("pass_rate", 0)
        
        # Calculate streak
        from datetime import datetime, timedelta
        today = datetime.now().date()
        last_date_str = current_dict.get("last_interview_date")
        
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str).date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day, keep current streak
                current_streak = current_dict["current_streak"]
            elif days_diff == 1:
                # Consecutive day, increment streak
                current_streak = current_dict["current_streak"] + 1
            else:
                # Streak broken, reset to 1
                current_streak = 1
        else:
            # First interview
            current_streak = 1
        
        best_streak = max(current_dict["best_streak"], current_streak)
        last_date = today.isoformat()
        
        # Check achievements
        if interview_count == 1 and "first_interview" not in achievements:
            achievements.append("first_interview")
            new_achievements.append({"id": "first_interview", "title": "🎉 Getting Started", "description": "Completed your first interview!"})
        
        if stats_update.get("pass_rate", 0) >= 100 and "perfect_score" not in achievements:
            achievements.append("perfect_score")
            new_achievements.append({"id": "perfect_score", "title": "⭐ Perfect!", "description": "Achieved 100% pass rate!"})
        
        if interview_count == 10 and "ten_interviews" not in achievements:
            achievements.append("ten_interviews")
            new_achievements.append({"id": "ten_interviews", "title": "🏆 Dedicated Learner", "description": "Completed 10 interviews!"})
        
        if current_streak == 5 and "five_day_streak" not in achievements:
            achievements.append("five_day_streak")
            new_achievements.append({"id": "five_day_streak", "title": "🔥 On Fire!", "description": "5 day streak maintained!"})
        
        if interview_count == 50 and "fifty_interviews" not in achievements:
            achievements.append("fifty_interviews")
            new_achievements.append({"id": "fifty_interviews", "title": "💎 Master Learner", "description": "Completed 50 interviews!"})
        
        # Update database
        cursor.execute("""
            UPDATE user_stats
            SET interview_count = ?,
                total_score = ?,
                current_streak = ?,
                best_streak = ?,
                last_interview_date = ?,
                achievements = ?
            WHERE user_id = ?
        """, (interview_count, total_score, current_streak, best_streak, last_date, json.dumps(achievements), user_id))
        
        conn.commit()
        return new_achievements
    finally:
        conn.close()
