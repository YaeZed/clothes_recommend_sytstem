from datetime import datetime
from backend.extensions import db


class Order(db.Model):
    """订单模型"""
    __tablename__ = "orders"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no   = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status       = db.Column(db.Enum("pending", "paid", "shipped", "completed", "cancelled"), default="pending", index=True)
    
    # 收货信息快照
    receiver_name  = db.Column(db.String(50), default="")
    receiver_phone = db.Column(db.String(20), default="")
    receiver_addr  = db.Column(db.String(255), default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at    = db.Column(db.DateTime, nullable=True)

    # 关系
    user  = db.relationship("User", backref=db.backref("orders", lazy="dynamic"))
    items = db.relationship("OrderItem", back_populates="order", lazy="joined", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":          self.id,
            "orderNo":     self.order_no,
            "totalAmount": float(self.total_amount),
            "status":      self.status,
            "receiver": {
                "name":    self.receiver_name,
                "phone":   self.receiver_phone,
                "address": self.receiver_addr,
            },
            "createdAt":   self.created_at.isoformat() if self.created_at else None,
            "paidAt":      self.paid_at.isoformat() if self.paid_at else None,
            "items":       [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    """订单商品详情。记录快照时的价格和名称"""
    __tablename__ = "order_items"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    
    product_title = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(255), default="")
    price         = db.Column(db.Numeric(10, 2), nullable=False)  # 购买时的单价
    quantity      = db.Column(db.Integer, nullable=False, default=1)
    attributes    = db.Column(db.JSON, default=dict)

    # 关系
    order   = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id":           self.id,
            "productId":    self.product_id,
            "productTitle": self.product_title,
            "productImage": self.product_image,
            "price":        float(self.price),
            "quantity":     self.quantity,
            "attributes":   self.attributes or {}
        }
