import request from "./request";

export const login = (payload) => request.post("/auth/login", payload);
export const register = (payload) => request.post("/auth/register", payload);
export const getProfile = () => request.get("/auth/profile");
export const updateProfile = (data) => request.put("/auth/profile", data);
export const updatePassword = (data) => request.put("/auth/password", data);
