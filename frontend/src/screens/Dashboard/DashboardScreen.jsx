import { useEffect, useState } from 'react';
import { RefreshControl, ScrollView } from 'react-native';
import styled from 'styled-components/native';
import Button from '../../atoms/Button';
import { BodyText, Caption, Heading } from '../../atoms/Text';
import { authActions, useAppDispatch, useAuthSelectors } from '../../hooks';
import api from '../../services/api';

const Container = styled(ScrollView)`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  padding: ${({ theme }) => theme.spacing.lg}px;
`;

const Card = styled.View`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.md}px;
  padding: ${({ theme }) => theme.spacing.lg}px;
  margin-bottom: ${({ theme }) => theme.spacing.md}px;
  border-width: 1px;
  border-color: ${({ theme }) => theme.colors.muted};
`;

const Header = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spacing.lg}px;
`;

const DashboardScreen = () => {
  const dispatch = useAppDispatch();
  const { user } = useAuthSelectors();
  const [stats, setStats] = useState({ users: 0, resources: 0, lessons: 0 });
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      setRefreshing(true);
      const [usersResponse, resourcesResponse, lessonsResponse] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/resources'),
        api.get('/public/lessons')
      ]);
      setStats({
        users: usersResponse.data.length,
        resources: resourcesResponse.data.length,
        lessons: lessonsResponse.data.length
      });
    } catch (error) {
      console.warn('Failed to load dashboard data', error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogout = () => {
    dispatch(authActions.logout());
  };

  return (
    <Container refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} />}>
      <Header>
        <Heading>Welcome, {user?.username}</Heading>
        <Button title="Sign Out" onPress={handleLogout} />
      </Header>
      <Card>
        <Heading>Platform Snapshot</Heading>
        <BodyText>{stats.users} registered users</BodyText>
        <BodyText>{stats.resources} uploaded resources</BodyText>
        <BodyText>{stats.lessons} published lessons</BodyText>
      </Card>
      <Card>
        <Heading>Next Steps</Heading>
        <Caption>Moderate new resources, trigger AI generation, and manage lessons.</Caption>
      </Card>
    </Container>
  );
};

export default DashboardScreen;
