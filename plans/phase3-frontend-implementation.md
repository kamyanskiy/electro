# Phase 3: Frontend Authentication & API Integration

## Overview

This phase focuses on building the React frontend with complete authentication flow, API integration, and connecting all components to the backend.

**Prerequisites:**
- ✅ Backend API running (Phase 1 complete)
- ✅ Database migrations applied
- ✅ Imperative ORM mapping implemented

**Goals:**
- Complete user authentication flow (register, login, logout)
- Integrate frontend with backend API
- Implement protected routes
- Connect ReadingForm to backend
- Build user dashboard

---

## Phase 3.1: API Service Layer

### 3.1.1 Create Base API Client

**File:** `/Users/matrix/Projects/electro/frontend/src/services/api.js`

```javascript
import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor - inject JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    // Extract error message
    const message = error.response?.data?.detail ||
                    error.message ||
                    'Произошла ошибка';

    return Promise.reject(new Error(message));
  }
);

export default api;
```

**Purpose:**
- Central axios instance with base URL
- Automatic JWT token injection
- Global error handling
- Token refresh logic

---

### 3.1.2 Create Authentication Service

**File:** `/Users/matrix/Projects/electro/frontend/src/services/auth.js`

```javascript
import api from './api';

class AuthService {
  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} User data
   */
  async register(userData) {
    const { data } = await api.post('/users/register', userData);
    return data;
  }

  /**
   * Login user
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} Token and user data
   */
  async login(username, password) {
    const { data } = await api.post('/users/login', {
      username,
      password,
    });

    // Store token
    localStorage.setItem('token', data.access_token);

    // Fetch user data
    const user = await this.getCurrentUser();
    localStorage.setItem('user', JSON.stringify(user));

    return { token: data.access_token, user };
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  /**
   * Get current authenticated user
   * @returns {Promise<Object>} User data
   */
  async getCurrentUser() {
    const { data } = await api.get('/users/me');
    return data;
  }

  /**
   * Check activation status
   * @returns {Promise<Object>} Activation status
   */
  async checkActivationStatus() {
    const { data } = await api.get('/users/me/activation-status');
    return data;
  }

  /**
   * Check if user is logged in
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  /**
   * Get stored user data
   * @returns {Object|null}
   */
  getStoredUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}

export default new AuthService();
```

---

### 3.1.3 Create Readings Service

**File:** `/Users/matrix/Projects/electro/frontend/src/services/readings.js`

```javascript
import api from './api';

class ReadingsService {
  /**
   * Submit new meter reading
   * @param {Object} readingData - Reading data
   * @returns {Promise<Object>} Created reading
   */
  async submitReading(readingData) {
    const { data } = await api.post('/readings', {
      day_reading: readingData.dayReading,
      night_reading: readingData.nightReading,
    });
    return data;
  }

  /**
   * Get readings history for current user
   * @param {number} limit - Number of readings to fetch
   * @returns {Promise<Array>} Array of readings
   */
  async getReadings(limit = 10) {
    const { data } = await api.get(`/readings?limit=${limit}`);
    return data.readings;
  }
}

export default new ReadingsService();
```

---

### 3.1.4 Create Admin Service

**File:** `/Users/matrix/Projects/electro/frontend/src/services/admin.js`

```javascript
import api from './api';

class AdminService {
  /**
   * Get pending user activations
   * @returns {Promise<Array>} Array of inactive users
   */
  async getPendingUsers() {
    const { data } = await api.get('/admin/users/pending');
    return data;
  }

  /**
   * Activate user
   * @param {string} userId - User ID to activate
   * @returns {Promise<Object>} Activated user
   */
  async activateUser(userId) {
    const { data } = await api.post(`/admin/users/${userId}/activate`);
    return data;
  }
}

export default new AdminService();
```

---

## Phase 3.2: Authentication State Management

### 3.2.1 Create AuthContext

**File:** `/Users/matrix/Projects/electro/frontend/src/context/AuthContext.jsx`

