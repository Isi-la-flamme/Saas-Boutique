import client from './client';

export const tenantApi = {
  getAll: (params) => client.get('/tenants/', { params }),
  getById: (id) => client.get(`/tenants/${id}`),
  create: (data) => client.post('/tenants/', data),
  update: (id, data) => client.put(`/tenants/${id}`, data),
  delete: (id) => client.delete(`/tenants/${id}`),
};