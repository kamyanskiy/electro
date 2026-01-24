import React, { useEffect } from 'react';
import './StatusMessage.css';

const StatusMessage = ({ type, title, message, data, errors, onClose }) => {
  useEffect(() => {
    if (type === 'success') {
      const timer = setTimeout(() => {
        if (onClose) onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [type, onClose]);

  const getIcon = () => {
    if (type === 'success') return '✓';
    if (type === 'error') return '✗';
    return 'ℹ';
  };

  return (
    <div className={`status-message ${type || 'info'}`}>
      <div className="status-container">
        <span className="status-icon">{getIcon()}</span>
        <div className="status-text">
          {title && <h3>{title}</h3>}
          <p>{message}</p>

          {data && (
            <div className="status-data">
              {data.day_reading && <p>День: {data.day_reading} кВт·ч</p>}
              {data.night_reading && <p>Ночь: {data.night_reading} кВт·ч</p>}
              {data.date && <p>Дата: {data.date}</p>}
            </div>
          )}

          {errors && (
            <div className="status-errors">
              <h4>Ошибки:</h4>
              <ul>
                {errors.map((error, index) => (
                  <li key={index}>{error.message}</li>
                ))}
              </ul>
            </div>
          )}

          {type === 'error' && onClose && (
            <button onClick={onClose} className="retry-button">
              Попробовать снова
            </button>
          )}
        </div>
        {type !== 'success' && onClose && (
          <button onClick={onClose} className="close-button">
            ×
          </button>
        )}
      </div>
    </div>
  );
};

StatusMessage.defaultProps = {
  onClose: null
};

export default StatusMessage;