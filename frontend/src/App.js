import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Box,
  Grid,
  GridItem,
  VStack,
  HStack,
  Text,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  useToast,
  Spinner,
} from '@chakra-ui/react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { userAPI, contentAPI, adAPI, moderationAPI, expandedAPI } from './api';
import EngagementPage from './pages/EngagementPage';
import ROIPerformancePage from './pages/ROIPerformancePage';
import SatisfactionPage from './pages/SatisfactionPage';
import SuggestionsPage from './pages/SuggestionsPage';

function App() {
  const [data, setData] = useState({
    users: [],
    content: [],
    ads: [],
    interactions: [],
    feedInteractions: [],
    contentReports: [],
    moderationActions: [],
    contentFlags: [],
    userSessions: [],
    userPreferences: [],
    userNetworkMetrics: [],
    contentRecommendations: [],
    userFeedback: [],
  });

  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalContent: 0,
    totalAds: 0,
    totalInteractions: 0,
    totalReports: 0,
    averageCTR: 0,
    averageEngagement: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Fetch data from all endpoints
      const [
        usersResponse,
        contentResponse,
        adsResponse,
        moderationStatsResponse,
        userRegionsResponse,
        ctrTrendResponse,
      ] = await Promise.all([
        userAPI.getAllUsers(),
        contentAPI.getAllContent(),
        adAPI.getAllAds(),
        moderationAPI.getModerationStats(),
        userAPI.getUserRegions(),
        adAPI.getCTRTrend(),
      ]);

      // Extract data from responses
      const users = usersResponse.data;
      const content = contentResponse.data;
      const ads = adsResponse.data;
      const moderationStats = moderationStatsResponse.data;
      const userRegions = userRegionsResponse.data;
      const ctrTrend = ctrTrendResponse.data;

      // Set data state
      setData({
        users,
        content,
        ads,
        userRegions,
        ctrTrend,
        moderationStats,
        // These would be fetched in a real app, but we'll use placeholders for now
        interactions: [],
        feedInteractions: [],
        contentReports: [],
        moderationActions: [],
        contentFlags: [],
        userSessions: [],
        userPreferences: [],
        userNetworkMetrics: [],
        contentRecommendations: [],
        userFeedback: [],
      });

      // Calculate metrics
      calculateMetrics({
        users,
        content,
        ads,
        moderationStats,
      });
    } catch (error) {
      setError(error.message);
      toast({
        title: 'Error fetching data',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateMetrics = (data) => {
    const {
      users,
      content,
      ads,
      moderationStats,
    } = data;

    setMetrics({
      totalUsers: users.length,
      activeUsers: users.filter(user => user.status === 'active').length,
      totalContent: content.length,
      totalAds: ads.length,
      totalInteractions: 0, // Placeholder
      totalReports: moderationStats?.total_reports || 0,
      averageCTR: ads.reduce((acc, ad) => acc + (ad.ctr || 0), 0) / (ads.length || 1),
      averageEngagement: 0, // Placeholder
    });
  };

  if (loading) {
    return (
      <ChakraProvider>
        <Box p={4} textAlign="center">
          <Spinner size="xl" />
          <Text mt={4}>Loading dashboard data...</Text>
        </Box>
      </ChakraProvider>
    );
  }

  if (error) {
    return (
      <ChakraProvider>
        <Box p={4}>
          <Heading size="md" color="red.500">Error</Heading>
          <Text>{error}</Text>
        </Box>
      </ChakraProvider>
    );
  }

  return (
    <ChakraProvider>
      <Box p={4}>
        <Heading mb={6}>Social Media Platform Dashboard</Heading>

        {/* Key Metrics */}
        <Grid templateColumns="repeat(4, 1fr)" gap={4} mb={6}>
          <Stat>
            <StatLabel>Total Users</StatLabel>
            <StatNumber>{metrics.totalUsers}</StatNumber>
            <StatHelpText>
              <StatArrow type="increase" />
              23.36%
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Active Users</StatLabel>
            <StatNumber>{metrics.activeUsers}</StatNumber>
            <StatHelpText>
              <StatArrow type="increase" />
              9.05%
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Total Content</StatLabel>
            <StatNumber>{metrics.totalContent}</StatNumber>
            <StatHelpText>
              <StatArrow type="increase" />
              12.5%
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Total Ads</StatLabel>
            <StatNumber>{metrics.totalAds}</StatNumber>
            <StatHelpText>
              <StatArrow type="decrease" />
              3.2%
            </StatHelpText>
          </Stat>
        </Grid>

        {/* Tabs for different views */}
        <Tabs variant="enclosed" mb={6}>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Engagement</Tab>
            <Tab>ROI Performance</Tab>
            <Tab>Satisfaction</Tab>
            <Tab>Insights</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <Grid templateColumns="repeat(2, 1fr)" gap={6}>
                {/* User Regions Chart */}
                <Card>
                  <CardHeader>
                    <Heading size="md">User Regions</Heading>
                  </CardHeader>
                  <CardBody>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={data.userRegions}
                          dataKey="count"
                          nameKey="region"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          label
                        />
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardBody>
                </Card>

                {/* CTR Trend Chart */}
                <Card>
                  <CardHeader>
                    <Heading size="md">CTR Trend</Heading>
                  </CardHeader>
                  <CardBody>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={data.ctrTrend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="ctr" stroke="#8884d8" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardBody>
                </Card>

                {/* Moderation Stats */}
                <Card>
                  <CardHeader>
                    <Heading size="md">Moderation Stats</Heading>
                  </CardHeader>
                  <CardBody>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Category</Th>
                          <Th isNumeric>Count</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        <Tr>
                          <Td>Total Reports</Td>
                          <Td isNumeric>{data.moderationStats?.total_reports || 0}</Td>
                        </Tr>
                        <Tr>
                          <Td>Pending Reports</Td>
                          <Td isNumeric>{data.moderationStats?.pending_reports || 0}</Td>
                        </Tr>
                        <Tr>
                          <Td>Resolved Reports</Td>
                          <Td isNumeric>{data.moderationStats?.resolved_reports || 0}</Td>
                        </Tr>
                        <Tr>
                          <Td>Dismissed Reports</Td>
                          <Td isNumeric>{data.moderationStats?.dismissed_reports || 0}</Td>
                        </Tr>
                        <Tr>
                          <Td>Total Flags</Td>
                          <Td isNumeric>{data.moderationStats?.total_flags || 0}</Td>
                        </Tr>
                      </Tbody>
                    </Table>
                  </CardBody>
                </Card>

                {/* Recent Content */}
                <Card>
                  <CardHeader>
                    <Heading size="md">Recent Content</Heading>
                  </CardHeader>
                  <CardBody>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>ID</Th>
                          <Th>Type</Th>
                          <Th>Status</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {data.content.slice(0, 5).map((item) => (
                          <Tr key={item.id}>
                            <Td>{item.id.substring(0, 8)}...</Td>
                            <Td>{item.content_type}</Td>
                            <Td>
                              <Badge colorScheme={item.status === 'active' ? 'green' : 'red'}>
                                {item.status}
                              </Badge>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </CardBody>
                </Card>
              </Grid>
            </TabPanel>
            <TabPanel>
              <EngagementPage />
            </TabPanel>
            <TabPanel>
              <ROIPerformancePage />
            </TabPanel>
            <TabPanel>
              <SatisfactionPage />
            </TabPanel>
            <TabPanel>
              <SuggestionsPage />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </ChakraProvider>
  );
}

export default App;
