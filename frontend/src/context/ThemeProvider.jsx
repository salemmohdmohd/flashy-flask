import React, { createContext, useContext } from 'react';
import { ThemeProvider as StyledProvider } from 'styled-components/native';
import { theme } from '../theme';

const ThemeContext = createContext(theme);

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => (
  <ThemeContext.Provider value={theme}>
    <StyledProvider theme={theme}>{children}</StyledProvider>
  </ThemeContext.Provider>
);
