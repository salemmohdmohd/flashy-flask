import 'dotenv/config';

export default ({ config }) => ({
  ...config,
  name: 'Flashy Mobile',
  slug: 'flashy-mobile',
  scheme: 'flashy',
  version: '1.0.0',
  orientation: 'portrait',
  userInterfaceStyle: 'light',
  updates: {
    fallbackToCacheTimeout: 0
  },
  assetBundlePatterns: ['**/*'],
  ios: {
    supportsTablet: true
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/icon.png',
      backgroundColor: '#ffffff'
    }
  },
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL
  },
  experiments: {
    typedRoutes: true
  }
});
