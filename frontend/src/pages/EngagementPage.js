import React, { useEffect, useState } from "react";
import { expandedAPI } from "../api";
import { Line } from "react-chartjs-2";
import { Box, Heading, Spinner, Text, useToast } from "@chakra-ui/react";

export default function EngagementPage() {
  const [dataRows, setDataRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await expandedAPI.getEngagementTimeseries();
        setDataRows(response.data);
      } catch (err) {
        setError(err.message);
        toast({
          title: "Error fetching engagement data",
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
        <Text mt={4}>Loading engagement data...</Text>
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

  const labels = dataRows.map(r => new Date(r.timestamp).toLocaleDateString());
  const data = {
    labels,
    datasets: [
      { label: "Likes", data: dataRows.map(r => r.likes), borderColor: "#10b981", fill: false },
      { label: "Comments", data: dataRows.map(r => r.comments), borderColor: "#6366f1", fill: false },
      { label: "Shares", data: dataRows.map(r => r.shares), borderColor: "#f59e0b", fill: false },
      { label: "Bookmarks", data: dataRows.map(r => r.bookmarks), borderColor: "#ef4444", fill: false },
    ]
  };

  return (
    <Box p={4}>
      <Heading size="lg" mb={4}>Engagement Over Time</Heading>
      <Line data={data} />
    </Box>
  );
}