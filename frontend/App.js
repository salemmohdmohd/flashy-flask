import { StatusBar } from 'react-native';
import 'react-native-gesture-handler';
import { Provider } from 'react-redux';
import { ThemeProvider } from './src/context/ThemeProvider';
import RootNavigator from './src/navigation';
import store from './src/state/store';

const App = () => (
  <Provider store={store}>
    <ThemeProvider>
      <StatusBar barStyle="dark-content" />
      <RootNavigator />
    </ThemeProvider>
  </Provider>
);

export default App;
