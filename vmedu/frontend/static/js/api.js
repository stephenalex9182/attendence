const API_URL = '';

class Api {
    static get token() {
        return localStorage.getItem('access_token');
    }

    static async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        return data;
    }

    static async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
        };

        const config = {
            method,
            headers,
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_URL}${endpoint}`, config);

        if (response.status === 401) {
            window.location.href = '/frontend/index.html';
            return;
        }

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'API request failed');
        }

        return response.json();
    }
}
