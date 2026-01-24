/**
 * Authentication service - handles user registration, login, logout
 */
import api from './api';

const authService = {
  /**
   * Register a new user
   * @param {Object} userData - Registration data
   * @param {string} userData.plot_number - Plot number
   * @param {string} userData.username - Username
   * @param {string} userData.email - Email address
   * @param {string} userData.password - Password
   * @returns {Promise<Object>} - Registered user data
   */
  async register(userData) {
    const response = await api.post('/users/register', userData);
    return response.data;
  },

  /**
   * Login user
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} - Token and user data
   */
  async login(username, password) {
    // FastAPI OAuth2 expects form data with specific field names
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/users/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, token_type, user } = response.data;

    // Store token and user in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));

    return { access_token, token_type, user };
  },

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user from localStorage
   * @returns {Object|null} - User object or null
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    try {
      return JSON.parse(userStr);
    } catch (e) {
      return null;
    }
  },

  /**
   * Get current token
   * @returns {string|null} - Token or null
   */
  getToken() {
    return localStorage.getItem('access_token');
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Check activation status
   * @returns {Promise<Object>} - Activation status
   */
  async checkActivationStatus() {
    const response = await api.get('/users/me/activation-status');
    return response.data;
  },
};

export default authService;
