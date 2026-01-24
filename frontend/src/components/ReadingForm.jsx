import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import readingsService from '../services/readings';
import StatusMessage from './StatusMessage';
import './ReadingForm.css';

const ReadingForm = ({ onSuccess }) => {
  const { user, checkActivationStatus } = useAuth();
  const [dayReading, setDayReading] = useState('');
  const [nightReading, setNightReading] = useState('');
  const [message, setMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activationStatus, setActivationStatus] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [existingReading, setExistingReading] = useState(null);
  const intervalRef = useRef(null);
  const isInitialized = useRef(false);

  // Check activation status on component mount and set up polling
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await checkActivationStatus();
        setActivationStatus(status);
      } catch (error) {
        console.error('Failed to check activation status:', error);
      }
    };

    // Only initialize once when user is available
    if (user && !isInitialized.current) {
      isInitialized.current = true;

      // Initial check
      checkStatus();

      // Set up polling interval - check every 15 seconds
      intervalRef.current = setInterval(() => {
        checkStatus();
      }, 15000);
    }

    // Cleanup interval on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [user, checkActivationStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    // Check if user is active
    if (activationStatus && !activationStatus.is_active) {
      setMessage({
        type: 'error',
        text: 'Ваш аккаунт еще не активирован администратором. Пожалуйста, дождитесь активации.',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Check if reading for today already exists
      const checkResult = await readingsService.checkReadingToday();

      if (checkResult.exists) {
        // Show confirmation modal
        setExistingReading(checkResult.reading);
        setShowConfirmModal(true);
        setIsSubmitting(false);
        return;
      }

      // If no existing reading, submit directly
      await submitReading();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || 'Не удалось проверить показания',
      });
      setIsSubmitting(false);
    }
  };

  const submitReading = async () => {
    setIsSubmitting(true);
    setShowConfirmModal(false);

    try {
      const result = await readingsService.submitReading({
        day_reading: parseFloat(dayReading),
        night_reading: parseFloat(nightReading),
      });

      setMessage({
        type: 'success',
        text: result.is_update
          ? 'Показания успешно обновлены'
          : 'Показания успешно сохранены',
      });

      // Reset form
      setDayReading('');
      setNightReading('');
      setExistingReading(null);

      // Notify parent component if callback provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || 'Не удалось сохранить показания',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelUpdate = () => {
    setShowConfirmModal(false);
    setExistingReading(null);
  };

  return (
    <div className="reading-form">
      <h2>Ввод показаний</h2>

      {message && <StatusMessage type={message.type} message={message.text} />}

      {activationStatus && !activationStatus.is_active && (
        <div className="warning-banner" style={{
          padding: '15px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          marginBottom: '20px',
          color: '#856404'
        }}>
          <strong>Ожидание активации:</strong> Ваш аккаунт еще не активирован администратором.
          Вы сможете отправлять показания после активации.
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="dayReading">Показания день (кВт·ч):</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="99999.99"
            id="dayReading"
            value={dayReading}
            onChange={(e) => setDayReading(e.target.value)}
            disabled={isSubmitting}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="nightReading">Показания ночь (кВт·ч):</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="99999.99"
            id="nightReading"
            value={nightReading}
            onChange={(e) => setNightReading(e.target.value)}
            disabled={isSubmitting}
            required
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting || (activationStatus && !activationStatus.is_active)}
        >
          {isSubmitting ? 'Отправка...' : 'Отправить'}
        </button>
      </form>

      {showConfirmModal && existingReading && (
        <div className="modal-overlay" onClick={handleCancelUpdate}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Предупреждение</h3>
            <p>
              Вы уже отправляли показания сегодня ({existingReading.reading_date}):
            </p>
            <div className="existing-readings">
              <p><strong>День:</strong> {existingReading.day_reading} кВт·ч</p>
              <p><strong>Ночь:</strong> {existingReading.night_reading} кВт·ч</p>
            </div>
            <p className="warning-text">
              При продолжении предыдущие данные будут перезаписаны новыми значениями.
            </p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={handleCancelUpdate}
                disabled={isSubmitting}
              >
                Отмена
              </button>
              <button
                className="btn-confirm"
                onClick={submitReading}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Обновление...' : 'Подтвердить обновление'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReadingForm;