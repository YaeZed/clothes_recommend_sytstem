"""
clean_dirty_data.py
───────────────────────────────────────────
从现有数据库中删除明显不是服装的商品（行李袋、药盒、首饰等）
保留真实的亚马逊商品图片和正确的服装商品
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product

# 中文非服装关键词黑名单（出现在商品标题里则删除）
NON_CLOTHING_ZH = [
    # 药品/保健
    "药", "药盒", "药片", "维生素", "营养", "保健",
    # 行李箱/包袋
    "行李", "旅行箱", "拉杆箱", "储物",
    # 手表/电子设备
    "手表", "腕表", "腕上电脑", "计步器", "指南针", "高度计", "气压计",
    "GPS", "心率", "码表", "秒表", "计时器", "指北针",
    "精准表", "电子表", "运动表", "智能表",
    # 工具/电器
    "工具", "电池", "充电", "数据线", "内存", "硬盘", "U盘",
    # 玩具
    "玩具", "积木", "娃娃",
    # 餐具/家居
    "餐具", "碗", "杯子", "水瓶", "文具", "钢笔",
    # 首饰珠宝
    "项链", "耳环", "戒指", "手镯", "吊坠", "珠宝",
    # 道具/演出服配件（不是真实的服装）
    "配件套件", "套件", "假发", "假牙", "义齿", "道具", "饰演", "角色",
    # 包袋
    "皮夹", "皮包", "手提包", "行李袋",
]

# 中文服装关键词白名单（标题含任意一个则强制保留，优先于黑名单）
CLOTHING_ZH = [
    "T恤", "衬衫", "上衣", "连衣裙", "裤", "外套", "夹克",
    "卫衣", "羽绒", "大衣", "风衣", "背心", "短裙", "裙",
    "运动", "泳装", "短裤", "女装", "男装", "针织", "毛衣",
    "内衣", "棉衣", "胸罩", "丝袜", "儿童", "婴儿",
    "鞋", "靴", "凉鞋", "运动鞋", "帆布鞋",
    "帽子", "围巾", "手套", "腰带", "皮带",
]

# 直接按 ID 强制删除的脏数据（无需关键词匹配）
FORCE_DELETE_IDS = [1001, 1159]

def main():
    app = create_app()
    with app.app_context():
        total = Product.query.count()
        print(f"数据库当前共有 {total} 件商品")

        to_delete = []
        all_products = Product.query.all()
        for p in all_products:
            title = p.title or ""
            # 强制删除指定 ID（图文不符的异类商品）
            if p.id in FORCE_DELETE_IDS:
                to_delete.append(p)
                continue
            # 白名单优先：只要含服装词就保留
            if any(kw in title for kw in CLOTHING_ZH):
                continue
            # 黑名单：含非服装词则标记删除
            if any(kw in title for kw in NON_CLOTHING_ZH):
                to_delete.append(p)

        print(f"发现 {len(to_delete)} 件非服装商品需要删除：")
        for p in to_delete[:20]:
            print(f"  [ID={p.id}] {p.title[:60]} (类目: {p.category})")

        if len(to_delete) > 20:
            print(f"  ... 以及另外 {len(to_delete) - 20} 件")

        if not to_delete:
            print("✅ 数据库里没有明显的脏数据，无需清理！")
            return

        # 先解除行为数据的外键关联，再删除商品
        ids = [p.id for p in to_delete]
        db.session.execute(
            db.text(f"DELETE FROM user_behaviors WHERE product_id IN ({','.join(str(i) for i in ids)})")
        )
        db.session.execute(
            db.text(f"DELETE FROM recommendations WHERE product_id IN ({','.join(str(i) for i in ids)})")
        )
        for p in to_delete:
            db.session.delete(p)
        db.session.commit()

        remaining = Product.query.count()
        print(f"\n✅ 清理完成！删除 {len(to_delete)} 件，剩余 {remaining} 件纯净服装商品。")

if __name__ == "__main__":
    main()
