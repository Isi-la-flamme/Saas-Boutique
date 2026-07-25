import client from './client';

export const saleApi = {
  getAll: (params) => client.get('/sales/', { params }),
  getById: (id) => client.get(`/sales/${id}`),
  create: (data) => client.post('/sales/', data),
  update: (id, data) => client.put(`/sales/${id}`, data),
  delete: (id) => client.delete(`/sales/${id}`),
};