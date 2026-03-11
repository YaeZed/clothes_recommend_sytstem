import json
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, cast, Date
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

    # 1. 品类分布统计
    category_stats = (
        db.session.query(Product.category, func.count(Product.id))
        .filter(Product.is_on_sale == True)
        .group_by(Product.category)
        .all()
    )

    # 2. 近7日行为趋势
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    trend_raw = (
        db.session.query(
            cast(UserBehavior.created_at, Date).label('date'),
            UserBehavior.action_type,
            func.count(UserBehavior.id)
        )
        .filter(UserBehavior.created_at >= seven_days_ago)
        .group_by('date', UserBehavior.action_type)
        .all()
    )
    
    # 格式化趋势数据: { "2023-01-01": { "view": 10, "cart": 2 }, ... }
    behavior_trend = {}
    for date, action, count in trend_raw:
        d_str = date.strftime('%m-%d')
        if d_str not in behavior_trend:
            behavior_trend[d_str] = {}
        behavior_trend[d_str][action] = count

    # 3. 算法评估指标 (从 JSON 加载)
    algo_metrics = {}
    metrics_path = os.path.join(current_app.root_path, 'data', 'algo_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r', encoding='utf-8') as f:
            algo_metrics = json.load(f)

    return jsonify({
        "code": 200,
        "data": {
            "userCount":    user_count,
            "productCount": product_count,
            "behaviorStats": {row[0]: row[1] for row in behavior_stats},
            "categoryStats": {row[0] or "未分类": row[1] for row in category_stats},
            "behaviorTrend": behavior_trend,
            "algoMetrics":   algo_metrics
        }
    })
