import { useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { login, logout, selectAuthError, selectAuthStatus, selectIsAuthenticated, selectUser } from '../state/authSlice';

export const useAppDispatch = () => useDispatch();
export const useAuthSelectors = () => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const status = useSelector(selectAuthStatus);
  const error = useSelector(selectAuthError);
  const user = useSelector(selectUser);
  return useMemo(() => ({ isAuthenticated, status, error, user }), [isAuthenticated, status, error, user]);
};

export const authActions = { login, logout };
