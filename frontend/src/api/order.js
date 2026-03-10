import request from "./request";

export function createOrder(data) {
  return request.post("/api/orders", data);
}

export function getOrders() {
  return request.get("/api/orders");
}

export function payOrder(id) {
  return request.post(`/api/orders/${id}/pay`);
}
