/**
 * Admin service - handles admin operations (user activation, readings management)
 */
import api from './api';

const adminService = {
  /**
   * Get list of pending users waiting for activation
   * @returns {Promise<Array>} - Array of inactive users
   */
  async getPendingUsers() {
    const response = await api.get('/admin/users/pending');
    return response.data;
  },

  /**
   * Activate a user
   * @param {string} userId - User ID (UUID)
   * @returns {Promise<Object>} - Updated user data
   */
  async activateUser(userId) {
    const response = await api.post(`/admin/users/${userId}/activate`);
    return response.data;
  },

  /**
   * Get all meter readings with optional filtering by month
   * @param {number|null} year - Year to filter (optional)
   * @param {number|null} month - Month to filter (1-12, optional)
   * @returns {Promise<Object>} - Object with readings array and total count
   */
  async getReadings(year = null, month = null) {
    const params = {};
    if (year !== null && month !== null) {
      params.year = year;
      params.month = month;
    }
    const response = await api.get('/admin/readings', { params });
    return response.data;
  },

  /**
   * Export readings to Excel file
   * @param {number|null} year - Year to filter (optional)
   * @param {number|null} month - Month to filter (1-12, optional)
   * @returns {Promise<Blob>} - Excel file blob
   */
  async exportReadings(year = null, month = null) {
    const params = {};
    if (year !== null && month !== null) {
      params.year = year;
      params.month = month;
    }
    const response = await api.get('/admin/readings/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

export default adminService;
