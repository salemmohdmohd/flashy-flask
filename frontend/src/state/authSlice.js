import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import api from '../services/api';
import { clearTokens, saveTokens } from '../utils/tokenStorage';

export const login = createAsyncThunk('auth/login', async ({ email, password }, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/auth/login', { email, password });
    await saveTokens({ accessToken: data.access_token, refreshToken: data.refresh_token });
    return data;
  } catch (error) {
    const message = error.response?.data?.message || 'Login failed';
    return rejectWithValue(message);
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  await clearTokens();
  return true;
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    accessToken: null,
    refreshToken: null,
    status: 'idle',
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
      })
      .addCase(login.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.status = 'idle';
        state.error = null;
      });
  }
});

export const selectIsAuthenticated = (state) => Boolean(state.auth.accessToken && state.auth.user);
export const selectAuthError = (state) => state.auth.error;
export const selectAuthStatus = (state) => state.auth.status;
export const selectUser = (state) => state.auth.user;

export default authSlice.reducer;
