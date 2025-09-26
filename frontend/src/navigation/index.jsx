import { NavigationContainer } from '@react-navigation/native';
import { useAuthSelectors } from '../hooks';
import AppNavigator from './AppNavigator';
import AuthNavigator from './AuthNavigator';

const RootNavigator = () => {
  const { isAuthenticated, user } = useAuthSelectors();
  const isAdmin = user?.roles?.includes('admin');

  return (
    <NavigationContainer>
      {isAuthenticated && isAdmin ? <AppNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

export default RootNavigator;
