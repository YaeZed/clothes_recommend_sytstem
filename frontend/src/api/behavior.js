import request from "./request";

export const recordBehavior = (data) => request.post("/behavior", data);
export const getBehaviorHistory = (params) =>
  request.get("/behavior/history", { params });
export const getFavorites = (params) =>
  request.get("/behavior/favorites", { params });
export const getFavoriteIds = () => request.get("/behavior/favorites/ids");
export const removeFavorite = (productId) =>
  request.delete(`/behavior/favorites/${productId}`);
export const getBehaviorStats = () => request.get("/behavior/stats");
export const getUserPortrait = () => request.get("/behavior/portrait");
export const getUserStats = () => request.get("/behavior/user_stats");
