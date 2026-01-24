/**
 * AdminPanel - Admin dashboard for managing users and viewing readings
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';
import adminService from '../services/admin';
import './AdminPanel.css';

const AdminPanel = () => {
  const { user } = useAuth();
  const [pendingUsers, setPendingUsers] = useState([]);
  const [readings, setReadings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingReadings, setIsLoadingReadings] = useState(false);
  const [error, setError] = useState(null);
  const [readingsError, setReadingsError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'readings'

  // Filter state
  const currentDate = new Date();
  const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth() + 1);
  const [showAllReadings, setShowAllReadings] = useState(false);

  // Redirect non-admin users
  if (!user || user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  const fetchPendingUsers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const users = await adminService.getPendingUsers();
      setPendingUsers(users);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить список пользователей');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchReadings = async () => {
    setIsLoadingReadings(true);
    setReadingsError(null);

    try {
      const year = showAllReadings ? null : selectedYear;
      const month = showAllReadings ? null : selectedMonth;
      const data = await adminService.getReadings(year, month);
      setReadings(data.readings);
    } catch (err) {
      setReadingsError(err.message || 'Не удалось загрузить показания');
    } finally {
      setIsLoadingReadings(false);
    }
  };

  const handleExportReadings = async () => {
    try {
      const year = showAllReadings ? null : selectedYear;
      const month = showAllReadings ? null : selectedMonth;
      const blob = await adminService.exportReadings(year, month);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const filename = showAllReadings
        ? `readings_all_${new Date().toISOString().split('T')[0]}.xlsx`
        : `readings_${selectedYear}_${String(selectedMonth).padStart(2, '0')}.xlsx`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccessMessage('Файл успешно экспортирован');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setReadingsError(err.message || 'Не удалось экспортировать показания');
    }
  };

  useEffect(() => {
    fetchPendingUsers();
  }, []);

  useEffect(() => {
    if (activeTab === 'readings') {
      fetchReadings();
    }
  }, [activeTab, selectedYear, selectedMonth, showAllReadings]);

  const handleActivateUser = async (userId) => {
    try {
      await adminService.activateUser(userId);
      setSuccessMessage('Пользователь успешно активирован');

      // Refresh the list
      await fetchPendingUsers();

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      setError(err.message || 'Не удалось активировать пользователя');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const months = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
  ];

  const years = Array.from({ length: 5 }, (_, i) => currentDate.getFullYear() - i);

  return (
    <div className="admin-panel">
      <div className="admin-container">
        <h1>Админ панель</h1>

        {successMessage && (
          <div className="alert alert-success">
            {successMessage}
          </div>
        )}

        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Активация пользователей
          </button>
          <button
            className={`tab ${activeTab === 'readings' ? 'active' : ''}`}
            onClick={() => setActiveTab('readings')}
          >
            Показания счетчиков
          </button>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="panel-section">
            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            <h2>Пользователи ожидающие активации</h2>

            {isLoading ? (
              <p className="loading-text">Загрузка...</p>
            ) : pendingUsers.length === 0 ? (
              <p className="empty-text">Нет пользователей ожидающих активации</p>
            ) : (
              <div className="table-container">
                <table className="users-table">
                  <thead>
                    <tr>
                      <th>Участок</th>
                      <th>Имя пользователя</th>
                      <th>Email</th>
                      <th>Дата регистрации</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingUsers.map((pendingUser) => (
                      <tr key={pendingUser.id}>
                        <td>{pendingUser.plot_number}</td>
                        <td>{pendingUser.username}</td>
                        <td>{pendingUser.email}</td>
                        <td>{formatDate(pendingUser.created_at)}</td>
                        <td>
                          <button
                            className="btn-activate"
                            onClick={() => handleActivateUser(pendingUser.id)}
                          >
                            Активировать
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Readings Tab */}
        {activeTab === 'readings' && (
          <div className="panel-section">
            {readingsError && (
              <div className="alert alert-error">
                {readingsError}
              </div>
            )}

            <h2>Показания счетчиков</h2>

            <div className="filters">
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={showAllReadings}
                  onChange={(e) => setShowAllReadings(e.target.checked)}
                />
                Показать все показания
              </label>

              {!showAllReadings && (
                <div className="filter-selects">
                  <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(Number(e.target.value))}
                    className="filter-select"
                  >
                    {months.map((month, index) => (
                      <option key={index} value={index + 1}>
                        {month}
                      </option>
                    ))}
                  </select>

                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                    className="filter-select"
                  >
                    {years.map((year) => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <button onClick={handleExportReadings} className="btn-export">
                Экспорт в Excel
              </button>
            </div>

            {isLoadingReadings ? (
              <p className="loading-text">Загрузка...</p>
            ) : readings.length === 0 ? (
              <p className="empty-text">Нет показаний за выбранный период</p>
            ) : (
              <div className="table-container">
                <table className="readings-table">
                  <thead>
                    <tr>
                      <th>Дата</th>
                      <th>Участок</th>
                      <th>Пользователь</th>
                      <th>День (кВт⋅ч)</th>
                      <th>Ночь (кВт⋅ч)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {readings.map((reading) => (
                      <tr key={reading.id}>
                        <td>{new Date(reading.reading_date).toLocaleDateString('ru-RU')}</td>
                        <td>{reading.plot_number}</td>
                        <td>{reading.username}</td>
                        <td>{Number(reading.day_reading).toFixed(2)}</td>
                        <td>{Number(reading.night_reading).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
