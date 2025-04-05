import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// User API endpoints
export const userAPI = {
  getAllUsers: (skip = 0, limit = 100) => api.get(`/api/users?skip=${skip}&limit=${limit}`),
  getUserById: (userId) => api.get(`/api/users/${userId}`),
  getUserMetrics: (userId) => api.get(`/api/users/${userId}/metrics`),
  getUserPreferences: (userId) => api.get(`/api/users/${userId}/preferences`),
  getUserRelationships: (userId) => api.get(`/api/users/${userId}/relationships`),
  getUserNetworkMetrics: (userId) => api.get(`/api/users/${userId}/network-metrics`),
  getUserFeedback: (userId, status) => api.get(`/api/users/${userId}/feedback${status ? `?status=${status}` : ''}`),
  getUserChurnEvents: (userId) => api.get(`/api/users/${userId}/churn-events`),
  createUser: (userData) => api.post('/api/users', userData),
  updateUser: (userId, userData) => api.put(`/api/users/${userId}`, userData),
  updateUserPreferences: (userId, preferences) => api.put(`/api/users/${userId}/preferences`, preferences),
  deleteUser: (userId) => api.delete(`/api/users/${userId}`),
  getUserRegions: () => api.get('/api/users/regions'),
};

// Content API endpoints
export const contentAPI = {
  getAllContent: (skip = 0, limit = 100) => api.get(`/api/content?skip=${skip}&limit=${limit}`),
  getContentById: (contentId) => api.get(`/api/content/${contentId}`),
  getThreads: (skip = 0, limit = 100) => api.get(`/api/content/threads?skip=${skip}&limit=${limit}`),
  getVideos: (skip = 0, limit = 100) => api.get(`/api/content/videos?skip=${skip}&limit=${limit}`),
  getMixedContent: (skip = 0, limit = 100) => api.get(`/api/content/mixed?skip=${skip}&limit=${limit}`),
  getContentInteractions: (contentId, interactionType) => 
    api.get(`/api/content/${contentId}/interactions${interactionType ? `?type=${interactionType}` : ''}`),
  getContentRecommendations: (contentId, userId) => 
    api.get(`/api/content/${contentId}/recommendations${userId ? `?user_id=${userId}` : ''}`),
  createContent: (contentData) => api.post('/api/content', contentData),
  createContentInteraction: (contentId, interactionData) => 
    api.post(`/api/content/${contentId}/interactions`, interactionData),
  updateContent: (contentId, contentData) => api.put(`/api/content/${contentId}`, contentData),
  deleteContent: (contentId) => api.delete(`/api/content/${contentId}`),
  predictContent: (contentData) => api.post('/api/content/predict', contentData),
  predictFeed: (userData) => api.post('/api/content/predict/feed', userData),
};

// Ad API endpoints
export const adAPI = {
  getAllAds: (skip = 0, limit = 100) => api.get(`/api/ads?skip=${skip}&limit=${limit}`),
  getAdById: (adId) => api.get(`/api/ads/${adId}`),
  getAdImpressions: (adId, skip = 0, limit = 100) => 
    api.get(`/api/ads/${adId}/impressions?skip=${skip}&limit=${limit}`),
  getAdAuctionLogs: (adId, skip = 0, limit = 100) => 
    api.get(`/api/ads/${adId}/auction-logs?skip=${skip}&limit=${limit}`),
  getAdCategories: () => api.get('/api/ads/categories'),
  createAd: (adData) => api.post('/api/ads', adData),
  recordAdImpression: (adId, impressionData) => 
    api.post(`/api/ads/${adId}/impressions`, impressionData),
  updateAd: (adId, adData) => api.put(`/api/ads/${adId}`, adData),
  deleteAd: (adId) => api.delete(`/api/ads/${adId}`),
  predictCTR: (adData) => api.post('/api/ads/predict/ctr', adData),
  getCTRTrend: () => api.get('/api/ads/ctr-trend'),
};

// Moderation API endpoints
export const moderationAPI = {
  getContentReports: (skip = 0, limit = 100, status) => 
    api.get(`/api/moderation/content-reports?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),
  getContentReport: (reportId) => api.get(`/api/moderation/content-reports/${reportId}`),
  getContentFlags: (skip = 0, limit = 100, status) => 
    api.get(`/api/moderation/content-flags?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),
  getContentFlag: (flagId) => api.get(`/api/moderation/content-flags/${flagId}`),
  createContentReport: (reportData) => api.post('/api/moderation/content-reports', reportData),
  createContentFlag: (flagData) => api.post('/api/moderation/content-flags', flagData),
  updateContentReport: (reportId, reportData) => 
    api.put(`/api/moderation/content-reports/${reportId}`, reportData),
  updateContentFlag: (flagId, flagData) => 
    api.put(`/api/moderation/content-flags/${flagId}`, flagData),
  getModerationStats: () => api.get('/api/moderation/stats'),
  predictModeration: (contentData) => api.post('/api/moderation/predict', contentData),
};

// Expanded metrics API endpoints
export const expandedAPI = {
  getUserSatisfaction: () => api.get('/api/expanded/users/satisfaction'),
  getEngagementTimeseries: (startDate, endDate, interval) => 
    api.get(`/api/expanded/engagement/timeseries${startDate ? `?start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}${interval ? `&interval=${interval}` : ''}`),
  getAdROI: (startDate, endDate, adId) => 
    api.get(`/api/expanded/ads/roi${startDate ? `?start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}${adId ? `&ad_id=${adId}` : ''}`),
  getSmartInsights: () => api.get('/api/expanded/insights'),
  createUserSatisfaction: (satisfactionData) => api.post('/api/expanded/users/satisfaction', satisfactionData),
  createEngagementMetrics: (metricsData) => api.post('/api/expanded/engagement', metricsData),
  createAdROI: (roiData) => api.post('/api/expanded/ads/roi', roiData),
};

// Model API endpoints
export const modelAPI = {
  getModelMetrics: (modelName, metricName, startDate, endDate, skip, limit) => 
    api.get(`/api/model/metrics${modelName ? `?model_name=${modelName}` : ''}${metricName ? `&metric_name=${metricName}` : ''}${startDate ? `&start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}${skip ? `&skip=${skip}` : ''}${limit ? `&limit=${limit}` : ''}`),
  getModelPredictions: (modelName, startDate, endDate, skip, limit) => 
    api.get(`/api/model/predictions${modelName ? `?model_name=${modelName}` : ''}${startDate ? `&start_date=${startDate}` : ''}${endDate ? `&end_date=${endDate}` : ''}${skip ? `&skip=${skip}` : ''}${limit ? `&limit=${limit}` : ''}`),
  createModelMetrics: (metricsData) => api.post('/api/model/metrics', metricsData),
  createModelPrediction: (predictionData) => api.post('/api/model/predictions', predictionData),
  getModelStats: () => api.get('/api/model/stats'),
};

export default api; 