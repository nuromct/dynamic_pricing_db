// ============================================
// DYNAMIC PRICING DASHBOARD - JavaScript
// ============================================

const API_BASE = '/api';

// Global chart instances
let categoryChart = null;
let inventoryChart = null;

// ============================================
// NAVIGATION
// ============================================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        // Show page
        const pageName = item.dataset.page;
        showPage(pageName);
    });
});

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    // Show selected page
    const page = document.getElementById(`${pageName}-page`);
    if (page) {
        page.classList.add('active');
        document.getElementById('page-title').textContent = getPageTitle(pageName);
        loadPageData(pageName);
    }
}

function getPageTitle(pageName) {
    const titles = {
        'dashboard': 'Dashboard',
        'products': 'Ürünler',
        'inventory': 'Stok Yönetimi',
        'orders': 'Siparişler',
        'price-history': 'Fiyat Geçmişi',
        'users': 'Kullanıcılar',
        'suppliers': 'Tedarikçiler'
    };
    return titles[pageName] || pageName;
}

// ============================================
// API CALLS
// ============================================

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error('API Error');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

async function postAPI(endpoint, data) {
    try {
        console.log('POST Request:', endpoint, data);
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        console.log('POST Response:', result);
        if (!response.ok) {
            alert('Hata: ' + (result.detail || JSON.stringify(result)));
            return null;
        }
        return result;
    } catch (error) {
        console.error('API Error:', error);
        alert('API Hatası: ' + error.message);
        return null;
    }
}

async function putAPI(endpoint, data) {
    try {
        console.log('PUT Request:', endpoint, data);
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) {
            alert('Hata: ' + (result.detail || JSON.stringify(result)));
            return null;
        }
        return result;
    } catch (error) {
        console.error('API Error:', error);
        alert('API Hatası: ' + error.message);
        return null;
    }
}

async function deleteAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
        const result = await response.json();
        if (!response.ok) {
            alert('Hata: ' + (result.detail || JSON.stringify(result)));
            return null;
        }
        return result;
    } catch (error) {
        console.error('API Error:', error);
        alert('API Hatası: ' + error.message);
        return null;
    }
}

// ============================================
// PAGE DATA LOADERS
// ============================================

function loadPageData(pageName) {
    switch (pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'products':
            loadProducts();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'price-history':
            loadPriceHistory();
            break;
        case 'users':
            loadUsers();
            break;
        case 'suppliers':
            loadSuppliers();
            break;
    }
}

// ============================================
// DASHBOARD
// ============================================

async function loadDashboard() {
    // Load stats
    const stats = await fetchAPI('/dashboard/stats');
    if (stats) {
        document.getElementById('stat-products').textContent = stats.total_products;
        document.getElementById('stat-orders').textContent = stats.total_orders;
        document.getElementById('stat-lowstock').textContent = stats.low_stock_count;
        document.getElementById('stat-revenue').textContent = `₺${stats.total_revenue.toLocaleString()}`;
    }

    // Load category chart
    const categories = await fetchAPI('/dashboard/category-distribution');
    if (categories && categories.length > 0) {
        renderCategoryChart(categories);
    }

    // Low stock warnings
    const lowStock = await fetchAPI('/inventory/low-stock');
    if (lowStock) {
        const list = document.getElementById('low-stock-list');
        if (list) {
            list.innerHTML = lowStock.map(i => `
                <li class="list-group-item" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; margin-bottom: 0.5rem; background: #1e293b; border-radius: 8px;">
                    <span style="flex: 1; margin-right: 1rem;">${i.title}</span>
                    <span class="badge badge-danger" style="white-space: nowrap;">${i.stockquantity} Adet</span>
                </li>
            `).join('');
        }
    }

    // Load inventory chart (stok durumu)
    const inventory = await fetchAPI('/inventory');
    if (inventory && inventory.length > 0) {
        renderInventoryChart(inventory);
    }
}

