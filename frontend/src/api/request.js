import axios from "axios";
import { ElMessage } from "element-plus";

const request = axios.create({
  baseURL: "http://localhost:5000/api",
  timeout: 10000,
});

// 请求拦截器：自动附加 JWT Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers["Authorization"] = `Bearer ${token}`;
  return config;
});

// 响应拦截器：统一错误提示
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.msg || error.message || "网络错误";
    ElMessage.error(msg);
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  },
);

export default request;
