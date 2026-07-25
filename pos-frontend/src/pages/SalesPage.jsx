import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productApi } from '../api/products';
import { saleApi } from '../api/sales';
import { customerApi } from '../api/customers';
import { Plus, Minus, Trash2, ShoppingCart, Search, Eye, X, Printer } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

const SalesPage = () => {
  const [cart, setCart] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedSale, setSelectedSale] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [lastSale, setLastSale] = useState(null);
  const [customerId, setCustomerId] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const { user } = useAuth();
  const queryClient = useQueryClient();

  useEffect(() => {
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') {
        setShowDetailModal(false);
        setShowReceiptModal(false);
      }
    };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, []);

  // Récupérer les produits
  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => productApi.getAll(),
  });

  // Récupérer les ventes
  const { data: salesData, isLoading: salesLoading } = useQuery({
    queryKey: ['sales'],
    queryFn: () => saleApi.getAll(),
  });
  const { data: customersData } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customerApi.getAll(),
  });

  // Créer une vente
  const createSaleMutation = useMutation({
    mutationFn: saleApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries(['sales']);
      queryClient.invalidateQueries(['products']);
      setLastSale(data.data);
      setCart([]);
      setCustomerId('');
      setCustomerSearch('');
      setLoading(false);
      toast.success('✅ Vente validée !');
      setShowReceiptModal(true);
    },
    onError: (error) => {
      setLoading(false);
      toast.error(error.response?.data?.detail || 'Erreur création vente');
    },
  });

  // Mettre à jour une vente (pour le paiement)
  const updateSaleMutation = useMutation({
    mutationFn: ({ id, data }) => saleApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['sales']);
      toast.success('✅ Vente payée !');
      setShowDetailModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erreur paiement');
    },
  });

  const products = productsData?.data?.items || [];
  const sales = salesData?.data?.items || [];
  const customers = customersData?.data?.items || [];

  const customerLabel = (customer) => `${customer.name}${customer.phone ? ` — ${customer.phone}` : ''}`;
  const selectCustomer = (value) => {
    setCustomerSearch(value);
    const customer = customers.find((item) => customerLabel(item).toLowerCase() === value.trim().toLowerCase());
    setCustomerId(customer ? String(customer.id) : '');
  };

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const addToCart = (product) => {
    const existingItem = cart.find((item) => item.id === product.id);
    if (existingItem) {
      setCart(
        cart.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    toast.success(`${product.name} ajouté au panier`);
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(
      cart.map((item) =>
        item.id === productId ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter((item) => item.id !== productId));
    toast.success('Produit retiré du panier');
  };

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // Valider la vente avec mode de paiement
  const handleCheckout = (mode = 'paid') => {
    if (cart.length === 0) {
      toast.error('Panier vide');
      return;
    }

    setLoading(true);
    
    const isDeferred = mode === 'deferred';
    const saleData = {
      status: 'completed',
      payment_status: isDeferred ? 'unpaid' : 'paid',
      payment_method: isDeferred ? 'deferred' : 'cash',
      amount_paid: isDeferred ? 0 : total,
      customer_id: customerId ? Number(customerId) : null,
      items: cart.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
        unit_price: item.price,
      })),
    };

    createSaleMutation.mutate(saleData);
  };

  // Payer une vente impayée
  const handlePaySale = (saleId) => {
    const saleToPay = sales.find(s => s.id === saleId);
    if (!saleToPay) return;
    
    const updateData = {
      payment_status: 'paid',
      amount_paid: saleToPay.total,
      payment_method: 'cash'
    };
    
    updateSaleMutation.mutate({ id: saleId, data: updateData });
  };

  const viewSaleDetail = (sale) => {
    setSelectedSale(sale);
    setShowDetailModal(true);
  };

  // Fonction d'impression
  const handlePrint = () => {
    const printContent = document.getElementById('receipt-content');
    if (!printContent) return;
    
    const printWindow = window.open('', '_blank', 'width=400,height=600');
    if (!printWindow) {
      toast.error('Veuillez autoriser les popups pour imprimer');
      return;
    }
    
    printWindow.document.write(`
      <html>
        <head>
          <title>Ticket de caisse</title>
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
              font-family: 'Courier New', monospace; 
              font-size: 12px; 
              padding: 20px; 
              max-width: 300px; 
              margin: 0 auto;
              background: white;
            }
            .receipt { 
              text-align: center; 
              border: 1px dashed #ccc; 
              padding: 15px;
            }
            .header { margin-bottom: 15px; }
            .header h2 { font-size: 18px; }
            .header .info { font-size: 10px; color: #666; }
            .divider { border-top: 1px dashed #ccc; margin: 10px 0; }
            .items { text-align: left; margin: 10px 0; }
            .item { display: flex; justify-content: space-between; padding: 4px 0; }
            .item .qty { width: 30px; }
            .item .name { flex: 1; padding: 0 10px; }
            .item .price { width: 80px; text-align: right; }
            .total { font-size: 16px; font-weight: bold; margin: 10px 0; }
            .footer { margin-top: 15px; font-size: 10px; color: #666; }
            .thank-you { font-size: 14px; font-weight: bold; margin: 10px 0; }
            @media print {
              body { padding: 0; }
              .receipt { border: none; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div id="receipt-content">
            ${printContent.innerHTML}
          </div>
          <script>
            window.print();
            window.onafterprint = function() { window.close(); };
          <\/script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  const renderReceipt = () => {
    if (!lastSale) return null;
    
    const date = new Date(lastSale.created_at);
    const totalItems = lastSale.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

    return (
      <div id="receipt-content">
        <div className="receipt">
          <div className="header">
            <h2>🏪 POINT DE VENTE</h2>
            <p className="info">Ticket #T-{String(lastSale.id).padStart(6, '0')}</p>
            <p className="info">{date.toLocaleDateString()} {date.toLocaleTimeString()}</p>
            <p className="info">Vendeur: {user?.full_name || user?.email}</p>
            {lastSale.customer_name && <p className="info">Client: {lastSale.customer_name}</p>}
          </div>

          <div className="divider"></div>

          <div className="items">
            {lastSale.items?.map((item, index) => (
              <div key={index} className="item">
                <span className="qty">{item.quantity}×</span>
                <span className="name">{item.product_name || `Produit #${item.product_id}`}</span>
                <span className="price">{(item.quantity * item.unit_price).toFixed(2)} F CFA</span>
              </div>
            ))}
          </div>

          <div className="divider"></div>

          <div className="total">
            <div className="item">
              <span>Total</span>
              <span style={{ fontSize: '18px' }}>{lastSale.total.toFixed(2)} F CFA</span>
            </div>
            <div className="item" style={{ fontSize: '10px', color: '#666' }}>
              <span>Articles: {totalItems}</span>
            </div>
          </div>

          <div className="divider"></div>

          <div className="thank-you">Merci de votre visite !</div>
          <div className="footer">
            <p>Retour possible sous 14 jours</p>
            <p>Super Boutique
              
            </p>
          </div>
        </div>
      </div>
    );
  };

  if (productsLoading || salesLoading) {
    return <div className="text-center py-12">Chargement...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Point de Vente (POS)</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne 1 & 2 : Produits */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Rechercher un produit..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="border rounded-lg p-4 hover:shadow-lg transition cursor-pointer hover:border-blue-500"
                  onClick={() => addToCart(product)}
                >
                  <h3 className="font-semibold text-sm">{product.name}</h3>
                  <p className="text-xs text-gray-500">Stock: {product.stock}</p>
                  <p className="text-lg font-bold text-blue-600">{product.price} F CFA</p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      addToCart(product);
                    }}
                    className="mt-2 w-full bg-blue-600 text-white text-sm py-1 rounded hover:bg-blue-700"
                    disabled={product.stock <= 0}
                  >
                    {product.stock > 0 ? 'Ajouter' : 'Rupture'}
                  </button>
                </div>
              ))}
            </div>

            {filteredProducts.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                Aucun produit trouvé
              </div>
            )}
          </div>
        </div>

        {/* Colonne 3 : Panier */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4 sticky top-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Panier</h2>
              <ShoppingCart className="w-5 h-5 text-gray-500" />
            </div>

            {cart.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <ShoppingCart className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                <p>Panier vide</p>
              </div>
            ) : (
              <>
                <div className="mb-4">
                  <label htmlFor="sale-customer" className="mb-1 block text-sm font-medium text-gray-700">Client <span className="font-normal text-gray-400">(facultatif)</span></label>
                  <input id="sale-customer" list="sale-customer-options" value={customerSearch} onChange={(event) => selectCustomer(event.target.value)} placeholder="Rechercher un client…" autoComplete="off" className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
                  <datalist id="sale-customer-options">
                    {customers.map((customer) => <option key={customer.id} value={customerLabel(customer)} />)}
                  </datalist>
                  <p className="mt-1 text-xs text-gray-500">Laissez ce champ vide pour une vente sans client.</p>
                  <select id="sale-customer-native" aria-hidden="true" tabIndex="-1" value={customerId} onChange={(event) => setCustomerId(event.target.value)} className="sr-only">
                    <option value="">Vente sans client</option>
                    {customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.name}{customer.phone ? ` — ${customer.phone}` : ''}</option>)}
                  </select>
                  <Link to="/customers" className="mt-2 inline-block text-xs font-medium text-blue-700 underline hover:text-blue-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">Gérer les clients</Link>
                </div>
                <div className="max-h-[300px] overflow-y-auto mb-4">
                  {cart.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between py-2 border-b"
                    >
                      <div className="flex-1">
                        <p className="text-sm font-medium">{item.name}</p>
                        <p className="text-xs text-gray-500">
                          {item.price} F CFA x {item.quantity}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="p-1 text-gray-500 hover:text-blue-600"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="w-8 text-center text-sm">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="p-1 text-gray-500 hover:text-blue-600"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeFromCart(item.id)}
                          className="p-1 text-red-500 hover:text-red-700 ml-2"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total</span>
                    <span className="text-blue-600">{total.toFixed(2)} F CFA</span>
                  </div>
                  
                  {/* Deux boutons */}
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleCheckout('paid')}
                      disabled={loading || cart.length === 0}
                      className="flex-1 bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center justify-center"
                    >
                      {loading ? 'Validation...' : '💰 Payer maintenant'}
                    </button>
                    <button
                      onClick={() => handleCheckout('deferred')}
                      disabled={loading || cart.length === 0}
                      className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                    >
                      {loading ? 'Validation...' : '📝 À crédit'}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Historique des ventes avec statut paiement */}
      <div className="mt-8 bg-white rounded-lg shadow p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Historique des ventes</h2>
          <span className="text-sm text-gray-500">{sales.length} ventes</span>
        </div>
        {sales.length === 0 ? (
          <div className="text-center py-4 text-gray-500">Aucune vente</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">#</th>
                  <th className="px-4 py-2 text-left">Total</th>
                  <th className="px-4 py-2 text-left">Client</th>
                  <th className="px-4 py-2 text-left">Articles</th>
                  <th className="px-4 py-2 text-left">Statut</th>
                  <th className="px-4 py-2 text-left">Paiement</th>
                  <th className="px-4 py-2 text-left">Date</th>
                  <th className="px-4 py-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {sales.map((sale) => (
                  <tr key={sale.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium">#{sale.id}</td>
                    <td className="px-4 py-2 font-medium">{sale.total} F CFA</td>
                    <td className="px-4 py-2">{sale.customer_name || '—'}</td>
                    <td className="px-4 py-2">{sale.items?.length || 0}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        sale.status === 'completed' ? 'bg-green-100 text-green-800' :
                        sale.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {sale.status}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        sale.payment_status === 'paid' ? 'bg-green-100 text-green-800' :
                        sale.payment_status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {sale.payment_status === 'paid' ? '✅ Payé' :
                         sale.payment_status === 'partial' ? '🔄 Partiel' :
                         '❌ Impayé'}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-gray-500">
                      {new Date(sale.created_at).toLocaleDateString()} {new Date(sale.created_at).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => viewSaleDetail(sale)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Eye className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Détail Vente avec boutons Imprimer, Payer, Fermer */}
      {showDetailModal && selectedSale && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" role="presentation">
          <div role="dialog" aria-modal="true" aria-labelledby="sale-detail-title" className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 id="sale-detail-title" className="text-xl font-bold">Détail de la vente #{selectedSale.id}</h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Fermer le détail de la vente"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Total</p>
                <p className="text-xl font-bold text-blue-600">{selectedSale.total} F CFA</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Statut</p>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  selectedSale.status === 'completed' ? 'bg-green-100 text-green-800' :
                  selectedSale.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {selectedSale.status}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500">Paiement</p>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  selectedSale.payment_status === 'paid' ? 'bg-green-100 text-green-800' :
                  selectedSale.payment_status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {selectedSale.payment_status === 'paid' ? '✅ Payé' :
                   selectedSale.payment_status === 'partial' ? '🔄 Partiel' :
                   '❌ Impayé'}
                </span>
              </div>
              {selectedSale.payment_status !== 'paid' && (
                <div>
                  <p className="text-sm text-gray-500">Reste à payer</p>
                  <p className="text-lg font-bold text-red-600">{selectedSale.remaining_amount?.toFixed(2)} F CFA</p>
                </div>
              )}
            </div>

            <h3 className="font-semibold mb-2">Articles</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Produit</th>
                    <th className="px-4 py-2 text-right">Quantité</th>
                    <th className="px-4 py-2 text-right">Prix unitaire</th>
                    <th className="px-4 py-2 text-right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedSale.items?.map((item, index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2">{item.product_name || `Produit #${item.product_id}`}</td>
                      <td className="px-4 py-2 text-right">{item.quantity}</td>
                      <td className="px-4 py-2 text-right">{item.unit_price} F CFA</td>
                      <td className="px-4 py-2 text-right font-medium">{(item.quantity * item.unit_price).toFixed(2)} F CFA</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-gray-50">
                  <tr>
                    <td colSpan="3" className="px-4 py-2 text-right font-bold">Total</td>
                    <td className="px-4 py-2 text-right font-bold text-blue-600">{selectedSale.total} F CFA</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Trois boutons */}
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => {
                  setLastSale(selectedSale);
                  setShowDetailModal(false);
                  setShowReceiptModal(true);
                }}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center justify-center"
              >
                <Printer className="w-4 h-4 mr-2" />
                Imprimer
              </button>
              
              {selectedSale.payment_status !== 'paid' && (
                <button
                  onClick={() => handlePaySale(selectedSale.id)}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center justify-center"
                >
                  <span className="mr-2">💰</span>
                  Payer
                </button>
              )}
              
              <button
                onClick={() => setShowDetailModal(false)}
                className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Ticket de caisse */}
      {showReceiptModal && lastSale && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" role="presentation">
          <div role="dialog" aria-modal="true" aria-labelledby="receipt-title" className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex justify-between items-center mb-4">
              <h2 id="receipt-title" className="text-xl font-bold">🧾 Ticket de caisse</h2>
              <button
                onClick={() => setShowReceiptModal(false)}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Fermer le ticket de caisse"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mb-4 max-h-[400px] overflow-y-auto">
              {renderReceipt()}
            </div>

            <div className="flex gap-2">
              <button
                onClick={handlePrint}
                className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 flex items-center justify-center"
              >
                <Printer className="w-4 h-4 mr-2" />
                Imprimer
              </button>
              <button
                onClick={() => setShowReceiptModal(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-md hover:bg-gray-300"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesPage;
