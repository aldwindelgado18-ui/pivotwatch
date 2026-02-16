import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Company {
  id: string;
  name: string;
  url: string;
  industry?: string;
  status: string;
  last_scanned?: string;
}

interface CompaniesState {
  list: Company[];
  selectedCompany: Company | null;
  loading: boolean;
}

const initialState: CompaniesState = {
  list: [],
  selectedCompany: null,
  loading: false,
};

const companiesSlice = createSlice({
  name: 'companies',
  initialState,
  reducers: {
    setCompanies: (state, action: PayloadAction<Company[]>) => {
      state.list = action.payload;
    },
    addCompany: (state, action: PayloadAction<Company>) => {
      state.list.push(action.payload);
    },
    removeCompany: (state, action: PayloadAction<string>) => {
      state.list = state.list.filter(c => c.id !== action.payload);
    },
    setSelectedCompany: (state, action: PayloadAction<Company | null>) => {
      state.selectedCompany = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setCompanies, addCompany, removeCompany, setSelectedCompany, setLoading } = companiesSlice.actions;
export default companiesSlice.reducer;