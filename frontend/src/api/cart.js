import request from "./request";

export function getCart() {
  return request.get("/api/cart");
}

export function addToCart(data) {
  return request.post("/api/cart", data);
}

export function updateCartItem(id, quantity) {
  return request.put(`/api/cart/${id}`, { quantity });
}

export function removeCartItem(id) {
  return request.delete(`/api/cart/${id}`);
}

export function clearCart() {
  return request.delete("/api/cart");
}
