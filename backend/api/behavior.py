from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, case
from backend.extensions import db
from backend.models.behavior import UserBehavior
from backend.models.product import Product

behavior_bp = Blueprint("behavior", __name__)

# 行为权重映射
BEHAVIOR_WEIGHTS = {
    "view":     0.2,
    "collect":  0.4,
    "cart":     0.6,
    "purchase": 1.0,
}

VALID_ACTIONS = set(BEHAVIOR_WEIGHTS.keys())


@behavior_bp.post("")
@jwt_required()
def record_behavior():
    """
    上报用户行为事件
    Body: { "productId": 1, "actionType": "view", "duration": 30 }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    product_id  = data.get("productId")
    action_type = data.get("actionType")
    duration    = data.get("duration", 0)

    if not product_id or action_type not in VALID_ACTIONS:
        return jsonify({"code": 400, "msg": f"参数错误，actionType 必须为 {'/'.join(VALID_ACTIONS)}"}), 400

    # 验证商品存在
    if not Product.query.get(product_id):
        return jsonify({"code": 404, "msg": "商品不存在"}), 404

    behavior = UserBehavior(
        user_id     = user_id,
        product_id  = product_id,
        action_type = action_type,
        duration    = duration,
    )
    db.session.add(behavior)
    db.session.commit()

    return jsonify({"code": 200, "msg": "行为记录成功"})


@behavior_bp.get("/history")
@jwt_required()
def behavior_history():
    """获取当前用户的行为历史（分页）"""
    user_id  = int(get_jwt_identity())
    page     = int(request.args.get("page",     1))
    per_page = min(int(request.args.get("perPage", 20)), 100)

    pagination = (
        UserBehavior.query
        .filter_by(user_id=user_id)
        .order_by(UserBehavior.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    # 批量加载商品信息
    product_ids = [b.product_id for b in pagination.items]
    products    = {p.id: p for p in Product.query.filter(Product.id.in_(product_ids)).all()}

    items = []
    for b in pagination.items:
        d = b.to_dict()
        p = products.get(b.product_id)
        d["product"] = p.to_dict() if p else None
        items.append(d)

    return jsonify({
        "code": 200,
        "data": {
            "items": items,
            "total": pagination.total,
            "page":  page,
        }
    })


@behavior_bp.get("/favorites")
@jwt_required()
def list_favorites():
    """收藏夹：返回用户收藏过（collect）的商品列表"""
    user_id  = int(get_jwt_identity())
    page     = int(request.args.get("page",     1))
    per_page = min(int(request.args.get("perPage", 20)), 100)

    # 用子查询去重，取最近 collect 时间
    from sqlalchemy import distinct
    subq = (
        db.session.query(func.max(UserBehavior.id).label("max_id"))
        .filter_by(user_id=user_id, action_type="collect")
        .group_by(UserBehavior.product_id)
        .subquery()
    )
    behaviors = (
        UserBehavior.query
        .join(subq, UserBehavior.id == subq.c.max_id)
        .order_by(UserBehavior.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    product_ids = [b.product_id for b in behaviors.items]
    products    = {p.id: p for p in Product.query.filter(Product.id.in_(product_ids)).all()}

    return jsonify({
        "code": 200,
        "data": {
            "items": [
                {**products[b.product_id].to_dict(), "collectedAt": b.created_at.isoformat()}
                for b in behaviors.items
                if b.product_id in products
            ],
            "total": behaviors.total,
            "page":  page,
        }
    })


@behavior_bp.get("/favorites/ids")
@jwt_required()
def list_favorite_ids():
    """返回当前用户收藏的所有商品 ID 列表（用于前端状态初始化）"""
    user_id = int(get_jwt_identity())
    rows = (
        db.session.query(UserBehavior.product_id)
        .filter_by(user_id=user_id, action_type="collect")
        .distinct()
        .all()
    )
    return jsonify({"code": 200, "data": [r.product_id for r in rows]})


@behavior_bp.delete("/favorites/<int:product_id>")
@jwt_required()
def remove_favorite(product_id):
    """取消收藏：删除该用户对该商品的所有 collect 行为记录"""
    user_id = int(get_jwt_identity())
    UserBehavior.query.filter_by(
        user_id=user_id, product_id=product_id, action_type="collect"
    ).delete()
    db.session.commit()
    return jsonify({"code": 200, "msg": "已取消收藏"})


@behavior_bp.get("/stats")
@jwt_required()
def behavior_stats():
    """当前用户行为统计（各类型行为数）"""
    user_id = int(get_jwt_identity())
    rows = (
        db.session.query(
            UserBehavior.action_type,
            func.count(UserBehavior.id).label("cnt")
        )
        .filter_by(user_id=user_id)
        .group_by(UserBehavior.action_type)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": {r.action_type: r.cnt for r in rows}
    })


@behavior_bp.get("/portrait")
@jwt_required()
def user_portrait():
    """
    用户画像接口 —— 为个人中心"我的画像"页提供可视化数据
    返回：
      - behaviorStats:  各行为类型数量（view/collect/cart/purchase）
      - categoryPref:   偏好品类 Top5（按加权行为分排序）
      - stylePref:      用户设置的风格偏好标签
      - weeklyActivity: 最近 7 天每日行为数量（折线图用）
    """
    from datetime import datetime, timedelta
    from backend.models.user import User

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    # 1. 行为类型统计
    action_rows = (
        db.session.query(
            UserBehavior.action_type,
            func.count(UserBehavior.id).label("cnt")
        )
        .filter_by(user_id=user_id)
        .group_by(UserBehavior.action_type)
        .all()
    )
    behavior_stats = {r.action_type: r.cnt for r in action_rows}

    # 2. 品类偏好（基于行为权重加权）
    category_rows = (
        db.session.query(
            Product.category,
            func.sum(
                case(
                    (UserBehavior.action_type == "view",     0.2),
                    (UserBehavior.action_type == "collect",  0.4),
                    (UserBehavior.action_type == "cart",     0.6),
                    (UserBehavior.action_type == "purchase", 1.0),
                    else_=0
                )
            ).label("score")
        )
        .join(Product, UserBehavior.product_id == Product.id)
        .filter(UserBehavior.user_id == user_id)
        .group_by(Product.category)
        .order_by(func.sum(
            case(
                (UserBehavior.action_type == "view",     0.2),
                (UserBehavior.action_type == "collect",  0.4),
                (UserBehavior.action_type == "cart",     0.6),
                (UserBehavior.action_type == "purchase", 1.0),
                else_=0
            )
        ).desc())
        .limit(5)
        .all()
    )
    category_pref = [{"category": r.category, "score": round(float(r.score), 2)} for r in category_rows]

    # 3. 最近 7 天每日行为数
    today = datetime.now().date()
    weekly = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        cnt = UserBehavior.query.filter(
            UserBehavior.user_id == user_id,
            func.date(UserBehavior.created_at) == day
        ).count()
        weekly.append({"date": str(day), "count": cnt})

    return jsonify({
        "code": 200,
        "data": {
            "behaviorStats":  behavior_stats,
            "categoryPref":   category_pref,
            "stylePref":      user.style_pref or [],
            "sizeInfo":       user.size_info or {},
            "weeklyActivity": weekly,
        }
    })

