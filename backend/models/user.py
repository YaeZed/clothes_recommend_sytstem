from datetime import datetime
from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username   = db.Column(db.String(50),  nullable=False, unique=True)
    password   = db.Column(db.String(255), nullable=False)
    email      = db.Column(db.String(100), unique=True)
    nickname   = db.Column(db.String(50), default="")
    phone      = db.Column(db.String(20), default="")
    birthday   = db.Column(db.String(20), default="")
    avatar     = db.Column(db.String(255), default="")
    role       = db.Column(db.Enum("user", "admin"), default="user")

    # 用户画像 JSON 字段
    style_pref = db.Column(db.JSON, default=lambda: [])   # e.g. ["休闲", "运动"]
    size_info  = db.Column(db.JSON, default=lambda: {})   # e.g. {"height":170,"weight":60}
    addresses  = db.Column(db.JSON, default=lambda: [])   # [{"id":1, "name":"...", "phone":"...", "address":"...", "isDefault":True}]

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    behaviors       = db.relationship("UserBehavior",  back_populates="user", lazy="dynamic")
    recommendations = db.relationship("Recommendation", back_populates="user", lazy="dynamic")
    cart_items      = db.relationship("CartItem", back_populates="user", lazy="dynamic")

    def to_dict(self, include_private=False):
        data = {
            "id":        self.id,
            "username":  self.username,
            "nickname":  self.nickname,
            "phone":     self.phone,
            "birthday":  self.birthday,
            "email":     self.email,
            "avatar":    self.avatar,
            "role":      self.role,
            "stylePref": self.style_pref,
            "sizeInfo":  self.size_info,
            "addresses": self.addresses or [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.username}>"
