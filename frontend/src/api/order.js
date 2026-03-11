import request from "./request";

export function createOrder(data) {
  return request.post("/orders", data);
}

export function getOrders() {
  return request.get("/orders");
}

export function payOrder(id) {
  return request.post(`/orders/${id}/pay`);
}
