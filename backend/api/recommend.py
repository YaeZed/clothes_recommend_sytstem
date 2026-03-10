from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func, text
from backend.extensions import db
from backend.models.product import Product
from backend.models.behavior import Recommendation, UserBehavior

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.get("/hot")
def hot_recommend():
    """热门推荐：按销量排序，无需登录"""
    limit = min(int(request.args.get("limit", 20)), 50)
    products = (
        Product.query
        .filter_by(is_on_sale=True)
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": {
            "algoType": "hot",
            "items": [p.to_dict() for p in products],
        }
    })


@recommend_bp.get("/similar/<int:product_id>")
def similar_recommend(product_id):
    """
    相似商品推荐：基于同类目 + 同风格
    优先同类目同风格；若不足则扩大到同类目
    """
    limit   = min(int(request.args.get("limit", 10)), 30)
    product = Product.query.get_or_404(product_id)

    # 同类目同风格
    similar = (
        Product.query
        .filter(
            Product.id       != product_id,
            Product.is_on_sale == True,
            Product.category == product.category,
            Product.style    == product.style,
        )
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )

    # 不足时用同类目补充
    if len(similar) < limit:
        existing_ids = {p.id for p in similar} | {product_id}
        extra = (
            Product.query
            .filter(
                ~Product.id.in_(existing_ids),
                Product.is_on_sale == True,
                Product.category == product.category,
            )
            .order_by(Product.sales_count.desc())
            .limit(limit - len(similar))
            .all()
        )
        similar.extend(extra)

    return jsonify({
        "code": 200,
        "data": {
            "algoType": "content",
            "items": [p.to_dict() for p in similar],
        }
    })


@recommend_bp.get("/personal")
@jwt_required()
def personal_recommend():
    """
    个性化推荐：读取 recommendations 表中预计算的混合推荐结果
    若该用户无推荐数据（冷启动），降级到热门推荐
    """
    user_id   = int(get_jwt_identity())
    limit     = min(int(request.args.get("limit", 20)), 50)
    algo_type = request.args.get("algo", "hybrid")

    # 查询推荐缓存
    recs = (
        Recommendation.query
        .filter_by(user_id=user_id, algo_type=algo_type)
        .order_by(Recommendation.score.desc())
        .limit(limit)
        .all()
    )

    if recs:
        product_ids = [r.product_id for r in recs]
        score_map   = {r.product_id: r.score for r in recs}
        products    = Product.query.filter(Product.id.in_(product_ids)).all()
        # 按推荐分数重排序
        products.sort(key=lambda p: score_map.get(p.id, 0), reverse=True)
        return jsonify({
            "code": 200,
            "data": {
                "algoType": algo_type,
                "items":    [p.to_dict() for p in products],
                "coldStart": False,
            }
        })

    # 冷启动：降级热门推荐
    products = (
        Product.query
        .filter_by(is_on_sale=True)
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": {
            "algoType": "hot",
            "items":    [p.to_dict() for p in products],
            "coldStart": True,
        }
    })


@recommend_bp.get("/search")
def search_recommend():
    """
    搜索结果推荐：按关键词搜索并按销量排序
    支持可选的类目/风格过滤
    """
    keyword  = request.args.get("keyword", "").strip()
    category = request.args.get("category", "")
    style    = request.args.get("style",    "")
    limit    = min(int(request.args.get("limit", 20)), 50)

    if not keyword:
        return jsonify({"code": 400, "msg": "请输入搜索关键词"}), 400

    # 将关键词按空格/全角空格拆分成多个词，对每个词做 ilike 匹配（OR 关系）
    # 例如："T恤" → ["T恤"]，"T 恤" → ["T", "恤"]
    from sqlalchemy import or_
    tokens = [t for t in keyword.replace("\u3000", " ").split(" ") if t]
    if not tokens:
        tokens = [keyword]

    token_filters = [Product.title.ilike(f"%{t}%") for t in tokens]
    query = (
        Product.query
        .filter(
            Product.is_on_sale == True,
            or_(*token_filters),
        )
    )
    if category:
        query = query.filter_by(category=category)
    if style:
        query = query.filter_by(style=style)

    products = query.order_by(Product.sales_count.desc()).limit(limit).all()

    return jsonify({
        "code": 200,
        "data": {
            "keyword": keyword,
            "algoType": "search",
            "items":   [p.to_dict() for p in products],
            "total":   len(products),
        }
    })


@recommend_bp.get("/for-you")
def for_you():
    """
    首页「猜你喜欢」：
    - 已登录 → 个性化推荐（hybrid），冷启动降级到热门
    - 未登录 → 热门推荐
    """
    try:
        verify_jwt_in_request(optional=True)
        from flask_jwt_extended import get_jwt_identity as _get
        uid_str = _get()
        user_id = int(uid_str) if uid_str else None
    except Exception:
        user_id = None

    limit = min(int(request.args.get("limit", 20)), 50)

    if user_id:
        recs = (
            Recommendation.query
            .filter_by(user_id=user_id, algo_type="hybrid")
            .order_by(Recommendation.score.desc())
            .limit(limit)
            .all()
        )
        if recs:
            product_ids = [r.product_id for r in recs]
            score_map   = {r.product_id: r.score for r in recs}
            products    = Product.query.filter(Product.id.in_(product_ids)).all()
            products.sort(key=lambda p: score_map.get(p.id, 0), reverse=True)
            return jsonify({
                "code": 200,
                "data": {
                    "algoType": "hybrid",
                    "items": [p.to_dict() for p in products],
                    "coldStart": False,
                }
            })

    # 未登录或冷启动：热门推荐
    products = (
        Product.query
        .filter_by(is_on_sale=True)
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": {
            "algoType": "hot",
            "items": [p.to_dict() for p in products],
            "coldStart": True,
        }
    })
