import { useEffect } from 'react';
import { Alert } from 'react-native';
import { authActions, useAppDispatch, useAuthSelectors } from '../../hooks';
import { LoginForm } from '../../molecules/LoginForm';
import AuthTemplate from '../../templates/AuthTemplate';

const LoginScreen = () => {
  const dispatch = useAppDispatch();
  const { status, error } = useAuthSelectors();

  useEffect(() => {
    if (status === 'failed' && error) {
      Alert.alert('Login Failed', error);
    }
  }, [status, error]);

  const handleSubmit = ({ email, password }) => {
    dispatch(authActions.login({ email, password }));
  };

  return (
    <AuthTemplate title="Admin Sign In" subtitle="Enter your credentials to manage the platform.">
      <LoginForm onSubmit={handleSubmit} loading={status === 'loading'} />
    </AuthTemplate>
  );
};

export default LoginScreen;
