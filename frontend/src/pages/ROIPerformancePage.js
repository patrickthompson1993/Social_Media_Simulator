import React, { useEffect, useState } from "react";
import { expandedAPI } from "../api";
import { Line } from "react-chartjs-2";
import { Box, Heading, Spinner, Text, useToast, Select, FormControl, FormLabel } from "@chakra-ui/react";

export default function ROIPerformancePage() {
  const [dataRows, setDataRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAdId, setSelectedAdId] = useState("");
  const [adOptions, setAdOptions] = useState([]);
  const toast = useToast();

  useEffect(() => {
    const fetchAds = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/ads");
        const ads = await response.json();
        setAdOptions(ads.map(ad => ({ value: ad.id, label: ad.title })));
      } catch (err) {
        console.error("Error fetching ads:", err);
      }
    };

    fetchAds();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await expandedAPI.getAdROI(null, null, selectedAdId);
        setDataRows(response.data);
      } catch (err) {
        setError(err.message);
        toast({
          title: "Error fetching ROI data",
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
  }, [selectedAdId, toast]);

  if (loading) {
    return (
      <Box p={4} textAlign="center">
        <Spinner size="xl" />
        <Text mt={4}>Loading ROI data...</Text>
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

  const labels = dataRows.map(r => new Date(r.date).toLocaleDateString());
  const data = {
    labels,
    datasets: [
      { label: "ROI", data: dataRows.map(r => r.roi), borderColor: "#10b981", fill: false },
      { label: "Impressions", data: dataRows.map(r => r.impressions), borderColor: "#6366f1", fill: false },
      { label: "Clicks", data: dataRows.map(r => r.clicks), borderColor: "#f59e0b", fill: false },
      { label: "Revenue", data: dataRows.map(r => r.revenue), borderColor: "#ef4444", fill: false },
      { label: "Cost", data: dataRows.map(r => r.cost), borderColor: "#8b5cf6", fill: false },
    ]
  };

  return (
    <Box p={4}>
      <Heading size="lg" mb={4}>Ad ROI Performance</Heading>
      
      <FormControl mb={4}>
        <FormLabel>Select Ad</FormLabel>
        <Select 
          placeholder="All Ads" 
          value={selectedAdId} 
          onChange={(e) => setSelectedAdId(e.target.value)}
        >
          {adOptions.map(ad => (
            <option key={ad.value} value={ad.value}>{ad.label}</option>
          ))}
        </Select>
      </FormControl>
      
      <Line data={data} />
    </Box>
  );
}