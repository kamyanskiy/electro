/**
 * Navigation - App navigation bar
 */
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

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/">СТ АВТО учет показаний эл. энергии</Link>
        </div>

        {isAuthenticated ? (
          <div className="nav-menu">
            <Link to="/dashboard" className="nav-link">
              Главная
            </Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="nav-link">
                Админ панель
              </Link>
            )}
            <div className="nav-user">
              <span className="user-info">
                {user?.username} (Участок: {user?.plot_number})
              </span>
              <button onClick={handleLogout} className="btn-logout">
                Выйти
              </button>
            </div>
          </div>
        ) : (
          <div className="nav-menu">
            <Link to="/login" className="nav-link">
              Войти
            </Link>
            <Link to="/register" className="nav-link">
              Регистрация
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
