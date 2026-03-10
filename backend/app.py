from flask import Flask
from backend.config import Config
from backend.extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── 初始化扩展 ─────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # ── 注册蓝图 ───────────────────────────────────────────
    from backend.api.auth      import auth_bp
    from backend.api.product   import product_bp
    from backend.api.behavior  import behavior_bp
    from backend.api.recommend import recommend_bp
    from backend.api.admin     import admin_bp
    from backend.api.cart      import cart_bp
    from backend.api.order     import order_bp

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(product_bp,   url_prefix="/api/products")
    app.register_blueprint(behavior_bp,  url_prefix="/api/behavior")
    app.register_blueprint(recommend_bp, url_prefix="/api/recommend")
    app.register_blueprint(admin_bp,     url_prefix="/api/admin")
    app.register_blueprint(cart_bp,      url_prefix="/api/cart")
    app.register_blueprint(order_bp,     url_prefix="/api/orders")

    # ── 自动建表（首次运行）────────────────────────────────
    with app.app_context():
        import backend.models  # noqa: F401 确保模型被加载
        db.create_all()

    # ── 健康检查 ───────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok", "message": "服装推荐系统后端运行中"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
