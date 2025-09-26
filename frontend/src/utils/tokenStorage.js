import * as SecureStore from 'expo-secure-store';

const ACCESS_TOKEN_KEY = 'flashy_access_token';
const REFRESH_TOKEN_KEY = 'flashy_refresh_token';

export const saveTokens = async ({ accessToken, refreshToken }) => {
  if (accessToken) {
    await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
  }
  if (refreshToken) {
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
  }
};

export const clearTokens = async () => {
  await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
};

export const getAccessToken = () => SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
export const getRefreshToken = () => SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
