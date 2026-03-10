import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.order import Order, OrderItem
from backend.models.cart import CartItem
from backend.models.product import Product
from backend.models.behavior import UserBehavior

order_bp = Blueprint("order", __name__)


@order_bp.post("")
@jwt_required()
def create_order():
    """从购物车生成订单"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    receiver = data.get("receiver", {})

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"code": 400, "msg": "购物车为空，无法生成订单"}), 400

    order_no = datetime.utcnow().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()
    order = Order(
        order_no=order_no,
        user_id=user_id,
        receiver_name=receiver.get("name", ""),
        receiver_phone=receiver.get("phone", ""),
        receiver_addr=receiver.get("address", "")
    )
    db.session.add(order)
    db.session.flush()  # 获取 order.id

    total_amount = 0
    for c_item in cart_items:
        product = Product.query.get(c_item.product_id)
        if not product or product.stock < c_item.quantity:
            continue  # 忽略或抛错，这里简单跳过

        price = product.price or 0
        total_amount += price * c_item.quantity

        o_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_title=product.title,
            product_image=product.images[0] if product.images else "",
            price=price,
            quantity=c_item.quantity,
            attributes=c_item.attributes
        )
        db.session.add(o_item)
        db.session.delete(c_item)

    if total_amount == 0:
        db.session.rollback()
        return jsonify({"code": 400, "msg": "所有商品失效或库存不足"}), 400

    order.total_amount = total_amount
    db.session.commit()

    return jsonify({"code": 201, "msg": "订单创建成功", "data": order.to_dict()}), 201


@order_bp.get("")
@jwt_required()
def list_orders():
    """获取当前用户的订单列表"""
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify({"code": 200, "data": [o.to_dict() for o in orders]})


@order_bp.post("/<int:order_id>/pay")
@jwt_required()
def pay_order(order_id):
    """模拟支付，扣减库存并记录购买行为"""
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        return jsonify({"code": 404, "msg": "订单不存在"}), 404
    if order.status != "pending":
        return jsonify({"code": 400, "msg": "订单状态不可支付"}), 400

    # 扣减库存 & 记录 purchase 行为
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock = max(0, product.stock - item.quantity)
            product.sales_count += item.quantity

        behavior = UserBehavior(
            user_id=user_id,
            product_id=item.product_id,
            action_type="purchase"
        )
        db.session.add(behavior)

    order.status = "paid"
    order.paid_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"code": 200, "msg": "支付成功"})
