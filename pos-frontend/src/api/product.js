import client from './client';

export const productApi = {
  getAll: (params) => client.get('/products/', { params }),
  getById: (id) => client.get(`/products/${id}`),
  create: (data) => client.post('/products/', data),
  update: (id, data) => client.put(`/products/${id}`, data),
  delete: (id) => client.delete(`/products/${id}`),
};