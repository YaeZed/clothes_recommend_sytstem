from datetime import datetime
from backend.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title       = db.Column(db.String(200), nullable=False)
    category    = db.Column(db.String(50),  index=True)   # 上衣/裤子/裙子/外套...
    style       = db.Column(db.String(50),  index=True)   # 休闲/正式/运动...
    price       = db.Column(db.Numeric(10, 2), default=0)
    sales_count = db.Column(db.Integer, default=0, index=True)
    stock       = db.Column(db.Integer, default=0)
    is_on_sale  = db.Column(db.Boolean, default=True, index=True)

    # JSON 字段
    images      = db.Column(db.JSON, default=list)   # 图片 URL 列表
    attributes  = db.Column(db.JSON, default=dict)   # 尺码/颜色/材质等
    description = db.Column(db.Text, default="")

    # 特征向量（推荐算法使用，存文本描述，向量计算时动态获取）
    tags        = db.Column(db.JSON, default=list)   # e.g. ["纯棉","宽松","百搭"]

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    behaviors       = db.relationship("UserBehavior",  back_populates="product", lazy="dynamic")
    recommendations = db.relationship("Recommendation", back_populates="product", lazy="dynamic")

    def to_dict(self, detail=False):
        data = {
            "id":         self.id,
            "title":      self.title,
            "category":   self.category,
            "style":      self.style,
            "price":      float(self.price) if self.price else 0,
            "salesCount": self.sales_count,
            "isOnSale":   self.is_on_sale,
            "images":     self.images or [],
            "tags":       self.tags or [],
        }
        if detail:
            data.update({
                "stock":       self.stock,
                "attributes":  self.attributes or {},
                "description": self.description,
                "createdAt":   self.created_at.isoformat() if self.created_at else None,
            })
        return data

    def __repr__(self):
        return f"<Product {self.id}: {self.title[:20]}>"
