import client from './client';

export const adminApi = {
  getTenants: () => client.get('/admin/tenants'),
  createTenant: (data) => client.post('/admin/tenants', data),
  updateTenant: (id, data) => client.put(`/admin/tenants/${id}`, data),
  deleteTenant: (id) => client.delete(`/admin/tenants/${id}`),
  getUsers: () => client.get('/admin/users'),
  createUser: (tenantId, data) => client.post(`/admin/users/${tenantId}`, data),
  toggleUser: (id) => client.put(`/admin/users/${id}/toggle-status`),
  deleteUser: (id) => client.delete(`/admin/users/${id}`),
};