```javascript
import React, { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = authService.getStoredUser();

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(storedUser);
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  // Register user
  const register = useCallback(async (userData) => {
    try {
      setError(null);
      setLoading(true);
      await authService.register(userData);
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  // Login user
  const login = useCallback(async (username, password) => {
    try {
      setError(null);
      setLoading(true);
      const { token: newToken, user: newUser } = await authService.login(username, password);
      setToken(newToken);
      setUser(newUser);
      return { success: true, user: newUser };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout user
  const logout = useCallback(() => {
    authService.logout();
    setToken(null);
    setUser(null);
  }, []);

  // Refresh user data
  const refreshUser = useCallback(async () => {
    try {
      const updatedUser = await authService.getCurrentUser();
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (err) {
      console.error('Failed to refresh user:', err);
    }
  }, []);

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated: !!token,
    register,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

---

### 3.2.2 Create useAuth Hook

**File:** `/Users/matrix/Projects/electro/frontend/src/hooks/useAuth.js`

```javascript
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
};
```

---

## Phase 3.3: Authentication Components

### 3.3.1 Registration Form

**File:** `/Users/matrix/Projects/electro/frontend/src/components/RegistrationForm.jsx`

```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './RegistrationForm.css';

const RegistrationForm = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    plotNumber: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.plotNumber.trim()) {
      newErrors.plotNumber = 'Номер участка обязателен';
    }

    if (!formData.username.trim()) {
      newErrors.username = 'Имя пользователя обязательно';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Минимум 3 символа';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Некорректный email';
    }

    if (!formData.password) {
      newErrors.password = 'Пароль обязателен';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Минимум 6 символов';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage('');

    const result = await register({
      plot_number: formData.plotNumber,
      username: formData.username,
      email: formData.email,
      password: formData.password,
    });

    setIsSubmitting(false);

    if (result.success) {
      setSuccessMessage('Регистрация успешна! Ожидайте активации администратором.');
      setTimeout(() => navigate('/login'), 3000);
    } else {
      setErrors({ submit: result.error });
    }
  };

  return (
    <div className="registration-container">
      <div className="registration-card">
        <h2>Регистрация</h2>

        {successMessage && (
          <div className="success-message">{successMessage}</div>
        )}

        {errors.submit && (
          <div className="error-message">{errors.submit}</div>
        )}

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-group">
            <label htmlFor="plotNumber">Номер участка</label>
            <input
              type="text"
              id="plotNumber"
              name="plotNumber"
              value={formData.plotNumber}
              onChange={handleChange}
              className={errors.plotNumber ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.plotNumber && <span className="field-error">{errors.plotNumber}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="username">Имя пользователя</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className={errors.username ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Подтвердите пароль</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={errors.confirmPassword ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.confirmPassword && <span className="field-error">{errors.confirmPassword}</span>}
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="form-footer">
          <p>Уже есть аккаунт? <Link to="/login">Войти</Link></p>
        </div>
      </div>
    </div>
  );
};

export default RegistrationForm;
```

**File:** `/Users/matrix/Projects/electro/frontend/src/components/RegistrationForm.css`

```css
.registration-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.registration-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  padding: 40px;
  max-width: 450px;
  width: 100%;
}

.registration-card h2 {
  margin: 0 0 30px 0;
  text-align: center;
  color: #333;
  font-size: 28px;
}

.registration-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input.error {
  border-color: #e74c3c;
}

.field-error {
  color: #e74c3c;
  font-size: 12px;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.submit-button:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}
```

---

### 3.3.2 Login Form

**File:** `/Users/matrix/Projects/electro/frontend/src/components/LoginForm.jsx`

```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './LoginForm.css';

