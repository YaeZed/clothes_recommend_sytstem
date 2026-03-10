from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from backend.extensions import db
from backend.models.user import User
from backend.models.product import Product
from backend.models.behavior import UserBehavior

admin_bp = Blueprint("admin", __name__)


def require_role(allowed_roles):
    """权限校验：检查当前用户是否具有允许的角色"""
    user_id = int(get_jwt_identity())
    user    = User.query.get(user_id)
    if not user or user.role not in allowed_roles:
        return jsonify({"code": 403, "msg": "权限不足，需要 " + "/".join(allowed_roles) + " 角色"}), 403
    return None


# ── 商品管理 (商家和管理员均可) ───────────────────────────────────────────────────

@admin_bp.get("/products")
@jwt_required()
def admin_list_products():
    err = require_role(["admin", "merchant"])
    if err:
        return err
    page     = int(request.args.get("page",     1))
    per_page = int(request.args.get("perPage", 20))
    pagination = Product.query.order_by(Product.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "code": 200,
        "data": {
            "items":   [p.to_dict(detail=True) for p in pagination.items],
            "total":   pagination.total,
            "page":    page,
            "pages":   pagination.pages,
        }
    })


@admin_bp.post("/products")
@jwt_required()
def admin_create_product():
    err = require_role(["admin", "merchant"])
    if err:
        return err
    data    = request.get_json()
    product = Product(
        title       = data["title"],
        category    = data.get("category", ""),
        style       = data.get("style",    ""),
        price       = data.get("price",    0),
        stock       = data.get("stock",    0),
        images      = data.get("images",   []),
        attributes  = data.get("attributes", {}),
        description = data.get("description", ""),
        tags        = data.get("tags",     []),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"code": 201, "msg": "商品创建成功", "data": product.to_dict(detail=True)}), 201


@admin_bp.put("/products/<int:product_id>")
@jwt_required()
def admin_update_product(product_id):
    err = require_role(["admin", "merchant"])
    if err:
        return err
    product = Product.query.get_or_404(product_id)
    data    = request.get_json()
    for field in ("title", "category", "style", "price", "stock",
                  "images", "attributes", "description", "tags", "is_on_sale"):
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({"code": 200, "msg": "更新成功", "data": product.to_dict(detail=True)})


@admin_bp.delete("/products/<int:product_id>")
@jwt_required()
def admin_delete_product(product_id):
    err = require_role(["admin", "merchant"])
    if err:
        return err
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"code": 200, "msg": "删除成功"})


# ── 数据统计 ───────────────────────────────────────────────────

@admin_bp.get("/stats")
@jwt_required()
def admin_stats():
    err = require_role(["admin"])
    if err:
        return err

    # 各行为类型统计
    behavior_stats = (
        db.session.query(UserBehavior.action_type, func.count(UserBehavior.id))
        .group_by(UserBehavior.action_type)
        .all()
    )
    # 用户总数
    user_count    = User.query.filter_by(role="user").count()
    product_count = Product.query.filter_by(is_on_sale=True).count()

    return jsonify({
        "code": 200,
        "data": {
            "userCount":    user_count,
            "productCount": product_count,
            "behaviorStats": {row[0]: row[1] for row in behavior_stats},
        }
    })