function renderInventoryChart(data) {
    const ctx = document.getElementById('inventoryChart');
    if (!ctx) return;

    if (inventoryChart) inventoryChart.destroy();

    // Büyükten küçüğe sırala - TÜM ürünler
    const sortedData = [...data].sort((a, b) => b.stockquantity - a.stockquantity);

    inventoryChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: sortedData.map(d => d.title.length > 10 ? d.title.substring(0, 10) + '...' : d.title),
            datasets: [{
                label: 'Stok Adedi',
                data: sortedData.map(d => d.stockquantity),
                backgroundColor: sortedData.map(d => {
                    if (d.stockquantity < d.lowstockthreshold) return '#ef4444'; // kırmızı - düşük
                    if (d.stockquantity > d.highstockthreshold) return '#22c55e'; // yeşil - yüksek
                    return '#f59e0b'; // sarı - normal
                }),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            const index = context[0].dataIndex;
                            return sortedData[index].title; // Tam ürün adı
                        },
                        label: function (context) {
                            return `Stok: ${context.raw} adet`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: { size: 9 }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    title: {
                        display: true,
                        text: 'Stok Adedi'
                    }
                }
            }
        }
    });
}

function renderCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    if (categoryChart) categoryChart.destroy();

    categoryChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => d.value),
                backgroundColor: [
                    '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                    '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

// ============================================
// PRODUCTS
// ============================================

async function loadProducts(search = '', category_id = '') {
    let url = '/products';
    const params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (category_id) params.push(`category_id=${category_id}`);
    if (params.length > 0) url += '?' + params.join('&');

    const result = await fetchAPI(url);
    if (result && result.products) {
        const tbody = document.querySelector('#products-table tbody');
        if (!tbody) return;

        tbody.innerHTML = result.products.map(p => `
            <tr>
                <td>${p.productid}</td>
                <td>
                    <strong>${p.title}</strong>
                </td>
                <td>${p.category_name || '-'}</td>
                <td>${p.supplier_name || '-'}</td>
                <td>₺${p.baseprice || '-'}</td>
                <td>₺${p.currentprice}</td>
                <td>
                    <span class="badge ${getStockBadge(p.stockquantity)}">
                        ${p.stockquantity || 0}
                    </span>
                </td>
                <td>
                    <button class="btn btn-primary btn-small" onclick="showPriceChart(${p.productid}, '${p.title.replace(/'/g, "\\'")}')">📈</button>
                    <button class="btn btn-danger btn-small" onclick="deleteProduct(${p.productid})">Sil</button>
                </td>
            </tr>
        `).join('');
    }
}

function getStockBadge(stock) {
    if (stock < 10) return 'badge-danger';
    if (stock > 100) return 'badge-success';
    return 'badge-warning';
}

async function showAddProductModal() {
    // Kategorileri ve tedarikçileri getir
    const categories = await fetchAPI('/categories');
    const suppliers = await fetchAPI('/suppliers');

    // Modal içini doldur
    document.getElementById('modal-title').textContent = 'Yeni Ürün Ekle';
    document.getElementById('modal-body').innerHTML = `
        <form id="product-form">
            <div class="form-group">
                <label>Ürün Adı</label>
                <input type="text" name="title" required>
            </div>
            <div class="form-group">
                <label>Açıklama</label>
                <textarea name="description"></textarea>
            </div>
            <div class="form-group">
                <label>Kategori</label>
                <select name="category_id">
                    <option value="">Seçiniz</option>
                    ${(categories || []).map(c => `<option value="${c.categoryid}">${c.categoryname}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Tedarikçi</label>
                <select name="supplier_id">
                    <option value="">Seçiniz</option>
                    ${(suppliers || []).map(s => `<option value="${s.supplierid}">${s.companyname}</option>`).join('')}
                </select>
            </div>
            <div class="row">
                <div class="form-group">
                    <label>Taban Fiyat</label>
                    <input type="number" name="base_price" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Satış Fiyatı</label>
                    <input type="number" name="current_price" step="0.01" required>
                </div>
            </div>
            <button type="submit" class="btn btn-success">Kaydet</button>
        </form>
    `;

    // Submit olayı
    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            category_id: formData.get('category_id') ? parseInt(formData.get('category_id')) : null,
            supplier_id: formData.get('supplier_id') ? parseInt(formData.get('supplier_id')) : null,
            base_price: parseFloat(formData.get('base_price')),
            current_price: parseFloat(formData.get('current_price')),
            is_active: true
        };

        const result = await postAPI('/products', data);
        if (result) {
            closeModal();
            alert('Ürün başarıyla eklendi!');
            loadProducts();
            loadDashboard();
        }
    });

    document.getElementById('modal').classList.add('active');
}

async function deleteProduct(productId) {
    if (!confirm('Bu ürünü silmek istediğinize emin misiniz?')) return;

    const result = await deleteAPI(`/products/${productId}`);
    if (result) {
        alert('Ürün silindi.');
        loadProducts();
    }
}

// ============================================
// INVENTORY
// ============================================

async function loadInventory() {
    const data = await fetchAPI('/inventory');
    if (data) {
        const tbody = document.querySelector('#inventory-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(i => `
            <tr>
                <td>${i.productid}</td>
                <td>${i.title}</td>
                <td>
                    <span class="badge ${getStatusBadge(i.stock_status)}">${i.stockquantity}</span>
                </td>
                <td>${i.lowstockthreshold}</td>
                <td>${i.highstockthreshold}</td>
                <td>${i.lastrestockdate || '-'}</td>
                <td>
                    <button class="btn btn-primary btn-small" onclick="editStock(${i.productid}, ${i.stockquantity})">Düzenle</button>
                </td>
            </tr>
        `).join('');
    }
}

function getStatusBadge(status) {
    if (status === 'LOW') return 'badge-danger';
    if (status === 'HIGH') return 'badge-success';
    return 'badge-warning';
}

async function editStock(productId, currentStock) {
    const newStock = prompt('Yeni stok adedi:', currentStock);
    if (newStock !== null) {
        const qty = parseInt(newStock);
        if (isNaN(qty)) return alert('Geçersiz sayı');

        await putAPI(`/inventory/${productId}`, {
            stock_quantity: qty,
            low_stock_threshold: 10,
            high_stock_threshold: 100
        });
        loadInventory();
        loadDashboard();
    }
}

// ============================================
// ORDERS
// ============================================

async function loadOrders() {
    const data = await fetchAPI('/orders');
    if (data) {
        const tbody = document.querySelector('#orders-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(o => `
            <tr>
                <td>${o.orderid}</td>
                <td>${o.customer_name}</td>
                <td style="max-width: 250px; font-size: 0.85rem; color: #94a3b8;">${o.order_items || '-'}</td>
                <td style="max-width: 150px; font-size: 0.85rem; color: #60a5fa;">${o.suppliers || '-'}</td>
                <td style="max-width: 200px; font-size: 0.85rem;">${o.shippingaddress || '-'}</td>
                <td>${new Date(o.orderdate).toLocaleDateString()}</td>
                <td>
                    <span class="badge ${o.status === 'completed' ? 'badge-success' : (o.status === 'cancelled' ? 'badge-danger' : 'badge-warning')}">
                        ${o.status}
                    </span>
                </td>
                <td>₺${o.totalamount}</td>
            </tr>
        `).join('');
    }
}

// ============================================
// PRICE HISTORY
// ============================================

async function loadPriceHistory() {
    const data = await fetchAPI('/price-history');
    if (data) {
        const tbody = document.querySelector('#price-history-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(h => {
            const change = ((h.newprice - h.oldprice) / h.oldprice * 100).toFixed(1);
            const isPositive = h.newprice > h.oldprice;
            const color = isPositive ? '#22c55e' : '#ef4444'; // yeşil: artış, kırmızı: düşüş
            const sign = isPositive ? '+' : '';

            return `
            <tr>
                <td>${h.title}</td>
                <td>₺${h.oldprice}</td>
                <td>₺${h.newprice}</td>
                <td style="color: ${color}; font-weight: bold;">
                    ${sign}${change}%
                </td>
                <td>${getReasonLabel(h.reason)}</td>
                <td>${new Date(h.changedate).toLocaleString()}</td>
            </tr>
        `}).join('');
    }
}

function getReasonLabel(reason) {
    const labels = {
        'low_stock': '📉 Düşük Stok (ZAM)',
        'high_stock': '📈 Yüksek Stok (İNDİRİM)',
        'campaign': '🏷️ Kampanya',
        'inflation': '📈 Enflasyon',
        'demand_increase': '📈 Talep Artışı',
        'manual_update': '✏️ Manuel'
    };
    return labels[reason] || reason;
}

// ============================================
// USERS
// ============================================

async function loadUsers() {
    const data = await fetchAPI('/users');
    if (data) {
        const tbody = document.querySelector('#users-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(user => `
            <tr>
                <td>${user.userid}</td>
                <td>${user.fullname}</td>
                <td>${user.email}</td>
                <td>
                    <span class="badge ${getRoleBadgeClass(user.role)}">
                        ${getRoleLabel(user.role)}
                    </span>
                </td>
                <td>${user.phonenumber || '-'}</td>
                <td>
                    <button class="btn btn-danger btn-small" onclick="deleteUser(${user.userid})">Sil</button>
                </td>
            </tr>
        `).join('');
    }
}

function getRoleBadgeClass(role) {
    switch (role) {
        case 'admin': return 'badge-danger';
        case 'seller': return 'badge-info';
        default: return 'badge-success';
    }
}

function getRoleLabel(role) {
    switch (role) {
        case 'admin': return 'Admin';
        case 'seller': return 'Satıcı';
        case 'customer': return 'Müşteri';
        default: return role;
    }
}

async function deleteUser(userId) {
    if (!confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) return;

    const result = await deleteAPI(`/users/${userId}`);
    if (result) {
        alert('Kullanıcı silindi.');
        loadUsers();
    }
}

// ============================================
// SUPPLIERS
// ============================================

async function loadSuppliers() {
    const data = await fetchAPI('/suppliers');
    if (data) {
        const tbody = document.querySelector('#suppliers-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(s => `
            <tr>
                <td>${s.supplierid}</td>
                <td>${s.companyname}</td>
                <td>${s.contactemail || '-'}</td>
                <td>${s.taxnumber || '-'}</td>
                <td>${s.address || '-'}</td>
                <td>${s.product_count || 0}</td>
                <td>
                    <button class="btn btn-danger btn-small" onclick="deleteSupplier(${s.supplierid})">Sil</button>
                </td>
            </tr>
        `).join('');
    }
}

async function deleteSupplier(supplierId) {
    if (!confirm('Bu tedarikçiyi silmek istediğinize emin misiniz?')) return;

    const result = await deleteAPI(`/suppliers/${supplierId}`);
    if (result) {
        alert('Tedarikçi silindi.');
        loadSuppliers();
    }
}

// ============================================
// MODAL
// ============================================

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
});

// ============================================
// REFRESH BUTTON
// ============================================

document.getElementById('refresh-btn').addEventListener('click', () => {
    const activeNav = document.querySelector('.nav-item.active');
    if (activeNav) {
        loadPageData(activeNav.dataset.page);
    }
});

// ============================================
// CAMPAIGNS & ADVANCED CHARTS
// ============================================

async function showCampaignModal() {
    const categories = await fetchAPI('/categories');

    document.getElementById('campaign-modal-body').innerHTML = `
    <form id="campaign-form">
        <div class="form-group">
            <label>Kategori Seçin</label>
            <select name="category_id" required>
                ${(categories || []).map(c => `<option value="${c.categoryid}">${c.categoryname}</option>`).join('')}
            </select>
        </div>
        <div class="form-group">
            <label>İndirim Oranı (%)</label>
            <input type="number" name="discount" min="1" max="99" value="10" required>
        </div>
        <div class="alert alert-info">
            Dikkat: Seçilen kategorideki tüm ürünlerin fiyatı düşürülecektir.
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%">Kampanyayı Uygula 🚀</button>
    </form>
`;

    document.getElementById('campaign-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        const data = {
            category_id: parseInt(formData.get('category_id')),
            discount_percentage: parseFloat(formData.get('discount'))
        };

        const result = await postAPI('/campaigns/apply', data);
        if (result) {
            alert(result.message);
            closeCampaignModal();
            loadDashboard();
        }
    });

    document.getElementById('campaign-modal').classList.add('active');
}

function closeCampaignModal() {
    document.getElementById('campaign-modal').classList.remove('active');
}

// Price History Chart
let productPriceChart = null;

async function showPriceChart(productId, productName) {
    const history = await fetchAPI(`/price-history?product_id=${productId}`);
    if (!history || history.length === 0) {
        alert('Bu ürün için fiyat geçmişi bulunamadı.');
        return;
    }

    // Veriyi hazırla (Eskiden yeniye sırala)
    const sortedHistory = history.reverse();
    const labels = sortedHistory.map(h => new Date(h.changedate).toLocaleDateString());
    const data = sortedHistory.map(h => h.newprice);

    document.getElementById('chart-modal-title').textContent = `${productName} - Fiyat Geçmişi`;
    document.getElementById('chart-modal').classList.add('active');

    const ctx = document.getElementById('productPriceChart').getContext('2d');

    if (productPriceChart) productPriceChart.destroy();

    productPriceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fiyat (₺)',
                data: data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

function closeChartModal() {
    document.getElementById('chart-modal').classList.remove('active');
}

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target.id === 'campaign-modal') closeCampaignModal();
    if (e.target.id === 'chart-modal') closeChartModal();
});

// ============================================
// SUPPLIERS
// ============================================

let currentSuppliers = [];

async function loadSuppliers() {
    const data = await fetchAPI('/suppliers');
    if (data) {
        currentSuppliers = data;
        const tbody = document.querySelector('#suppliers-table tbody');
        if (!tbody) return;

        tbody.innerHTML = data.map(s => `
            <tr>
                <td>${s.supplierid}</td>
                <td><strong>${s.companyname}</strong></td>
                <td>${s.contactemail || '-'}</td>
                <td>${s.taxnumber || '-'}</td>
                <td style="max-width: 200px; font-size: 0.85rem;">${s.address || '-'}</td>
                <td>${s.product_count || 0}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editSupplier(${s.supplierid})">Düzenle</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSupplier(${s.supplierid})">Sil</button>
                </td>
            </tr>
        `).join('');
    }
}

async function addSupplier() {
    const companyName = prompt('Şirket Adı:');
    if (!companyName) return;

    const contactEmail = prompt('İletişim Email:');
    const taxNumber = prompt('Vergi Numarası:');
    const address = prompt('Adres:');

    const result = await postAPI('/suppliers', {
        company_name: companyName,
        contact_email: contactEmail || null,
        tax_number: taxNumber || null,
        address: address || null
    });

    if (result) {
        alert('Tedarikçi eklendi!');
        loadSuppliers();
    }
}

async function editSupplier(id) {
    const supplier = currentSuppliers.find(s => s.supplierid === id);
    if (!supplier) return;

    const companyName = prompt('Şirket Adı:', supplier.companyname);
    if (!companyName) return;

    const contactEmail = prompt('İletişim Email:', supplier.contactemail || '');
    const taxNumber = prompt('Vergi Numarası:', supplier.taxnumber || '');
    const address = prompt('Adres:', supplier.address || '');

    const result = await putAPI(`/suppliers/${id}`, {
        company_name: companyName,
        contact_email: contactEmail || null,
        tax_number: taxNumber || null,
        address: address || null
    });

    if (result) {
        alert('Tedarikçi güncellendi!');
        loadSuppliers();
    }
}

async function deleteSupplier(id) {
    if (!confirm('Bu tedarikçiyi silmek istediğinizden emin misiniz?')) return;

    const result = await deleteAPI(`/suppliers/${id}`);
    if (result) {
        alert('Tedarikçi silindi!');
        loadSuppliers();
    }
}

// ============================================
// INITIAL LOAD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
