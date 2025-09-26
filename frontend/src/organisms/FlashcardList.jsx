import React from 'react';
import styled from 'styled-components/native';
import { BodyText, Heading } from '../atoms/Text';

const Container = styled.View`
  padding: ${({ theme }) => theme.spacing.md}px;
`;

const Card = styled.View`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.md}px;
  padding: ${({ theme }) => theme.spacing.md}px;
  margin-bottom: ${({ theme }) => theme.spacing.sm}px;
  border-width: 1px;
  border-color: ${({ theme }) => theme.colors.muted};
`;

export const FlashcardList = ({ deck }) => (
  <Container>
    <Heading>{deck.title}</Heading>
    {deck.flashcards.map((card) => (
      <Card key={card.id}>
        <BodyText>Q: {card.question}</BodyText>
        <BodyText>A: {card.answer}</BodyText>
      </Card>
    ))}
  </Container>
);

export default FlashcardList;
