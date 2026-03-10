from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email    = data.get("email", "").strip()

    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"code": 409, "msg": "用户名已存在"}), 409

    user = User(
        username   = username,
        password   = generate_password_hash(password),
        email      = email or None,
        style_pref = data.get("stylePref", []),
        size_info  = data.get("sizeInfo",  {}),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"code": 200, "msg": "注册成功", "data": {"token": token, "user": user.to_dict()}}), 201


@auth_bp.post("/login")
def login():
    data     = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"code": 200, "msg": "登录成功", "data": {"token": token, "user": user.to_dict()}})


@auth_bp.get("/profile")
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    return jsonify({"code": 200, "data": user.to_dict()})


@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json()

    if "stylePref" in data:
        user.style_pref = data["stylePref"]
    if "sizeInfo"  in data:
        user.size_info  = data["sizeInfo"]
    if "avatar"    in data:
        user.avatar     = data["avatar"]
    if "nickname"  in data:
        user.nickname   = data["nickname"]
    if "phone"     in data:
        user.phone      = data["phone"]
    if "birthday"  in data:
        user.birthday   = data["birthday"]
    if "addresses" in data:
        user.addresses  = data["addresses"]

    db.session.commit()
    return jsonify({"code": 200, "msg": "更新成功", "data": user.to_dict()})

@auth_bp.put("/password")
@jwt_required()
def update_password():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json()

    old_pw = data.get("oldPassword")
    new_pw = data.get("newPassword")

    if not old_pw or not new_pw:
        return jsonify({"code": 400, "msg": "旧密码和新密码不能为空"}), 400

    if not check_password_hash(user.password, old_pw):
        return jsonify({"code": 400, "msg": "旧密码错误"}), 400

    user.password = generate_password_hash(new_pw)
    db.session.commit()

    return jsonify({"code": 200, "msg": "密码修改成功，请重新登录"})
