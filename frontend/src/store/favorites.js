/**
 * favorites.js  ——  全局收藏状态管理
 * 在用户登录后初始化，将收藏的商品 ID 集合存储在内存中，
 * 并同步到后端接口。刷新页面后从 API 重新加载，保证持久化。
 */
import { defineStore } from "pinia";
import { ref } from "vue";
import {
  getFavoriteIds,
  recordBehavior,
  removeFavorite,
} from "../api/behavior";

export const useFavStore = defineStore("favorites", () => {
  /** 已收藏的商品 ID 集合 */
  const ids = ref(new Set());
  const loaded = ref(false);

  /** 从 API 加载当前用户的收藏 ID（登录后调用一次） */
  async function load() {
    try {
      const res = await getFavoriteIds();
      ids.value = new Set(res.data || []);
      loaded.value = true;
    } catch (_) {}
  }

  /** 查询某商品是否已收藏 */
  function isFaved(productId) {
    return ids.value.has(productId);
  }

  /**
   * 切换收藏状态：
   *  - 未收藏 → 发送 collect 行为 → 加入集合
   *  - 已收藏 → 调用 DELETE 接口 → 从集合移除
   *
   * @returns {boolean} 操作后的收藏状态（true = 已收藏）
   */
  async function toggle(productId) {
    if (ids.value.has(productId)) {
      await removeFavorite(productId);
      ids.value = new Set([...ids.value].filter((id) => id !== productId));
      return false;
    } else {
      await recordBehavior({ productId, actionType: "collect", duration: 0 });
      ids.value = new Set([...ids.value, productId]);
      return true;
    }
  }

  /** 退出登录时清空 */
  function clear() {
    ids.value = new Set();
    loaded.value = false;
  }

  return { ids, loaded, load, isFaved, toggle, clear };
});
