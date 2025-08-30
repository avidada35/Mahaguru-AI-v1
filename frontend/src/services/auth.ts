import api from './api';
import { setToken, removeToken } from '@/utils/token';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export const login = async (credentials: LoginCredentials) => {
  const form = new URLSearchParams();
  form.append('username', credentials.email);
  form.append('password', credentials.password);
  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  setToken(data.access_token);
  const me = await getCurrentUser();
  return me;
};

export const register = async (userData: RegisterData) => {
  const { data } = await api.post('/auth/register', userData);
  return data;
};

export const logout = async () => {
  try {
    await api.post('/auth/logout');
  } catch (_) {
    // ignore
  } finally {
    removeToken();
    window.location.href = '/auth/login';
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/users/me');
    return response.data;
  } catch (error) {
    return null;
  }
};
