const API_BASE = '/api';

let cart = [];
let currentUser = null;

// ============================================
// AUTH SYSTEM
// ============================================

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

function checkAuth() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        onLoginSuccess();
    } else {
        showAuthOverlay();
    }
}

function showAuthOverlay() {
    document.getElementById('auth-overlay').classList.remove('hidden');
}

function hideAuthOverlay() {
    document.getElementById('auth-overlay').classList.add('hidden');
}

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-error').style.display = 'none';
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('register-error').style.display = 'none';
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();

        if (response.ok) {
            currentUser = result.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            onLoginSuccess();
        } else {
            errorDiv.textContent = result.detail || 'Giriş başarısız';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Bağlantı hatası';
        errorDiv.style.display = 'block';
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('register-error');

    if (password.length < 6) {
        errorDiv.textContent = 'Şifre en az 6 karakter olmalı';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: name,
                email: email,
                password: password,
                phone_number: phone || null,
                role: 'customer'
            })
        });

        const result = await response.json();

        if (response.ok) {
            // Auto-login after register
            alert('Kayıt başarılı! Şimdi giriş yapabilirsiniz.');
            showLogin();
            document.getElementById('login-email').value = email;
        } else {
            errorDiv.textContent = result.detail || 'Kayıt başarısız';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Bağlantı hatası';
        errorDiv.style.display = 'block';
    }
}

function onLoginSuccess() {
    hideAuthOverlay();
    document.getElementById('user-info').style.display = 'flex';
    document.getElementById('user-display-name').textContent = currentUser.fullname;

    // Show role badge (only for admin and seller)
    const roleBadge = document.getElementById('user-role-badge');
    if (currentUser.role === 'admin' || currentUser.role === 'seller') {
        const roleLabels = { admin: 'Admin', seller: 'Satıcı' };
        roleBadge.textContent = roleLabels[currentUser.role];
        roleBadge.className = 'role-badge ' + currentUser.role;
        roleBadge.style.display = 'inline';
    } else {
        roleBadge.style.display = 'none';
    }

    // Show Dashboard link only for admin
    if (currentUser.role === 'admin') {
        document.getElementById('admin-dashboard-link').style.display = 'inline';
    }

    // Load store data
    loadCategories();
    loadProducts();
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    cart = [];
    updateCartUI();
    showAuthOverlay();
    document.getElementById('user-info').style.display = 'none';
}

// ============================================
// PRODUCTS
// ============================================

async function loadProducts(search = '', category = '') {
    try {
        let url = `${API_BASE}/products?is_active=true&min_stock=1`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (category) url += `&category_id=${category}`;

        const response = await fetch(url);
        const data = await response.json();
        renderProducts(data.products || []);
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const categories = await response.json();
        const select = document.getElementById('category-filter');
        select.innerHTML = '<option value="">Tüm Kategoriler</option>' +
            categories.map(c => `<option value="${c.categoryid}">${c.categoryname}</option>`).join('');

        select.addEventListener('change', (e) => {
            const search = document.getElementById('search-input').value;
            loadProducts(search, e.target.value);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

document.getElementById('search-input').addEventListener('input', (e) => {
    if (!currentUser) return;
    const category = document.getElementById('category-filter').value;
    loadProducts(e.target.value, category);
});

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = products.map(product => {
        return `
        <div class="product-card">
            <div class="product-image">
                <i class="fas fa-box"></i>
            </div>
            <div class="product-info">
                <span class="product-category">${product.category_name || 'Genel'}</span>
                <h3 class="product-title">${product.title}</h3>
                <div class="product-details">
                    <span class="price">₺${Number(product.currentprice).toLocaleString()}</span>
                </div>
                <button class="add-btn" onclick="addToCart(${product.productid}, '${product.title.replace(/'/g, "\\'")}', ${product.currentprice})">
                    Sepete Ekle
                </button>
            </div>
        </div>
        `;
    }).join('');
}

// ============================================
// CART
// ============================================

function toggleCart() {
    document.getElementById('cart-sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

function addToCart(id, title, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ id, title, price, qty: 1 });
    }
    updateCartUI();
    document.getElementById('cart-sidebar').classList.add('active');
    document.getElementById('overlay').classList.add('active');
}

function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    updateCartUI();
}

function updateCartUI() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    const countEl = document.getElementById('cart-count');

    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    countEl.textContent = totalQty;

    if (cart.length === 0) {
        container.innerHTML = '<div class="empty-cart">Sepetiniz boş</div>';
    } else {
        container.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="item-info">
                    <h4>${item.title}</h4>
                    <span class="item-price">${item.qty} x ₺${item.price.toLocaleString()}</span>
                </div>
                <div class="remove-item" onclick="removeFromCart(${item.id})">
                    <i class="fas fa-trash"></i>
                </div>
            </div>
        `).join('');
    }

    const total = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    totalEl.textContent = `₺${total.toLocaleString()}`;
}

// ============================================
// CHECKOUT
// ============================================

async function checkout() {
    if (!currentUser) {
        alert('Lütfen önce giriş yapın!');
        showAuthOverlay();
        return;
    }

    if (cart.length === 0) {
        alert('Sepetiniz boş!');
        return;
    }

    const address = document.getElementById('shipping-address').value;
    if (!address.trim()) {
        alert('Lütfen teslimat adresinizi girin!');
        return;
    }

    const orderData = {
        user_id: currentUser.userid,
        shipping_address: address,
        items: cart.map(item => ({
            product_id: item.id,
            quantity: item.qty
        }))
    };

    try {
        const response = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (response.ok) {
            alert(`Siparişiniz alındı! (Sipariş No: #${result.order_id})\n\nTeşekkürler, ${currentUser.fullname}!`);
            cart = [];
            updateCartUI();
            toggleCart();
            document.getElementById('shipping-address').value = '';
        } else {
            alert('Hata: ' + result.detail);
        }
    } catch (error) {
        console.error('Checkout error:', error);
        alert('Sipariş oluşturulurken bir hata oluştu.');
    }
}
