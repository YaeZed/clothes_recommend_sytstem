import request from "./request";

export const getProducts = (params) => request.get("/products", { params });
export const getProduct = (id) => request.get(`/products/${id}`);
export const getCategories = () => request.get("/products/categories");
export const getStyles = () => request.get("/products/styles");
export const getHotProducts = (limit = 10) =>
  request.get("/products/hot", { params: { limit } });
