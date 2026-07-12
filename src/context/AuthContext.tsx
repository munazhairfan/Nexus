import React, { createContext, useState, useContext, useEffect } from 'react';
import { User, UserRole, AuthContextType } from '../types';
import apiClient from '../api/client';
import toast from 'react-hot-toast';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('business_nexus_token');
    if (token) {
      syncProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

  const syncProfile = async () => {
    try {
      const res = await apiClient.get('/auth/me');
      setUser(res.data);
    } catch (error) {
      localStorage.removeItem('business_nexus_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string, role: UserRole): Promise<void> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post('/auth/login', { email, password, role });
      localStorage.setItem('business_nexus_token', res.data.access_token);
      await syncProfile();
      toast.success('Successfully logged in!');
    } catch (error) {
      toast.error('Login failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string, role: UserRole, profileData: any = {}): Promise<void> => {
    setIsLoading(true);
    try {
      await apiClient.post('/auth/register', { name, email, password, role, ...profileData });
      toast.success('Account created successfully! Please log in.');
    } catch (error) {
      toast.error('Registration failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    setUser(null);
    localStorage.removeItem('business_nexus_token');
    toast.success('Logged out successfully');
  };

  // Mock implementations for unsupported functions
  const forgotPassword = async (email: string): Promise<void> => { toast('Not implemented'); };
  const resetPassword = async (token: string, newPassword: string): Promise<void> => { toast('Not implemented'); };
  const updateProfile = async (userId: string, updates: Partial<User>): Promise<void> => { toast('Not implemented'); };

  const value = {
    user,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    updateProfile,
    isAuthenticated: !!user,
    isLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
