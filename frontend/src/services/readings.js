/**
 * Readings service - handles meter reading operations
 */
import api from './api';

const readingsService = {
  /**
   * Submit a new meter reading
   * @param {Object} readingData - Reading data
   * @param {number} readingData.day_reading - Day tariff reading
   * @param {number} readingData.night_reading - Night tariff reading
   * @returns {Promise<Object>} - Created reading
   */
  async submitReading(readingData) {
    const response = await api.post('/readings', readingData);
    return response.data;
  },

  /**
   * Get user's reading history
   * @param {number} limit - Number of readings to fetch (default: 10)
   * @returns {Promise<Object>} - Object with readings array and total count
   */
  async getReadings(limit = 10) {
    const response = await api.get('/readings', {
      params: { limit },
    });
    return response.data.readings;
  },

  /**
   * Check if user has already submitted reading for today
   * @returns {Promise<Object>} - Object with exists flag and reading data if exists
   */
  async checkReadingToday() {
    const response = await api.get('/readings/check-today');
    return response.data;
  },
};

export default readingsService;
