import React, { useEffect, useState } from "react";
import { expandedAPI } from "../api";
import { Pie } from "react-chartjs-2";
import { Box, Heading, Spinner, Text, useToast } from "@chakra-ui/react";

export default function SatisfactionPage() {
  const [dataRows, setDataRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await expandedAPI.getUserSatisfaction();
        setDataRows(response.data);
      } catch (err) {
        setError(err.message);
        toast({
          title: "Error fetching satisfaction data",
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
        <Text mt={4}>Loading satisfaction data...</Text>
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

  const data = {
    labels: dataRows.map(r => r.satisfaction_level),
    datasets: [
      {
        data: dataRows.map(r => r.count),
        backgroundColor: [
          "#10b981", // High - green
          "#f59e0b", // Medium - yellow
          "#ef4444", // Low - red
        ],
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: "bottom",
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || "";
            const value = context.raw || 0;
            const total = dataRows.reduce((sum, row) => sum + row.count, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <Box p={4}>
      <Heading size="lg" mb={4}>User Satisfaction Distribution</Heading>
      <Box maxW="600px" mx="auto">
        <Pie data={data} options={options} />
      </Box>
    </Box>
  );
}