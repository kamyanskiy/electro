/**
 * ReadingHistory - Display user's reading history
 */
import { useState, useEffect } from 'react';
import readingsService from '../services/readings';
import './ReadingHistory.css';

const ReadingHistory = ({ refresh }) => {
  const [readings, setReadings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReadings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await readingsService.getReadings(20);
      setReadings(data);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить историю показаний');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReadings();
  }, [refresh]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="reading-history">
        <h3>История показаний</h3>
        <p className="loading-text">Загрузка...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reading-history">
        <h3>История показаний</h3>
        <p className="error-text">{error}</p>
      </div>
    );
  }

  if (readings.length === 0) {
    return (
      <div className="reading-history">
        <h3>История показаний</h3>
        <p className="empty-text">Нет сохраненных показаний</p>
      </div>
    );
  }

  return (
    <div className="reading-history">
      <h3>История показаний</h3>
      <div className="table-container">
        <table className="readings-table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>День (кВт·ч)</th>
              <th>Ночь (кВт·ч)</th>
              <th>Всего (кВт·ч)</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((reading) => (
              <tr key={reading.id}>
                <td>{formatDate(reading.reading_date)}</td>
                <td>{Number(reading.day_reading).toFixed(2)}</td>
                <td>{Number(reading.night_reading).toFixed(2)}</td>
                <td>
                  <strong>{(Number(reading.day_reading) + Number(reading.night_reading)).toFixed(2)}</strong>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReadingHistory;
