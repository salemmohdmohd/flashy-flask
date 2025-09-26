import axios from 'axios';
import Constants from 'expo-constants';
import { clearTokens, getAccessToken, getRefreshToken, saveTokens } from '../utils/tokenStorage';

const baseURL =
  Constants.expoConfig?.extra?.apiUrl || process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

export const api = axios.create({
  baseURL,
  timeout: 15000
});

api.interceptors.request.use(async (config) => {
  if (!config.headers.Authorization) {
    const token = await getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  config.headers['Content-Type'] = 'application/json';
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = await getRefreshToken();
      if (!refreshToken) {
        await clearTokens();
        return Promise.reject(error);
      }
      try {
        const { data } = await api.post(
          '/auth/refresh',
          {},
          {
            headers: { Authorization: `Bearer ${refreshToken}` }
          }
        );
        if (data?.access_token) {
          await saveTokens({ accessToken: data.access_token, refreshToken });
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        await clearTokens();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
