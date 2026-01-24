/**
 * Dashboard - Main dashboard page for authenticated users
 */
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import ReadingForm from '../components/ReadingForm';
import ReadingHistory from '../components/ReadingHistory';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleReadingSuccess = () => {
    // Trigger refresh of reading history
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Добро пожаловать, {user?.username}!</h1>
          <div className="user-details">
            <p>
              <strong>Участок:</strong> {user?.plot_number}
            </p>
            <p>
              <strong>Email:</strong> {user?.email}
            </p>
            <p>
              <strong>Статус:</strong>{' '}
              <span className={user?.is_active ? 'status-active' : 'status-inactive'}>
                {user?.is_active ? 'Активен' : 'Ожидает активации'}
              </span>
            </p>
          </div>
        </div>

        <div className="dashboard-content">
          <div className="reading-form-section">
            <ReadingForm onSuccess={handleReadingSuccess} />
          </div>

          <div className="reading-history-section">
            <ReadingHistory refresh={refreshKey} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
