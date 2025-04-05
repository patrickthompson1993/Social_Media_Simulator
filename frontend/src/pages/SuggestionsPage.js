import React, { useEffect, useState } from "react";
import { expandedAPI } from "../api";
import { Box, Heading, Spinner, Text, useToast, VStack, HStack, Badge, Card, CardBody } from "@chakra-ui/react";

export default function SuggestionsPage() {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await expandedAPI.getSmartInsights();
        setInsights(response.data);
      } catch (err) {
        setError(err.message);
        toast({
          title: "Error fetching insights",
          description: err.message,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [toast]);

  if (loading) {
    return (
      <Box p={4} textAlign="center">
        <Spinner size="xl" />
        <Text mt={4}>Loading insights...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Heading size="md" color="red.500">Error</Heading>
        <Text>{error}</Text>
      </Box>
    );
  }

  const getTrendColor = (trend) => {
    switch (trend) {
      case "up": return "green";
      case "down": return "red";
      default: return "gray";
    }
  };

  return (
    <Box p={4}>
      <Heading size="lg" mb={4}>Smart Insights</Heading>
      <VStack spacing={4} align="stretch">
        {insights.map((insight, index) => (
          <Card key={index} variant="outline">
            <CardBody>
              <HStack justify="space-between" mb={2}>
                <Heading size="md">{insight.type.replace(/_/g, " ").toUpperCase()}</Heading>
                <Badge colorScheme={getTrendColor(insight.trend)}>
                  {insight.trend.toUpperCase()}
                </Badge>
              </HStack>
              <Text>{insight.description}</Text>
              <HStack mt={2}>
                <Badge colorScheme="blue">{insight.metric}</Badge>
                <Text fontWeight="bold">{typeof insight.value === 'number' ? insight.value.toFixed(2) : insight.value}</Text>
              </HStack>
            </CardBody>
          </Card>
        ))}
      </VStack>
    </Box>
  );
}