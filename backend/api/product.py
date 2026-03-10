from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func
from backend.extensions import db
from backend.models.product import Product
from backend.models.behavior import UserBehavior

product_bp = Blueprint("product", __name__)


@product_bp.get("")
def list_products():
    """商品列表：支持关键词搜索、类目/风格筛选、多维度排序、分页"""
    keyword  = request.args.get("keyword",  "")
    category = request.args.get("category", "")
    style    = request.args.get("style",    "")
    sort_by  = request.args.get("sortBy",   "sales_count")   # sales_count | price_asc | price_desc | newest
    page     = int(request.args.get("page",     1))
    per_page = min(int(request.args.get("perPage", 20)), 100)  # 最大 100

    query = Product.query.filter_by(is_on_sale=True)

    if keyword:
        import re
        from sqlalchemy import or_
        # 先检查关键词是否直接匹配某个 category（精确分类搜索优先）
        from backend.models.product import Product as P_check
        matching_cats = [
            row[0] for row in
            db.session.query(P_check.category).distinct().filter(
                P_check.category == keyword
            ).all()
        ]
        if matching_cats:
            # 关键词精确匹配某分类 → 只按分类过滤
            query = query.filter(Product.category == keyword)
        else:
            # 普通模糊搜索：将关键词按空格和中英文边界分割，所有词必须同时出现（AND）
            normalized = keyword.replace("\u3000", " ")
            parts = normalized.split(" ")
            tokens = []
            for part in parts:
                if not part:
                    continue
                sub = re.split(
                    r"(?<=[a-zA-Z0-9])(?=[\u4e00-\u9fff])|(?<=[\u4e00-\u9fff])(?=[a-zA-Z0-9])",
                    part,
                )
                tokens.extend([s for s in sub if s])
            if not tokens:
                tokens = [keyword]
            # AND 逻辑：每个 token 都必须出现在标题中，避免单字母Token('T')污染结果
            for t in tokens:
                query = query.filter(Product.title.ilike(f"%{t}%"))
    if category:
        query = query.filter_by(category=category)
    if style:
        query = query.filter_by(style=style)

    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.sales_count.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "code": 200,
        "data": {
            "items":   [p.to_dict() for p in pagination.items],
            "total":   pagination.total,
            "page":    page,
            "perPage": per_page,
            "pages":   pagination.pages,
        }
    })


@product_bp.get("/<int:product_id>")
def get_product(product_id):
    """商品详情（含完整描述、属性、尺码表等）"""
    product = Product.query.get_or_404(product_id)
    return jsonify({"code": 200, "data": product.to_dict(detail=True)})


@product_bp.get("/categories")
def list_categories():
    """获取所有在售商品的类目列表（前端筛选用）"""
    rows = (
        db.session.query(Product.category, func.count(Product.id).label("cnt"))
        .filter_by(is_on_sale=True)
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    return jsonify({
        "code": 200,
        "data": [{"name": r.category, "count": r.cnt} for r in rows]
    })


@product_bp.get("/styles")
def list_styles():
    """获取所有在售商品的风格列表（前端筛选用）"""
    rows = (
        db.session.query(Product.style, func.count(Product.id).label("cnt"))
        .filter_by(is_on_sale=True)
        .filter(Product.style.isnot(None))
        .group_by(Product.style)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    return jsonify({
        "code": 200,
        "data": [{"name": r.style, "count": r.cnt} for r in rows]
    })


@product_bp.get("/hot")
def hot_products():
    """热门商品（按销量 Top-N）"""
    limit = min(int(request.args.get("limit", 10)), 50)
    products = (
        Product.query
        .filter_by(is_on_sale=True)
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": [p.to_dict() for p in products]
    })