const LoginForm = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Имя пользователя обязательно';
    }

    if (!formData.password) {
      newErrors.password = 'Пароль обязателен';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);

    const result = await login(formData.username, formData.password);

    setIsSubmitting(false);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setErrors({ submit: result.error });
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Вход</h2>

        {errors.submit && (
          <div className="error-message">{errors.submit}</div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Имя пользователя</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className={errors.username ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? 'error' : ''}
              disabled={isSubmitting}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="form-footer">
          <p>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
```

**File:** `/Users/matrix/Projects/electro/frontend/src/components/LoginForm.css`

```css
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  padding: 40px;
  max-width: 400px;
  width: 100%;
}

.login-card h2 {
  margin: 0 0 30px 0;
  text-align: center;
  color: #333;
  font-size: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input.error {
  border-color: #e74c3c;
}

.field-error {
  color: #e74c3c;
  font-size: 12px;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.submit-button:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}
```

---

### 3.3.3 Private Route Component

**File:** `/Users/matrix/Projects/electro/frontend/src/components/PrivateRoute.jsx`

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <div>Загрузка...</div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
```

---

### 3.3.4 Navigation Component

**File:** `/Users/matrix/Projects/electro/frontend/src/components/Navigation.jsx`

```javascript
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Navigation.css';

const Navigation = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/dashboard">Электро СНТ</Link>
        </div>

        <div className="nav-menu">
          <Link to="/dashboard" className="nav-link">Главная</Link>
          <Link to="/readings" className="nav-link">Показания</Link>
          {user?.role === 'admin' && (
            <Link to="/admin" className="nav-link">Администрирование</Link>
          )}
        </div>

        <div className="nav-user">
          <span className="username">{user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Выйти
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
```

**File:** `/Users/matrix/Projects/electro/frontend/src/components/Navigation.css`

```css
.navigation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.nav-link:hover {
  opacity: 0.8;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: 500;
}

.logout-button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.3);
}
```

---

## Phase 3.4: Update Existing Components

### 3.4.1 Update ReadingForm

**File:** `/Users/matrix/Projects/electro/frontend/src/components/ReadingForm.jsx`

Update to integrate with API:

```javascript
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import readingsService from '../services/readings';
import StatusMessage from './StatusMessage';
import './ReadingForm.css';

const ReadingForm = ({ onSuccess }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    dayReading: '',
    nightReading: '',
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check if user is active
    if (!user?.is_active) {
      setStatus({
        type: 'error',
        message: 'Ваш аккаунт еще не активирован администратором'
      });
      return;
    }

    setIsSubmitting(true);
    setStatus({ type: '', message: '' });

    try {
      await readingsService.submitReading({
        dayReading: formData.dayReading,
        nightReading: formData.nightReading,
      });

      setStatus({
        type: 'success',
        message: 'Показания успешно отправлены!'
      });

      setFormData({ dayReading: '', nightReading: '' });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.message || 'Ошибка при отправке показаний'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="reading-form-container">
      <h2>Передать показания счетчика</h2>

      {status.message && (
        <StatusMessage type={status.type} message={status.message} />
      )}

      <form onSubmit={handleSubmit} className="reading-form">
        <div className="form-group">
          <label htmlFor="dayReading">Дневной тариф (кВт⋅ч)</label>
          <input
            type="number"
            id="dayReading"
            name="dayReading"
            step="0.01"
            min="0"
            value={formData.dayReading}
            onChange={handleChange}
            required
            disabled={isSubmitting || !user?.is_active}
          />
        </div>

        <div className="form-group">
          <label htmlFor="nightReading">Ночной тариф (кВт⋅ч)</label>
          <input
            type="number"
            id="nightReading"
            name="nightReading"
            step="0.01"
            min="0"
            value={formData.nightReading}
            onChange={handleChange}
            required
            disabled={isSubmitting || !user?.is_active}
          />
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={isSubmitting || !user?.is_active}
        >
          {isSubmitting ? 'Отправка...' : 'Отправить показания'}
        </button>
      </form>
    </div>
  );
};

export default ReadingForm;
```

---

## Phase 3.5: Dashboard and Pages

### 3.5.1 Dashboard Page

**File:** `/Users/matrix/Projects/electro/frontend/src/pages/Dashboard.jsx`

```javascript
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import authService from '../services/auth';
import ReadingForm from '../components/ReadingForm';
import ReadingHistory from '../components/ReadingHistory';
import Navigation from '../components/Navigation';
import './Dashboard.css';

const Dashboard = () => {
  const { user, refreshUser } = useAuth();
  const [activationStatus, setActivationStatus] = useState(null);
  const [refreshHistory, setRefreshHistory] = useState(0);

  useEffect(() => {
    const fetchActivationStatus = async () => {
      try {
        const status = await authService.checkActivationStatus();
        setActivationStatus(status);
      } catch (error) {
        console.error('Failed to fetch activation status:', error);
      }
    };

    fetchActivationStatus();
  }, []);

  const handleReadingSuccess = () => {
    setRefreshHistory(prev => prev + 1);
    refreshUser();
  };

  return (
    <>
      <Navigation />
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Личный кабинет</h1>
          <div className="user-info">
            <p><strong>Участок:</strong> {user?.plot_number}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p>
              <strong>Статус:</strong>{' '}
              <span className={user?.is_active ? 'status-active' : 'status-inactive'}>
                {user?.is_active ? 'Активирован' : 'Ожидает активации'}
              </span>
            </p>
          </div>
        </div>

        {!user?.is_active && (
          <div className="warning-message">
            <h3>⚠️ Аккаунт не активирован</h3>
            <p>
              Ваш аккаунт ожидает активации администратором.
              После активации вы сможете передавать показания счетчика.
            </p>
          </div>
        )}

        <div className="dashboard-content">
          <div className="dashboard-section">
            <ReadingForm onSuccess={handleReadingSuccess} />
          </div>

          <div className="dashboard-section">
            <ReadingHistory key={refreshHistory} />
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
```

**File:** `/Users/matrix/Projects/electro/frontend/src/pages/Dashboard.css`

```css
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  color: #333;
  margin-bottom: 1rem;
}

.user-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.user-info p {
  margin: 0.5rem 0;
}

.status-active {
  color: #28a745;
  font-weight: 600;
}

.status-inactive {
  color: #ffc107;
  font-weight: 600;
}

.warning-message {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.warning-message h3 {
  margin: 0 0 0.5rem 0;
  color: #856404;
}

.warning-message p {
  margin: 0;
  color: #856404;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.dashboard-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}
```

---

### 3.5.2 Reading History Component

**File:** `/Users/matrix/Projects/electro/frontend/src/components/ReadingHistory.jsx`

```javascript
import React, { useState, useEffect } from 'react';
import readingsService from '../services/readings';
import './ReadingHistory.css';

const ReadingHistory = () => {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReadings = async () => {
      try {
        setLoading(true);
        const data = await readingsService.getReadings(10);
        setReadings(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReadings();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (error) {
    return <div className="error">Ошибка: {error}</div>;
  }

  if (readings.length === 0) {
    return (
      <div className="reading-history">
        <h2>История показаний</h2>
        <p className="no-data">Показаний пока нет</p>
      </div>
    );
  }

  return (
    <div className="reading-history">
      <h2>История показаний</h2>
      <div className="readings-table">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>День (кВт⋅ч)</th>
              <th>Ночь (кВт⋅ч)</th>
              <th>Всего (кВт⋅ч)</th>
            </tr>
          </thead>
          <tbody>
            {readings.map(reading => {
              const total = parseFloat(reading.day_reading) + parseFloat(reading.night_reading);
              return (
                <tr key={reading.id}>
                  <td>{new Date(reading.reading_date).toLocaleDateString('ru-RU')}</td>
                  <td>{parseFloat(reading.day_reading).toFixed(2)}</td>
                  <td>{parseFloat(reading.night_reading).toFixed(2)}</td>
                  <td>{total.toFixed(2)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReadingHistory;
```

**File:** `/Users/matrix/Projects/electro/frontend/src/components/ReadingHistory.css`

```css
.reading-history h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #e74c3c;
}

.readings-table {
  overflow-x: auto;
}

.readings-table table {
  width: 100%;
  border-collapse: collapse;
}

.readings-table th,
.readings-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.readings-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.readings-table tbody tr:hover {
  background: #f8f9fa;
}
```

---

## Phase 3.6: Update App.jsx

**File:** `/Users/matrix/Projects/electro/frontend/src/App.jsx`

```javascript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import RegistrationForm from './components/RegistrationForm';
import LoginForm from './components/LoginForm';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App">
          <Routes>
            <Route path="/register" element={<RegistrationForm />} />
            <Route path="/login" element={<LoginForm />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

---

## Phase 3.7: Testing Checklist

### Backend Testing
- [ ] Start PostgreSQL: `docker compose up -d postgres`
- [ ] Start backend: `cd backend && pdm run uvicorn main:app --reload`
- [ ] Verify API docs: http://localhost:8000/docs
- [ ] Test health endpoint: http://localhost:8000/health

### Frontend Testing
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Open browser: http://localhost:5173

### User Flow Testing

#### 1. Registration Flow
- [ ] Navigate to /register
- [ ] Fill registration form with valid data
- [ ] Submit and verify success message
- [ ] Check database for new user record
- [ ] Verify user is inactive (is_active = false)

#### 2. Login Flow
- [ ] Navigate to /login
- [ ] Login with registered credentials
- [ ] Verify redirect to /dashboard
- [ ] Verify token stored in localStorage
- [ ] Verify user data stored in localStorage

#### 3. Dashboard Flow
- [ ] Verify user info displayed correctly
- [ ] Verify "not activated" warning shown for inactive users
- [ ] Verify reading form is disabled for inactive users

#### 4. Reading Submission (requires active user)
- [ ] Activate user via database or admin panel
- [ ] Refresh page
- [ ] Fill reading form with day/night values
- [ ] Submit and verify success message
- [ ] Verify reading appears in history table
- [ ] Check database for reading record

#### 5. Authentication Persistence
- [ ] Login
- [ ] Refresh page
- [ ] Verify still logged in
- [ ] Close and reopen browser
- [ ] Verify still logged in

#### 6. Logout Flow
- [ ] Click logout button
- [ ] Verify redirect to /login
- [ ] Verify token removed from localStorage
- [ ] Try accessing /dashboard
- [ ] Verify redirected to /login

#### 7. Protected Routes
- [ ] Logout
- [ ] Try accessing /dashboard directly
- [ ] Verify redirect to /login

---

## Phase 3.8: Known Issues & Solutions

### Issue 1: CORS Errors
**Symptom:** Browser console shows CORS policy errors

**Solution:**
- Verify backend CORS settings in [main.py](backend/main.py:34-41)
- Ensure `FRONTEND_URL=http://localhost:5173` in `.env`
- Restart backend after changes

### Issue 2: Token Expiration
**Symptom:** User gets logged out unexpectedly

**Solution:**
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`
- Implement token refresh mechanism (future enhancement)

### Issue 3: API Request Failures
**Symptom:** Network errors or timeouts

**Solution:**
- Verify backend is running on port 8000
- Check axios baseURL in [api.js](frontend/src/services/api.js:4)
- Verify PostgreSQL is running

### Issue 4: Reading Form Disabled
**Symptom:** Cannot submit readings even when logged in

**Solution:**
- Check user activation status in database
- Activate user: `UPDATE users SET is_active = true WHERE username = 'testuser';`
- Refresh page after activation

---

## Phase 3.9: Next Steps (Phase 4 Preview)

After completing Phase 3, you'll have:
- ✅ Working authentication flow
- ✅ Protected routes
- ✅ Reading submission
- ✅ Reading history display

**Phase 4 will add:**
- Admin panel for user activation
- Advanced dashboard features
- Reading analytics and charts
- Export functionality
- Mobile responsive design improvements

---

## Quick Start Commands

```bash
# Terminal 1 - Backend
cd /Users/matrix/Projects/electro
docker compose up -d postgres
cd backend
pdm run alembic upgrade head
pdm run uvicorn main:app --reload

# Terminal 2 - Frontend
cd /Users/matrix/Projects/electro/frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Success Criteria

Phase 3 is complete when:
- [ ] Users can register successfully
- [ ] Users can login and receive JWT token
- [ ] Token persists across page refreshes
- [ ] Protected routes redirect unauthenticated users
- [ ] Inactive users see activation warning
- [ ] Active users can submit readings
- [ ] Reading history displays correctly
- [ ] Logout clears token and redirects
- [ ] Navigation shows for authenticated users
- [ ] No console errors in browser
- [ ] All API calls use proper authentication

---

**Last Updated:** 2026-01-23
**Plan Status:** Ready for implementation
**Estimated Time:** 4-6 hours for full implementation
