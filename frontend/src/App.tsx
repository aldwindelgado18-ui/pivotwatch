import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { store } from './store';

// Layout components
import Layout from './components/layout/Layout';
import PrivateRoute from './components/auth/PrivateRoute';

// Pages
import Dashboard from './pages/Dashboard';
import Companies from './pages/Companies';
import CompanyDetail from './pages/CompanyDetail';
import Changes from './pages/Changes';
import ChangeDetail from './pages/ChangeDetail';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Styles
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route path="/" element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="companies" element={<Companies />} />
              <Route path="companies/:id" element={<CompanyDetail />} />
              <Route path="changes" element={<Changes />} />
              <Route path="changes/:id" element={<ChangeDetail />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </Router>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;