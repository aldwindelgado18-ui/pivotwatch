import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  id: string | null;
  email: string | null;
  name: string | null;
  plan: string;
  isAuthenticated: boolean;
}

const initialState: UserState = {
  id: null,
  email: null,
  name: null,
  plan: 'free',
  isAuthenticated: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<any>) => {
      state.id = action.payload.id;
      state.email = action.payload.email;
      state.name = action.payload.name;
      state.plan = action.payload.plan;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      localStorage.removeItem('access_token');
      return initialState;
    },
  },
});

export const { setUser, logout } = userSlice.actions;
export default userSlice.reducer;