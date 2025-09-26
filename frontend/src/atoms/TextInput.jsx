import styled from 'styled-components/native';

const InputWrapper = styled.View`
  margin-bottom: ${({ theme }) => theme.spacing.md}px;
`;

const StyledLabel = styled.Text`
  font-size: ${({ theme }) => theme.typography.caption}px;
  color: ${({ theme }) => theme.colors.muted};
  margin-bottom: ${({ theme }) => theme.spacing.xs}px;
`;

const StyledTextInput = styled.TextInput`
  border-width: 1px;
  border-color: ${({ theme }) => theme.colors.muted};
  border-radius: ${({ theme }) => theme.radii.sm}px;
  padding: ${({ theme }) => theme.spacing.sm}px;
  background-color: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
`;

const ErrorText = styled.Text`
  color: ${({ theme }) => theme.colors.danger};
  font-size: ${({ theme }) => theme.typography.caption}px;
  margin-top: ${({ theme }) => theme.spacing.xs}px;
`;

export const TextField = ({ label, error, ...props }) => (
  <InputWrapper>
    {label ? <StyledLabel>{label}</StyledLabel> : null}
    <StyledTextInput placeholderTextColor="#94A3B8" {...props} />
    {error ? <ErrorText>{error}</ErrorText> : null}
  </InputWrapper>
);

export default TextField;
