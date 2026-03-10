from datetime import datetime
from backend.extensions import db


class UserBehavior(db.Model):
    """用户行为日志表 —— 推荐算法的核心输入"""
    __tablename__ = "user_behaviors"

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False, index=True)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    action_type = db.Column(
        db.Enum("view", "collect", "cart", "purchase"),
        nullable=False,
        index=True,
    )
    duration    = db.Column(db.Integer, default=0)   # 停留时长（秒），view 时有意义
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 关系
    user    = db.relationship("User",    back_populates="behaviors")
    product = db.relationship("Product", back_populates="behaviors")

    def to_dict(self):
        return {
            "id":         self.id,
            "userId":     self.user_id,
            "productId":  self.product_id,
            "actionType": self.action_type,
            "duration":   self.duration,
            "createdAt":  self.created_at.isoformat() if self.created_at else None,
        }


class Recommendation(db.Model):
    """推荐结果缓存表 —— 离线计算后写入，API 直接读取"""
    __tablename__ = "recommendations"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    score      = db.Column(db.Float,   nullable=False)
    algo_type  = db.Column(
        db.Enum("hot", "cf", "content", "deepfm", "hybrid"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user    = db.relationship("User",    back_populates="recommendations")
    product = db.relationship("Product", back_populates="recommendations")

    def to_dict(self):
        return {
            "userId":    self.user_id,
            "productId": self.product_id,
            "score":     self.score,
            "algoType":  self.algo_type,
        }
