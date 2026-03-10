from datetime import datetime
from backend.extensions import db


class CartItem(db.Model):
    """购物车单品模型"""
    __tablename__ = "cart_items"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    
    quantity   = db.Column(db.Integer, default=1, nullable=False)
    # 商品的规格属性，比如颜色、尺码等，前端加购时传入 {"color": "Red", "size": "L"}
    attributes = db.Column(db.JSON, default=dict)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user    = db.relationship("User",    back_populates="cart_items")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id":         self.id,
            "userId":     self.user_id,
            "productId":  self.product_id,
            "quantity":   self.quantity,
            "attributes": self.attributes or {},
            "createdAt":  self.created_at.isoformat() if self.created_at else None,
            "updatedAt":  self.updated_at.isoformat() if self.updated_at else None,
            "product":    self.product.to_dict() if self.product else None,
        }

    def __repr__(self):
        return f"<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>"
