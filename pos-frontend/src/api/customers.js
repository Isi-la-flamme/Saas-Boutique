import client from './client';

export const customerApi = {
  getAll: (params) => client.get('/customers/', { params }),
  create: (data) => client.post('/customers/', data),
  update: (id, data) => client.put(`/customers/${id}`, data),
  delete: (id) => client.delete(`/customers/${id}`),
};
