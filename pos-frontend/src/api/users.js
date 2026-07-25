import client from './client';

export const userApi = {
  getAll: (params) => client.get('/users/', { params }),
  getById: (id) => client.get(`/users/${id}`),
  create: (data) => client.post('/users/', data),
  update: (id, data) => client.put(`/users/${id}`, data),
  toggleStatus: (id) => client.patch(`/users/${id}/status`),
  delete: (id) => client.delete(`/users/${id}`),
};
