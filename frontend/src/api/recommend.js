import request from "./request";

export const getHotRecommend = (limit = 20) =>
  request.get("/recommend/hot", { params: { limit } });
export const getSimilarRecommend = (id, limit = 10) =>
  request.get(`/recommend/similar/${id}`, { params: { limit } });
export const getPersonalRecommend = (limit = 20) =>
  request.get("/recommend/personal", { params: { limit } });
