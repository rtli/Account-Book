import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// ========== Types ==========
export interface Category {
  id: number;
  name: string;
  parent_id: number | null;
  level: number;
}

export interface CategoryTree {
  id: number;
  name: string;
  level: number;
  children: CategoryTree[];
}

export interface Spending {
  id: number;
  item_name: string;
  category_id: number;
  category_name: string;
  amount: number;
  spend_date: string;
  created_at: string;
}

export interface SpendingList {
  items: Spending[];
  total: number;
  page: number;
  page_size: number;
}

export interface SankeyData {
  nodes: { name: string }[];
  links: { source: string; target: string; value: number }[];
}

export interface MonthlySummary {
  month: string;
  total: number;
}

export interface CategorySummary {
  name: string;
  total: number;
}

// ========== Spending API ==========
export const spendingApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    keyword?: string;
    category_id?: number;
    start_date?: string;
    end_date?: string;
  }) => api.get<SpendingList>('/spending', { params }),

  create: (data: {
    item_name: string;
    category_id: number;
    amount: number;
    spend_date?: string;
  }) => api.post<Spending>('/spending', data),

  update: (id: number, data: {
    item_name?: string;
    category_id?: number;
    amount?: number;
    spend_date?: string;
  }) => api.put<Spending>(`/spending/${id}`, data),

  delete: (id: number) => api.delete(`/spending/${id}`),
};

// ========== Category API ==========
export const categoryApi = {
  list: () => api.get<Category[]>('/category'),
  tree: () => api.get<CategoryTree[]>('/category/tree'),
  create: (data: { name: string; parent_id?: number; level?: number }) =>
    api.post<Category>('/category', data),
  delete: (id: number) => api.delete(`/category/${id}`),
  importCsv: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/category/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ========== Statistics API ==========
export const statisticsApi = {
  sankey: (params?: { year?: number; month?: number }) =>
    api.get<SankeyData>('/statistics/sankey', { params }),
  monthly: (params?: { year?: number }) =>
    api.get<MonthlySummary[]>('/statistics/monthly', { params }),
  categorySummary: (params?: { year?: number; month?: number }) =>
    api.get<CategorySummary[]>('/statistics/category-summary', { params }),
};

// ========== Data API ==========
export const dataApi = {
  importCsv: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/data/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  exportCsv: () => api.get('/data/export', { responseType: 'blob' }),
};

export default api;
