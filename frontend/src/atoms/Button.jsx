import React from 'react';
import styled from 'styled-components/native';
import { ActivityIndicator } from 'react-native';

const ButtonContainer = styled.Pressable`
  background-color: ${({ disabled, theme }) =>
    disabled ? theme.colors.muted : theme.colors.primary};
  padding: ${({ theme }) => theme.spacing.md}px;
  border-radius: ${({ theme }) => theme.radii.md}px;
  align-items: center;
  justify-content: center;
`;

const ButtonLabel = styled.Text`
  color: #ffffff;
  font-weight: 600;
  font-size: ${({ theme }) => theme.typography.body}px;
`;

export const Button = ({ onPress, title, loading = false, ...props }) => (
  <ButtonContainer onPress={onPress} disabled={loading || props.disabled} {...props}>
    {loading ? <ActivityIndicator color="#FFFFFF" /> : <ButtonLabel>{title}</ButtonLabel>}
  </ButtonContainer>
);

export default Button;
