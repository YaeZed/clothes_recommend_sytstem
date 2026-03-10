from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.cart import CartItem
from backend.models.product import Product
from backend.models.behavior import UserBehavior

cart_bp = Blueprint("cart", __name__)


@cart_bp.get("")
@jwt_required()
def get_cart():
    """获取当前用户的购物车列表"""
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).order_by(CartItem.created_at.desc()).all()
    return jsonify({"code": 200, "data": [item.to_dict() for item in items]})


@cart_bp.post("")
@jwt_required()
def add_to_cart():
    """添加到购物车"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get("productId")
    quantity = int(data.get("quantity", 1))
    attributes = data.get("attributes", {})

    if not product_id or quantity <= 0:
        return jsonify({"code": 400, "msg": "参数错误"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"code": 404, "msg": "商品不存在"}), 404
    if product.stock < quantity:
        return jsonify({"code": 400, "msg": "商品库存不足"}), 400

    # 检查购物车是否已有相同规格商品
    # 注意 JSON 字段精确匹配比较麻烦，这里用基础过滤后内存比对
    existing_items = CartItem.query.filter_by(user_id=user_id, product_id=product_id).all()
    item = next((i for i in existing_items if i.attributes == attributes), None)

    if item:
        new_qty = item.quantity + quantity
        if product.stock < new_qty:
            return jsonify({"code": 400, "msg": "商品库存不足，无法继续添加"}), 400
        item.quantity = new_qty
    else:
        item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            attributes=attributes
        )
        db.session.add(item)

    # 记录加购行为用于算法权重
    behavior = UserBehavior(
        user_id=user_id,
        product_id=product_id,
        action_type="cart"
    )
    db.session.add(behavior)
    db.session.commit()

    return jsonify({"code": 200, "msg": "已加入购物车", "data": item.to_dict()})


@cart_bp.put("/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    """修改购物车内商品数量"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    new_quantity = int(data.get("quantity", 1))

    if new_quantity <= 0:
        return jsonify({"code": 400, "msg": "数量必须大于0"}), 400

    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"code": 404, "msg": "购物车商品不存在"}), 404

    product = Product.query.get(item.product_id)
    if product and product.stock < new_quantity:
        return jsonify({"code": 400, "msg": f"库存不足，当前库存：{product.stock}"}), 400

    item.quantity = new_quantity
    db.session.commit()
    return jsonify({"code": 200, "msg": "修改成功", "data": item.to_dict()})


@cart_bp.delete("/<int:item_id>")
@jwt_required()
def delete_cart_item(item_id):
    """删除购物车商品"""
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"code": 404, "msg": "购物车商品不存在"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"code": 200, "msg": "删除成功"})


@cart_bp.delete("")
@jwt_required()
def clear_cart():
    """清空当前用户的购物车"""
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"code": 200, "msg": "购物车已清空"})
