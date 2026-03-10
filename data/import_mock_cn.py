import sys, os, random
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product
from backend.models.user import User
from backend.models.behavior import UserBehavior

# 纯净的分类映射与子分类定义
CATEGORIES = {
    "上衣": ["T恤", "衬衫", "雪纺衫", "针织衫", "Polo衫", "打底衫", "休闲打底"],
    "裤子": ["牛仔裤", "休闲裤", "阔腿裤", "运动裤", "短裤", "九分裤", "直筒裤", "西装裤"],
    "裙子": ["连衣裙", "半身裙", "A字裙", "包臀裙", "碎花裙", "背带裙", "百褶裙"],
    "外套": ["风衣", "夹克", "西装外套", "大衣", "羽绒服", "针织开衫", "皮衣", "棉服"],
    "卫衣": ["连帽卫衣", "圆领卫衣", "加绒卫衣", "开衫卫衣", "套头卫衣", "印花卫衣"],
    "鞋靴": ["运动鞋", "帆布鞋", "马丁靴", "高跟鞋", "平底鞋", "凉鞋", "休闲鞋", "皮鞋"],
    "配饰": ["棒球帽", "渔夫帽", "羊毛围巾", "丝巾", "太阳镜", "皮带", "发带", "手饰"]
}

STYLE_LIST = ["休闲", "正式", "运动", "街头", "复古", "简约", "时尚", "森系", "潮流"]

ADJECTIVES = ["修身", "宽松", "百搭", "显瘦", "保暖", "透气", "轻薄", "高腰", "加厚", "春款", "夏款", "秋款", "冬款", "加绒", "新款", "仙女", "气质", "文艺", "重工", "纯棉", "高级感"]

COLORS_HEX = {
    "黑色": ("#1E1E1E", "#4A4A4A"),
    "白色": ("#D0D0D0", "#A0A0A0"), # 白色的渐变深一点，以防白底白字
    "灰色": ("#808080", "#A9A9A9"),
    "蓝色": ("#4A90E2", "#003366"),
    "红色": ("#D0021B", "#8B0000"),
    "粉色": ("#FFB6C1", "#FF69B4"),
    "黄色": ("#F5A623", "#B8860B"),
    "绿色": ("#417505", "#228B22"),
    "卡其色": ("#C3B091", "#8B7355"),
    "紫色": ("#9013FE", "#4B0082"),
}

def generate_svg_image(text, bg_colors):
    c1, c2 = bg_colors
    return (
        f"data:image/svg+xml;utf8,"
        f"<svg viewBox='0 0 400 500' xmlns='http://www.w3.org/2000/svg'>"
        f"<defs><linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='100%'>"
        f"<stop offset='0%' style='stop-color:{c1};stop-opacity:1' />"
        f"<stop offset='100%' style='stop-color:{c2};stop-opacity:1' />"
        f"</linearGradient></defs>"
        f"<rect width='400' height='500' fill='url(#grad)'/>"
        f"<text x='50%' y='45%' font-size='36' text-anchor='middle' alignment-baseline='middle' fill='white' font-family='sans-serif' font-weight='bold'>{text}</text>"
        f"<text x='50%' y='55%' font-size='18' text-anchor='middle' alignment-baseline='middle' fill='rgba(255,255,255,0.8)' font-family='sans-serif'>纯净演示数据</text>"
        f"</svg>"
    )

def main():
    app = create_app()
    with app.app_context():
        print("[1/3] 正在清空旧的亚马逊脏数据...")
        db.session.execute(db.text("DELETE FROM recommendations"))
        db.session.execute(db.text("DELETE FROM user_behaviors"))
        db.session.execute(db.text("DELETE FROM products"))
        db.session.commit()

        print("[2/3] 正在生成纯净版高品质中文商品数据...")
        product_count = 0
        products = []
        for cat, subcats in CATEGORIES.items():
            for subcat in subcats:
                # 每个细分类生成大概 5-8 件商品
                num_items = random.randint(5, 8)
                for _ in range(num_items):
                    style = random.choice(STYLE_LIST)
                    color_name = random.choice(list(COLORS_HEX.keys()))
                    bg_colors = COLORS_HEX[color_name]
                    adj = random.sample(ADJECTIVES, 2)
                    
                    title = f"{' '.join(adj)} {color_name} {style}风格 {subcat}"
                    price = round(random.uniform(39, 499), 2)
                    sales = random.randint(10, 5000)
                    
                    # 生成带有品类名称和颜色的漂亮渐变 SVG 作为图片
                    img_data_uri = generate_svg_image(subcat, bg_colors)

                    p = Product(
                        title=title,
                        category=cat,
                        style=style,
                        price=price,
                        sales_count=sales,
                        stock=random.randint(50, 999),
                        images=[img_data_uri],
                        description=f"这是一件非常高品质的{title}。采用上乘面料制作，{style}风格设计，适合日常穿搭，百搭显瘦，是您衣橱中不可或缺的单品。",
                        tags=adj + [style, cat],
                        attributes={
                            "color": [color_name] + random.sample(list(COLORS_HEX.keys()), 2),
                            "size": ["S", "M", "L", "XL"] if cat not in ["配饰", "鞋靴"] else ["均码"] if cat == "配饰" else ["36", "37", "38", "39", "40", "41", "42", "43"]
                        }
                    )
                    db.session.add(p)
                    products.append(p)
                    product_count += 1
        
        db.session.commit()
        print(f"  ✅ 成功生成了 {product_count} 件纯净商品记录！")

        print("[3/3] 正在生成随机用户及行为数据以便测试推荐算法...")
        users = User.query.filter_by(role="user").all()
        if not users:
            print("  没有普通用户，自动创建 50 个测试用户...")
            for i in range(1, 51):
                u = User(
                    username=f"user{i:03d}",
                    password=generate_password_hash("123456"),
                    style_pref=random.sample(STYLE_LIST, 2),
                    size_info={"height": random.randint(155, 185), "weight": random.randint(45, 90)},
                )
                db.session.add(u)
                users.append(u)
            db.session.commit()

        # 随机分配 2000 条行为
        action_weights = ["view"] * 6 + ["collect"] * 2 + ["cart"] * 2 + ["purchase"]
        products_db = Product.query.all()
        for i in range(2000):
            p = random.choice(products_db)
            u = random.choice(users)
            behavior = UserBehavior(
                user_id=u.id,
                product_id=p.id,
                action_type=random.choice(action_weights),
                duration=random.randint(10, 180),
            )
            db.session.add(behavior)
            if i % 500 == 0:
                db.session.flush()
        db.session.commit()
        print("  ✅ 成功生成 2000 条行为记录！")
        print("\n🎉 全新、纯净的中文化数据初始化完成！再也不会有乱七八糟的亚马逊老鼠屎数据了！")

if __name__ == "__main__":
    main()
