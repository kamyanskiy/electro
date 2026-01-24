/**
 * AuthContext - manages global authentication state
 */
import { createContext, useState, useEffect } from 'react';
import authService from '../services/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initAuth = () => {
      const storedUser = authService.getCurrentUser();
      const token = authService.getToken();

      if (storedUser && token) {
        setUser(storedUser);
        setIsAuthenticated(true);
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Register a new user
   */
  const register = async (userData) => {
    const registeredUser = await authService.register(userData);
    return registeredUser;
  };

  /**
   * Login user
   */
  const login = async (username, password) => {
    const { user: loggedInUser } = await authService.login(username, password);
    setUser(loggedInUser);
    setIsAuthenticated(true);
    return loggedInUser;
  };

  /**
   * Logout user
   */
  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  /**
   * Check activation status
   */
  const checkActivationStatus = async () => {
    const status = await authService.checkActivationStatus();
    // Only update user if activation status has actually changed
    if (user && user.is_active !== status.is_active) {
      const updatedUser = { ...user, is_active: status.is_active };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    return status;
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    register,
    login,
    logout,
    checkActivationStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
