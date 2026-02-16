import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';
import companiesReducer from './slices/companiesSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    companies: companiesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;