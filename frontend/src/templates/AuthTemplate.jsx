import styled from 'styled-components/native';
import { BodyText, Heading } from '../atoms/Text';

const Container = styled.View`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  align-items: center;
  justify-content: center;
  padding: ${({ theme }) => theme.spacing.lg}px;
`;

const Card = styled.View`
  width: 100%;
  max-width: 420px;
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.lg}px;
  padding: ${({ theme }) => theme.spacing.lg}px;
  shadow-color: #000;
  shadow-opacity: 0.1;
  shadow-radius: 10px;
  elevation: 5;
`;

const Header = styled.View`
  margin-bottom: ${({ theme }) => theme.spacing.lg}px;
`;

export const AuthTemplate = ({ title, subtitle, children }) => (
  <Container>
    <Card>
      <Header>
        <Heading>{title}</Heading>
        {subtitle ? <BodyText>{subtitle}</BodyText> : null}
      </Header>
      {children}
    </Card>
  </Container>
);

export default AuthTemplate;
